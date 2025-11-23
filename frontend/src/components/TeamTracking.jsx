import React, { useState, useEffect } from 'react'
import { apiClient } from '../api/client'
import './TeamTracking.css'

const TeamTracking = ({ lottoId, teamId }) => {
  const [teamStatus, setTeamStatus] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (lottoId && teamId) {
      loadTeamStatus()
    }
  }, [lottoId, teamId])

  const loadTeamStatus = async () => {
    setLoading(true)
    try {
      const response = await apiClient.getTeamViewStatus(lottoId, teamId)
      if (response.success) {
        setTeamStatus(response.team_status)
      }
    } catch (err) {
      setError('팀 상태를 불러올 수 없습니다')
    } finally {
      setLoading(false)
    }
  }

  const trackView = async (memberName) => {
    try {
      await apiClient.trackTeamView(lottoId, teamId, memberName)
      await loadTeamStatus() // 상태 새로고침
    } catch (err) {
      setError('추적 실패')
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return '미확인'
    return new Date(dateString).toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return <div className="team-tracking-loading">로딩 중...</div>
  }

  return (
    <div className="team-tracking">
      <h4>팀원 확인 현황</h4>
      
      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      <div className="team-members">
        {teamStatus.length > 0 ? (
          teamStatus.map((member, index) => (
            <div key={index} className={`member-card ${member.is_viewed ? 'viewed' : 'not-viewed'}`}>
              <div className="member-info">
                <div className="member-name">
                  {member.member_name}
                </div>
                <div className="member-status">
                  {member.is_viewed ? (
                    <span className="status-viewed">✅ 확인함</span>
                  ) : (
                    <span className="status-not-viewed">❌ 미확인</span>
                  )}
                </div>
                <div className="member-details">
                  <div className="view-time">
                    {formatDate(member.viewed_at)}
                  </div>
                  {member.ip_address && (
                    <div className="ip-address">
                      IP: {member.ip_address}
                    </div>
                  )}
                </div>
              </div>
              
              {!member.is_viewed && (
                <button 
                  className="btn btn-small"
                  onClick={() => trackView(member.member_name)}
                >
                  확인했음
                </button>
              )}
            </div>
          ))
        ) : (
          <div className="no-members">
            <p>아직 팀원 확인 기록이 없습니다</p>
            <button 
              className="btn btn-primary"
              onClick={() => trackView('현재 사용자')}
            >
              내가 확인했음
            </button>
          </div>
        )}
      </div>

      <div className="tracking-info">
        <h5>추적 정보</h5>
        <ul>
          <li>📱 IP 주소 및 브라우저 정보 자동 수집</li>
          <li>⏰ 확인 시간 자동 기록</li>
          <li>👥 팀원별 개별 추적</li>
          <li>🔒 개인정보 보호 준수</li>
        </ul>
      </div>
    </div>
  )
}

export default TeamTracking





