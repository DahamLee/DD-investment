import ModuleSlot from './ModuleSlot.jsx'

export default function StockRankingBlock({ title, stocks, loading, error }) {
  return (
    <div className="stock-ranking-block">
      <div className="ranking-header">
        <h3>{title}</h3>
        <ModuleSlot name={`homepage:${title.toLowerCase().replace(' ', '-')}`} note={`${title} 주식 종목`} />
      </div>
      
      <div className="stocks-list">
        {loading && (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>종목을 불러오는 중...</p>
          </div>
        )}
        
        {error && (
          <div className="error-state">
            <p>❌ {error}</p>
          </div>
        )}
        
        {!loading && !error && stocks.length === 0 && (
          <div className="empty-state">
            <p>종목 데이터가 없습니다.</p>
          </div>
        )}
        
        {!loading && !error && stocks.map((stock, index) => (
          <div key={stock.symbol} className="stock-item">
            <div className="stock-rank">#{index + 1}</div>
            <div className="stock-info">
              <div className="stock-symbol">{stock.symbol}</div>
              <div className="stock-name">{stock.name}</div>
            </div>
            <div className="stock-price">
              <div className="price">
                {stock.currentPrice ? Number(stock.currentPrice).toLocaleString() + '원' : 'N/A'}
              </div>
              <div className={`change ${stock.changePercent >= 0 ? 'positive' : 'negative'}`}>
                {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent}%
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
