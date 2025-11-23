"""
인증 서비스
"""
import secrets
import smtplib
from datetime import datetime, timedelta
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import User, RoleEnum, SubscriptionTypeEnum, EmailVerification
from app.schemas.user import UserCreate, UserResponse, UserLoginRequest, UserLoginResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings


class AuthService:
    """인증 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, user_data: UserCreate) -> User:
        """회원가입"""
        # 중복 확인
        existing_user = self.db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 사용자명입니다"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 이메일입니다"
                )
        
        # 비밀번호 해싱
        hashed_password = get_password_hash(user_data.password)
        
        # 닉네임 중복 확인
        existing_nickname = self.db.query(User).filter(User.nickname == user_data.nickname).first()
        if existing_nickname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 닉네임입니다"
            )
        
        # 사용자 생성
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            nickname=user_data.nickname,
            full_name=user_data.full_name,
            birth_date=user_data.birth_date,
            gender=user_data.gender,
            phone=user_data.phone,
            is_active=True,
            is_verified=False,
            marketing_agreed=user_data.marketing_agreed,
            marketing_agreed_at=datetime.utcnow() if user_data.marketing_agreed else None,
            terms_agreed=user_data.terms_agreed,
            terms_agreed_at=datetime.utcnow() if user_data.terms_agreed else None,
            privacy_agreed=user_data.privacy_agreed,
            privacy_agreed_at=datetime.utcnow() if user_data.privacy_agreed else None,
            role=RoleEnum.USER,
            subscription_type=SubscriptionTypeEnum.FREE,
            login_count=0,
            failed_login_attempts=0,
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return new_user
    
    def login(self, login_data: UserLoginRequest) -> dict:
        """로그인"""
        # 사용자 조회 (username 또는 email)
        user = self.db.query(User).filter(
            (User.username == login_data.username) | (User.email == login_data.username)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ID가 올바르지 않습니다"
            )
        
        # 비밀번호 검증
        if not verify_password(login_data.password, user.password_hash):
            # 로그인 실패 횟수 증가
            user.failed_login_attempts += 1
            
            # 5회 실패 시 계정 잠금 (30분)
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                self.db.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="로그인 실패 횟수 초과. 30분 후 다시 시도해주세요."
                )
            
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="비밀번호가 올바르지 않습니다"
            )
        
        # 계정 상태 확인
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="비활성화된 계정입니다"
            )
        
        # 계정 잠금 확인
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="계정이 잠겨있습니다. 잠시 후 다시 시도해주세요."
            )
        
        # 로그인 성공 처리
        user.last_login_at = datetime.utcnow()
        user.login_count += 1
        user.failed_login_attempts = 0
        user.locked_until = None
        self.db.commit()
        
        # JWT 토큰 생성
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.value if hasattr(user.role, 'value') else user.role
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    def get_current_user(self, token: str) -> Optional[User]:
        """현재 사용자 조회 (토큰 기반)"""
        from app.core.security import decode_access_token
        
        payload = decode_access_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        return user
    
    def send_verification_email(self, email: str) -> dict:
        """이메일 인증 코드 발송"""
        # 이메일 형식 검증
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="올바른 이메일 형식이 아닙니다"
            )
        
        # 6자리 랜덤 코드 생성
        verification_code = secrets.randbelow(900000) + 100000  # 100000-999999
        
        # 기존 인증 코드가 있으면 삭제
        existing_verification = self.db.query(EmailVerification).filter(
            EmailVerification.email == email
        ).first()
        
        if existing_verification:
            self.db.delete(existing_verification)
        
        # 새로운 인증 코드를 데이터베이스에 저장
        verification = EmailVerification(
            email=email,
            code=str(verification_code),
            expires_at=datetime.utcnow() + timedelta(minutes=10),  # 10분 유효
            is_used="false"
        )
        
        self.db.add(verification)
        self.db.commit()
        
        # 이메일 발송
        try:
            # Gmail SMTP 설정이 있고 실제 이메일 주소인 경우에만 실제 이메일 발송
            if (settings.email_sender and 
                settings.email_password and 
                settings.email_sender != "your-email@gmail.com" and
                settings.email_password != "your-app-password"):
                self._send_email(email, verification_code)
                print(f"이메일 발송 완료: {email}")
            else:
                print(f"=== 이메일 인증 코드 ===")
                print(f"이메일: {email}")
                print(f"인증 코드: {verification_code}")
                print(f"유효 시간: 10분")
                print(f"=====================")
                print("💡 실제 이메일 발송을 원하면 .env 파일에 실제 Gmail 계정과 앱 비밀번호를 설정하세요")
            
            return {
                "success": True,
                "message": "인증 코드가 발송되었습니다",
                "email": email
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이메일 발송에 실패했습니다: {str(e)}"
            )
    
    def verify_email_code(self, email: str, code: str) -> dict:
        """이메일 인증 코드 검증"""
        # 데이터베이스에서 인증 코드 조회
        verification = self.db.query(EmailVerification).filter(
            EmailVerification.email == email,
            EmailVerification.is_used == "false"
        ).first()
        
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="인증 코드를 먼저 요청해주세요"
            )
        
        # 만료 시간 확인
        if datetime.utcnow() > verification.expires_at:
            # 만료된 코드 삭제
            self.db.delete(verification)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="인증 코드가 만료되었습니다. 다시 요청해주세요"
            )
        
        # 코드 검증
        if verification.code != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="인증 코드가 올바르지 않습니다"
            )
        
        # 인증 성공 시 코드 삭제
        self.db.delete(verification)
        self.db.commit()
        
        return {
            "success": True,
            "message": "이메일 인증이 완료되었습니다",
            "email": email
        }
    
    def cleanup_expired_verifications(self):
        """만료된 인증 코드들 정리"""
        try:
            expired_count = self.db.query(EmailVerification).filter(
                EmailVerification.expires_at < datetime.utcnow()
            ).delete()
            
            self.db.commit()
            print(f"✅ 만료된 인증 코드 {expired_count}개 정리 완료")
            return expired_count
        except Exception as e:
            print(f"❌ 인증 코드 정리 중 오류: {e}")
            return 0
    
    def _send_email(self, email: str, code: int):
        """실제 이메일 발송 (SMTP)"""
        # Gmail 또는 다른 SMTP 서버 사용 가능
        smtp_server = "smtp.gmail.com"  # Gmail: smtp.gmail.com, Outlook: smtp-mail.outlook.com
        smtp_port = 587
        sender_email = settings.email_sender  # your-email@gmail.com 또는 noreply@yourcompany.com
        sender_password = settings.email_password
        
        # 이메일 내용
        subject = "DD Investment 이메일 인증 코드"
        
        # HTML 이메일 내용
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                <h2 style="color: #1e3a8a; margin-bottom: 20px;">DD Investment</h2>
                <h3 style="color: #333; margin-bottom: 20px;">이메일 인증 코드</h3>
                
                <p style="color: #666; font-size: 16px; margin-bottom: 30px;">
                    안녕하세요!<br>
                    회원가입을 완료하기 위한 인증 코드입니다.
                </p>
                
                <div style="background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h1 style="margin: 0; font-size: 32px; letter-spacing: 5px;">{code}</h1>
                </div>
                
                <p style="color: #666; font-size: 14px; margin-bottom: 20px;">
                    이 코드는 <strong>10분간</strong> 유효합니다.
                </p>
                
                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    이 이메일을 요청하지 않으셨다면 무시하셔도 됩니다.
                </p>
            </div>
        </body>
        </html>
        """
        
        # 텍스트 이메일 내용
        text_body = f"""
        DD Investment 이메일 인증 코드
        
        안녕하세요!
        
        회원가입을 완료하기 위한 인증 코드입니다.
        
        인증 코드: {code}
        
        이 코드는 10분간 유효합니다.
        
        이 이메일을 요청하지 않으셨다면 무시하셔도 됩니다.
        
        감사합니다.
        DD Investment 팀
        """
        
        # 이메일 생성
        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = subject
        
        # 텍스트와 HTML 버전 모두 추가
        text_part = MIMEText(text_body, "plain", "utf-8")
        html_part = MIMEText(html_body, "html", "utf-8")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # 이메일 발송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
