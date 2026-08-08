<template>
  <view class="home">
    <!-- 顶部导航 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content" :style="navContentStyle">
        <view class="nav-title">
          <text class="title-main">兴宁旅游</text>
          <text class="title-sub">梅州市兴宁市景点推荐</text>
        </view>
        <view class="nav-search" @click="goSearch">
          <text class="icon-search">🔍</text>
          <text class="search-placeholder">搜索景点</text>
        </view>
      </view>
    </view>

    <!-- 占位 -->
    <view :style="placeholderStyle"></view>

    <!-- 轮播图 -->
    <view class="banner-wrap" v-if="banners.length">
      <swiper class="banner-swiper" circular autoplay :interval="4000" :duration="500"
              indicator-dots indicator-color="rgba(255,255,255,0.4)" indicator-active-color="#fff">
        <swiper-item v-for="item in banners" :key="item.id" @click="goDetail(item.attraction_id)">
          <view class="banner-item">
            <image class="banner-img" :src="getImageUrl(item.image)" mode="aspectFill" />
            <view class="banner-mask"></view>
            <text class="banner-title">{{ item.title }}</text>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <!-- 分类导航 -->
    <view class="section">
      <view class="category-grid">
        <view class="category-item" v-for="item in categories" :key="item.id"
              @click="goList(item.id, item.name)">
          <view class="cat-icon">{{ item.icon }}</view>
          <text class="cat-name">{{ item.name }}</text>
        </view>
      </view>
    </view>

    <!-- 热门推荐 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">🔥 热门景点</text>
        <text class="section-more" @click="goList()">查看更多 ></text>
      </view>
      <scroll-view scroll-x class="hot-scroll" show-scrollbar="false" :enable-flex="true" v-if="hotList.length">
        <view class="hot-list">
          <view class="hot-card" v-for="item in hotList" :key="item.id" @click="goDetail(item.id)">
            <image class="hot-img" :src="getImageUrl(item.cover)" mode="aspectFill" />
            <view class="hot-info">
              <text class="hot-name ellipsis-1">{{ item.name }}</text>
              <view class="hot-meta">
                <text class="hot-rating">⭐ {{ item.rating }}</text>
                <text class="hot-views">{{ formatViews(item.view_count) }}浏览</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
      <view class="hot-empty" v-else>
        <text>暂无热门景点</text>
      </view>
    </view>

    <!-- 精选推荐 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">⭐ 精选推荐</text>
        <text class="section-more" @click="goList()">查看更多 ></text>
      </view>
      <view class="rec-list">
        <view class="rec-card card" v-for="item in recList" :key="item.id" @click="goDetail(item.id)">
          <image class="rec-img" :src="getImageUrl(item.cover)" mode="aspectFill" />
          <view class="rec-info">
            <view class="rec-top">
              <text class="rec-name ellipsis-1">{{ item.name }}</text>
              <text class="rec-cat" v-if="item.category_name">{{ item.category_name }}</text>
            </view>
            <text class="rec-loc ellipsis-1">📍 {{ item.location }}</text>
            <view class="rec-bottom">
              <text class="rec-rating">⭐ {{ item.rating }}</text>
              <text class="rec-price" v-if="Number(item.ticket_price) > 0">¥{{ item.ticket_price }}</text>
              <text class="rec-price free" v-else>免费</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="footer-tip">
      <text>— 兴宁欢迎您 —</text>
    </view>

    <!-- 自定义底部导航 -->
    <custom-tabbar :active="0"></custom-tabbar>
  </view>
</template>

<script>
import { getBanners, getCategories, getHotAttractions, getRecommendedAttractions } from '@/utils/api'
import { sharedState } from '@/utils/shared'
import { getImageUrl } from '@/utils/image'

