import { Outlet, NavLink, Link } from 'react-router-dom'
import logoUrl from './assets/images/logo.png'
import ModuleSlot from './components/ModuleSlot.jsx'
import { useAuth } from './contexts/AuthContext.jsx'
import './App.css'

export default function App() {
  const { user, logout, isAuthenticated } = useAuth()
  return (
    <div className="site-container">
      <header className="site-header">
        <Link to="/" className="branding-link">
          <div className="branding">
            <img 
              src={logoUrl} 
              alt="DD Investment" 
              className="logo-responsive"
            />
            <div className="brand-text">
              <div className="brand-title">DD Investment</div>
              <div className="brand-subtitle">Data Driven, Invest Wisen</div>
            </div>
          </div>
        </Link>
        <nav className="top-nav">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/markets">Markets</NavLink>
          <NavLink to="/stock-ranking">Stock Ranking</NavLink>
          <NavLink to="/financial-statement">재무제표</NavLink>
          <NavLink to="/lotto">Lotto</NavLink>
          {isAuthenticated ? (
            <>
              <NavLink to="/mypage">MyPage</NavLink>
              <button onClick={logout} className="logout-btn">LogOut</button>
            </>
          ) : (
            <>
              <NavLink to="/login">LogIn</NavLink>
              <NavLink to="/register">회원가입</NavLink>
            </>
          )}
        </nav>
      </header>

      <div className="markets-bar">
        <span>S&P 500</span>
        <span>NASDAQ</span>
        <span>DOW</span>
        <span>10Y</span>
        <span>BTC</span>
      </div>

      <main className="main-content">
        <Outlet />
        <ModuleSlot name="global:footer-cta" note="전역 하단 CTA 자리" />
      </main>

      <footer className="site-footer">© {new Date().getFullYear()} DD Investment</footer>
    </div>
  )
}
