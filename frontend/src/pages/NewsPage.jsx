import ModuleSlot from '../components/ModuleSlot.jsx'

export default function NewsPage() {
  return (
    <div className="container">
      <h2>News</h2>
      <ModuleSlot name="news:breaking" note="브레이킹 뉴스 실시간 피드" />
      <p>섹터/기업별 뉴스 리스트와 필터</p>
      <ul>
        <li>[모듈] 브레이킹 뉴스 피드</li>
        <li>[모듈] 카테고리 탭(마켓/테크/ETF/옵션 등)</li>
        <li>[모듈] 기사 카드 리스트(페이지네이션/무한스크롤)</li>
        <li>[모듈] 태그/키워드 필터</li>
        <li>[모듈] 추천/연관 기사</li>
      </ul>
    </div>
  )
}


