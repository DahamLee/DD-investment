import { useParams, useNavigate } from 'react-router-dom'
import StockDetail from '../components/StockDetail.jsx'
import ModuleSlot from '../components/ModuleSlot.jsx'

export default function StockDetailPage() {
  const { symbol } = useParams()
  const navigate = useNavigate()

  return (
    <div className="stock-detail-page">
      <ModuleSlot name="stocks:detail-page" note="종목 상세 페이지 모듈" />
      
      <div style={{ marginBottom: 20 }}>
        <button 
          onClick={() => navigate('/markets')}
          style={{
            padding: '8px 16px',
            border: '1px solid #ddd',
            borderRadius: 4,
            background: '#fff',
            cursor: 'pointer'
          }}
        >
          ← Markets로 돌아가기
        </button>
      </div>

      <StockDetail symbol={symbol} />
    </div>
  )
}
