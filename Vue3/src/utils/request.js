// 网络请求封装
// API 基础地址：通过 Vite 环境变量注入，开发/生产自动切换
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// H5 开发环境使用 vite 代理（/api），避免跨域；H5 生产及其他平台使用完整地址
// #ifdef H5
const FULL_BASE = import.meta.env.DEV ? '/api' : API_BASE
// #endif
// #ifndef H5
const FULL_BASE = API_BASE
// #endif

// 防止 401 时重复跳转登录页
let isRedirecting = false

function getToken() {
  return uni.getStorageSync('token') || ''
}

function handleUnauthorized(msg) {
  uni.removeStorageSync('token')
  uni.removeStorageSync('userInfo')
  if (isRedirecting) return
  isRedirecting = true
  uni.showToast({ title: msg || '登录已过期，请重新登录', icon: 'none' })
  setTimeout(() => {
    uni.reLaunch({ url: '/pages/login/login', complete: () => { isRedirecting = false } })
  }, 800)
}

export function request(options) {
  const { url, method = 'GET', data = {}, header = {} } = options
  const token = getToken()
  const authHeader = token ? { 'Authorization': 'Token ' + token } : {}
  return new Promise((resolve, reject) => {
    uni.request({
      url: FULL_BASE + url,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...authHeader,
        ...header,
      },
      withCredentials: true,
      success: (res) => {
        if (res.statusCode === 401 || (res.data && res.data.code === 401)) {
          handleUnauthorized(res.data && res.data.msg)
          reject(res.data || res)
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          uni.showToast({ title: '请求失败(' + res.statusCode + ')', icon: 'none' })
          reject(res)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      },
    })
  })
}

export default request
