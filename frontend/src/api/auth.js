/**
 * 인증 API 클라이언트
 */
import apiClient from './client'

const authAPI = {
  /**
   * 회원가입
   */
  register: async (userData) => {
    try {
      const response = await apiClient.request('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData)
      })
      return response
    } catch (error) {
      throw error.message || '회원가입에 실패했습니다'
    }
  },

  /**
   * 로그인
   */
  login: async (username, password) => {
    try {
      const response = await apiClient.request('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: username,
          password: password
        })
      })
      
      // 토큰 저장
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
      }
      
      return response
    } catch (error) {
      throw error.message || '로그인에 실패했습니다'
    }
  },

  /**
   * 로그아웃
   */
  logout: async () => {
    try {
      await apiClient.request('/auth/logout', {
        method: 'POST'
      })
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      return { success: true }
    } catch (error) {
      // 로그아웃은 실패해도 로컬 데이터는 삭제
      console.error('Logout failed:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      return { success: true }
    }
  },

  /**
   * 현재 사용자 정보 조회
   */
  getCurrentUser: async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('토큰이 없습니다')
      }
      
      const response = await apiClient.request(`/auth/me?token=${token}`)
      return response
    } catch (error) {
      throw error.message || '사용자 정보 조회에 실패했습니다'
    }
  },

  /**
   * 사용자명 중복 확인
   */
  checkUsername: async (username) => {
    try {
      const response = await apiClient.request(`/auth/check-username?username=${encodeURIComponent(username)}`, {
        method: 'POST'
      })
      return response
    } catch (error) {
      console.error('Username check error:', error)
      throw error.message || '사용자명 확인에 실패했습니다'
    }
  },

  /**
   * 이메일 중복 확인
   */
  checkEmail: async (email) => {
    try {
      const response = await apiClient.request(`/auth/check-email?email=${encodeURIComponent(email)}`, {
        method: 'POST'
      })
      return response
    } catch (error) {
      console.error('Email check error:', error)
      throw error.message || '이메일 확인에 실패했습니다'
    }
  },

  /**
   * 닉네임 중복 확인
   */
  checkNickname: async (nickname) => {
    try {
      const response = await apiClient.request(`/auth/check-nickname?nickname=${encodeURIComponent(nickname)}`, {
        method: 'POST'
      })
      return response
    } catch (error) {
      console.error('Nickname check error:', error)
      throw error.message || '닉네임 확인에 실패했습니다'
    }
  },

  /**
   * 로그인 상태 확인
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token')
  },

  /**
   * 저장된 사용자 정보 가져오기
   */
  getStoredUser: () => {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  /**
   * 이메일 인증 코드 발송
   */
  sendVerificationEmail: async (email) => {
    try {
      const response = await apiClient.request(`/auth/send-verification-email?email=${encodeURIComponent(email)}`, {
        method: 'POST'
      })
      return response
    } catch (error) {
      console.error('Email verification send error:', error)
      throw error.message || '이메일 발송에 실패했습니다'
    }
  },

  /**
   * 이메일 인증 코드 검증
   */
  verifyEmailCode: async (email, code) => {
    try {
      const response = await apiClient.request(`/auth/verify-email-code?email=${encodeURIComponent(email)}&code=${encodeURIComponent(code)}`, {
        method: 'POST'
      })
      return response
    } catch (error) {
      console.error('Email verification error:', error)
      throw error.message || '이메일 인증에 실패했습니다'
    }
  }
}

export default authAPI


