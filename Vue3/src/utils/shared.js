// 页面间共享状态（用于 tabBar 页面间传参，避免事件时序问题）
export const sharedState = {
  // 待应用的分类筛选 { categoryId, categoryName }
  pendingCategoryFilter: null,
}

export default sharedState
