import React, { useState } from 'react'
import { apiClient } from '../api/client'
import TeamTracking from './TeamTracking'
import './LottoGenerator.css'

const LottoGenerator = () => {
  const [numbers, setNumbers] = useState([])
  const [multipleSets, setMultipleSets] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lottoId, setLottoId] = useState(null)
  const [showTeamTracking, setShowTeamTracking] = useState(false)

  const generateSingleSet = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await apiClient.generateLottoNumbers()
      
      if (data.success) {
        setNumbers(data.numbers)
        setAnalysis(data.analysis)
        setMultipleSets([])
        setLottoId(data.lotto_id)
        setShowTeamTracking(true)
      } else {
        setError('번호 생성에 실패했습니다')
      }
    } catch (err) {
      setError('서버 연결에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const generateMultipleSets = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await apiClient.generateMultipleLottoSets(5)
      
      if (data.success) {
        setMultipleSets(data.sets)
        setNumbers([])
        setAnalysis(null)
      } else {
        setError('번호 생성에 실패했습니다')
      }
    } catch (err) {
      setError('서버 연결에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const getNumberColor = (number) => {
    if (number <= 10) return '#ff6b6b'
    if (number <= 20) return '#4ecdc4'
    if (number <= 30) return '#45b7d1'
    if (number <= 40) return '#96ceb4'
    return '#feca57'
  }

  const NumberBall = ({ number, size = 'large' }) => (
    <div 
      className={`number-ball ${size}`}
      style={{ backgroundColor: getNumberColor(number) }}
    >
      {number}
    </div>
  )

  return (
    <div className="lotto-generator">
      <div className="lotto-header">
        <h2>🎲 로또 번호 생성기</h2>
        <p>1부터 45까지의 숫자 중 6개를 랜덤하게 선택합니다</p>
      </div>

      <div className="lotto-controls">
        <button 
          className="btn btn-primary"
          onClick={generateSingleSet}
          disabled={loading}
        >
          {loading ? '생성 중...' : '번호 1세트 생성'}
        </button>
        
        <button 
          className="btn btn-secondary"
          onClick={generateMultipleSets}
          disabled={loading}
        >
          {loading ? '생성 중...' : '번호 5세트 생성'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {numbers.length > 0 && (
        <div className="lotto-result">
          <h3>생성된 번호</h3>
          <div className="number-display">
            {numbers.map((number, index) => (
              <NumberBall key={index} number={number} />
            ))}
          </div>
          
          {analysis && (
            <div className="analysis">
              <h4>번호 분석</h4>
              <div className="analysis-grid">
                <div className="analysis-item">
                  <span className="label">홀수:</span>
                  <span className="value">{analysis.odd_count}개</span>
                </div>
                <div className="analysis-item">
                  <span className="label">짝수:</span>
                  <span className="value">{analysis.even_count}개</span>
                </div>
                <div className="analysis-item">
                  <span className="label">합계:</span>
                  <span className="value">{analysis.sum}</span>
                </div>
                <div className="analysis-item">
                  <span className="label">평균:</span>
                  <span className="value">{analysis.average}</span>
                </div>
                <div className="analysis-item">
                  <span className="label">저구간(1-15):</span>
                  <span className="value">{analysis.low_range}개</span>
                </div>
                <div className="analysis-item">
                  <span className="label">중구간(16-30):</span>
                  <span className="value">{analysis.mid_range}개</span>
                </div>
                <div className="analysis-item">
                  <span className="label">고구간(31-45):</span>
                  <span className="value">{analysis.high_range}개</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {multipleSets.length > 0 && (
        <div className="multiple-sets">
          <h3>생성된 번호 세트들</h3>
          <div className="sets-grid">
            {multipleSets.map((set, index) => (
              <div key={index} className="set-item">
                <div className="set-header">
                  <span className="set-number">{set.set_number}세트</span>
                </div>
                <div className="number-display">
                  {set.numbers.map((number, numIndex) => (
                    <NumberBall key={numIndex} number={number} size="small" />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 팀원 추적 섹션 */}
      {showTeamTracking && lottoId && (
        <div className="team-tracking-section">
          <TeamTracking 
            lottoId={lottoId} 
            teamId="default-team" 
          />
        </div>
      )}
    </div>
  )
}

export default LottoGenerator
