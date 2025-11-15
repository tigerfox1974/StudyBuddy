"""
Migration: Add Payment table
Date: 2024
Description: Ödeme takibi için Payment tablosu ekleme
"""

import sys
import os

# Parent directory'yi path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Payment


def run_migration():
    """Migration'ı çalıştır"""
    with app.app_context():
        print("Starting migration: add_payment_model")
        
        # Payment tablosunu oluştur
        print("Creating Payment table...")
        db.create_all()
        print("[OK] Payment table created")
        
        # invoices/ klasörünü oluştur
        invoice_dir = 'invoices'
        if not os.path.exists(invoice_dir):
            os.makedirs(invoice_dir)
            print(f"[OK] Created {invoice_dir}/ directory")
        
        print("\n" + "="*60)
        print("Migration completed successfully!")
        print("="*60)
        print("\nNotes:")
        print("- Payment table created")
        print("- Invoice storage directory created")
        print("- Configure Stripe keys in .env file")
        print("\nNext steps:")
        print("1. Add Stripe keys to .env (STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET)")
        print("2. Create products and prices in Stripe Dashboard")
        print("3. Update Config.SUBSCRIPTION_PLANS with stripe_price_id")
        print("4. Set up webhook endpoint in Stripe Dashboard")
        print("5. Test checkout flow with Stripe test cards")
        print("="*60)


if __name__ == '__main__':
    run_migration()


