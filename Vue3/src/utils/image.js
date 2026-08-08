// API 基础地址（可能带 /api 后缀，如 http://localhost:8000/api）
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 媒体文件基础地址：去掉 /api 后缀，因为 media 路径是 /media/... 而非 /api/media/...
const MEDIA_BASE = API_BASE.replace(/\/api\/?$/, '')

// H5 开发环境使用 vite 代理
// #ifdef H5
const FULL_BASE = import.meta.env.DEV ? '' : MEDIA_BASE
// #endif
// #ifndef H5
const FULL_BASE = MEDIA_BASE
// #endif

/**
 * 获取图片完整 URL
 * - H5 开发环境：使用相对路径（Vite 代理）
 * - 其他环境：拼接完整后端地址（不含 /api）
 * - 自动对 URL 中的中文进行编码
 */
export function getImageUrl(url) {
  if (!url) return ''
  // 已经是完整 URL
  if (url.startsWith('http')) return encodeURI(url)
  // 拼接基础地址并编码路径
  const full = FULL_BASE + url
  return encodeURI(full)
}

export { API_BASE, FULL_BASE }
