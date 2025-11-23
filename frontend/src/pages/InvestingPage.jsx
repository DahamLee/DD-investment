import ModuleSlot from '../components/ModuleSlot.jsx'

export default function InvestingPage() {
  return (
    <div className="container">
      <h2>Investing</h2>
      <ModuleSlot name="investing:featured" note="추천 전략/가이드 강조" />
      <p>전략, 교육, 리서치 도구 소개 섹션</p>
      <ul>
        <li>[모듈] 학습 가이드(초급/중급/고급)</li>
        <li>[모듈] 전략 허브(성장/가치/배당/모멘텀)</li>
        <li>[모듈] 포트폴리오 빌더(모의)</li>
        <li>[모듈] 스크리너/리더보드 바로가기</li>
        <li>[모듈] 교육 영상/웹세미나</li>
      </ul>
    </div>
  )
}


