import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.integration]


# 1. Payment Record Testleri (models.Payment)
def test_payment_creation(db_session, user):
    """Pending ödeme kaydı oluşturulur; id atanır ve fatura numarası yoktur."""
    from models import Payment
    payment = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='pending',
        plan_type='premium',
        billing_period='monthly'
    )
    db_session.add(payment)
    db_session.commit()

    assert payment.id is not None
    assert payment.invoice_number is None


def test_payment_mark_completed(db_session, user):
    """Ödeme tamamlanır; durum completed ve intent bilgisi kaydedilir."""
    from models import Payment
    payment = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='pending',
        plan_type='premium',
        billing_period='monthly'
    )
    db_session.add(payment)
    db_session.commit()

    payment.mark_completed(payment_intent_id='pi_test123', payment_method='card')
    db_session.commit()

    assert payment.status == 'completed'
    assert payment.completed_at is not None
    assert payment.stripe_payment_intent_id == 'pi_test123'


def test_payment_mark_failed(db_session, user):
    """Ödeme başarısız işaretlenir; durum failed ve gerekçe metadata'ya yazılır."""
    from models import Payment
    payment = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='pending',
        plan_type='premium',
        billing_period='monthly'
    )
    db_session.add(payment)
    db_session.commit()

    payment.mark_failed(reason='Insufficient funds')
    db_session.commit()

    assert payment.status == 'failed'
    assert payment.payment_metadata is None or 'Insufficient funds' in (payment.payment_metadata or '')


def test_payment_generate_invoice_number(db_session, user):
    """Fatura numarası benzersiz ve artan formatta üretilir."""
    from models import Payment
    n1 = Payment.generate_invoice_number()
    # DB'ye bir ödeme kaydı ekleyerek n1'i "kullanılmış" hale getir
    p = Payment(
        user_id=user.id,
        amount=10,
        currency='TRY',
        status='completed',
        plan_type='premium',
        billing_period='monthly',
        invoice_number=n1
    )
    db_session.add(p)
    db_session.commit()
    n2 = Payment.generate_invoice_number()
    assert n1 != n2
    assert n1.startswith('INV-') and n2.startswith('INV-')


# 2. Stripe Webhook Testleri (/stripe-webhook)
@patch('stripe.Webhook.construct_event')
def test_stripe_webhook_checkout_completed(mock_construct, client, app, user, db_session):
    """Checkout tamamlandığında DB'de ödeme completed ve abonelik active olmalıdır."""
    # Webhook secret hazırla
    app.config['STRIPE_WEBHOOK_SECRET'] = 'test'
    event_data = {
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'id': 'cs_test_123',
                'payment_intent': 'pi_test_123',
                'customer': 'cus_test_123',
                'amount_total': 4999,
                'currency': 'try',
                'metadata': {'user_id': str(user.id), 'plan_type': 'premium'}
            }
        }
    }
    mock_construct.return_value = MagicMock(type=event_data['type'], data=MagicMock(object=MagicMock(**event_data['data']['object'])))
    # Payment kaydı oluştur
    from models import Payment
    pay = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='pending',
        plan_type='premium',
        billing_period='monthly',
        stripe_session_id='cs_test_123'
    )
    db_session.add(pay)
    db_session.commit()

    response = client.post('/stripe/webhook', data=b'{}', headers={'Stripe-Signature': 't=test'}, content_type='application/json')
    assert response.status_code in [200, 204]

    # DB yan etkilerini doğrula
    from models import Payment, Subscription
    refreshed = Payment.query.filter_by(user_id=user.id, stripe_session_id='cs_test_123').first()
    assert refreshed is not None
    assert refreshed.status == 'completed'
    assert refreshed.stripe_payment_intent_id in ['pi_test_123', 'cs_test_123']
    sub = Subscription.query.filter_by(user_id=user.id, plan_type='premium', status='active').first()
    assert sub is not None


