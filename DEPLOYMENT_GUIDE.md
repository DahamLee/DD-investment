# 🚀 DD Investment 배포 가이드

## 📋 개발 로드맵

### **Phase 1: 기본 기능 완성 (현재)**
- ✅ 사용자 인증 (회원가입, 로그인, 로그아웃)
- ✅ 이메일 인증 (코드 기반)
- ✅ 기본 UI/UX (테마 적용)
- ✅ 데이터베이스 설계 (users, email_verifications)

### **Phase 2: 핵심 기능 개발**
- 🔄 주식 데이터 API 연동
- 🔄 실시간 시세 표시
- 🔄 포트폴리오 관리
- 🔄 관심 종목 기능
- 🔄 뉴스/분석 데이터

### **Phase 3: 고급 기능**
- 📅 알림 시스템
- 📅 차트 분석 도구
- 📅 백테스팅 기능
- 📅 소셜 기능 (팔로우, 공유)

### **Phase 4: 운영 최적화**
- 📅 성능 최적화
- 📅 보안 강화
- 📅 모니터링 시스템
- 📅 로그 분석

---

## 🌐 배포 시 변경사항

### **1. 환경변수 설정**

#### **개발 환경 (.env)**
```bash
# 현재 설정
FRONTEND_URL=http://localhost:3000
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
ENVIRONMENT=development
```

#### **운영 환경 (.env.production)**
```bash
# 배포 시 변경
FRONTEND_URL=https://yourdomain.com
EMAIL_SENDER=noreply@yourdomain.com
EMAIL_PASSWORD=your-domain-email-password
ENVIRONMENT=production

# 추가 설정
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### **2. 이메일 서비스 설정**

#### **옵션 1: Gmail SMTP (무료)**
```bash
# .env.production
EMAIL_SENDER=your-company@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```
- **장점**: 무료, 설정 간단
- **단점**: 하루 500통 제한, Gmail 도메인

#### **옵션 2: 도메인 이메일 (권장)**
```bash
# .env.production
EMAIL_SENDER=noreply@yourdomain.com
EMAIL_PASSWORD=your-domain-email-password
SMTP_SERVER=smtp.yourdomain.com
SMTP_PORT=587
```
- **장점**: 전문적, 브랜드 신뢰도
- **비용**: 도메인 + 이메일 서비스

#### **옵션 3: 전문 이메일 서비스**
```bash
# SendGrid
EMAIL_SERVICE=sendgrid
EMAIL_API_KEY=your-sendgrid-api-key
EMAIL_SENDER=noreply@yourdomain.com

# Mailgun
EMAIL_SERVICE=mailgun
EMAIL_API_KEY=your-mailgun-api-key
EMAIL_SENDER=noreply@yourdomain.com

# AWS SES
EMAIL_SERVICE=aws_ses
EMAIL_API_KEY=your-aws-access-key
EMAIL_SECRET_KEY=your-aws-secret-key
EMAIL_SENDER=noreply@yourdomain.com
```

### **3. 코드 변경사항**

#### **A. 이메일 발송 로직 개선**
```python
# app/services/auth_service.py
def _send_email(self, email: str, code: int):
    """실제 이메일 발송 (운영 환경용)"""
    
    # 환경별 SMTP 설정
    if settings.environment == "production":
        if settings.email_service == "sendgrid":
            return self._send_via_sendgrid(email, code)
        elif settings.email_service == "mailgun":
            return self._send_via_mailgun(email, code)
        elif settings.email_service == "aws_ses":
            return self._send_via_aws_ses(email, code)
        else:
            # 기본 SMTP
            return self._send_via_smtp(email, code)
    else:
        # 개발 환경: 콘솔 출력
        print(f"=== 이메일 인증 코드 ===")
        print(f"이메일: {email}")
        print(f"인증 코드: {code}")
        return True
```

#### **B. 보안 설정 강화**
```python
# app/core/config.py
class Settings(BaseSettings):
    # 운영 환경 보안 설정
    secret_key: str = "your-production-secret-key"  # 강력한 키로 변경
    access_token_expire_minutes: int = 30
    cors_origins: List[str] = ["https://yourdomain.com"]  # CORS 설정
    
    # 데이터베이스 설정
    database_url: str = "postgresql://user:password@host:port/dbname"
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "/var/log/dd-investment.log"
```

#### **C. 프론트엔드 API URL 변경**
```javascript
// frontend/src/api/client.js
const API_BASE_URL = process.env.NODE_ENV === 'production' 
    ? 'https://api.yourdomain.com' 
    : 'http://localhost:8000';
```

### **4. 데이터베이스 설정**

#### **운영 데이터베이스**
```bash
# PostgreSQL 설정
DATABASE_HOST=your-db-host
DATABASE_PORT=5432
DATABASE_NAME=dd_investment_prod
DATABASE_USER=your-db-user
DATABASE_PASSWORD=your-db-password
```

#### **데이터베이스 마이그레이션**
```bash
# 운영 환경에서 실행
cd /app/backend
python -c "
from app.core.database import engine
from app.models import User, EmailVerification
User.metadata.create_all(bind=engine)
EmailVerification.metadata.create_all(bind=engine)
print('✅ 운영 데이터베이스 테이블 생성 완료')
"
```

### **5. 도메인 및 SSL 설정**

#### **도메인 설정**
```bash
# DNS 설정
A    yourdomain.com        → 서버 IP
A    api.yourdomain.com    → 서버 IP
CNAME www.yourdomain.com   → yourdomain.com
```

#### **SSL 인증서**
```bash
# Let's Encrypt (무료)
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

### **6. 서버 설정**

#### **Nginx 설정**
```nginx
# /etc/nginx/sites-available/dd-investment
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # 프론트엔드
    location / {
        root /var/www/dd-investment/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 백엔드 API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### **Docker 배포**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/dd_investment
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=dd_investment
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 💰 비용 예상

### **도메인 및 호스팅**
- **도메인**: 연 $10-15
- **VPS/서버**: 월 $5-20
- **SSL 인증서**: 무료 (Let's Encrypt)

### **이메일 서비스**
- **Gmail SMTP**: 무료 (하루 500통)
- **SendGrid**: 월 100통 무료, 이후 유료
- **Mailgun**: 월 5,000통 무료, 이후 유료
- **AWS SES**: 1,000통당 $0.10

### **데이터베이스**
- **PostgreSQL**: 무료 (자체 서버)
- **클라우드 DB**: 월 $5-20

---

## 🔧 배포 체크리스트

### **배포 전**
- [ ] 도메인 구매 및 DNS 설정
- [ ] 서버 준비 (VPS/클라우드)
- [ ] SSL 인증서 설정
- [ ] 데이터베이스 설정
- [ ] 환경변수 설정

### **코드 변경**
- [ ] 환경변수 업데이트
- [ ] API URL 변경
- [ ] 이메일 서비스 설정
- [ ] 보안 설정 강화

### **배포 후**
- [ ] 기능 테스트
- [ ] 성능 모니터링
- [ ] 로그 확인
- [ ] 백업 설정

---

## 📞 지원 및 문의

배포 과정에서 문제가 발생하면 이 가이드를 참고하거나 개발팀에 문의하세요.

**마지막 업데이트**: 2024년 1월
