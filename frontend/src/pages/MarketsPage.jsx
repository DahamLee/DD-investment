import ModuleSlot from '../components/ModuleSlot.jsx'
import StockList from '../components/StockList.jsx'

export default function MarketsPage() {
  return (
    <div className="container">
      <h2>Markets</h2>
      <ModuleSlot name="markets:index-overview" note="지수/선물/섹터 요약" />
      <p>지수, 선물, 섹터, 환율 등 마켓 개요 섹션</p>
      
      <div style={{ marginTop: 40 }}>
        <h3>주식 종목</h3>
        <StockList />
      </div>
      <ul>
        <li>[모듈] 인덱스 개요 카드(S&P/NASDAQ/DOW)</li>
        <li>[모듈] 선물/원자재 요약(금/유가/구리 등)</li>
        <li>[모듈] 섹터 퍼포먼스 히트맵</li>
        <li>[모듈] 환율/금리(10Y/2Y) 차트</li>
        <li>[모듈] 마켓 캘린더(경제지표/실적 발표)</li>
      </ul>
    </div>
  )
}


