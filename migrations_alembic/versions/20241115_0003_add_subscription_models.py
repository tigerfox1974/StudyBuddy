"""add_subscription_models

Revision ID: 20241115_0003
Revises: 20241115_0002
Create Date: 2024-11-15 00:03:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20241115_0003'
down_revision: Union[str, None] = '20241115_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Abonelik yönetimi ve kullanıcı bazlı istatistikler
    # subscriptions: Kullanıcı abonelik geçmişi
    # user_usage_stats: Aylık kullanım istatistikleri
    
    # subscriptions tablosunu oluştur
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # subscriptions için index oluştur
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'], unique=False)
    
    # user_usage_stats tablosunu oluştur
    op.create_table(
        'user_usage_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('documents_processed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cache_hits', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cache_misses', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('tokens_saved', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'year', 'month', name='_user_year_month_uc')
    )
    
    # user_usage_stats için index'ler oluştur
    op.create_index('ix_user_usage_stats_user_id', 'user_usage_stats', ['user_id'], unique=False)
    op.create_index('ix_user_usage_stats_year', 'user_usage_stats', ['year'], unique=False)
    op.create_index('ix_user_usage_stats_month', 'user_usage_stats', ['month'], unique=False)
    
    # Mevcut kullanıcılar için default subscription kayıtları oluştur
    op.execute("""
        INSERT INTO subscriptions (user_id, plan_type, status, start_date, created_at, updated_at)
        SELECT 
            id, 
            COALESCE(subscription_plan, 'free') as plan_type,
            'active' as status,
            COALESCE(created_at, datetime('now')) as start_date,
            COALESCE(created_at, datetime('now')) as created_at,
            datetime('now') as updated_at
        FROM users
        WHERE NOT EXISTS (
            SELECT 1 FROM subscriptions WHERE subscriptions.user_id = users.id
        )
    """)


def downgrade() -> None:
    # user_usage_stats tablosunu kaldır
    op.drop_index('ix_user_usage_stats_month', table_name='user_usage_stats')
    op.drop_index('ix_user_usage_stats_year', table_name='user_usage_stats')
    op.drop_index('ix_user_usage_stats_user_id', table_name='user_usage_stats')
    op.drop_table('user_usage_stats')
    
    # subscriptions tablosunu kaldır
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')

