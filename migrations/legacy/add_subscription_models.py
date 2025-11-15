"""
Migration: Add Subscription and UserUsageStats tables
Date: 2024
Description: Abonelik yönetimi ve kullanıcı bazlı kullanım takibi için yeni tablolar
"""

import sys
import os

# Parent directory'yi path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Subscription, UserUsageStats, User
from datetime import datetime


def run_migration():
    """Migration'ı çalıştır"""
    with app.app_context():
        print("Starting migration: add_subscription_models")
        
        # 1. Yeni tabloları oluştur
        print("Creating new tables...")
        db.create_all()
        print("[OK] Tables created: subscription, user_usage_stats")
        
        # 2. Mevcut kullanıcılar için default subscription kayıtları oluştur
        print("Creating default subscriptions for existing users...")
        users = User.query.all()
        
        for user in users:
            # Kullanıcının zaten subscription'ı var mı kontrol et
            existing_sub = Subscription.query.filter_by(
                user_id=user.id, 
                status='active'
            ).first()
            
            if not existing_sub:
                # User.subscription_plan field'ından plan tipini al
                plan_type = user.subscription_plan or 'free'
                
                # Yeni subscription kaydı oluştur
                subscription = Subscription(
                    user_id=user.id,
                    plan_type=plan_type,
                    status='active',
                    start_date=user.created_at or datetime.utcnow(),
                    end_date=None  # Süresiz
                )
                db.session.add(subscription)
                print(f"  [OK] Created subscription for user {user.email} (plan: {plan_type})")
        
        db.session.commit()
        print(f"[OK] Created subscriptions for {len(users)} users")
        
        # 3. Bilgilendirme mesajları
        print("\n" + "="*60)
        print("Migration completed successfully!")
        print("="*60)
        print("\nNotes:")
        print("- Subscription table created with existing users")
        print("- UserUsageStats table created (empty, will populate on first upload)")
        print("- All existing users have 'active' subscriptions")
        print("- User.subscription_plan field is still used as current plan indicator")
        print("\nNext steps:")
        print("1. Test the /pricing page")
        print("2. Test file upload with limit checking")
        print("3. Check /dashboard for usage stats")
        print("="*60)


if __name__ == '__main__':
    run_migration()

