import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../api/client'
import { useAuth } from '../contexts/AuthContext.jsx'
import './MyPage.css'

const MyPage = () => {
  const navigate = useNavigate()
  const { user: authUser, isAuthenticated } = useAuth()
  const [user, setUser] = useState(null)
  const [lottoHistory, setLottoHistory] = useState([])
  const [todayLotto, setTodayLotto] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    // 로그인되지 않은 사용자는 로그인 페이지로 리다이렉트
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadUserData()
  }, [isAuthenticated, navigate])

  const loadUserData = async () => {
    setLoading(true)
    try {
      // 인증된 사용자 정보 사용
      if (authUser) {
        setUser(authUser)
      }

      // 오늘의 로또 번호 로드
      await loadTodayLotto()
      
      // 로또 히스토리 로드
      await loadLottoHistory()
    } catch (err) {
      setError('데이터 로드에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const loadTodayLotto = async () => {
    try {
      const response = await apiClient.request('/lotto/today?user_id=1')
      if (response.success) {
        setTodayLotto(response)
      }
    } catch (err) {
      console.log('오늘의 로또 번호가 없습니다')
    }
  }

  const loadLottoHistory = async () => {
    try {
      const response = await apiClient.request('/lotto/history?user_id=1&limit=10')
      if (response.success) {
        setLottoHistory(response.history)
      }
    } catch (err) {
      console.log('로또 히스토리를 불러올 수 없습니다')
    }
  }

  const generateTodayLotto = async () => {
    setLoading(true)
    try {
      const response = await apiClient.generateLottoNumbers()
      if (response.success) {
        setTodayLotto(response)
        await loadLottoHistory() // 히스토리 새로고침
      }
    } catch (err) {
      setError('로또 번호 생성에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const markAsViewed = async (lottoId) => {
    try {
      await apiClient.request(`/lotto/mark-viewed/${lottoId}?user_id=1`, {
        method: 'POST'
      })
      await loadTodayLotto() // 상태 새로고침
    } catch (err) {
      console.log('확인 상태 업데이트 실패')
    }
  }

  const getNumberColor = (number) => {
    if (number <= 10) return '#ff6b6b'
    if (number <= 20) return '#4ecdc4'
    if (number <= 30) return '#45b7d1'
    if (number <= 40) return '#96ceb4'
    return '#feca57'
  }

  const NumberBall = ({ number, size = 'medium' }) => (
    <div 
      className={`number-ball ${size}`}
      style={{ backgroundColor: getNumberColor(number) }}
    >
      {number}
    </div>
  )

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="mypage-container">
        <div className="loading">로딩 중...</div>
      </div>
    )
  }

  return (
    <div className="mypage-container">
      <div className="mypage-header">
        <h1>마이페이지</h1>
        {user && (
          <div className="user-info">
            <h2>안녕하세요, {user.username}님!</h2>
            <p>{user.email}</p>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      <div className="mypage-content">
        {/* 오늘의 로또 번호 섹션 */}
        <div className="today-lotto-section">
          <h3>🎲 오늘의 로또 번호</h3>
          
          {todayLotto ? (
            <div className="today-lotto-card">
              <div className="lotto-info">
                <div className="lotto-numbers">
                  {todayLotto.numbers.map((number, index) => (
                    <NumberBall key={index} number={number} />
                  ))}
                </div>
                <div className="lotto-details">
                  <p>생성일: {formatDate(todayLotto.generated_at)}</p>
                  <p>확인 상태: {todayLotto.is_viewed ? '✅ 확인함' : '❌ 미확인'}</p>
                  {todayLotto.viewed_at && (
                    <p>확인일: {formatDate(todayLotto.viewed_at)}</p>
                  )}
                </div>
              </div>
              
              {!todayLotto.is_viewed && (
                <button 
                  className="btn btn-primary"
                  onClick={() => markAsViewed(todayLotto.lotto_id)}
                >
                  확인했음
                </button>
              )}
            </div>
          ) : (
            <div className="no-lotto-card">
              <p>오늘 아직 로또 번호를 생성하지 않았습니다</p>
              <button 
                className="btn btn-primary"
                onClick={generateTodayLotto}
                disabled={loading}
              >
                {loading ? '생성 중...' : '오늘의 로또 번호 생성'}
              </button>
            </div>
          )}
        </div>

        {/* 로또 히스토리 섹션 */}
        <div className="lotto-history-section">
          <h3>📊 로또 번호 히스토리</h3>
          
          {lottoHistory.length > 0 ? (
            <div className="history-grid">
              {lottoHistory.map((record, index) => (
                <div key={record.id} className="history-item">
                  <div className="history-header">
                    <span className="history-date">
                      {formatDate(record.generated_at)}
                    </span>
                    <span className={`view-status ${record.is_viewed ? 'viewed' : 'not-viewed'}`}>
                      {record.is_viewed ? '✅' : '❌'}
                    </span>
                  </div>
                  <div className="history-numbers">
                    {record.numbers.map((number, numIndex) => (
                      <NumberBall key={numIndex} number={number} size="small" />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-history">
              <p>아직 생성된 로또 번호가 없습니다</p>
            </div>
          )}
        </div>

        {/* 팀원 추적 섹션 (관리자용) */}
        <div className="team-tracking-section">
          <h3>👥 팀원 로또 추천 확인 현황</h3>
          <div className="tracking-info">
            <p>팀원들이 로또 추천을 확인했는지 추적할 수 있습니다</p>
            <div className="tracking-features">
              <div className="feature-item">
                <span className="feature-icon">📱</span>
                <span>IP 주소 및 브라우저 정보 추적</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">⏰</span>
                <span>확인 시간 기록</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">👤</span>
                <span>팀원별 확인 상태 관리</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MyPage





