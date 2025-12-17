import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import HomePage from './pages/HomePage.jsx'
import MarketsPage from './pages/MarketsPage.jsx'
import NewsPage from './pages/NewsPage.jsx'
import InvestingPage from './pages/InvestingPage.jsx'
import StockDetailPage from './pages/StockDetailPage.jsx'
import StockRankingPage from './pages/StockRankingPage.jsx'
import FinancialStatementPage from './pages/FinancialStatementPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import LottoPage from './pages/LottoPage.jsx'
import MyPage from './pages/MyPage.jsx'
import { AuthProvider } from './contexts/AuthContext.jsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'markets', element: <MarketsPage /> },
      { path: 'markets/stock/:symbol', element: <StockDetailPage /> },
      { path: 'stock-ranking', element: <StockRankingPage /> },
      { path: 'financial-statement', element: <FinancialStatementPage /> },
      { path: 'news', element: <NewsPage /> },
      { path: 'investing', element: <InvestingPage /> },
      { path: 'lotto', element: <LottoPage /> },
      { path: 'mypage', element: <MyPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> }
    ]
  }
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>
)