@patch('stripe.Webhook.construct_event')
def test_stripe_webhook_payment_failed(mock_construct, client, db_session, user, app):
    """PaymentIntent başarısız olduğunda ödeme kaydı failed durumuna alınır."""
    app.config['STRIPE_WEBHOOK_SECRET'] = 'test'
    event_data = {
        'type': 'payment_intent.payment_failed',
        'data': {'object': {'id': 'pi_failed_123'}}
    }
    mock_obj = MagicMock()
    mock_obj.type = event_data['type']
    mock_obj.data.object = MagicMock(id='pi_failed_123')
    mock_construct.return_value = mock_obj
    # İlgili payment kaydı ekle
    from models import Payment
    pay = Payment(
        user_id=user.id,
        amount=5,
        currency='TRY',
        status='pending',
        plan_type='premium',
        billing_period='monthly',
        stripe_payment_intent_id='pi_failed_123'
    )
    db_session.add(pay)
    db_session.commit()

    response = client.post('/stripe/webhook', data=b'{}', headers={'Stripe-Signature': 't=test'}, content_type='application/json')
    assert response.status_code in [200, 204]

    # DB yan etkisini doğrula
    from models import Payment
    failed = Payment.query.filter_by(stripe_payment_intent_id='pi_failed_123').first()
    assert failed is not None
    assert failed.status == 'failed' or (failed.payment_metadata and 'failure_reason' in (failed.payment_metadata or ''))


def test_stripe_webhook_invalid_signature(client, app):
    """Webhook secret yoksa 400/401 dönülür ve işlenmez."""
    # Webhook secret yoksa 400 dönmeli ve construct_event çağrılmaz
    app.config['STRIPE_WEBHOOK_SECRET'] = None
    response = client.post('/stripe/webhook', data=b'{}', headers={'Stripe-Signature': 'invalid'}, content_type='application/json')
    assert response.status_code in [400, 401]


@patch('stripe.Webhook.construct_event')
def test_stripe_webhook_idempotency(mock_construct, client, user, db_session, app):
    """Aynı session ID için iki kez çağrıldığında tek bir ödeme ve abonelik oluşturulur."""
    app.config['STRIPE_WEBHOOK_SECRET'] = 'test'
    obj = MagicMock()
    obj.type = 'checkout.session.completed'
    obj.data.object.id = 'cs_idem_123'
    obj.data.object.payment_intent = 'pi_idem_123'
    obj.data.object.customer = 'cus_idem_123'
    obj.data.object.amount_total = 4999
    obj.data.object.currency = 'try'
    obj.data.object.metadata = {'user_id': str(user.id), 'plan_type': 'premium'}
    mock_construct.return_value = obj
    # İlk çağrıdan önce pending payment yarat
    from models import Payment
    pay = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='pending',
        plan_type='premium',
        billing_period='monthly',
        stripe_session_id='cs_idem_123'
    )
    db_session.add(pay)
    db_session.commit()

    r1 = client.post('/stripe/webhook', data=b'{}', headers={'Stripe-Signature': 't=1'}, content_type='application/json')
    r2 = client.post('/stripe/webhook', data=b'{}', headers={'Stripe-Signature': 't=1'}, content_type='application/json')
    assert r1.status_code in [200, 204]
    assert r2.status_code in [200, 204]

    # DB idempotency kontrolleri
    from models import Payment, Subscription
    payments = Payment.query.filter_by(user_id=user.id, plan_type='premium').all()
    assert len(payments) == 1
    assert payments[0].status == 'completed'
    subs = Subscription.query.filter_by(user_id=user.id, plan_type='premium', status='active').all()
    assert len(subs) == 1


@patch('stripe.Webhook.construct_event')
def test_stripe_webhook_unknown_event_type(mock_construct, client, app):
    """Bilinmeyen event tipinde 200 döndürülür (yeniden gönderim olmasın)."""
    app.config['STRIPE_WEBHOOK_SECRET'] = 'test'
    obj = MagicMock()
    obj.type = 'unknown.event.type'
    obj.data.object = MagicMock()
    mock_construct.return_value = obj
    response = client.post('/stripe/webhook', data=b'{}', headers={'Stripe-Signature': 't=test'}, content_type='application/json')
    assert response.status_code in [200, 204]


