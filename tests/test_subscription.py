import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from config import Config

pytestmark = pytest.mark.unit


# 1. Token Refresh Testleri (refresh_monthly_tokens)
def test_refresh_monthly_tokens_due(db_session, user):
    """30+ gün geçmiş kullanıcı için aylık fişler yenilenir ve tarih güncellenir."""
    from utils import refresh_monthly_tokens
    # 30+ gün geçmiş kullanıcı için token yenileme
    user.last_token_refresh = datetime.utcnow() - timedelta(days=31)
    user.tokens_remaining = 2
    db_session.commit()

    refresh_monthly_tokens(user)
    db_session.commit()
    db_session.refresh(user)

    expected = Config.SUBSCRIPTION_PLANS[user.subscription_plan]['features']['monthly_tokens']
    assert user.tokens_remaining == expected
    assert user.last_token_refresh is not None


def test_refresh_monthly_tokens_not_due(db_session, user):
    """30 günden az zamanda yenileme yapılmaz; fiş sayısı değişmez."""
    from utils import refresh_monthly_tokens
    user.last_token_refresh = datetime.utcnow() - timedelta(days=15)
    user.tokens_remaining = 5
    db_session.commit()

    refresh_monthly_tokens(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.tokens_remaining == 5


def test_refresh_monthly_tokens_first_time(db_session, user):
    """İlk yenilemede aylık fişler atanır ve tarih belirlenir."""
    from utils import refresh_monthly_tokens
    user.last_token_refresh = None
    user.tokens_remaining = 0
    db_session.commit()

    refresh_monthly_tokens(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.tokens_remaining > 0
    assert user.last_token_refresh is not None


def test_refresh_monthly_tokens_different_plans(db_session):
    """Farklı planlarda doğru aylık fiş sayısı atanır."""
    from models import User
    from utils import refresh_monthly_tokens

    for plan in ['free', 'standard', 'premium']:
        test_user = User(
            email=f'{plan}@example.com',
            username=f'{plan}user',
            subscription_plan=plan,
            tokens_remaining=0,
            trial_ends_at=datetime.utcnow() + timedelta(days=7)
        )
        test_user.set_password('Test123!')
        db_session.add(test_user)
        db_session.commit()

        refresh_monthly_tokens(test_user)
        db_session.commit()
        db_session.refresh(test_user)
        expected = Config.SUBSCRIPTION_PLANS[plan]['features']['monthly_tokens']
        assert test_user.tokens_remaining == expected


# 2. Trial Period Testleri (is_trial_active, initialize_user_tokens)
def test_trial_active(user):
    """Deneme süresi bitmemiş kullanıcı için trial aktiftir."""
    from utils import is_trial_active
    user.trial_ends_at = datetime.utcnow() + timedelta(days=3)
    assert is_trial_active(user) is True


def test_trial_expired(user):
    """Denemesi bitmiş kullanıcı için trial aktif değildir."""
    from utils import is_trial_active
    user.trial_ends_at = datetime.utcnow() - timedelta(days=1)
    assert is_trial_active(user) is False


def test_trial_no_end_date_premium(premium_user):
    """Premium kullanıcıda trial tarih yoksa aktif kabul edilmez."""
    from utils import is_trial_active
    premium_user.trial_ends_at = None
    assert is_trial_active(premium_user) is False


def test_initialize_user_tokens_free_plan(db_session):
    """Free plan kullanıcı için başlangıç fişleri ve trial atanır."""
    from models import User
    from utils import initialize_user_tokens
    u = User(
        email='freeinit@example.com',
        username='freeinit',
        subscription_plan='free',
        tokens_remaining=0,
        trial_ends_at=None
    )
    u.set_password('Test123!')
    db_session.add(u)
    db_session.commit()

    initialize_user_tokens(u)
    db_session.commit()
    db_session.refresh(u)
    assert u.tokens_remaining == 10
    assert u.trial_ends_at is not None
    assert 6 <= (u.trial_ends_at - datetime.utcnow()).days <= 8


def test_initialize_user_tokens_premium_plan(db_session):
    """Premium plan kullanıcı için trial fişleri atanır (plan bağımsız)."""
    from models import User
    from utils import initialize_user_tokens
    u = User(
        email='premiuminit@example.com',
        username='premiuminit',
        subscription_plan='premium',
        tokens_remaining=0,
        trial_ends_at=None
    )
    u.set_password('Test123!')
    db_session.add(u)
    db_session.commit()

    initialize_user_tokens(u)
    db_session.commit()
    db_session.refresh(u)
    # initialize_user_tokens deneme fişlerini atar (plan bağımsız)
    assert u.tokens_remaining == 10
    assert u.trial_ends_at is not None


# 3. Token Cost Calculation Testleri (calculate_token_cost)
def test_calculate_token_cost_all_question_types():
    """Tüm soru türleri seçildiğinde toplam maliyet doğru hesaplanır."""
    from utils import calculate_token_cost
    cost = calculate_token_cost(question_types=None, include_export=False, user_plan='free')
    assert cost == 3.0


def test_calculate_token_cost_partial_question_types():
    """Kısmi soru türlerinde maliyet doğru artar."""
    from utils import calculate_token_cost
    cost = calculate_token_cost(question_types=['multiple_choice', 'short_answer'], include_export=False, user_plan='free')
    assert cost == 2.0


def test_calculate_token_cost_with_export_free():
    """Free planda export dahil olunca maliyet artar."""
    from utils import calculate_token_cost
    cost = calculate_token_cost(question_types=None, include_export=True, user_plan='free')
    assert cost == 5.0


def test_calculate_token_cost_with_export_premium():
    """Premium planda export ücretsiz olduğundan toplam maliyet düşer."""
    from utils import calculate_token_cost
    cost = calculate_token_cost(question_types=None, include_export=True, user_plan='premium')
    assert cost == 3.0


# 4. Token Deduction & Addition Testleri
def test_deduct_tokens_sufficient(db_session, user):
    """Yeterli fiş varsa düşüldükten sonra kalan doğru olur."""
    from utils import deduct_tokens
    user.tokens_remaining = 10
    db_session.commit()
    deduct_tokens(user, 3)
    db_session.commit()
    db_session.refresh(user)
    assert user.tokens_remaining == 7


def test_deduct_tokens_exact_amount(db_session, user):
    """Tam miktar düşüldüğünde kalan sıfır olur."""
    from utils import deduct_tokens
    user.tokens_remaining = 5
    db_session.commit()
    deduct_tokens(user, 5)
    db_session.commit()
    db_session.refresh(user)
    assert user.tokens_remaining == 0


def test_deduct_tokens_insufficient_protection(db_session, user):
    """Yetersiz fişte negatif olmadan sıfıra çekilir."""
    from utils import deduct_tokens
    user.tokens_remaining = 2
    db_session.commit()
    deduct_tokens(user, 5)
    db_session.commit()
    db_session.refresh(user)
    assert user.tokens_remaining == 0


def test_add_tokens(db_session, user):
    """Fiş ekleme doğru şekilde artırır."""
    from utils import add_tokens
    user.tokens_remaining = 5
    db_session.commit()
    add_tokens(user, 10)
    db_session.commit()
    db_session.refresh(user)
    assert user.tokens_remaining == 15


# 5. Plan Upgrade/Downgrade Testleri
def test_plan_upgrade_free_to_premium(db_session, user):
    """Free'den premium'a yükseltme ve fiş ekleme sonrası değerler doğru olur."""
    from utils import add_tokens
    user.subscription_plan = 'free'
    user.tokens_remaining = 2
    db_session.commit()

    user.subscription_plan = 'premium'
    add_tokens(user, 60)
    db_session.commit()
    db_session.refresh(user)
    assert user.subscription_plan == 'premium'
    assert user.tokens_remaining == 62


def test_plan_downgrade_premium_to_free(db_session, premium_user):
    """Premium'dan free'e dönüşte plan güncellenir ve fişler korunur."""
    premium_user.subscription_plan = 'free'
    db_session.commit()
    assert premium_user.subscription_plan == 'free'
    assert premium_user.tokens_remaining == 60


# 6. Subscription Activation Testleri (activate_subscription)
def test_activate_subscription_success(db_session, user):
    """Tamamlanmış ödeme ile abonelik aktif edilir ve kullanıcı planı güncellenir."""
    from models import Payment, Subscription
    from utils import activate_user_subscription

    payment = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='completed',
        plan_type='premium',
        billing_period='monthly'
    )
    db_session.add(payment)
    db_session.commit()

    success, sub, err = activate_user_subscription(user.id, 'premium', payment.id)
    assert success is True
    assert sub is not None
    db_session.refresh(user)
    assert user.subscription_plan == 'premium'
    p = Payment.query.get(payment.id)
    assert p is not None


def test_activate_subscription_idempotency(db_session, user):
    """Aynı ödeme ile birden çok çağrıda aynı abonelik döner (idempotent)."""
    from models import Payment
    from utils import activate_user_subscription

    payment = Payment(
        user_id=user.id,
        amount=49.99,
        currency='TRY',
        status='completed',
        plan_type='premium',
        billing_period='monthly'
    )
    db_session.add(payment)
    db_session.commit()

    success1, first, _ = activate_user_subscription(user.id, 'premium', payment.id)
    success2, second, _ = activate_user_subscription(user.id, 'premium', payment.id)
    assert success1 and success2
    assert first.id == second.id


def test_activate_subscription_invalid_payment(db_session, user):
    """Geçersiz ödeme id'si ile abonelik aktive edilemez; hata mesajı döner."""
    from utils import activate_user_subscription
    success, sub, err = activate_user_subscription(user.id, 'premium', 9999)
    assert success is False
    assert sub is None
    assert isinstance(err, str)


# 7. Export Permission Testleri (can_user_export)
def test_can_user_export_free_sufficient_tokens(user):
    """Free planda yeterli fiş varsa export mümkün olur."""
    from utils import can_user_export
    user.subscription_plan = 'free'
    user.tokens_remaining = 5
    can_export, error_msg, required = can_user_export(user)
    assert can_export is True
    assert required == 2


def test_can_user_export_free_insufficient_tokens(user):
    """Free planda yetersiz fişte export engellenir ve mesaj döner."""
    from utils import can_user_export
    user.subscription_plan = 'free'
    user.tokens_remaining = 1
    user.last_token_refresh = datetime.utcnow()
    can_export, error_msg, required = can_user_export(user)
    assert can_export is False
    assert error_msg is None or ('fiş' in error_msg.lower() or 'token' in error_msg.lower() or 'yetersiz' in error_msg.lower())


def test_can_user_export_premium(premium_user):
    """Premium planda export ücretsizdir; gereken fiş 0 olur."""
    from utils import can_user_export
    can_export, error_msg, required = can_user_export(premium_user)
    assert can_export is True
    assert required == 0


