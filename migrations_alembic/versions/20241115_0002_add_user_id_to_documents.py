"""add_user_id_to_documents

Revision ID: 20241115_0002
Revises: 20241115_0001
Create Date: 2024-11-15 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20241115_0002'
down_revision: Union[str, None] = '20241115_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # documents tablosuna user_id kolonu ekleme
    # Her doküman bir kullanıcıya ait olmalıdır
    # SQLite'da ALTER COLUMN NOT NULL direkt desteklenmediği için
    # tablo yeniden oluşturma pattern'i kullanılıyor
    
    from sqlalchemy import inspect
    import sqlalchemy as sa
    
    # Veritabanında documents tablosunun varlığını kontrol et
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    documents_exists = 'documents' in tables
    documents_new_exists = 'documents_new' in tables
    
    # Eğer documents_new tablosu zaten varsa (yarım kalan migration), temizle
    if documents_new_exists:
        op.execute("DROP INDEX IF EXISTS ix_documents_new_file_hash")
        op.execute("DROP INDEX IF EXISTS ix_documents_new_user_level")
        op.execute("DROP INDEX IF EXISTS ix_documents_new_user_type")
        op.execute("DROP INDEX IF EXISTS ix_documents_new_user_id")
        op.drop_table('documents_new')
    
    if not documents_exists:
        # documents tablosu yoksa, bu migration'ı atla (ilk migration'da oluşturuldu)
        return
    
    # users tablosunun varlığını kontrol et
    users_exists = 'users' in tables
    
    # 1. SQLite'da NOT NULL kolon eklemek için tablo yeniden oluşturma pattern'i
    
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
    
    # 1.3. Mevcut verileri kopyala (sadece users tablosu varsa ve documents'te veri varsa)
    if users_exists:
        # documents tablosunda kayıt var mı kontrol et
        result = conn.execute(sa.text("SELECT COUNT(*) FROM documents")).scalar()
        if result > 0:
            # Verileri kopyala (user_id için ilk kullanıcıyı kullan)
            op.execute("""
                INSERT INTO documents_new (id, file_hash, original_filename, file_type, file_size, 
                                          user_level, user_type, user_id, created_at, last_accessed)
                SELECT id, file_hash, original_filename, file_type, file_size, 
                       user_level, user_type, 
                       (SELECT id FROM users LIMIT 1) as user_id,
                       created_at, last_accessed
                FROM documents
            """)
        # Kullanıcı yoksa kayıtları sil (zaten kopyalanmadı)
    else:
        # users tablosu yoksa, documents'teki tüm kayıtları sil
        op.execute("DELETE FROM documents")
    
    # 1.4. Eski tabloyu sil
    op.drop_table('documents')
    
    # 1.5. Yeni tabloyu yeniden adlandır
    op.rename_table('documents_new', 'documents')
    
    # 1.6. Index'leri düzelt
    op.execute("DROP INDEX IF EXISTS ix_documents_new_file_hash")
    op.execute("DROP INDEX IF EXISTS ix_documents_new_user_level")
    op.execute("DROP INDEX IF EXISTS ix_documents_new_user_type")
    op.execute("DROP INDEX IF EXISTS ix_documents_new_user_id")
    
    op.create_index('ix_documents_file_hash', 'documents', ['file_hash'], unique=False)
    op.create_index('ix_documents_user_level', 'documents', ['user_level'], unique=False)
    op.create_index('ix_documents_user_type', 'documents', ['user_type'], unique=False)
    op.create_index('ix_documents_user_id', 'documents', ['user_id'], unique=False)


def downgrade() -> None:
    # Geri alma: user_id kolonunu kaldırmak için tablo yeniden oluştur
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
    
    op.execute("""
        INSERT INTO documents_old (id, file_hash, original_filename, file_type, file_size, 
                                  user_level, user_type, created_at, last_accessed)
        SELECT id, file_hash, original_filename, file_type, file_size, 
               user_level, user_type, created_at, last_accessed
        FROM documents
    """)
    
    op.drop_table('documents')
    op.rename_table('documents_old', 'documents')
    
    op.create_index('ix_documents_file_hash', 'documents', ['file_hash'], unique=False)
    op.create_index('ix_documents_user_level', 'documents', ['user_level'], unique=False)
    op.create_index('ix_documents_user_type', 'documents', ['user_type'], unique=False)

