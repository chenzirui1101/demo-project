import request from './request'

// 分类列表
export const getCategories = () => request({ url: '/categories/' })

// 分类 - 管理
export const createCategory = (data) => request({ url: '/categories/', method: 'POST', data })
export const updateCategory = (id, data) => request({ url: `/categories/${id}/`, method: 'PUT', data })
export const deleteCategory = (id) => request({ url: `/categories/${id}/`, method: 'DELETE' })

// 轮播图
export const getBanners = () => request({ url: '/banners/' })

// 轮播图 - 管理
export const createBanner = (data) => request({ url: '/banners/', method: 'POST', data })
export const updateBanner = (id, data) => request({ url: `/banners/${id}/`, method: 'PUT', data })
export const deleteBanner = (id) => request({ url: `/banners/${id}/`, method: 'DELETE' })

// 景点列表
export const getAttractions = (params = {}) =>
  request({ url: '/attractions/', data: params })

// 景点详情
export const getAttractionDetail = (id) =>
  request({ url: `/attractions/${id}/` })

// 景点 - 管理
export const createAttraction = (data) => request({ url: '/attractions/', method: 'POST', data })
export const updateAttraction = (id, data) => request({ url: `/attractions/${id}/`, method: 'PUT', data })
export const deleteAttraction = (id) => request({ url: `/attractions/${id}/`, method: 'DELETE' })

// 热门景点
export const getHotAttractions = () => request({ url: '/attractions/hot/' })

// 精选推荐
export const getRecommendedAttractions = () => request({ url: '/attractions/recommended/' })

// 评论列表
export const getReviews = (attractionId) =>
  request({ url: '/reviews/', data: { attraction: attractionId } })

// 发表评论
export const addReview = (data) =>
  request({ url: '/reviews/', method: 'POST', data })

// 收藏列表
export const getFavorites = () => request({ url: '/favorites/' })

// 添加收藏
export const addFavorite = (attractionId) =>
  request({ url: '/favorites/', method: 'POST', data: { attraction: attractionId } })

// 检查是否收藏
export const checkFavorite = (attractionId) =>
  request({ url: '/favorites/check/', data: { attraction: attractionId } })

// 按景点ID取消收藏
export const removeFavorite = (attractionId) =>
  request({ url: '/favorites/remove_by_attraction/', method: 'DELETE', data: { attraction: attractionId } })

// 注册
export const register = (data) =>
  request({ url: '/auth/register/', method: 'POST', data })

// 登录
export const login = (data) =>
  request({ url: '/auth/login/', method: 'POST', data })

// 退出
export const logout = () => request({ url: '/auth/logout/', method: 'POST' })

// 用户信息
export const getUserInfo = () => request({ url: '/auth/user/' })

// 更新用户信息
export const updateUserInfo = (data) =>
  request({ url: '/auth/user/', method: 'PUT', data })

// 浏览历史 - 获取列表
export const getBrowsingHistory = () => request({ url: '/browsing-history/' })

// 浏览历史 - 记录浏览
export const recordBrowsing = (attractionId) =>
  request({ url: '/browsing-history/batch_record/', method: 'POST', data: { attraction: attractionId } })

// 浏览历史 - 清空
export const clearBrowsingHistory = () =>
  request({ url: '/browsing-history/clear/', method: 'DELETE' })

// 管理员 - 上传图片
export const uploadImage = (file, subdir = 'attractions') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('subdir', subdir)
  return request({ url: '/admin/upload/', method: 'POST', data: formData, header: { 'Content-Type': 'multipart/form-data' } })
}

// 管理员 - 获取统计数据
export const getAdminStats = () => request({ url: '/admin/stats/' })
