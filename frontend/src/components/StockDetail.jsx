import { useState, useEffect } from 'react'
import { apiClient } from '../api/client.js'
import ModuleSlot from './ModuleSlot.jsx'
import RealCandlestickChart from './RealCandlestickChart.jsx'
import RSIChart from './RSIChart.jsx'

export default function StockDetail({ symbol }) {
  const [stock, setStock] = useState(null)
  const [candles, setCandles] = useState([])
  const [indicators, setIndicators] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('detail')

  useEffect(() => {
    console.log('StockDetail symbol:', symbol)
    if (symbol) {
      loadStockData()
    }
  }, [symbol])

  async function loadStockData() {
    setLoading(true)
    setError('')
    try {
      const [stockData, candlesData, indicatorsData] = await Promise.all([
        apiClient.getStockDetail(symbol),
        apiClient.getStockCandles(symbol, null, null, '1d'),
        apiClient.getStockIndicators(symbol, null, null, 'ma,rsi,macd,bollinger')
      ])
      
      setStock(stockData)
      setCandles(Array.isArray(candlesData) ? candlesData.slice(-30) : []) // 최근 30일
      setIndicators(Array.isArray(indicatorsData) ? indicatorsData.slice(-30) : [])
    } catch (err) {
      setError(err.message || '종목 데이터 조회 오류')
    } finally {
      setLoading(false)
    }
  }

  if (!symbol) {
    return <div>종목을 선택해주세요.</div>
  }

  return (
    <div className="stock-detail">
      <ModuleSlot name="stocks:detail" note="종목 상세 정보 모듈" />
      
      {loading && <div>로딩 중...</div>}
      
      {error && (
        <div style={{ color: '#c00', marginBottom: 16 }}>
          오류: {error}
        </div>
      )}

      {stock && (
        <div>
          {/* 종목 기본 정보 */}
          <div className="stock-header" style={{ 
            border: '1px solid #eee', 
            borderRadius: 8, 
            padding: 20, 
            marginBottom: 20,
            background: '#fff'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div>
                <h2 style={{ margin: 0, fontSize: 24 }}>{stock.name}</h2>
                <p style={{ margin: '4px 0', color: '#666' }}>{stock.symbol} | {stock.market}</p>
                {stock.sector && <p style={{ margin: '4px 0', color: '#666' }}>섹터: {stock.sector}</p>}
              </div>
              <div style={{ textAlign: 'right' }}>
                {stock.price && (
                  <div style={{ fontSize: 28, fontWeight: 'bold', marginBottom: 4 }}>
                    {stock.price.toLocaleString()}원
                  </div>
                )}
                {stock.change && (
                  <div style={{ 
                    color: stock.change >= 0 ? '#c62828' : '#2e7d32',
                    fontSize: 16
                  }}>
                    {stock.change >= 0 ? '+' : ''}{stock.change} ({stock.change_percent}%)
                  </div>
                )}
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginTop: 16 }}>
              {stock.market_cap && (
                <div>
                  <strong>시가총액:</strong> {stock.market_cap.toLocaleString()}억원
                </div>
              )}
              {stock.volume && (
                <div>
                  <strong>거래량:</strong> {stock.volume.toLocaleString()}
                </div>
              )}
              {stock.high_52w && (
                <div>
                  <strong>52주 최고:</strong> {stock.high_52w.toLocaleString()}원
                </div>
              )}
              {stock.low_52w && (
                <div>
                  <strong>52주 최저:</strong> {stock.low_52w.toLocaleString()}원
                </div>
              )}
            </div>
          </div>

          {/* 탭 네비게이션 */}
          <div className="tabs" style={{ marginBottom: 20 }}>
            <button 
              onClick={() => setActiveTab('detail')}
              style={{ 
                padding: '8px 16px', 
                marginRight: 8, 
                border: '1px solid #ddd',
                background: activeTab === 'detail' ? '#1976d2' : '#fff',
                color: activeTab === 'detail' ? '#fff' : '#333',
                borderRadius: 4
              }}
            >
              상세 정보
            </button>
            <button 
              onClick={() => setActiveTab('candles')}
              style={{ 
                padding: '8px 16px', 
                marginRight: 8, 
                border: '1px solid #ddd',
                background: activeTab === 'candles' ? '#1976d2' : '#fff',
                color: activeTab === 'candles' ? '#fff' : '#333',
                borderRadius: 4
              }}
            >
              캔들차트
            </button>
            <button 
              onClick={() => setActiveTab('indicators')}
              style={{ 
                padding: '8px 16px', 
                border: '1px solid #ddd',
                background: activeTab === 'indicators' ? '#1976d2' : '#fff',
                color: activeTab === 'indicators' ? '#fff' : '#333',
                borderRadius: 4
              }}
            >
              기술지표
            </button>
          </div>

          {/* 탭 내용 */}
          {activeTab === 'detail' && (
            <div className="detail-content">
              <h3>종목 상세 정보</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
                <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 16 }}>
                  <h4>기본 정보</h4>
                  <p><strong>종목명:</strong> {stock.name}</p>
                  <p><strong>종목코드:</strong> {stock.symbol}</p>
                  <p><strong>시장:</strong> {stock.market}</p>
                  {stock.sector && <p><strong>섹터:</strong> {stock.sector}</p>}
                </div>
                
                <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 16 }}>
                  <h4>시장 정보</h4>
                  {stock.market_cap && <p><strong>시가총액:</strong> {stock.market_cap.toLocaleString()}억원</p>}
                  {stock.volume && <p><strong>거래량:</strong> {stock.volume.toLocaleString()}</p>}
                  {stock.high_52w && <p><strong>52주 최고:</strong> {stock.high_52w.toLocaleString()}원</p>}
                  {stock.low_52w && <p><strong>52주 최저:</strong> {stock.low_52w.toLocaleString()}원</p>}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'candles' && (
            <div className="candles-content">
              <h3>최근 30일 캔들차트</h3>
              
              {/* 진짜 캔들스틱 차트 */}
              <div style={{ marginBottom: 20 }}>
                <RealCandlestickChart candles={candles} indicators={indicators} />
              </div>

              {/* 데이터 테이블 */}
              <div style={{ maxHeight: 400, overflow: 'auto', border: '1px solid #eee', borderRadius: 8 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#f5f5f5' }}>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>날짜</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>시가</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>고가</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>저가</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>종가</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>거래량</th>
                    </tr>
                  </thead>
                  <tbody>
                    {candles.map((candle, index) => (
                      <tr key={index}>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{candle.date}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{candle.open.toLocaleString()}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{candle.high.toLocaleString()}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{candle.low.toLocaleString()}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{candle.close.toLocaleString()}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{candle.volume?.toLocaleString() || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'indicators' && (
            <div className="indicators-content">
              <h3>기술지표 (최근 30일)</h3>
              
              {/* RSI & MACD 차트 */}
              <div style={{ marginBottom: 20 }}>
                <RSIChart indicators={indicators} />
              </div>

              {/* 데이터 테이블 */}
              <div style={{ maxHeight: 400, overflow: 'auto', border: '1px solid #eee', borderRadius: 8 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#f5f5f5' }}>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>날짜</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>MA5</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>MA20</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>MA60</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>RSI</th>
                      <th style={{ padding: 8, border: '1px solid #ddd' }}>MACD</th>
                    </tr>
                  </thead>
                  <tbody>
                    {indicators.map((indicator, index) => (
                      <tr key={index}>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{indicator.date}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{indicator.ma5?.toFixed(2) || '-'}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{indicator.ma20?.toFixed(2) || '-'}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{indicator.ma60?.toFixed(2) || '-'}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{indicator.rsi?.toFixed(2) || '-'}</td>
                        <td style={{ padding: 8, border: '1px solid #ddd' }}>{indicator.macd?.toFixed(2) || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