export default {
  data() {
    return {
      statusBarHeight: 20,
      navHeightPx: 44,
      navHeightRpx: 88,
      navRightPaddingRpx: 30,
      banners: [],
      categories: [],
      hotList: [],
      recList: [],
    }
  },
  computed: {
    navContentStyle() {
      return {
        height: this.navHeightRpx + 'rpx',
        paddingRight: this.navRightPaddingRpx + 'rpx',
      }
    },
    placeholderStyle() {
      return { height: (this.statusBarHeight + this.navHeightPx) + 'px' }
    },
  },
  onLoad() {
    const sys = uni.getSystemInfoSync()
    this.statusBarHeight = sys.statusBarHeight || 20
    // #ifdef MP-WEIXIN
    try {
      const menuBtn = uni.getMenuButtonBoundingClientRect()
      // 导航栏内容高度 (px)
      const navH = (menuBtn.top - this.statusBarHeight) * 2 + menuBtn.height
      this.navHeightPx = navH
      // 转为 rpx
      this.navHeightRpx = Math.round(navH * 750 / sys.windowWidth)
      // 右侧避让宽度 (px)，多留 10px 间距
      const rightGap = sys.windowWidth - menuBtn.left + 10
      this.navRightPaddingRpx = Math.round(rightGap * 750 / sys.windowWidth)
    } catch (e) {}
    // #endif
    this.loadData()
  },
  onShow() {
    // 刷新数据
  },
  methods: {
    getImageUrl,
    async loadData() {
      try {
        const [bannerRes, catRes, hotRes, recRes] = await Promise.all([
          getBanners(),
          getCategories(),
          getHotAttractions(),
          getRecommendedAttractions(),
        ])
        this.banners = bannerRes.data || []
        this.categories = catRes.data || []
        this.hotList = hotRes.data || []
        this.recList = recRes.data || []
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    formatViews(n) {
      if (!n) return '0'
      if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
      return n + ''
    },
    goSearch() {
      uni.navigateTo({ url: '/pages/search/search' })
    },
    goDetail(id) {
      if (!id) return
      uni.navigateTo({ url: `/pages/detail/detail?id=${id}` })
    },
    goList(categoryId, categoryName) {
      // 通过共享状态传递分类筛选，list 页在 onShow 中读取（避免事件时序问题）
      if (categoryId) {
        sharedState.pendingCategoryFilter = { categoryId, categoryName }
      } else {
        sharedState.pendingCategoryFilter = null
      }
      uni.switchTab({ url: '/pages/list/list' })
    },
  },
}
</script>

<style lang="scss" scoped>
.home {
  min-height: 100vh;
}
/* 导航栏 */
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 999;
  background: linear-gradient(135deg, #1aad19, #4ecdc4);
  .nav-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-left: 30rpx;
  }
  .nav-title {
    display: flex;
    flex-direction: column;
    .title-main {
      color: #fff;
      font-size: 36rpx;
      font-weight: bold;
    }
    .title-sub {
      color: rgba(255, 255, 255, 0.8);
      font-size: 20rpx;
    }
  }
  .nav-search {
    display: flex;
    align-items: center;
    height: 60rpx;
    padding: 0 24rpx;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 30rpx;
    .icon-search {
      font-size: 26rpx;
      margin-right: 10rpx;
    }
    .search-placeholder {
      color: #999;
      font-size: 26rpx;
    }
  }
}
/* 轮播 */
.banner-wrap {
  padding: 20rpx 24rpx 0;
  .banner-swiper {
    height: 320rpx;
    border-radius: 20rpx;
    overflow: hidden;
  }
  .banner-item {
    position: relative;
    width: 100%;
    height: 100%;
  }
  .banner-img {
    width: 100%;
    height: 100%;
  }
  .banner-mask {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 120rpx;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
  }
  .banner-title {
    position: absolute;
    left: 24rpx;
    bottom: 24rpx;
    color: #fff;
    font-size: 32rpx;
    font-weight: bold;
    text-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.4);
  }
}
/* 区块通用 */
.section {
  margin-top: 30rpx;
  padding: 0 24rpx;
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20rpx;
    .section-title {
      font-size: 32rpx;
      font-weight: bold;
      color: #222;
    }
    .section-more {
      font-size: 24rpx;
      color: #888;
    }
  }
}
/* 分类 */
.category-grid {
  display: flex;
  justify-content: space-between;
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx 10rpx;
  .category-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 20%;
    .cat-icon {
      width: 88rpx;
      height: 88rpx;
      border-radius: 50%;
      background: #f0faf0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 44rpx;
    }
    .cat-name {
      margin-top: 12rpx;
      font-size: 24rpx;
      color: #555;
    }
  }
}
/* 热门横滑 */
.hot-scroll {
  white-space: nowrap;
  width: 100%;
  .hot-list {
    display: flex;
    flex-wrap: nowrap;
    padding-bottom: 6rpx;
  }
  .hot-card {
    flex-shrink: 0;
    width: 280rpx;
    margin-right: 20rpx;
    background: #fff;
    border-radius: 16rpx;
    overflow: hidden;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
    .hot-img {
      width: 100%;
      height: 180rpx;
    }
    .hot-info {
      padding: 16rpx;
    }
    .hot-name {
      font-size: 26rpx;
      font-weight: 600;
      color: #333;
    }
    .hot-meta {
      display: flex;
      justify-content: space-between;
      margin-top: 8rpx;
      .hot-rating {
        font-size: 22rpx;
        color: #ff9500;
      }
      .hot-views {
        font-size: 20rpx;
        color: #aaa;
      }
    }
  }
}
.hot-empty {
  text-align: center;
  padding: 60rpx 0;
  color: #bbb;
  font-size: 26rpx;
  background: #fff;
  border-radius: 16rpx;
}
/* 精选列表 */
.rec-list {
  .rec-card {
    display: flex;
    margin-bottom: 20rpx;
    overflow: hidden;
    .rec-img {
      width: 220rpx;
      height: 180rpx;
      flex-shrink: 0;
    }
    .rec-info {
      flex: 1;
      padding: 18rpx 22rpx;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-width: 0;
    }
    .rec-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .rec-name {
        font-size: 30rpx;
        font-weight: 600;
        color: #222;
        flex: 1;
        min-width: 0;
      }
      .rec-cat {
        font-size: 20rpx;
        color: #1aad19;
        background: #f0faf0;
        padding: 4rpx 14rpx;
        border-radius: 20rpx;
        margin-left: 12rpx;
        flex-shrink: 0;
      }
    }
    .rec-loc {
      font-size: 24rpx;
      color: #888;
      margin-top: 8rpx;
    }
    .rec-bottom {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .rec-rating {
        font-size: 24rpx;
        color: #ff9500;
      }
      .rec-price {
        font-size: 28rpx;
        color: #ff5a5f;
        font-weight: bold;
        &.free {
          color: #1aad19;
        }
      }
    }
  }
}
.footer-tip {
  text-align: center;
  padding: 40rpx 0 160rpx;
  color: #bbb;
  font-size: 24rpx;
}
</style>