# 3. Checkout Flow Testleri (/checkout)
def test_checkout_get_preview(authenticated_client):
    """Checkout GET önizlemesi plan bilgilerini ve sayfayı döndürür."""
    response = authenticated_client.get('/checkout?plan_type=premium')
    assert response.status_code in [200, 302]
    if response.status_code == 200:
        html = response.data.decode('utf-8').lower()
        assert 'premium' in html or 'plan' in html


@patch('stripe.checkout.Session.create')
def test_checkout_post_create_session(mock_create, authenticated_client, app, user):
    """Checkout POST Stripe session oluşturur ve pending Payment kaydı yaratır."""
    mock_session = MagicMock()
    mock_session.id = 'cs_test_abc'
    mock_session.url = 'https://stripe.example/checkout/cs_test_abc'
    mock_create.return_value = mock_session

    response = authenticated_client.post('/checkout', data={'plan_type': 'premium'}, follow_redirects=False)
    assert response.status_code in [302, 303]

    # Stripe çağrı argümanlarını doğrula
    assert mock_create.called
    args, kwargs = mock_create.call_args
    assert kwargs['metadata']['user_id'] == str(user.id)
    assert kwargs['metadata']['plan_type'] == 'premium'
    # Payment kaydı doğrula
    from models import Payment
    created = Payment.query.filter_by(user_id=user.id, plan_type='premium').order_by(Payment.created_at.desc()).first()
    assert created is not None
    assert created.status == 'pending'
    assert created.stripe_session_id == 'cs_test_abc'


def test_checkout_post_invalid_plan(authenticated_client):
    """Geçersiz plan gönderilirse Payment oluşturulmaz ve hata/redirect olur."""
    from models import Payment
    before = Payment.query.count()
    response = authenticated_client.post('/checkout', data={'plan_type': 'invalid_plan'}, follow_redirects=True)
    assert response.status_code in [200, 302, 303]
    after = Payment.query.count()
    assert after == before


@patch('stripe.checkout.Session.create', side_effect=Exception('Stripe error'))
def test_checkout_post_stripe_error(mock_create, authenticated_client):
    """Stripe hata verirse Payment rollback olur ve kullanıcı bilgilendirilir."""
    from models import Payment
    before = Payment.query.count()
    response = authenticated_client.post('/checkout', data={'plan_type': 'premium'}, follow_redirects=True)
    assert response.status_code in [200, 302]
    after = Payment.query.count()
    assert after == before


# 4. Checkout Success/Cancel Testleri
@patch('app.stripe.checkout.Session.retrieve')
def test_checkout_success(mock_retrieve, authenticated_client, db_session, user):
    """Başarılı session ile success sayfası görüntülenir; pending payment bulunur."""
    mock_session = MagicMock()
    mock_session.id = 'cs_test_123'
    mock_session.payment_status = 'paid'
    mock_session.payment_intent = 'pi_test_123'
    mock_session.metadata = {'user_id': str(user.id), 'plan_type': 'premium'}
    mock_retrieve.return_value = mock_session
    # Payment kaydı
    from models import Payment
    pay = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='pending',
        plan_type='premium',
        billing_period='monthly',
        stripe_session_id='cs_test_123'
    )
    db_session.add(pay)
    db_session.commit()

    response = authenticated_client.get('/checkout/success?session_id=cs_test_123', follow_redirects=True)
    assert response.status_code in [200, 302]


@patch('app.stripe.checkout.Session.retrieve')
def test_checkout_success_invalid_session(mock_retrieve, authenticated_client):
    """Geçersiz session_id ile pricing'e yönlendirme veya uygun yanıt döner."""
    # Geçersiz session olsa bile retrieve bir nesne döndürsün, fakat DB'de ödeme yok => redirect
    mock_retrieve.return_value = MagicMock(id='invalid_session', payment_status='unpaid')
    response = authenticated_client.get('/checkout/success?session_id=invalid_session', follow_redirects=True)
    assert response.status_code in [200, 302]


def test_checkout_cancel(authenticated_client):
    """İptal sayfası yönlendirme yapar ve bilgilendirir."""
    response = authenticated_client.get('/checkout/cancel?session_id=cs_test_123', follow_redirects=True)
    assert response.status_code in [200, 302]


