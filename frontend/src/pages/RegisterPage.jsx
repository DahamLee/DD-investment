import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import ModuleSlot from '../components/ModuleSlot.jsx'
import { useAuth } from '../contexts/AuthContext.jsx'
import authAPI from '../api/auth'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
    nickname: '',
    full_name: '',
    birth_date: '',
    gender: '',
    phone: '',
    terms_agreed: false,
    privacy_agreed: false,
    marketing_agreed: false
  })
  const [error, setError] = useState('')
  const [usernameChecked, setUsernameChecked] = useState(false)

  // 이미 로그인된 사용자는 홈페이지로 리다이렉트
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, navigate])
  const [passwordValidation, setPasswordValidation] = useState({
    hasEnglish: false,
    hasNumbers: false,
    hasSpecialChar: false,
    hasMinLength: false
  })
  const [showPasswordError, setShowPasswordError] = useState(false)
  const [showEmailError, setShowEmailError] = useState(false)
  const [showBirthDateError, setShowBirthDateError] = useState(false)
  
  // 이메일 인증 관련 상태
  const [emailVerified, setEmailVerified] = useState(false)
  const [verificationCode, setVerificationCode] = useState('')
  const [showVerificationForm, setShowVerificationForm] = useState(false)
  const [verificationLoading, setVerificationLoading] = useState(false)

  const handleNaverRegister = () => {
    setLoading(true)
    // 네이버 회원가입 로직
    console.log('네이버 회원가입 시도')
    // 실제 구현 시 네이버 OAuth API 호출
    setTimeout(() => {
      setLoading(false)
      alert('네이버 회원가입 기능은 준비 중입니다.')
    }, 1000)
  }

  const handleGoogleRegister = () => {
    setLoading(true)
    // 구글 회원가입 로직
    console.log('구글 회원가입 시도')
    // 실제 구현 시 구글 OAuth API 호출
    setTimeout(() => {
      setLoading(false)
      alert('구글 회원가입 기능은 준비 중입니다.')
    }, 1000)
  }

  const validatePassword = (password) => {
    const hasEnglish = /[a-zA-Z]/.test(password)
    const hasNumbers = /\d/.test(password)
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password)
    const hasMinLength = password.length >= 8
    
    return {
      hasEnglish,
      hasNumbers,
      hasSpecialChar,
      hasMinLength,
      isValid: hasEnglish && hasNumbers && hasSpecialChar && hasMinLength
    }
  }

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validateBirthDate = (birthDate) => {
    // YYYY-MM-DD 형식인 경우 원본으로 변환
    let inputDate = birthDate
    if (birthDate.includes('-')) {
      // YYYY-MM-DD 형식을 YYYYMMDD로 변환
      inputDate = birthDate.replace(/-/g, '')
    }
    
    // 8자리 숫자인지 확인
    if (!inputDate || inputDate.length !== 8) {
      return false
    }
    
    // 숫자만 있는지 확인
    if (!/^\d{8}$/.test(inputDate)) {
      return false
    }
    
    // 년도 범위 확인 (1900~2100)
    const year = parseInt(inputDate.substring(0, 4))
    if (year < 1900 || year > 2100) {
      return false
    }
    
    // 유효한 날짜인지 확인
    const month = inputDate.substring(4, 6)
    const day = inputDate.substring(6, 8)
    
    const date = new Date(year, month - 1, day)
    return date.getFullYear() == year && date.getMonth() == month - 1 && date.getDate() == day
  }

  const formatBirthDate = (input) => {
    // yyyymmdd 형식을 yyyy-mm-dd로 변환
    const cleanInput = input.replace(/\D/g, '') // 숫자만 추출
    
    if (cleanInput.length === 8) {
      const year = cleanInput.substring(0, 4)
      const month = cleanInput.substring(4, 6)
      const day = cleanInput.substring(6, 8)
      
      // 유효한 날짜인지 확인
      const date = new Date(year, month - 1, day)
      if (date.getFullYear() == year && date.getMonth() == month - 1 && date.getDate() == day) {
        return `${year}-${month}-${day}`
      }
    }
    
    return input // 변환 실패 시 원본 반환
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    let processedValue = value
    
    // 생년월일 입력 처리
    if (name === 'birth_date') {
      // 숫자만 입력 허용
      const numericValue = value.replace(/\D/g, '')
      if (numericValue.length <= 8) {
        processedValue = numericValue
      } else {
        return // 8자리 초과 입력 방지
      }
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : processedValue
    }))
    setError('')
    
    // 입력값이 변경되면 중복확인 상태 초기화
    if (name === 'username') setUsernameChecked(false)
    
    // 이메일이 변경되면 인증 상태 초기화
    if (name === 'email') {
      setEmailVerified(false)
      setShowVerificationForm(false)
      setVerificationCode('')
    }
    
    // 비밀번호 실시간 검증 (에러 표시는 하지 않음)
    if (name === 'password') {
      const validation = validatePassword(value)
      setPasswordValidation(validation)
    }
  }

  const handlePasswordBlur = () => {
    // 비밀번호 필드에서 포커스가 벗어날 때 에러 표시
    if (formData.password) {
      setShowPasswordError(true)
    }
  }

  const handlePasswordFocus = () => {
    // 비밀번호 필드에 포커스가 들어올 때 에러 숨김
    setShowPasswordError(false)
  }

  const handleEmailBlur = () => {
    // 이메일 필드에서 포커스가 벗어날 때 에러 표시
    if (formData.email) {
      setShowEmailError(true)
    }
  }

  const handleEmailFocus = () => {
    // 이메일 필드에 포커스가 들어올 때 에러 숨김
    setShowEmailError(false)
  }

  const handleBirthDateBlur = () => {
    // 생년월일 필드에서 포커스가 벗어날 때 에러 표시 및 형식 변환
    if (formData.birth_date) {
      setShowBirthDateError(true)
      
      // 8자리이고 유효한 날짜인 경우 형식 변환
      if (formData.birth_date.length === 8 && validateBirthDate(formData.birth_date)) {
        const formattedDate = formatBirthDate(formData.birth_date)
        if (formattedDate !== formData.birth_date) {
          setFormData(prev => ({
            ...prev,
            birth_date: formattedDate
          }))
        }
      }
    }
  }

  const handleBirthDateFocus = () => {
    // 생년월일 필드에 포커스가 들어올 때 에러 숨김
    setShowBirthDateError(false)
  }

  const handleCheckUsername = async () => {
    if (!formData.username) {
      setError('ID를 입력해주세요')
      return
    }
    
    try {
      const result = await authAPI.checkUsername(formData.username)
      if (result.available) {
        setUsernameChecked(true)
        setError('')
        alert('사용 가능한 ID입니다')
      } else {
        setUsernameChecked(false)
        setError(result.message)
      }
    } catch (err) {
      setError('ID 중복 확인에 실패했습니다')
    }
  }

  const handleSendVerificationEmail = async () => {
    if (!formData.email) {
      setError('이메일을 입력해주세요')
      return
    }
    
    if (!validateEmail(formData.email)) {
      setError('올바른 이메일 형식을 입력해주세요')
      return
    }
    
    setVerificationLoading(true)
    setError('')
    
    try {
      const result = await authAPI.sendVerificationEmail(formData.email)
      setShowVerificationForm(true)
      alert('인증 코드가 발송되었습니다. 이메일을 확인해주세요.')
    } catch (err) {
      setError(err)
    } finally {
      setVerificationLoading(false)
    }
  }

  const handleVerifyEmailCode = async () => {
    if (!verificationCode) {
      setError('인증 코드를 입력해주세요')
      return
    }
    
    if (verificationCode.length !== 6) {
      setError('인증 코드는 6자리입니다')
      return
    }
    
    setVerificationLoading(true)
    setError('')
    
    try {
      const result = await authAPI.verifyEmailCode(formData.email, verificationCode)
      setEmailVerified(true)
      setShowVerificationForm(false)
      alert('이메일 인증이 완료되었습니다!')
    } catch (err) {
      setError(err)
    } finally {
      setVerificationLoading(false)
    }
  }



  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // 비밀번호 확인
    if (formData.password !== formData.passwordConfirm) {
      setError('비밀번호가 일치하지 않습니다')
      return
    }

    // 필수 동의 확인
    if (!formData.terms_agreed || !formData.privacy_agreed) {
      setError('이용약관 및 개인정보처리방침에 동의해주세요')
      return
    }

    // 중복확인 체크
    if (!usernameChecked) {
      setError('ID 중복확인을 해주세요')
      return
    }

    // 이메일 인증 체크
    if (!emailVerified) {
      setError('이메일 인증을 완료해주세요')
      return
    }

    setLoading(true)

    try {
      const registerData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        nickname: formData.nickname,
        full_name: formData.full_name || null,
        birth_date: formData.birth_date || null,
        gender: formData.gender || null,
        phone: formData.phone || null,
        terms_agreed: formData.terms_agreed,
        privacy_agreed: formData.privacy_agreed,
        marketing_agreed: formData.marketing_agreed
      }

      const result = await authAPI.register(registerData)
      console.log('회원가입 성공:', result)
      alert('회원가입이 완료되었습니다! 로그인해주세요.')
      navigate('/login')
    } catch (err) {
      console.error('회원가입 실패:', err)
      // 이메일 중복 에러 처리
      if (err.includes('이미 존재하는 이메일') || err.includes('email')) {
        alert('이미 가입한 이메일입니다')
      } else {
        setError(err)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <h2>회원가입</h2>
          <p>DD Investment에 가입하여 투자 정보를 확인하세요</p>
        </div>

        <ModuleSlot name="register:form" note="일반 회원가입 폼" />

        <form onSubmit={handleSubmit} className="register-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-section">
            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="username">ID (필수)</label>
                <div className="input-with-button">
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    placeholder="ID (3-50자)"
                    required
                    minLength={3}
                    maxLength={50}
                    className={`form-input ${usernameChecked ? 'checked' : ''}`}
                  />
                  <button 
                    type="button" 
                    className="check-btn"
                    onClick={handleCheckUsername}
                    disabled={!formData.username}
                  >
                    {usernameChecked ? '✓' : '중복확인'}
                  </button>
                </div>
              </div>
            </div>

            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="email">이메일 (필수)</label>
                <div className="input-with-button">
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    onFocus={handleEmailFocus}
                    onBlur={handleEmailBlur}
                    placeholder="email@example.com"
                    required
                    className={`form-input ${emailVerified ? 'checked' : ''}`}
                  />
                  <button 
                    type="button" 
                    className="check-btn"
                    onClick={handleSendVerificationEmail}
                    disabled={!formData.email || !validateEmail(formData.email) || verificationLoading}
                  >
                    {emailVerified ? '✓' : verificationLoading ? '발송중...' : '이메일 인증'}
                  </button>
                </div>
              </div>
              {showEmailError && formData.email && !validateEmail(formData.email) && (
                <div className="error-message">
                  올바른 이메일 형식이 아닙니다. 예: email@example.com
                </div>
              )}
              
              {/* 이메일 인증 코드 입력 폼 */}
              {showVerificationForm && !emailVerified && (
                <div className="verification-form">
                  <div className="label-with-input">
                    <label htmlFor="verificationCode">인증 코드</label>
                    <div className="input-with-button">
                      <input
                        type="text"
                        id="verificationCode"
                        value={verificationCode}
                        onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        placeholder="6자리 인증 코드"
                        maxLength={6}
                        className="form-input"
                      />
                      <button 
                        type="button" 
                        className="check-btn"
                        onClick={handleVerifyEmailCode}
                        disabled={verificationCode.length !== 6 || verificationLoading}
                      >
                        {verificationLoading ? '인증중...' : '인증'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
              
              {/* 이메일 인증 완료 표시 */}
              {emailVerified && (
                <div className="verification-success">
                  <span className="success-icon">✓</span>
                  <span className="success-text">인증 되었습니다.</span>
                </div>
              )}
            </div>

            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="password">비밀번호 (필수)</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  onFocus={handlePasswordFocus}
                  onBlur={handlePasswordBlur}
                  placeholder="비밀번호 (영문, 숫자, 특수문자 포함)"
                  required
                  minLength={8}
                  maxLength={72}
                  className="form-input"
                />
              </div>
              {showPasswordError && formData.password && !passwordValidation.isValid && (
                <div className="error-message">
                  잘못된 양식의 비밀번호입니다. 영문, 숫자, 특수문자를 포함하여 최소 8자 이상 입력해주세요.
                </div>
              )}
            </div>

            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="passwordConfirm">비밀번호 확인 (필수)</label>
                <input
                  type="password"
                  id="passwordConfirm"
                  name="passwordConfirm"
                  value={formData.passwordConfirm}
                  onChange={handleInputChange}
                  placeholder="비밀번호 재입력"
                  required
                  minLength={8}
                  maxLength={72}
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="nickname">닉네임 (필수)</label>
                <input
                  type="text"
                  id="nickname"
                  name="nickname"
                  value={formData.nickname}
                  onChange={handleInputChange}
                  placeholder="닉네임 (2-50자, 화면에 표시됩니다)"
                  required
                  minLength={2}
                  maxLength={50}
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="full_name">이름</label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  placeholder="이름 (실명, 선택)"
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="birth_date">생년월일</label>
                <input
                  type="text"
                  id="birth_date"
                  name="birth_date"
                  value={formData.birth_date}
                  onChange={handleInputChange}
                  onFocus={handleBirthDateFocus}
                  onBlur={handleBirthDateBlur}
                  placeholder="YYYYMMDD (예: 19900315)"
                  maxLength={8}
                  className="form-input"
                />
              </div>
              {showBirthDateError && formData.birth_date && !validateBirthDate(formData.birth_date) && (
                <div className="error-message">
                  올바른 생년월일 형식이 아닙니다. YYYYMMDD 형식으로 8자리 숫자를 입력해주세요. (예: 19900315)
                </div>
              )}
            </div>

            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="gender">성별</label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  <option value="">선택하세요</option>
                  <option value="male">남성</option>
                  <option value="female">여성</option>
                  <option value="other">기타</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <div className="label-with-input">
                <label htmlFor="phone">전화번호</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="010-1234-5678"
                  className="form-input"
                />
              </div>
            </div>
          </div>

          <div className="form-agreements">
            <div className="form-check">
              <input
                type="checkbox"
                id="terms_agreed"
                name="terms_agreed"
                checked={formData.terms_agreed}
                onChange={handleInputChange}
                required
              />
              <label htmlFor="terms_agreed">이용약관 동의 (필수) *</label>
            </div>

            <div className="form-check">
              <input
                type="checkbox"
                id="privacy_agreed"
                name="privacy_agreed"
                checked={formData.privacy_agreed}
                onChange={handleInputChange}
                required
              />
              <label htmlFor="privacy_agreed">개인정보처리방침 동의 (필수) *</label>
            </div>

            <div className="form-check">
              <input
                type="checkbox"
                id="marketing_agreed"
                name="marketing_agreed"
                checked={formData.marketing_agreed}
                onChange={handleInputChange}
              />
              <label htmlFor="marketing_agreed">마케팅 정보 수신 동의 (선택)</label>
            </div>
          </div>

          <button type="submit" className="register-btn" disabled={loading}>
            {loading ? '회원가입 중...' : '회원가입'}
          </button>
        </form>

        <div className="divider">
          <span>또는</span>
        </div>

        <ModuleSlot name="register:social-register" note="소셜 회원가입 모듈" />

        <div className="social-register">
          <button 
            className="naver-register-btn"
            onClick={handleNaverRegister}
            disabled={loading}
          >
            <div className="btn-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect width="20" height="20" rx="4" fill="#03C75A"/>
                <path d="M10 4C6.68629 4 4 6.68629 4 10C4 13.3137 6.68629 16 10 16C13.3137 16 16 13.3137 16 10C16 6.68629 13.3137 4 10 4Z" fill="white"/>
                <path d="M8.5 7.5H11.5V12.5H8.5V7.5Z" fill="#03C75A"/>
              </svg>
            </div>
            <span>네이버로 가입하기</span>
          </button>

          <button 
            className="google-register-btn"
            onClick={handleGoogleRegister}
            disabled={loading}
          >
            <div className="btn-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M19.6 10.23c0-.82-.1-1.42-.25-2.05H10v3.72h5.5c-.15.96-.74 2.36-2.13 3.26v2.77h3.44c2.01-1.85 3.17-4.58 3.17-7.7z" fill="#4285F4"/>
                <path d="M10 20c2.7 0 4.96-.89 6.62-2.42l-3.44-2.77c-.89.6-2.04.95-3.18.95-2.43 0-4.5-1.58-5.25-3.71H1.3v2.84C2.96 17.43 6.3 20 10 20z" fill="#34A853"/>
                <path d="M4.75 12.95c-.22-.6-.35-1.24-.35-1.95s.13-1.35.35-1.95V6.21H1.3C.47 7.77 0 9.33 0 11s.47 3.23 1.3 4.79l3.45-2.84z" fill="#FBBC05"/>
                <path d="M10 3.98c1.35 0 2.56.47 3.52 1.38l2.64-2.64C12.96.89 10.7 0 10 0 6.3 0 2.96 2.57 1.3 6.21l3.45 2.84C5.5 5.56 7.57 3.98 10 3.98z" fill="#EA4335"/>
              </svg>
            </div>
            <span>Google로 가입하기</span>
          </button>
        </div>

        <div className="register-benefits">
          <h4>회원가입 혜택</h4>
          <ul>
            <li>📊 실시간 주식 시세 확인</li>
            <li>📈 개인화된 포트폴리오 관리</li>
            <li>🔔 관심 종목 알림 서비스</li>
            <li>📰 맞춤형 투자 뉴스 제공</li>
            <li>💼 전문가 분석 리포트</li>
          </ul>
        </div>

        <div className="register-footer">
          <p>이미 계정이 있으신가요? <Link to="/login">로그인</Link></p>
        </div>

        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>회원가입 중...</p>
          </div>
        )}
      </div>
    </div>
  )
}

