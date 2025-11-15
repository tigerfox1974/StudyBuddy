"""
DocumentReader servis testleri
"""

import pytest
import os
import tempfile
from services.document_reader import DocumentReader


@pytest.mark.unit
def test_extract_text_from_pdf(sample_pdf_path):
    """PDF okuma testi"""
    text = DocumentReader.extract_text_from_pdf(sample_pdf_path)
    assert text is not None
    assert len(text) > 0
    assert 'test' in text.lower() or 'Test' in text


@pytest.mark.unit
def test_extract_text_from_pdf_invalid_file():
    """Geçersiz PDF testi"""
    invalid_path = '/nonexistent/file.pdf'
    with pytest.raises(Exception) as exc_info:
        DocumentReader.extract_text_from_pdf(invalid_path)
    assert 'PDF okuma hatası' in str(exc_info.value) or 'PDF' in str(exc_info.value)


@pytest.mark.unit
def test_extract_text_from_docx(sample_docx_path):
    """DOCX okuma testi"""
    text = DocumentReader.extract_text_from_docx(sample_docx_path)
    assert text is not None
    assert len(text) > 0
    assert 'test' in text.lower() or 'Test' in text or 'content' in text.lower()


@pytest.mark.unit
def test_extract_text_from_docx_invalid_file():
    """Geçersiz DOCX testi"""
    invalid_path = '/nonexistent/file.docx'
    with pytest.raises(Exception) as exc_info:
        DocumentReader.extract_text_from_docx(invalid_path)
    assert 'DOCX okuma hatası' in str(exc_info.value) or 'DOCX' in str(exc_info.value)


@pytest.mark.unit
def test_extract_text_from_pptx(sample_pptx_path):
    """PPTX okuma testi"""
    text = DocumentReader.extract_text_from_pptx(sample_pptx_path)
    assert text is not None
    assert len(text) > 0
    assert 'Slayt' in text or 'test' in text.lower() or 'Test' in text or 'content' in text.lower()


@pytest.mark.unit
def test_extract_text_from_txt(sample_txt_path):
    """TXT okuma testi"""
    text = DocumentReader.extract_text_from_txt(sample_txt_path)
    assert text is not None
    assert len(text) > 0
    assert 'Test TXT Content' in text or 'test' in text.lower()


@pytest.mark.unit
def test_extract_text_from_txt_different_encodings(tmp_path):
    """Farklı encoding'ler testi"""
    # UTF-8
    utf8_path = tmp_path / 'utf8.txt'
    with open(utf8_path, 'w', encoding='utf-8') as f:
        f.write('UTF-8 test: Türkçe karakterler: ışğüöç')
    text_utf8 = DocumentReader.extract_text_from_txt(str(utf8_path))
    assert 'Türkçe' in text_utf8 or 'test' in text_utf8.lower()
    
    # Latin-1
    latin1_path = tmp_path / 'latin1.txt'
    with open(latin1_path, 'w', encoding='latin-1') as f:
        f.write('Latin-1 test content')
    text_latin1 = DocumentReader.extract_text_from_txt(str(latin1_path))
    assert 'test' in text_latin1.lower() or 'content' in text_latin1.lower()


@pytest.mark.unit
def test_clean_text():
    """Metin temizleme testi"""
    dirty_text = "Bu   metin    çok    fazla    boşluk    içeriyor.\n\n\n\nÇok fazla yeni satır var."
    cleaned = DocumentReader.clean_text(dirty_text)
    assert '   ' not in cleaned  # Çok fazla boşluk olmamalı
    assert '\n\n\n' not in cleaned  # Çok fazla yeni satır olmamalı
    assert len(cleaned) < len(dirty_text)  # Temizlenmiş metin daha kısa olmalı


@pytest.mark.unit
def test_extract_text_from_file_pdf(sample_pdf_path):
    """Ana fonksiyon PDF testi"""
    text, error = DocumentReader.extract_text_from_file(sample_pdf_path, 'pdf')
    assert error is None
    assert text is not None
    assert len(text) > 0


@pytest.mark.unit
def test_extract_text_from_file_unsupported_format(tmp_path):
    """Desteklenmeyen format testi"""
    invalid_file = tmp_path / 'test.xyz'
    invalid_file.write_text('test content')
    text, error = DocumentReader.extract_text_from_file(str(invalid_file), 'xyz')
    assert error is not None
    assert 'Desteklenmeyen' in error or 'format' in error.lower()
    assert text == ''


@pytest.mark.unit
def test_extract_text_from_file_empty_file(tmp_path):
    """Boş dosya testi"""
    empty_file = tmp_path / 'empty.txt'
    empty_file.write_text('a')  # Çok kısa içerik (< 50 karakter)
    text, error = DocumentReader.extract_text_from_file(str(empty_file), 'txt')
    assert error is not None
    assert 'yeterli metin' in error.lower() or 'boş' in error.lower()


@pytest.mark.unit
def test_truncate_text():
    """Metin kısaltma testi"""
    long_text = 'Test metni. ' * 5000  # Çok uzun metin
    truncated = DocumentReader.truncate_text(long_text, max_tokens=12000)
    assert len(truncated) < len(long_text)
    assert '[Not: Metin çok uzun olduğu için kısaltılmıştır]' in truncated or 'kısaltılmıştır' in truncated


@pytest.mark.unit
def test_truncate_text_short_text():
    """Kısa metin kısaltma testi"""
    short_text = 'Bu kısa bir metindir.'
    truncated = DocumentReader.truncate_text(short_text)
    assert truncated == short_text  # Kısaltma yapılmamalı

