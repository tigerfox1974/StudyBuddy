"""add_payment_model

Revision ID: 20241115_0005
Revises: 20241115_0004
Create Date: 2024-11-15 00:05:00.000000

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20241115_0005'
down_revision: Union[str, None] = '20241115_0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ödeme işlemleri ve fatura yönetimi
    # Stripe entegrasyonu için gerekli kolonlar
    
    # payments tablosunu oluştur
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='TRY'),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('stripe_session_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('plan_type', sa.String(length=20), nullable=False),
        sa.Column('billing_period', sa.String(length=20), nullable=False, server_default='monthly'),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('invoice_number', sa.String(length=50), nullable=True),
        sa.Column('invoice_pdf_path', sa.String(length=255), nullable=True),
        sa.Column('payment_metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_session_id', name='uq_payments_stripe_session_id'),
        sa.UniqueConstraint('invoice_number', name='uq_payments_invoice_number')
    )
    
    # payments için index'ler oluştur
    op.create_index('ix_payments_user_id', 'payments', ['user_id'], unique=False)
    op.create_index('ix_payments_status', 'payments', ['status'], unique=False)
    op.create_index('ix_payments_stripe_session_id', 'payments', ['stripe_session_id'], unique=False)
    
    # invoices klasörünü oluştur
    invoice_dir = 'invoices'
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)


def downgrade() -> None:
    # payments tablosunu kaldır
    op.drop_index('ix_payments_stripe_session_id', table_name='payments')
    op.drop_index('ix_payments_status', table_name='payments')
    op.drop_index('ix_payments_user_id', table_name='payments')
    op.drop_table('payments')
    
    # invoices klasörünü silme (veri kaybını önlemek için)

