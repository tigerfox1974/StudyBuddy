"""add_user_id_column

Revision ID: 20241115_0001
Revises: 
Create Date: 2024-11-15 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20241115_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # documents tablosuna user_id kolonu ekleme
    # Her doküman bir kullanıcıya ait olmalıdır
    # SQLite'da ALTER COLUMN NOT NULL direkt desteklenmediği için
    # tablo yeniden oluşturma pattern'i kullanılıyor (legacy script ile aynı)
    
    # NOT: Bu migration çalıştığında documents tablosunda user_id kolonu yoktur.
    # Bu nedenle direkt tablo yeniden oluşturma pattern'ini kullanıyoruz.
    
    # 1. SQLite'da NOT NULL kolon eklemek için tablo yeniden oluşturma pattern'i
    # Legacy script'teki yaklaşımı Alembic migration'a uyarlıyoruz
    
    # 1.1. Yeni tablo oluştur (user_id NOT NULL ile)
    op.create_table(
        'documents_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_hash', sa.String(length=32), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=10), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('user_level', sa.String(length=20), nullable=False),
        sa.Column('user_type', sa.String(length=20), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 1.2. Index'leri oluştur
    op.create_index('ix_documents_new_file_hash', 'documents_new', ['file_hash'], unique=False)
    op.create_index('ix_documents_new_user_level', 'documents_new', ['user_level'], unique=False)
    op.create_index('ix_documents_new_user_type', 'documents_new', ['user_type'], unique=False)
    op.create_index('ix_documents_new_user_id', 'documents_new', ['user_id'], unique=False)
    
    # 1.3. Verileri kopyala (user_id için ilk kullanıcıyı kullan)
    # Eğer kullanıcı yoksa, kayıtlar kopyalanmayacak (NOT NULL constraint nedeniyle)
    op.execute("""
        INSERT INTO documents_new (id, file_hash, original_filename, file_type, file_size, 
                                  user_level, user_type, user_id, created_at, last_accessed)
        SELECT id, file_hash, original_filename, file_type, file_size, 
               user_level, user_type, 
               (SELECT id FROM users LIMIT 1) as user_id,
               created_at, last_accessed
        FROM documents
        WHERE EXISTS (SELECT 1 FROM users)
    """)
    
    # 1.4. Kullanıcı yoksa ve kayıt varsa, kayıtları sil (NOT NULL constraint için gerekli)
    # Bu durumda kayıtlar zaten kopyalanmamış olacak, ama eski tablodaki kayıtları da silelim
    op.execute("""
        DELETE FROM documents 
        WHERE NOT EXISTS (SELECT 1 FROM users)
    """)
    
    # 1.5. Eski tabloyu sil
    op.drop_table('documents')
    
    # 1.6. Yeni tabloyu yeniden adlandır
    op.rename_table('documents_new', 'documents')
    
    # 1.7. Index'leri documents tablosuna yeniden adlandır (Alembic otomatik yapmaz)
    # Not: Index'ler tablo ile birlikte taşınır, ancak isimler düzeltilmeli
    op.execute("DROP INDEX IF EXISTS ix_documents_new_file_hash")
    op.execute("DROP INDEX IF EXISTS ix_documents_new_user_level")
    op.execute("DROP INDEX IF EXISTS ix_documents_new_user_type")
    op.execute("DROP INDEX IF EXISTS ix_documents_new_user_id")
    
    op.create_index('ix_documents_file_hash', 'documents', ['file_hash'], unique=False)
    op.create_index('ix_documents_user_level', 'documents', ['user_level'], unique=False)
    op.create_index('ix_documents_user_type', 'documents', ['user_type'], unique=False)
    op.create_index('ix_documents_user_id', 'documents', ['user_id'], unique=False)


def downgrade() -> None:
    # Geri alma işlemleri
    # NOT: Downgrade için de tablo yeniden oluşturma pattern'i kullanılmalı
    # Ancak basit yaklaşım: user_id kolonunu nullable yaparak bırakmak
    # Tam geri alma için tablo yeniden oluşturulabilir ama bu karmaşık olabilir
    
    # Basit yaklaşım: user_id kolonunu kaldırmak için tablo yeniden oluştur
    # Önce mevcut tabloyu yedekle (veri kaybını önlemek için)
    
    # Yeni tablo oluştur (user_id olmadan)
    op.create_table(
        'documents_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_hash', sa.String(length=32), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=10), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('user_level', sa.String(length=20), nullable=False),
        sa.Column('user_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Verileri kopyala (user_id hariç)
    op.execute("""
        INSERT INTO documents_old (id, file_hash, original_filename, file_type, file_size, 
                                  user_level, user_type, created_at, last_accessed)
        SELECT id, file_hash, original_filename, file_type, file_size, 
               user_level, user_type, created_at, last_accessed
        FROM documents
    """)
    
    # Eski tabloyu sil
    op.drop_table('documents')
    
    # Yeni tabloyu yeniden adlandır
    op.rename_table('documents_old', 'documents')
    
    # Index'leri yeniden oluştur
    op.create_index('ix_documents_file_hash', 'documents', ['file_hash'], unique=False)
    op.create_index('ix_documents_user_level', 'documents', ['user_level'], unique=False)
    op.create_index('ix_documents_user_type', 'documents', ['user_type'], unique=False)

