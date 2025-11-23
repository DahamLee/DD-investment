"""
인증 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserDetailResponse
)

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """인증 서비스 의존성"""
    return AuthService(db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    회원가입
    
    - **username**: 사용자명 (3-50자, 고유)
    - **email**: 이메일 (고유)
    - **password**: 비밀번호 (최소 8자)
    - **birth_date**: 생년월일 (선택)
    - **gender**: 성별 (선택)
    - **phone**: 전화번호 (선택)
    - **full_name**: 실명 (선택)
    - **terms_agreed**: 이용약관 동의 (필수)
    - **privacy_agreed**: 개인정보처리방침 동의 (필수)
    - **marketing_agreed**: 마케팅 수신 동의 (선택)
    """
    try:
        # 필수 동의 확인
        if not user_data.terms_agreed or not user_data.privacy_agreed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이용약관 및 개인정보처리방침에 동의해야 합니다"
            )
        
        user = auth_service.register(user_data)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/login", response_model=UserLoginResponse)
async def login(
    login_data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    로그인
    
    - **username**: 사용자명 또는 이메일
    - **password**: 비밀번호
    """
    try:
        result = auth_service.login(login_data)
        
        return UserLoginResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            user=UserResponse.from_orm(result["user"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    현재 로그인한 사용자 정보 조회
    
    - **token**: JWT 액세스 토큰
    """
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/logout")
async def logout():
    """
    로그아웃
    
    클라이언트에서 토큰을 삭제하면 됩니다.
    """
    return {
        "success": True,
        "message": "로그아웃되었습니다"
    }


@router.post("/check-username")
async def check_username(
    username: str = Query(..., description="확인할 사용자명"),
    db: Session = Depends(get_db)
):
    """
    사용자명 중복 확인
    """
    from app.models import User
    
    existing = db.query(User).filter(User.username == username).first()
    
    return {
        "available": existing is None,
        "message": "사용 가능한 사용자명입니다" if not existing else "이미 존재하는 사용자명입니다"
    }


@router.post("/check-email")
async def check_email(
    email: str = Query(..., description="확인할 이메일"),
    db: Session = Depends(get_db)
):
    """
    이메일 중복 확인
    """
    from app.models import User
    
    existing = db.query(User).filter(User.email == email).first()
    
    return {
        "available": existing is None,
        "message": "사용 가능한 이메일입니다" if not existing else "이미 존재하는 이메일입니다"
    }


@router.post("/check-nickname")
async def check_nickname(
    nickname: str = Query(..., description="확인할 닉네임"),
    db: Session = Depends(get_db)
):
    """
    닉네임 중복 확인
    """
    from app.models import User
    
    existing = db.query(User).filter(User.nickname == nickname).first()
    
    return {
        "available": existing is None,
        "message": "사용 가능한 닉네임입니다" if not existing else "이미 존재하는 닉네임입니다"
    }


@router.post("/send-verification-email")
async def send_verification_email(
    email: str = Query(..., description="인증할 이메일"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    이메일 인증 코드 발송
    """
    try:
        result = auth_service.send_verification_email(email)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이메일 발송 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/verify-email-code")
async def verify_email_code(
    email: str = Query(..., description="인증할 이메일"),
    code: str = Query(..., description="인증 코드"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    이메일 인증 코드 검증
    """
    try:
        result = auth_service.verify_email_code(email, code)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이메일 인증 중 오류가 발생했습니다: {str(e)}"
        )
