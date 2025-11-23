import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../api/client.js'
import ModuleSlot from './ModuleSlot.jsx'

export default function StockList({ onStockSelect }) {
  const navigate = useNavigate()
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [market, setMarket] = useState('')
  const [sector, setSector] = useState('')

  function handleStockClick(symbol) {
    if (onStockSelect) {
      onStockSelect(symbol)
    } else {
      // onStockSelect가 없으면 별도 페이지로 이동
      navigate(`/markets/stock/${symbol}`)
    }
  }

  useEffect(() => {
    loadStocks()
  }, [market, sector])

  async function loadStocks() {
    setLoading(true)
    setError('')
    try {
      const data = await apiClient.getStocks(market || null, sector || null, 50)
      setStocks(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || '종목 조회 오류')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="stock-list">
      <ModuleSlot name="stocks:list" note="종목 리스트 모듈" />
      
      <div className="filters" style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
        <select 
          value={market} 
          onChange={(e) => setMarket(e.target.value)}
          style={{ padding: 8, border: '1px solid #ddd', borderRadius: 4 }}
        >
          <option value="">전체 시장</option>
          <option value="KOSPI">KOSPI</option>
          <option value="KOSDAQ">KOSDAQ</option>
        </select>
        
        <input
          type="text"
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          placeholder="섹터 검색"
          style={{ padding: 8, border: '1px solid #ddd', borderRadius: 4, flex: 1 }}
        />
        
        <button onClick={loadStocks} disabled={loading}>
          {loading ? '조회 중...' : '새로고침'}
        </button>
      </div>

      {error && (
        <div style={{ color: '#c00', marginBottom: 16 }}>
          오류: {error}
        </div>
      )}

      <div className="stocks-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
        {stocks.map((stock) => (
          <div 
            key={stock.symbol} 
            className="stock-card" 
            onClick={() => handleStockClick(stock.symbol)}
            style={{ 
              border: '1px solid #eee', 
              borderRadius: 8, 
              padding: 16,
              background: '#fff',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              ':hover': {
                borderColor: '#1976d2',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }
            }}
            onMouseEnter={(e) => {
              e.target.style.borderColor = '#1976d2'
              e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'
            }}
            onMouseLeave={(e) => {
              e.target.style.borderColor = '#eee'
              e.target.style.boxShadow = 'none'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 8 }}>
              <div>
                <h4 style={{ margin: 0, fontSize: 16 }}>{stock.name}</h4>
                <p style={{ margin: 0, color: '#666', fontSize: 12 }}>{stock.symbol}</p>
              </div>
              <span style={{ 
                fontSize: 12, 
                padding: '2px 6px', 
                borderRadius: 4, 
                background: stock.market === 'KOSPI' ? '#e3f2fd' : '#f3e5f5',
                color: stock.market === 'KOSPI' ? '#1976d2' : '#7b1fa2'
              }}>
                {stock.market}
              </span>
            </div>
            
            <div style={{ fontSize: 14, color: '#666' }}>
              {stock.sector && <div>섹터: {stock.sector}</div>}
              {stock.market_cap && (
                <div>시가총액: {stock.market_cap.toLocaleString()}억원</div>
              )}
              {stock.price && (
                <div style={{ marginTop: 8, fontSize: 16, fontWeight: 'bold' }}>
                  {stock.price.toLocaleString()}원
                  {stock.change && (
                    <span style={{ 
                      color: stock.change >= 0 ? '#c62828' : '#2e7d32',
                      marginLeft: 8
                    }}>
                      {stock.change >= 0 ? '+' : ''}{stock.change} ({stock.change_percent}%)
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {stocks.length === 0 && !loading && (
        <div style={{ textAlign: 'center', color: '#666', padding: 40 }}>
          조회된 종목이 없습니다.
        </div>
      )}
    </div>
  )
}
