import { useState, useEffect } from 'react'

export default function StockRankingPage() {
  const [rankings, setRankings] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedMetric, setSelectedMetric] = useState('ROE')
  const [selectedOrder, setSelectedOrder] = useState('desc')
  const [selectedIndustry, setSelectedIndustry] = useState('')
  const [industries, setIndustries] = useState([])
  const [metrics, setMetrics] = useState([])

  // 초기 데이터 로드
  useEffect(() => {
    loadIndustries()
    loadMetrics()
    loadRankings()
  }, [])

  // 지표 변경 시 랭킹 다시 로드
  useEffect(() => {
    loadRankings()
  }, [selectedMetric, selectedOrder, selectedIndustry])

  const loadIndustries = async () => {
    try {
      const response = await fetch('/api/v1/stock-ranking/industries')
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
      
      const data = await response.json()
      setIndustries(data)
    } catch (err) {
      console.error('업종 목록 로드 실패:', err)
    }
  }

  const loadMetrics = async () => {
    try {
      const response = await fetch('/api/v1/stock-ranking/metrics')
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
      
      const data = await response.json()
      setMetrics(data)
    } catch (err) {
      console.error('지표 목록 로드 실패:', err)
    }
  }

  const loadRankings = async () => {
    setLoading(true)
    setError('')
    
    try {
      const params = new URLSearchParams({
        metric: selectedMetric,
        order: selectedOrder,
        limit: '50'
      })
      
      if (selectedIndustry) {
        params.append('industry', selectedIndustry)
      }
      
      const response = await fetch(`/api/v1/stock-ranking/rankings?${params}`)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
      
      const data = await response.json()
      setRankings(data.stocks || [])
    } catch (err) {
      setError(`랭킹 데이터를 불러오는데 실패했습니다: ${err.message}`)
      console.error('랭킹 로드 실패:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatValue = (value, metric) => {
    if (value === null || value === undefined) return '-'
    
    if (metric.includes('비율') || metric.includes('증가율') || metric === 'ROA' || metric === 'ROE') {
      return `${value.toFixed(2)}%`
    } else if (metric === 'PER' || metric === 'PBR' || metric === 'EV/EBITDA') {
      return value.toFixed(2)
    } else {
      return value.toLocaleString()
    }
  }

  const getValueColor = (value, metric) => {
    if (value === null || value === undefined) return '#666'
    
    // 높을수록 좋은 지표
    const goodHighMetrics = ['ROA', 'ROE', 'EPS증가율', '매출액증가율', '유보율']
    // 낮을수록 좋은 지표  
    const goodLowMetrics = ['부채비율', 'PER', 'PBR', 'EV/EBITDA']
    
    if (goodHighMetrics.includes(metric)) {
      return value > 0 ? '#2e7d32' : '#d32f2f'
    } else if (goodLowMetrics.includes(metric)) {
      return value < 10 ? '#2e7d32' : value < 20 ? '#f57c00' : '#d32f2f'
    }
    
    return '#1976d2'
  }


  return (
    <div className="stock-ranking-container">
      <div className="ranking-header">
        <h1>📊 종목별 랭킹 분석</h1>
        <p>재무 지표별로 종목을 비교하고 분석하세요</p>
      </div>

      {/* 필터 섹션 */}
      <div className="filter-section">
        <div className="filter-group">
          <label>정렬 지표:</label>
          <select 
            value={selectedMetric} 
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="filter-select"
          >
            {metrics.map(metric => (
              <option key={metric} value={metric}>{metric}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>정렬 순서:</label>
          <select 
            value={selectedOrder} 
            onChange={(e) => setSelectedOrder(e.target.value)}
            className="filter-select"
          >
            <option value="desc">내림차순 (높은 순)</option>
            <option value="asc">오름차순 (낮은 순)</option>
          </select>
        </div>

        <div className="filter-group">
          <label>업종:</label>
          <select 
            value={selectedIndustry} 
            onChange={(e) => setSelectedIndustry(e.target.value)}
            className="filter-select"
          >
            <option value="">전체</option>
            {industries.map(industry => (
              <option key={industry} value={industry}>{industry}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 랭킹 테이블 */}
      <div className="ranking-table-container">
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>데이터를 불러오는 중...</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <table className="ranking-table">
          <thead>
            <tr>
              <th>순위</th>
              <th>종목코드</th>
              <th>회사명</th>
              <th>업종</th>
              <th>부채비율</th>
              <th>유보율</th>
              <th>매출액증가율</th>
              <th>EPS증가율</th>
              <th>ROA</th>
              <th>ROE</th>
              <th>EPS</th>
              <th>BPS</th>
              <th>PER</th>
              <th>PBR</th>
              <th>EV/EBITDA</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((stock, index) => (
              <tr key={stock.stock_id}>
                <td className="rank-cell">{index + 1}</td>
                <td className="ticker-cell">{stock.ticker}</td>
                <td className="company-cell">{stock.company_name}</td>
                <td className="industry-cell">{stock.industry}</td>
                <td style={{ color: getValueColor(stock.부채비율, '부채비율') }}>
                  {formatValue(stock.부채비율, '부채비율')}
                </td>
                <td style={{ color: getValueColor(stock.유보율, '유보율') }}>
                  {formatValue(stock.유보율, '유보율')}
                </td>
                <td style={{ color: getValueColor(stock.매출액증가율, '매출액증가율') }}>
                  {formatValue(stock.매출액증가율, '매출액증가율')}
                </td>
                <td style={{ color: getValueColor(stock.EPS증가율, 'EPS증가율') }}>
                  {formatValue(stock.EPS증가율, 'EPS증가율')}
                </td>
                <td style={{ color: getValueColor(stock.ROA, 'ROA') }}>
                  {formatValue(stock.ROA, 'ROA')}
                </td>
                <td style={{ color: getValueColor(stock.ROE, 'ROE') }}>
                  {formatValue(stock.ROE, 'ROE')}
                </td>
                <td>{formatValue(stock.EPS, 'EPS')}</td>
                <td>{formatValue(stock.BPS, 'BPS')}</td>
                <td style={{ color: getValueColor(stock.PER, 'PER') }}>
                  {formatValue(stock.PER, 'PER')}
                </td>
                <td style={{ color: getValueColor(stock.PBR, 'PBR') }}>
                  {formatValue(stock.PBR, 'PBR')}
                </td>
                <td style={{ color: getValueColor(stock.EV_EBITDA, 'EV/EBITDA') }}>
                  {formatValue(stock.EV_EBITDA, 'EV/EBITDA')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {rankings.length === 0 && !loading && (
          <div className="no-data">
            <p>📊 표시할 데이터가 없습니다.</p>
          </div>
        )}
      </div>
    </div>
  )
}
