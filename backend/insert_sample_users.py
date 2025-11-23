#!/usr/bin/env python3
"""
샘플 User 데이터 삽입 스크립트
"""
import sys
sys.path.append('/app/backend')

from datetime import datetime, date, timedelta
from app.core.database import SessionLocal
from app.models import User, GenderEnum, RoleEnum, SubscriptionTypeEnum

def insert_sample_users():
    """샘플 사용자 데이터 삽입"""
    db = SessionLocal()
    
    print("👥 샘플 사용자 데이터 생성 시작...")
    print("=" * 60)
    
    # 샘플 사용자들
    sample_users = [
        {
            "username": "kimcoding",
            "email": "kim@example.com",
            "password_hash": "hashed_password_1",  # 실제로는 암호화해야 함
            "full_name": "김코딩",
            "nickname": "코딩마스터",
            "birth_date": date(1990, 5, 15),
            "gender": GenderEnum.MALE,
            "phone": "010-1234-5678",
            "is_active": True,
            "is_verified": True,
            "email_verified_at": datetime.now() - timedelta(days=30),
            "last_login_at": datetime.now() - timedelta(hours=2),
            "marketing_agreed": True,
            "marketing_agreed_at": datetime.now() - timedelta(days=30),
            "terms_agreed": True,
            "terms_agreed_at": datetime.now() - timedelta(days=30),
            "privacy_agreed": True,
            "privacy_agreed_at": datetime.now() - timedelta(days=30),
            "role": RoleEnum.PREMIUM,
            "is_premium": True,
            "premium_expires_at": datetime.now() + timedelta(days=365),
            "subscription_type": SubscriptionTypeEnum.PRO,
            "subscription_started_at": datetime.now() - timedelta(days=30),
            "subscription_expires_at": datetime.now() + timedelta(days=335),
            "subscription_auto_renew": True,
            "login_count": 150,
            "failed_login_attempts": 0,
        },
        {
            "username": "parkdev",
            "email": "park@example.com",
            "password_hash": "hashed_password_2",
            "full_name": "박개발",
            "nickname": "개발왕",
            "birth_date": date(1995, 8, 20),
            "gender": GenderEnum.FEMALE,
            "phone": "010-2345-6789",
            "is_active": True,
            "is_verified": True,
            "email_verified_at": datetime.now() - timedelta(days=10),
            "last_login_at": datetime.now() - timedelta(hours=5),
            "marketing_agreed": False,
            "terms_agreed": True,
            "terms_agreed_at": datetime.now() - timedelta(days=10),
            "privacy_agreed": True,
            "privacy_agreed_at": datetime.now() - timedelta(days=10),
            "role": RoleEnum.USER,
            "is_premium": False,
            "subscription_type": SubscriptionTypeEnum.BASIC,
            "subscription_started_at": datetime.now() - timedelta(days=10),
            "subscription_expires_at": datetime.now() + timedelta(days=20),
            "subscription_auto_renew": False,
            "login_count": 45,
            "failed_login_attempts": 0,
        },
        {
            "username": "leedata",
            "email": "lee@example.com",
            "password_hash": "hashed_password_3",
            "full_name": "이데이터",
            "nickname": "데이터분석가",
            "birth_date": date(1988, 3, 10),
            "gender": GenderEnum.MALE,
            "phone": "010-3456-7890",
            "is_active": True,
            "is_verified": False,
            "last_login_at": datetime.now() - timedelta(days=1),
            "marketing_agreed": True,
            "marketing_agreed_at": datetime.now() - timedelta(days=5),
            "terms_agreed": True,
            "terms_agreed_at": datetime.now() - timedelta(days=5),
            "privacy_agreed": True,
            "privacy_agreed_at": datetime.now() - timedelta(days=5),
            "role": RoleEnum.USER,
            "is_premium": False,
            "subscription_type": SubscriptionTypeEnum.FREE,
            "subscription_auto_renew": False,
            "login_count": 12,
            "failed_login_attempts": 1,
        },
        {
            "username": "choiadmin",
            "email": "choi@example.com",
            "password_hash": "hashed_password_4",
            "full_name": "최관리",
            "nickname": "Admin",
            "birth_date": date(1985, 12, 25),
            "gender": GenderEnum.MALE,
            "phone": "010-4567-8901",
            "is_active": True,
            "is_verified": True,
            "email_verified_at": datetime.now() - timedelta(days=365),
            "last_login_at": datetime.now() - timedelta(minutes=30),
            "marketing_agreed": True,
            "marketing_agreed_at": datetime.now() - timedelta(days=365),
            "terms_agreed": True,
            "terms_agreed_at": datetime.now() - timedelta(days=365),
            "privacy_agreed": True,
            "privacy_agreed_at": datetime.now() - timedelta(days=365),
            "role": RoleEnum.ADMIN,
            "is_premium": True,
            "premium_expires_at": datetime.now() + timedelta(days=3650),  # 10년
            "subscription_type": SubscriptionTypeEnum.ENTERPRISE,
            "subscription_started_at": datetime.now() - timedelta(days=365),
            "subscription_expires_at": datetime.now() + timedelta(days=3285),
            "subscription_auto_renew": True,
            "login_count": 500,
            "failed_login_attempts": 0,
        },
        {
            "username": "jungtest",
            "email": "jung@example.com",
            "password_hash": "hashed_password_5",
            "full_name": "정테스트",
            "birth_date": date(2000, 7, 7),
            "gender": GenderEnum.OTHER,
            "phone": "010-5678-9012",
            "is_active": True,
            "is_verified": True,
            "email_verified_at": datetime.now() - timedelta(days=1),
            "last_login_at": datetime.now() - timedelta(hours=12),
            "marketing_agreed": False,
            "terms_agreed": True,
            "terms_agreed_at": datetime.now() - timedelta(days=1),
            "privacy_agreed": True,
            "privacy_agreed_at": datetime.now() - timedelta(days=1),
            "role": RoleEnum.USER,
            "is_premium": False,
            "subscription_type": SubscriptionTypeEnum.FREE,
            "subscription_auto_renew": False,
            "login_count": 3,
            "failed_login_attempts": 0,
        },
    ]
    
    try:
        created_users = []
        for user_data in sample_users:
            # 이미 존재하는지 확인
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if existing:
                print(f"⚠️  {user_data['username']} - 이미 존재합니다. 스킵...")
                continue
            
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users.append(user)
            
            print(f"✓ {user.username:<15} {user.full_name:<10} {user.email:<25} (Role: {user.role}, Sub: {user.subscription_type})")
        
        print()
        print("=" * 60)
        print(f"✅ 샘플 사용자 {len(created_users)}명 생성 완료!")
        print()
        
        # 통계 출력
        total_users = db.query(User).count()
        premium_users = db.query(User).filter(User.is_premium == True).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        
        print("📊 데이터베이스 통계:")
        print(f"   총 사용자: {total_users}명")
        print(f"   프리미엄 사용자: {premium_users}명")
        print(f"   인증된 사용자: {verified_users}명")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 삽입 실패: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("🚀 DD Investment 샘플 사용자 생성")
    print("=" * 60)
    print()
    
    success = insert_sample_users()
    
    if not success:
        sys.exit(1)

