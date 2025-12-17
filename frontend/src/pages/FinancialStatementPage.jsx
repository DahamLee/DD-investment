import { useState, useEffect } from 'react'
import { apiClient } from '../api/client'
import './FinancialStatementPage.css'

export default function FinancialStatementPage() {
  const [statements, setStatements] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // 필터 상태
  const [fsCode, setFsCode] = useState('당기순이익')
  const [quarter, setQuarter] = useState('Q2')
  const [year, setYear] = useState(new Date().getFullYear())
  const [comparisonType, setComparisonType] = useState(0) // 0: 전기대비, 1: 전년동기대비

  // 재무제표 코드 옵션
  const fsCodeOptions = [
    '당기순이익',
    '매출액',
    '영업이익',
    '자산총계',
    '부채총계',
    '자본총계'
  ]

  // 분기 옵션
  const quarterOptions = ['Q1', 'Q2', 'Q3', 'Q4']

  // 데이터 로드
  useEffect(() => {
    loadFinancialStatements()
  }, [fsCode, quarter, year, comparisonType])

  const loadFinancialStatements = async () => {
    setLoading(true)
    setError('')
    
    try {
      const data = await apiClient.getFinancialStatements(
        fsCode,
        quarter,
        year,
        comparisonType
      )
      setStatements(data || [])
    } catch (err) {
      setError(`재무제표 데이터를 불러오는데 실패했습니다: ${err.message}`)
      console.error('재무제표 로드 실패:', err)
      setStatements([])
    } finally {
      setLoading(false)
    }
  }

  const formatValue = (value) => {
    if (value === null || value === undefined) return '-'
    if (typeof value === 'number') {
      return value.toLocaleString('ko-KR')
    }
    return value
  }

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return '-'
    if (typeof value === 'number') {
      return `${(value * 100).toFixed(2)}%`
    }
    return value
  }

  const getScoreColor = (score) => {
    if (score === null || score === undefined) return '#666'
    // 점수가 높을수록 좋음 (1-10 스케일)
    if (score >= 8) return '#2e7d32' // 초록색
    if (score >= 5) return '#f57c00' // 주황색
    return '#d32f2f' // 빨간색
  }

  const getChangeColor = (changePct) => {
    if (changePct === null || changePct === undefined) return '#666'
    if (changePct > 0) return '#2e7d32' // 초록색
    if (changePct < 0) return '#d32f2f' // 빨간색
    return '#666' // 회색
  }

  // 연도 옵션 생성 (최근 5년)
  const yearOptions = []
  const currentYear = new Date().getFullYear()
  for (let i = 0; i < 5; i++) {
    yearOptions.push(currentYear - i)
  }

  return (
    <div className="financial-statement-container">
      <div className="fs-header">
        <h1>📊 국내주식 재무제표 정보</h1>
        <p>재무제표 항목별 종목 점수 및 변화율을 확인하세요</p>
      </div>

      {/* 필터 섹션 */}
      <div className="fs-filter-section">
        <div className="fs-filter-group">
          <label>재무제표 항목:</label>
          <select 
            value={fsCode} 
            onChange={(e) => setFsCode(e.target.value)}
            className="fs-filter-select"
          >
            {fsCodeOptions.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>

        <div className="fs-filter-group">
          <label>연도:</label>
          <select 
            value={year} 
            onChange={(e) => setYear(Number(e.target.value))}
            className="fs-filter-select"
          >
            {yearOptions.map(y => (
              <option key={y} value={y}>{y}년</option>
            ))}
          </select>
        </div>

        <div className="fs-filter-group">
          <label>분기:</label>
          <select 
            value={quarter} 
            onChange={(e) => setQuarter(e.target.value)}
            className="fs-filter-select"
          >
            {quarterOptions.map(q => (
              <option key={q} value={q}>{q}</option>
            ))}
          </select>
        </div>

        <div className="fs-filter-group">
          <label>비교 기준:</label>
          <select 
            value={comparisonType} 
            onChange={(e) => setComparisonType(Number(e.target.value))}
            className="fs-filter-select"
          >
            <option value={0}>전기 대비</option>
            <option value={1}>전년 동기 대비</option>
          </select>
        </div>
      </div>

      {/* 테이블 섹션 */}
      <div className="fs-table-container">
        {loading && (
          <div className="fs-loading-overlay">
            <div className="fs-loading-spinner"></div>
            <p>데이터를 불러오는 중...</p>
          </div>
        )}

        {error && (
          <div className="fs-error-message">
            ⚠️ {error}
          </div>
        )}

        {!loading && !error && statements.length > 0 && (
          <table className="fs-table">
            <thead>
              <tr>
                <th>순위</th>
                <th>종목코드</th>
                <th>분기</th>
                <th>연도</th>
                <th>값</th>
                <th>{comparisonType === 0 ? '전기대비' : '전년동기대비'}</th>
                <th>점수</th>
              </tr>
            </thead>
            <tbody>
              {statements.map((item, index) => (
                <tr key={`${item.stock_code}-${item.quarter}-${item.year}`}>
                  <td className="fs-rank-cell">{index + 1}</td>
                  <td className="fs-stock-code-cell">{item.stock_code}</td>
                  <td className="fs-quarter-cell">{item.quarter}</td>
                  <td className="fs-year-cell">{item.year}</td>
                  <td className="fs-value-cell">{formatValue(item.value)}</td>
                  <td 
                    className="fs-change-cell"
                    style={{ color: getChangeColor(item.change_pct) }}
                  >
                    {formatPercentage(item.change_pct)}
                  </td>
                  <td 
                    className="fs-score-cell"
                    style={{ 
                      color: getScoreColor(item.score),
                      fontWeight: 'bold'
                    }}
                  >
                    {item.score || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {!loading && !error && statements.length === 0 && (
          <div className="fs-no-data">
            <p>📊 표시할 데이터가 없습니다.</p>
            <p>필터 조건을 변경해보세요.</p>
          </div>
        )}
      </div>
    </div>
  )
}


