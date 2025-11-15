"""initial_schema

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
    # İlk migration: Temel tabloları oluştur
    # users, documents (user_id OLMADAN), results, usage_stats tablolarını oluşturur
    # user_id kolonu 20241115_0002 migration'ında eklenecek
    
    # 1. users tablosunu oluştur (temel kolonlar, token kolonları sonra eklenecek)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('subscription_plan', sa.String(length=20), nullable=False, server_default='free'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('reset_token', sa.String(length=100), nullable=True),
        sa.Column('reset_token_expiry', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # users için index'ler
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # 2. documents tablosunu oluştur (user_id OLMADAN - sonra eklenecek)
    op.create_table(
        'documents',
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
    
    # documents için index'ler
    op.create_index('ix_documents_file_hash', 'documents', ['file_hash'], unique=False)
    op.create_index('ix_documents_user_level', 'documents', ['user_level'], unique=False)
    op.create_index('ix_documents_user_type', 'documents', ['user_type'], unique=False)
    
    # 3. results tablosunu oluştur
    op.create_table(
        'results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('multiple_choice', sa.Text(), nullable=False),
        sa.Column('short_answer', sa.Text(), nullable=False),
        sa.Column('fill_blank', sa.Text(), nullable=False),
        sa.Column('true_false', sa.Text(), nullable=False),
        sa.Column('flashcards', sa.Text(), nullable=False),
        sa.Column('ai_model', sa.String(length=50), nullable=False),
        sa.Column('token_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('processing_time', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 4. usage_stats tablosunu oluştur
    op.create_table(
        'usage_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('total_documents', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cache_hits', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cache_misses', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tokens_saved', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def upgrade_old() -> None:
    # Eski kod - artık kullanılmıyor, sadece referans için
    pass


def downgrade() -> None:
    # Geri alma: Tüm temel tabloları sil
    op.drop_table('usage_stats')
    op.drop_table('results')
    op.drop_index('ix_documents_user_type', table_name='documents')
    op.drop_index('ix_documents_user_level', table_name='documents')
    op.drop_index('ix_documents_file_hash', table_name='documents')
    op.drop_table('documents')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

