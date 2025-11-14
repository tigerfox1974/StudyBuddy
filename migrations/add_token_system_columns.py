"""
Migration: Token Sistemi Kolonları ve TokenPurchase Tablosu Ekleme

Bu migration script'i şunları yapar:
1. users tablosuna yeni kolonlar ekler:
   - tokens_remaining (INTEGER, default=0)
   - trial_ends_at (DATETIME, nullable)
   - last_token_refresh (DATETIME, nullable)
2. token_purchases tablosunu oluşturur

Kullanım:
    python migrations/add_token_system_columns.py
"""

import sys
import os
import sqlite3
from datetime import datetime

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, TokenPurchase


def check_column_exists(cursor, table_name, column_name):
    """Kolonun var olup olmadığını kontrol et"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def check_table_exists(cursor, table_name):
    """Tablonun var olup olmadığını kontrol et"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None


def safe_print(text):
    """Unicode-safe print function"""
    try:
        print(text)
    except UnicodeEncodeError:
        # ASCII-safe encoding
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)


def migrate():
    """Migration işlemini gerçekleştir"""
    safe_print("=" * 60)
    safe_print("Token Sistemi Migration Baslatiliyor...")
    safe_print("=" * 60)
    
    with app.app_context():
        # SQLite connection al
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        try:
            # 1. users tablosuna yeni kolonlar ekle
            safe_print("\n[1/3] users tablosuna yeni kolonlar ekleniyor...")
            
            columns_to_add = [
                ('tokens_remaining', 'INTEGER NOT NULL DEFAULT 0'),
                ('trial_ends_at', 'DATETIME'),
                ('last_token_refresh', 'DATETIME')
            ]
            
            for column_name, column_def in columns_to_add:
                if check_column_exists(cursor, 'users', column_name):
                    safe_print(f"  - {column_name} kolonu zaten mevcut, atlaniyor.")
                else:
                    try:
                        cursor.execute(f"""
                            ALTER TABLE users 
                            ADD COLUMN {column_name} {column_def}
                        """)
                        safe_print(f"  + {column_name} kolonu eklendi.")
                    except sqlite3.OperationalError as e:
                        safe_print(f"  ! {column_name} kolonu eklenirken hata: {e}")
            
            # 2. Mevcut kullanıcılar için varsayılan değerleri ayarla
            safe_print("\n[2/3] Mevcut kullanicilar icin varsayilan degerler ayarlaniyor...")
            
            # tokens_remaining için 0 zaten default, ama emin olmak için
            cursor.execute("""
                UPDATE users 
                SET tokens_remaining = 0 
                WHERE tokens_remaining IS NULL
            """)
            updated = cursor.rowcount
            if updated > 0:
                safe_print(f"  + {updated} kullanicinin tokens_remaining degeri guncellendi.")
            
            # 3. token_purchases tablosunu oluştur
            safe_print("\n[3/3] token_purchases tablosu olusturuluyor...")
            
            if check_table_exists(cursor, 'token_purchases'):
                safe_print("  - token_purchases tablosu zaten mevcut, atlaniyor.")
            else:
                cursor.execute("""
                    CREATE TABLE token_purchases (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        package_type VARCHAR(20) NOT NULL,
                        tokens INTEGER NOT NULL,
                        price NUMERIC(10, 2) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'TL' NOT NULL,
                        payment_id INTEGER,
                        created_at DATETIME NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users (id),
                        FOREIGN KEY(payment_id) REFERENCES payments (id)
                    )
                """)
                safe_print("  + token_purchases tablosu olusturuldu.")
                
                # Index oluştur
                try:
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS ix_token_purchases_user_id 
                        ON token_purchases (user_id)
                    """)
                    safe_print("  + token_purchases.user_id index'i olusturuldu.")
                except sqlite3.OperationalError as e:
                    safe_print(f"  ! Index olusturulurken hata: {e}")
            
            # Commit
            conn.commit()
            safe_print("\n" + "=" * 60)
            safe_print("Migration basariyla tamamlandi!")
            safe_print("=" * 60)
            
        except Exception as e:
            conn.rollback()
            safe_print(f"\n! HATA: Migration sirasinda bir hata olustu: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            conn.close()
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Token sistemi migration script')
    parser.add_argument('-y', '--yes', '--auto', action='store_true',
                        help='Otomatik olarak devam et (soru sorma)')
    args = parser.parse_args()
    
    if not args.yes:
        safe_print("\nBu migration script'i sunlari yapacak:")
        safe_print("1. users tablosuna tokens_remaining, trial_ends_at, last_token_refresh kolonlari ekleyecek")
        safe_print("2. Mevcut kullanicilar icin varsayilan degerleri ayarlayacak")
        safe_print("3. token_purchases tablosunu olusturacak")
        safe_print("\nDevam etmek istiyor musunuz? (Evet/Hayir): ", end='')
        
        try:
            response = input().strip().lower()
            if response not in ['evet', 'e', 'yes', 'y']:
                safe_print("Migration iptal edildi.")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            safe_print("\n\nMigration iptal edildi.")
            sys.exit(0)
    
    success = migrate()
    sys.exit(0 if success else 1)

