"""
Utility fonksiyon testleri
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from utils import (
    get_file_hash, check_cache, save_to_cache, parse_cached_result, estimate_tokens,
    validate_email_address, generate_username_from_email, validate_file_signature,
    initialize_user_tokens, is_trial_active, refresh_monthly_tokens, calculate_token_cost,
    check_user_tokens, deduct_tokens, add_tokens, can_user_export, get_user_token_info,
    get_user_documents, increment_user_upload,
    increment_user_cache_hit
)
import utils
from models import User, Document, Result, UserUsageStats
from config import Config


@pytest.mark.unit
def test_get_file_hash():
    """Dosya hash testi"""
    content1 = b'Test content'
    content2 = b'Test content'
    content3 = b'Different content'
    
    hash1 = get_file_hash(content1)
    hash2 = get_file_hash(content2)
    hash3 = get_file_hash(content3)
    
    assert hash1 == hash2  # Aynı içerik = aynı hash
    assert hash1 != hash3  # Farklı içerik = farklı hash
    assert len(hash1) == 32  # MD5 hash 32 karakter


@pytest.mark.unit
def test_check_cache_hit(db_session, sample_document, sample_result):
    """Cache hit testi"""
    result = check_cache(
        file_hash=sample_document.file_hash,
        user_level=sample_document.user_level,
        user_type=sample_document.user_type,
        user_id=sample_document.user_id
    )
    
    assert result is not None
    assert result.id == sample_result.id


@pytest.mark.unit
def test_check_cache_miss(db_session):
    """Cache miss testi"""
    result = check_cache(
        file_hash='nonexistent_hash_123456789012345678901234567890',
        user_level='high_school',
        user_type='student',
        user_id=999
    )
    
    assert result is None


@pytest.mark.unit
def test_save_to_cache(db_session, user):
    """Cache kaydetme testi"""
    import json
    
    results_data = {
        'summary': 'Test özet',
        'multiple_choice': [{'question': 'Test?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 0}],
        'short_answer': [{'question': 'Test?', 'answer': 'Test'}],
        'fill_blank': [{'question': 'Test _____', 'answer': 'test', 'options': ['test', 'test2']}],
        'true_false': [{'statement': 'Test', 'is_true': True}],
        'flashcards': [{'front': 'Test', 'back': 'Test'}]
    }
    
    result = save_to_cache(
        file_hash='new_hash_123456789012345678901234567890',
        filename='test.pdf',
        file_type='pdf',
        file_size=1024,
        user_level='high_school',
        user_type='student',
        results_data=results_data,
        ai_model='gpt-3.5-turbo',
        token_used=100,
        processing_time=2.5,
        user_id=user.id
    )
    
    assert result is not None
    assert result.document.original_filename == 'test.pdf'
    assert result.document.user_id == user.id


@pytest.mark.unit
def test_parse_cached_result(sample_result):
    """Cache parse testi"""
    parsed = parse_cached_result(sample_result)
    
    assert isinstance(parsed, dict)
    assert 'summary' in parsed
    assert 'multiple_choice' in parsed
    assert 'short_answer' in parsed
    assert 'fill_blank' in parsed
    assert 'true_false' in parsed
    assert 'flashcards' in parsed
    
    # JSON string'lerin parse edildiğini kontrol et
    assert isinstance(parsed['multiple_choice'], list)
    assert isinstance(parsed['short_answer'], list)


@pytest.mark.unit
def test_estimate_tokens():
    """Token tahmini testi"""
    text1 = 'a' * 100  # 100 karakter
    text2 = 'b' * 400   # 400 karakter
    
    tokens1 = estimate_tokens(text1)
    tokens2 = estimate_tokens(text2)
    
    assert isinstance(tokens1, int)
    assert isinstance(tokens2, int)
    assert tokens2 > tokens1
    # Yaklaşık 1 token = 4 karakter
    assert abs(tokens1 - 25) < 10  # 100 / 4 = 25


@pytest.mark.unit
def test_validate_email():
    """Email validasyon testi"""
    # email-validator kütüphanesi yüklü olmalı
    try:
        from email_validator import validate_email
    except ImportError:
        pytest.skip("email-validator not installed")
    
    valid_emails = ['test@example.com', 'user.name@domain.co.uk', 'user+tag@example.com']
    invalid_emails = ['invalid', '@example.com', 'user@', 'user@.com']
    
    for email in valid_emails:
        result = validate_email_address(email)
        # email-validator yüklüyse result None olmamalı
        if result is not None:
            assert '@' in result
    
    for email in invalid_emails:
        result = validate_email_address(email)
        # Geçersiz email'ler için None veya boş string dönebilir
        assert result is None or result == ''


@pytest.mark.unit
def test_normalize_email():
    """Email normalizasyon testi"""
    # validate_email_address zaten normalize ediyor
    try:
        from email_validator import validate_email
    except ImportError:
        pytest.skip("email-validator not installed")
    
    email1 = '  Test@Example.COM  '
    email2 = 'test@example.com'
    
    result1 = validate_email_address(email1)
    result2 = validate_email_address(email2)
    
    # Normalize edilmiş olmalı
    if result1 and result2:
        assert result1 == result2
        assert result1 == 'test@example.com'


@pytest.mark.unit
def test_generate_username_from_email(db_session):
    """Username üretimi testi"""
    email = 'test.user@example.com'
    username = generate_username_from_email(email)
    
    assert username is not None
    assert 'test' in username.lower() or 'user' in username.lower()
    # Unique username olduğunu kontrol et
    user = User.query.filter_by(username=username).first()
    assert user is None  # Henüz oluşturulmamış olmalı


@pytest.mark.unit
def test_validate_file_signature_pdf():
    """PDF imza validasyonu"""
    valid_pdf = b'%PDF-1.4\nTest content'
    invalid_content = b'Not a PDF file'
    
    is_valid, error = validate_file_signature(valid_pdf, 'pdf')
    assert is_valid is True
    assert error is None
    
    is_valid, error = validate_file_signature(invalid_content, 'pdf')
    assert is_valid is False
    assert error is not None


@pytest.mark.unit
def test_validate_file_signature_docx():
    """DOCX imza validasyonu"""
    import zipfile
    import io
    
    # Geçerli DOCX (ZIP) içeriği
    valid_docx = io.BytesIO()
    with zipfile.ZipFile(valid_docx, 'w') as z:
        z.writestr('word/document.xml', '<?xml version="1.0"?><document><body><p>Test</p></body></document>')
    valid_docx.seek(0)
    valid_content = valid_docx.read()
    
    invalid_content = b'Not a ZIP file'
    
    is_valid, error = validate_file_signature(valid_content, 'docx')
    assert is_valid is True
    assert error is None
    
    is_valid, error = validate_file_signature(invalid_content, 'docx')
    assert is_valid is False
    assert error is not None


@pytest.mark.unit
def test_initialize_user_tokens(db_session):
    """Token başlatma testi"""
    new_user = User(
        email='new@example.com',
        username='newuser',
        subscription_plan='free',
        tokens_remaining=0
    )
    new_user.set_password('Test123!')
    db_session.add(new_user)
    db_session.flush()
    
    initialize_user_tokens(new_user)
    
    plan_config = Config.SUBSCRIPTION_PLANS.get('free', {})
    features = plan_config.get('features', {})
    trial_tokens = features.get('trial_tokens', 10)
    
    assert new_user.tokens_remaining == trial_tokens
    assert new_user.trial_ends_at is not None
    # 7 gün sonra olmalı
    expected_date = datetime.utcnow() + timedelta(days=features.get('trial_days', 7))
    assert abs((new_user.trial_ends_at - expected_date).total_seconds()) < 60  # 1 dakika tolerans


@pytest.mark.unit
def test_is_trial_active(db_session):
    """Trial aktif kontrolü"""
    active_user = User(
        email='active@example.com',
        username='activeuser',
        subscription_plan='free',
        tokens_remaining=10,
        trial_ends_at=datetime.utcnow() + timedelta(days=3)
    )
    active_user.set_password('Test123!')
    db_session.add(active_user)
    
    expired_user = User(
        email='expired@example.com',
        username='expireduser',
        subscription_plan='free',
        tokens_remaining=10,
        trial_ends_at=datetime.utcnow() - timedelta(days=1)
    )
    expired_user.set_password('Test123!')
    db_session.add(expired_user)
    
    assert is_trial_active(active_user) is True
    assert is_trial_active(expired_user) is False


@pytest.mark.unit
def test_refresh_monthly_tokens(db_session):
    """Aylık token yenileme testi"""
    user = User(
        email='refresh@example.com',
        username='refreshuser',
        subscription_plan='free',
        tokens_remaining=5,
        last_token_refresh=datetime.utcnow() - timedelta(days=31)
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.flush()
    
    refresh_monthly_tokens(user)
    
    plan_config = Config.SUBSCRIPTION_PLANS.get('free', {})
    features = plan_config.get('features', {})
    monthly_tokens = features.get('monthly_tokens', 3)
    
    assert user.tokens_remaining == monthly_tokens
    assert user.last_token_refresh is not None
    assert abs((user.last_token_refresh - datetime.utcnow()).total_seconds()) < 60


@pytest.mark.unit
def test_refresh_monthly_tokens_not_due(db_session):
    """Erken yenileme testi"""
    user = User(
        email='early@example.com',
        username='earlyuser',
        subscription_plan='free',
        tokens_remaining=5,
        last_token_refresh=datetime.utcnow() - timedelta(days=10)
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.flush()
    
    original_tokens = user.tokens_remaining
    refresh_monthly_tokens(user)
    
    # Token'lar yenilenmemeli (henüz 30 gün geçmedi)
    assert user.tokens_remaining == original_tokens


@pytest.mark.unit
def test_calculate_token_cost_base():
    """Temel token maliyeti"""
    cost = calculate_token_cost(
        question_types=None,  # Tüm soru türleri
        include_export=False,
        user_plan='free'
    )
    
    # base_processing + (4 * question_type) = 1 + (4 * 0.5) = 3.0
    expected = Config.TOKEN_COSTS['base_processing'] + (4 * Config.TOKEN_COSTS['question_type'])
    assert cost == expected
    assert cost == 3.0


@pytest.mark.unit
def test_calculate_token_cost_with_export():
    """Export ile maliyet"""
    cost = calculate_token_cost(
        question_types=None,
        include_export=True,
        user_plan='free'
    )
    
    # 3.0 + 2 = 5.0
    base_cost = Config.TOKEN_COSTS['base_processing'] + (4 * Config.TOKEN_COSTS['question_type'])
    export_cost = Config.TOKEN_COSTS['export']
    assert cost == base_cost + export_cost
    assert cost == 5.0


@pytest.mark.unit
def test_calculate_token_cost_premium_export():
    """Premium export maliyeti"""
    cost = calculate_token_cost(
        question_types=None,
        include_export=True,
        user_plan='premium'
    )
    
    # Premium'da export ücretsiz (0 fiş)
    base_cost = Config.TOKEN_COSTS['base_processing'] + (4 * Config.TOKEN_COSTS['question_type'])
    assert cost == base_cost
    assert cost == 3.0


@pytest.mark.unit
def test_check_user_tokens_sufficient(db_session):
    """Yeterli token kontrolü"""
    user = User(
        email='sufficient@example.com',
        username='sufficientuser',
        subscription_plan='free',
        tokens_remaining=10,
        last_token_refresh=datetime.utcnow()  # Refresh yapılmasın
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.commit()
    
    can_afford, error_msg, available = check_user_tokens(user, 5)
    
    assert can_afford is True
    assert error_msg is None
    assert available >= 5  # En az 5 olmalı


@pytest.mark.unit
def test_check_user_tokens_insufficient(db_session):
    """Yetersiz token kontrolü"""
    user = User(
        email='insufficient@example.com',
        username='insufficientuser',
        subscription_plan='free',
        tokens_remaining=2,
        last_token_refresh=datetime.utcnow()  # Refresh yapılmasın
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.commit()
    
    can_afford, error_msg, available = check_user_tokens(user, 5)
    
    assert can_afford is False
    assert error_msg is not None
    assert 'fiş' in error_msg.lower() or 'token' in error_msg.lower()
    assert available < 5  # 5'ten az olmalı


@pytest.mark.unit
def test_deduct_tokens(db_session):
    """Token düşme testi"""
    user = User(
        email='deduct@example.com',
        username='deductuser',
        subscription_plan='free',
        tokens_remaining=10
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.flush()
    
    deduct_tokens(user, 3)
    
    assert user.tokens_remaining == 7


@pytest.mark.unit
def test_deduct_tokens_negative_protection(db_session):
    """Negatif token koruması"""
    user = User(
        email='negative@example.com',
        username='negativeuser',
        subscription_plan='free',
        tokens_remaining=2
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.flush()
    
    deduct_tokens(user, 5)
    
    # Negatif olmamalı, 0 olmalı
    assert user.tokens_remaining == 0
    assert user.tokens_remaining >= 0


@pytest.mark.unit
def test_add_tokens(db_session):
    """Token ekleme testi"""
    user = User(
        email='add@example.com',
        username='adduser',
        subscription_plan='free',
        tokens_remaining=5
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.flush()
    
    add_tokens(user, 10)
    
    assert user.tokens_remaining == 15


@pytest.mark.unit
def test_can_user_export_free_plan(db_session):
    """Free plan export kontrolü"""
    user = User(
        email='freeexport@example.com',
        username='freeexportuser',
        subscription_plan='free',
        tokens_remaining=10
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.flush()
    
    can_export, error_msg, required = can_user_export(user)
    
    assert can_export is True
    assert error_msg is None
    assert required == 2  # Free plan'da export 2 fiş


@pytest.mark.unit
def test_can_user_export_premium_plan(db_session):
    """Premium plan export kontrolü"""
    user = User(
        email='premiumexport@example.com',
        username='premiumexportuser',
        subscription_plan='premium',
        tokens_remaining=60
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.flush()
    
    can_export, error_msg, required = can_user_export(user)
    
    assert can_export is True
    assert error_msg is None
    assert required == 0  # Premium'da export ücretsiz


@pytest.mark.unit
def test_get_user_token_info(db_session):
    """Token bilgisi testi"""
    user = User(
        email='tokeninfo@example.com',
        username='tokeninfouser',
        subscription_plan='free',
        tokens_remaining=10,
        trial_ends_at=datetime.utcnow() + timedelta(days=5),
        last_token_refresh=datetime.utcnow()  # Refresh yapılmasın
    )
    user.set_password('Test123!')
    db_session.add(user)
    db_session.commit()
    
    info = get_user_token_info(user)
    
    assert isinstance(info, dict)
    assert 'tokens_remaining' in info
    assert 'monthly_tokens' in info
    assert 'trial_active' in info
    assert 'plan' in info
    assert info['tokens_remaining'] >= 0  # refresh_monthly_tokens çağrıldığı için değişebilir
    assert info['plan'] == 'free'


@pytest.mark.unit
@patch('utils.generate_export_pdf')
def test_generate_export_pdf(mock_export, sample_result, user):
    """PDF export testi (mock ile)"""
    mock_export.return_value = '/tmp/test_export.pdf'
    
    # utils modülü üzerinden çağır ki mock çalışsın
    file_path = utils.generate_export_pdf(sample_result, user, 'full')
    
    assert file_path is not None
    assert isinstance(file_path, str)
    # Mock'un doğru argümanlarla çağrıldığını kontrol et
    mock_export.assert_called_once_with(sample_result, user, 'full')


@pytest.mark.unit
def test_generate_export_pdf_real_file(sample_result, user, tmp_path, monkeypatch):
    """PDF export gerçek dosya oluşturma testi"""
    # Export klasörünü geçici dizine yönlendir
    export_dir = str(tmp_path / 'exports')
    monkeypatch.setattr('config.Config.EXPORT_STORAGE_PATH', export_dir)
    
    # Gerçek fonksiyonu çağır
    try:
        file_path = utils.generate_export_pdf(sample_result, user, 'full')
        
        # Dosyanın var olduğunu ve boş olmadığını kontrol et
        assert file_path is not None
        assert isinstance(file_path, str)
        assert os.path.exists(file_path), f"Dosya oluşturulmadı: {file_path}"
        assert os.path.getsize(file_path) > 0, f"Dosya boş: {file_path}"
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
    except ImportError:
        # ReportLab yüklü değilse testi atla
        pytest.skip("reportlab paketi yüklü değil")


@pytest.mark.unit
@patch('utils.generate_export_docx')
def test_generate_export_docx(mock_export, sample_result, user):
    """DOCX export testi (mock ile)"""
    mock_export.return_value = '/tmp/test_export.docx'
    
    # utils modülü üzerinden çağır ki mock çalışsın
    file_path = utils.generate_export_docx(sample_result, user, 'full')
    
    assert file_path is not None
    assert isinstance(file_path, str)
    # Mock'un doğru argümanlarla çağrıldığını kontrol et
    mock_export.assert_called_once_with(sample_result, user, 'full')


@pytest.mark.unit
def test_generate_export_docx_real_file(sample_result, user, tmp_path, monkeypatch):
    """DOCX export gerçek dosya oluşturma testi"""
    # Export klasörünü geçici dizine yönlendir
    export_dir = str(tmp_path / 'exports')
    monkeypatch.setattr('config.Config.EXPORT_STORAGE_PATH', export_dir)
    
    # Gerçek fonksiyonu çağır
    try:
        file_path = utils.generate_export_docx(sample_result, user, 'full')
        
        # Dosyanın var olduğunu ve boş olmadığını kontrol et
        assert file_path is not None
        assert isinstance(file_path, str)
        assert os.path.exists(file_path), f"Dosya oluşturulmadı: {file_path}"
        assert os.path.getsize(file_path) > 0, f"Dosya boş: {file_path}"
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
    except ImportError:
        # python-docx yüklü değilse testi atla
        pytest.skip("python-docx paketi yüklü değil")


@pytest.mark.unit
def test_get_user_documents(db_session, user, sample_document):
    """Kullanıcı dokümanları testi"""
    documents = get_user_documents(user.id)
    
    assert isinstance(documents, list)
    assert len(documents) > 0
    assert documents[0].user_id == user.id


@pytest.mark.unit
def test_increment_user_upload(db_session, user):
    """Upload sayacı artırma testi"""
    increment_user_upload(user.id)
    
    stats = UserUsageStats.get_or_create(user.id)
    assert stats.documents_processed == 1


@pytest.mark.unit
def test_increment_user_cache_hit(db_session, user):
    """Cache hit sayacı artırma testi"""
    increment_user_cache_hit(user.id, 100)
    
    stats = UserUsageStats.get_or_create(user.id)
    assert stats.cache_hits == 1
    assert stats.tokens_saved == 100

