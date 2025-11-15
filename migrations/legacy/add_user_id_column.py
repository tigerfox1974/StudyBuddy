"""
Migration Script: documents tablosuna user_id kolonu ekleme

Bu script, mevcut documents tablosuna user_id kolonunu ekler ve
legacy kayıtları bir sistem kullanıcısına veya siler.

KULLANIM:
    python migrations/add_user_id_column.py

NOT: Bu script'i çalıştırmadan önce veritabanınızın yedeğini alın!
"""

import sys
import os
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask
from sqlalchemy import text, inspect
from models import db, Document, User
from config import Config


def migrate_documents_table():
    """
    documents tablosuna user_id kolonunu ekler ve legacy kayıtları işler
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Veritabanı bağlantısını kontrol et
        try:
            db.engine.connect()
            print("[OK] Veritabani baglantisi basarili")
        except Exception as e:
            print(f"[ERROR] Veritabani baglanti hatasi: {e}")
            return False
        
        # user_id kolonunun varlığını kontrol et
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('documents')]
        
        if 'user_id' in columns:
            print("[OK] user_id kolonu zaten mevcut")
            # Kolon nullable mı kontrol et
            user_id_col = next(col for col in inspector.get_columns('documents') if col['name'] == 'user_id')
            if user_id_col['nullable']:
                print("[WARNING] user_id kolonu nullable, NOT NULL yapiliyor...")
                # SQLite'da ALTER COLUMN sınırlı, bu yüzden yeni tablo oluşturup veri taşıma gerekebilir
                # Basit yaklaşım: NULL değerleri doldur
                null_count = db.session.query(Document).filter(Document.user_id.is_(None)).count()
                if null_count > 0:
                    print(f"[WARNING] {null_count} adet NULL user_id kaydi bulundu")
                    # İlk kullanıcıyı sistem kullanıcısı olarak kullan veya kayıtları sil
                    first_user = User.query.first()
                    if first_user:
                        print(f"[WARNING] NULL kayitlar {first_user.id} ID'li kullaniciya ataniyor...")
                        db.session.query(Document).filter(Document.user_id.is_(None)).update(
                            {Document.user_id: first_user.id}, synchronize_session=False
                        )
                        db.session.commit()
                        print("[OK] NULL kayitlar guncellendi")
                    else:
                        print("[ERROR] Hic kullanici bulunamadi, NULL kayitlar silinecek...")
                        db.session.query(Document).filter(Document.user_id.is_(None)).delete()
                        db.session.commit()
                        print("[OK] NULL kayitlar silindi")
            else:
                print("[OK] user_id kolonu zaten NOT NULL")
            return True
        
        print("-> user_id kolonu ekleniyor...")
        
        # SQLite'da ALTER TABLE ADD COLUMN kullan
        try:
            # Önce kolonu nullable olarak ekle
            db.session.execute(text("""
                ALTER TABLE documents 
                ADD COLUMN user_id INTEGER REFERENCES users(id)
            """))
            db.session.commit()
            print("[OK] user_id kolonu eklendi (nullable)")
            
            # Mevcut kayıtları kontrol et
            null_count = db.session.query(Document).filter(Document.user_id.is_(None)).count()
            total_count = db.session.query(Document).count()
            
            print(f"-> Toplam {total_count} kayit, {null_count} tanesi NULL user_id'ye sahip")
            
            if null_count > 0:
                # İlk kullanıcıyı bul veya oluştur
                first_user = User.query.first()
                if first_user:
                    print(f"-> NULL kayitlar {first_user.id} ID'li kullaniciya ataniyor...")
                    db.session.query(Document).filter(Document.user_id.is_(None)).update(
                        {Document.user_id: first_user.id}, synchronize_session=False
                    )
                    db.session.commit()
                    print("[OK] NULL kayitlar guncellendi")
                else:
                    print("[WARNING] Hic kullanici bulunamadi!")
                    print("[WARNING] NULL kayitlar silinecek...")
                    response = input("Devam etmek istiyor musunuz? (evet/hayir): ")
                    if response.lower() in ['evet', 'e', 'yes', 'y']:
                        db.session.query(Document).filter(Document.user_id.is_(None)).delete()
                        db.session.commit()
                        print("[OK] NULL kayitlar silindi")
                    else:
                        print("[ERROR] Islem iptal edildi")
                        return False
            
            # Şimdi kolonu NOT NULL yapmak için yeni tablo oluşturup veri taşıma
            # SQLite'da ALTER COLUMN NOT NULL direkt desteklenmez
            print("-> user_id kolonunu NOT NULL yapmak icin tablo yeniden olusturuluyor...")
            
            # 1. Yeni tablo oluştur
            db.session.execute(text("""
                CREATE TABLE documents_new (
                    id INTEGER PRIMARY KEY,
                    file_hash VARCHAR(32) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    file_type VARCHAR(10) NOT NULL,
                    file_size INTEGER NOT NULL,
                    user_level VARCHAR(20) NOT NULL,
                    user_type VARCHAR(20) NOT NULL,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    created_at DATETIME,
                    last_accessed DATETIME
                )
            """))
            
            # 2. Index'leri oluştur (IF NOT EXISTS ile)
            db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_documents_file_hash ON documents_new(file_hash)"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_documents_user_level ON documents_new(user_level)"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_documents_user_type ON documents_new(user_type)"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_documents_user_id ON documents_new(user_id)"))
            
            # 3. Verileri kopyala
            db.session.execute(text("""
                INSERT INTO documents_new 
                SELECT * FROM documents
            """))
            
            # 4. Eski tabloyu sil
            db.session.execute(text("DROP TABLE documents"))
            
            # 5. Yeni tabloyu yeniden adlandır
            db.session.execute(text("ALTER TABLE documents_new RENAME TO documents"))
            
            db.session.commit()
            
            print("[OK] user_id kolonu NOT NULL olarak ayarlandi")
            print("[OK] Migration tamamlandi!")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Migration hatasi: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("Documents Tablosu Migration Script")
    print("=" * 60)
    print()
    print("Bu script documents tablosuna user_id kolonunu ekler.")
    print("[WARNING] ONEMLI: Bu islemi yapmadan once veritabaninizin yedegini alin!")
    print()
    
    # Non-interactive mod için komut satırı argümanı kontrol et
    auto_yes = len(sys.argv) > 1 and sys.argv[1] in ['-y', '--yes', '--auto']
    
    if not auto_yes:
        try:
            response = input("Devam etmek istiyor musunuz? (evet/hayir): ")
            if response.lower() not in ['evet', 'e', 'yes', 'y']:
                print("Islem iptal edildi.")
                sys.exit(0)
        except EOFError:
            # Non-interactive ortamda otomatik devam et
            print("[INFO] Non-interactive mod: otomatik devam ediliyor...")
    
    print()
    success = migrate_documents_table()
    
    if success:
        print()
        print("=" * 60)
        print("[OK] Migration basariyla tamamlandi!")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("[ERROR] Migration basarisiz oldu!")
        print("=" * 60)
        sys.exit(1)

