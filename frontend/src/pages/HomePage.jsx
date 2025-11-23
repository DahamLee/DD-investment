import { useState, useEffect } from 'react'
import ModuleSlot from '../components/ModuleSlot.jsx'
import StockRankingBlock from '../components/StockRankingBlock.jsx'
import { apiClient } from '../api/client.js'

export default function HomePage() {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadStocks()
  }, [])

  async function loadStocks() {
    setLoading(true)
    setError('')
    try {
      const data = await apiClient.getStocks()
      setStocks(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || '종목 조회 오류')
    } finally {
      setLoading(false)
    }
  }

  // 시가총액 순으로 정렬하고 A, B, C 순위로 분할
  const sortedStocks = stocks
    .sort((a, b) => (b.marketCap || 0) - (a.marketCap || 0))
    .slice(0, 30) // 상위 30개만

  const aRankStocks = sortedStocks.slice(0, 10)
  const bRankStocks = sortedStocks.slice(10, 20)
  const cRankStocks = sortedStocks.slice(20, 30)

  return (
    <div className="homepage-container">
      {/* 광고 블록 */}
      <div className="ad-banner">
        <ModuleSlot name="homepage:ad-banner" note="메인 광고 배너" />
        <div className="ad-placeholder">
          <h3>광고 영역</h3>
          <p>적절한 크기의 광고 블록</p>
        </div>
      </div>
      
      {/* 주식 종목 순위 블록들 */}
      <div className="stock-rankings">
        <StockRankingBlock 
          title="A 순위" 
          stocks={aRankStocks} 
          loading={loading}
          error={error}
        />
        <StockRankingBlock 
          title="B 순위" 
          stocks={bRankStocks} 
          loading={loading}
          error={error}
        />
        <StockRankingBlock 
          title="C 순위" 
          stocks={cRankStocks} 
          loading={loading}
          error={error}
        />
      </div>
    </div>
  )
}