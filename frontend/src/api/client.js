const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    // body가 있으면 config에 추가
    if (options.body) {
      config.body = options.body
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API Request failed:', error)
      throw error
    }
  }

  // Markets API
  async getTickers(market = null) {
    const params = market ? `?market=${encodeURIComponent(market)}` : ''
    return this.request(`/markets/tickers${params}`)
  }

  async getOhlc(ticker, start = null, end = null, prevOnly = true) {
    const params = new URLSearchParams({
      ticker,
      prev_only: prevOnly.toString()
    })
    if (start) params.append('start', start)
    if (end) params.append('end', end)
    
    return this.request(`/markets/ohlc?${params}`)
  }

  // News API
  async getNews(category = null, page = 1, pageSize = 20, search = null) {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString()
    })
    if (category) params.append('category', category)
    if (search) params.append('search', search)
    
    return this.request(`/news/news?${params}`)
  }

  async getNewsDetail(newsId) {
    return this.request(`/news/news/${newsId}`)
  }

  // Stocks API
  async getStocks(market = null, sector = null, limit = 100) {
    const params = new URLSearchParams({
      limit: limit.toString()
    })
    if (market) params.append('market', market)
    if (sector) params.append('sector', sector)
    
    return this.request(`/stocks/stocks?${params}`)
  }

  async getStockDetail(symbol) {
    return this.request(`/stocks/stocks/${symbol}`)
  }

  async getStockCandles(symbol, start = null, end = null, interval = '1d') {
    const params = new URLSearchParams({
      interval
    })
    if (start) params.append('start', start)
    if (end) params.append('end', end)
    
    return this.request(`/stocks/stocks/${symbol}/candles?${params}`)
  }

  async getStockIndicators(symbol, start = null, end = null, indicators = 'ma,rsi,macd,bollinger') {
    const params = new URLSearchParams({
      indicators
    })
    if (start) params.append('start', start)
    if (end) params.append('end', end)
    
    return this.request(`/stocks/stocks/${symbol}/indicators?${params}`)
  }

  // Lotto API
  async generateLottoNumbers(userId = null) {
    const params = userId ? `?user_id=${userId}` : ''
    return this.request(`/lotto/generate${params}`)
  }

  async generateMultipleLottoSets(count = 5) {
    return this.request(`/lotto/generate-multiple?count=${count}`)
  }

  async analyzeLottoNumbers(numbers) {
    return this.request('/lotto/analyze', {
      method: 'POST',
      body: JSON.stringify(numbers)
    })
  }

  async getTodayLotto(userId = null) {
    const params = userId ? `?user_id=${userId}` : ''
    return this.request(`/lotto/today${params}`)
  }

  async markLottoAsViewed(lottoId, userId = null) {
    const params = userId ? `?user_id=${userId}` : ''
    return this.request(`/lotto/mark-viewed/${lottoId}${params}`, {
      method: 'POST'
    })
  }

  async getLottoHistory(userId, limit = 10) {
    return this.request(`/lotto/history?user_id=${userId}&limit=${limit}`)
  }

  async trackTeamView(lottoId, teamId, memberName) {
    return this.request('/lotto/track-team-view', {
      method: 'POST',
      body: JSON.stringify({
        lotto_id: lottoId,
        team_id: teamId,
        member_name: memberName
      })
    })
  }

  async getTeamViewStatus(lottoId, teamId) {
    return this.request(`/lotto/team-status/${lottoId}?team_id=${teamId}`)
  }

  // Health API
  async getHealth() {
    return this.request('/health')
  }
}

export const apiClient = new ApiClient()
export default apiClient
