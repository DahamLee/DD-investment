import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import ModuleSlot from '../components/ModuleSlot.jsx'
import { useAuth } from '../contexts/AuthContext.jsx'
import authAPI from '../api/auth'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [error, setError] = useState('')

  // 이미 로그인된 사용자는 홈페이지로 리다이렉트
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, navigate])

  const handleNaverLogin = () => {
    setLoading(true)
    // 네이버 로그인 로직
    console.log('네이버 로그인 시도')
    // 실제 구현 시 네이버 OAuth API 호출
    setTimeout(() => {
      setLoading(false)
      alert('네이버 로그인 기능은 준비 중입니다.')
    }, 1000)
  }

  const handleGoogleLogin = () => {
    setLoading(true)
    // 구글 로그인 로직
    console.log('구글 로그인 시도')
    // 실제 구현 시 구글 OAuth API 호출
    setTimeout(() => {
      setLoading(false)
      alert('구글 로그인 기능은 준비 중입니다.')
    }, 1000)
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await login(formData.username, formData.password)
      console.log('로그인 성공:', result)
      alert(`환영합니다, ${result.user.username}님!`)
      navigate('/')
    } catch (err) {
      console.error('로그인 실패:', err)
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>로그인</h2>
          <p>DD Investment에 오신 것을 환영합니다</p>
        </div>

        <ModuleSlot name="login:form" note="일반 로그인 폼" />

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label htmlFor="username">사용자명 또는 이메일</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="사용자명 또는 이메일을 입력하세요"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="비밀번호를 입력하세요"
              required
              minLength={8}
            />
          </div>

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <div className="divider">
          <span>또는</span>
        </div>

        <ModuleSlot name="login:social-login" note="소셜 로그인 모듈" />

        <div className="social-login">
          <button 
            className="naver-login-btn"
            onClick={handleNaverLogin}
            disabled={loading}
          >
            <div className="btn-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect width="20" height="20" rx="4" fill="#03C75A"/>
                <path d="M10 4C6.68629 4 4 6.68629 4 10C4 13.3137 6.68629 16 10 16C13.3137 16 16 13.3137 16 10C16 6.68629 13.3137 4 10 4Z" fill="white"/>
                <path d="M8.5 7.5H11.5V12.5H8.5V7.5Z" fill="#03C75A"/>
              </svg>
            </div>
            <span>네이버로 로그인</span>
          </button>

          <button 
            className="google-login-btn"
            onClick={handleGoogleLogin}
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
            <span>구글로 로그인</span>
          </button>
        </div>

        <div className="login-footer">
          <p>계정이 없으신가요? <Link to="/register">회원가입</Link></p>
        </div>

        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>로그인 중...</p>
          </div>
        )}
      </div>
    </div>
  )
}