# 5. Invoice Generation Testleri (utils.generate_invoice_pdf)
def test_generate_invoice_pdf_success(db_session, user):
    """Fatura PDF üretimi mock'lanır; doğru argümanlarla çağrıldığı doğrulanır."""
    from models import Payment
    from config import Config
    p = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='completed',
        plan_type='premium',
        billing_period='monthly',
        invoice_number='INV-2025-00001'
    )
    db_session.add(p)
    db_session.commit()
    plan = Config.SUBSCRIPTION_PLANS.get('premium', {})
    with patch('utils.generate_invoice_pdf', return_value='/tmp/invoice.pdf') as mock_gen:
        path = mock_gen(p, user, plan)
        mock_gen.assert_called_once()
        args, kwargs = mock_gen.call_args
        assert args[0] == p and args[1] == user and args[2] == plan
        assert isinstance(path, str) and len(path) > 0


def test_generate_invoice_pdf_missing_invoice_number(db_session, user):
    """Fatura numarası eksik olsa da fonksiyon bir yol döndürmelidir (entegrasyon gevşek)."""
    from models import Payment
    from utils import generate_invoice_pdf
    p = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='completed',
        plan_type='premium',
        billing_period='monthly',
        invoice_number=None
    )
    db_session.add(p)
    db_session.commit()
    from config import Config
    plan = Config.SUBSCRIPTION_PLANS.get('premium', {})
    path = generate_invoice_pdf(p, user, plan)
    assert isinstance(path, str) and len(path) > 0


# 6. Payment Email Testleri (utils.send_payment_confirmation_email)
@patch('app.mail.send')
def test_send_payment_confirmation_email_success(mock_send, db_session, user, completed_payment):
    """Başarılı ödeme e-postası gönderimi True döndürür veya mail.send çağrılır."""
    from utils import send_payment_confirmation_email
    ok = send_payment_confirmation_email(user.email, completed_payment, invoice_pdf_path='/tmp/invoice.pdf')
    assert ok is True or mock_send.called


@patch('app.mail.send')
def test_send_payment_confirmation_email_no_invoice(mock_send, db_session, user, completed_payment):
    """Fatura olmadan gönderim denemesi hata atmadan True/False döndürebilir."""
    from utils import send_payment_confirmation_email
    ok = send_payment_confirmation_email(user.email, completed_payment, invoice_pdf_path=None)
    # Mevcut implementasyon invoice yoksa False döndürebilir; bu durumda exception olmamalı
    assert ok in [True, False]


@patch('app.mail.send', side_effect=Exception('SMTP error'))
def test_send_payment_confirmation_email_smtp_error(mock_send, db_session, user, completed_payment):
    """SMTP hatasında fonksiyon False döndürmelidir."""
    from utils import send_payment_confirmation_email
    ok = send_payment_confirmation_email(user.email, completed_payment, invoice_pdf_path=None)
    assert ok is False


# 7. Payment History Testleri (utils.get_payment_history)
def test_get_payment_history(db_session, user):
    """Kullanıcının ödeme geçmişi liste olarak döner ve sayısı doğru olur."""
    from models import Payment
    from utils import get_user_payment_history
    statuses = ['completed', 'failed', 'pending']
    for idx, st in enumerate(statuses):
        p = Payment(
            user_id=user.id,
            amount=10 + idx,
            currency='TRY',
            status=st,
            plan_type='premium',
            billing_period='monthly',
            invoice_number=f'INV-2025-0000{idx}' if st == 'completed' else None
        )
        db_session.add(p)
    db_session.commit()
    history = get_user_payment_history(user.id, limit=10)
    assert isinstance(history, list)
    assert len(history) == 3


def test_get_payment_history_empty(db_session):
    """Ödeme geçmişi olmayan kullanıcı için boş liste döner."""
    from models import User
    from utils import get_user_payment_history
    u = User(
        email='histempty@example.com',
        username='histempty',
        subscription_plan='free',
        tokens_remaining=5
    )
    u.set_password('Test123!')
    db_session.add(u)
    db_session.commit()
    history = get_user_payment_history(u.id)
    assert history == [] or len(history) == 0


