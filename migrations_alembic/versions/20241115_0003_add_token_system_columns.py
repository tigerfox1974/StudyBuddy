"""add_token_system_columns

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
    # Token (fiş) sistemi için gerekli kolonlar
    # tokens_remaining: Kullanıcının kalan fiş sayısı
    # trial_ends_at: 7 günlük deneme bitiş tarihi
    # last_token_refresh: Son fiş yenileme tarihi
    
    # users tablosuna yeni kolonlar ekle
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tokens_remaining', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('trial_ends_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('last_token_refresh', sa.DateTime(), nullable=True))
    
    # Mevcut kullanıcılar için default değerleri ayarla
    op.execute("""
        UPDATE users 
        SET tokens_remaining = 0 
        WHERE tokens_remaining IS NULL
    """)
    
    # token_purchases tablosunu oluştur
    # NOT: payment_id foreign key constraint'i kaldırıldı çünkü payments tablosu
    # daha sonraki bir migration'da (20241115_0004) oluşturuluyor.
    # payment_id normal Integer kolon olarak bırakıldı, ilişkisel bütünlük
    # uygulama tarafında veya ileride ek bir migration ile sağlanabilir.
    op.create_table(
        'token_purchases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('package_type', sa.String(length=20), nullable=False),
        sa.Column('tokens', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='TL'),
        sa.Column('payment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Index oluştur
    op.create_index('ix_token_purchases_user_id', 'token_purchases', ['user_id'], unique=False)


def downgrade() -> None:
    # token_purchases tablosunu kaldır
    op.drop_index('ix_token_purchases_user_id', table_name='token_purchases')
    op.drop_table('token_purchases')
    
    # users tablosundan kolonları kaldır
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('last_token_refresh')
        batch_op.drop_column('trial_ends_at')
        batch_op.drop_column('tokens_remaining')

