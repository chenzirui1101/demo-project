<template>
  <view class="list-page">
    <!-- 搜索栏 -->
    <view class="search-bar" @click="goSearch">
      <text class="icon">🔍</text>
      <text class="placeholder">搜索兴宁景点</text>
    </view>

    <!-- 分类筛选 -->
    <scroll-view scroll-x class="cat-tabs" show-scrollbar="false">
      <view class="cat-tab" :class="{ active: activeCategory === 0 }" @click="selectCategory(0)">全部</view>
      <view class="cat-tab" :class="{ active: activeCategory === item.id }" v-for="item in categories"
            :key="item.id" @click="selectCategory(item.id)">{{ item.name }}</view>
    </scroll-view>

    <!-- 排序栏 -->
    <view class="sort-bar">
      <view class="sort-item" :class="{ active: sortType === 'default' }" @click="changeSort('default')">
        <text>综合</text>
      </view>
      <view class="sort-item" :class="{ active: sortType === 'hot' }" @click="changeSort('hot')">
        <text>人气</text>
      </view>
      <view class="sort-item" :class="{ active: sortType === 'rating' }" @click="changeSort('rating')">
        <text>评分</text>
      </view>
    </view>

    <!-- 景点列表 -->
    <view class="attraction-list">
      <view class="attraction-item card" v-for="item in list" :key="item.id" @click="goDetail(item.id)">
        <view class="item-img-wrap" v-if="item.cover && !imgErrors[item.id]">
          <image class="item-img" :src="getImageUrl(item.cover)" mode="aspectFill" @error="onImgError(item.id)" />
        </view>
        <view class="item-img-placeholder" v-else>
          <uni-icons type="images" size="40" color="#ccc"></uni-icons>
        </view>
        <view class="item-info">
          <view class="item-top">
            <text class="item-name ellipsis-1">{{ item.name }}</text>
            <text class="item-cat" v-if="item.category_name">{{ item.category_name }}</text>
          </view>
          <text class="item-loc ellipsis-1">📍 {{ item.location }}</text>
          <view class="item-bottom">
            <view class="item-tags">
              <text class="tag hot" v-if="item.is_hot">热门</text>
              <text class="tag rec" v-if="item.is_recommended">精选</text>
            </view>
            <view class="item-meta">
              <text class="rating">⭐ {{ item.rating }}</text>
              <text class="price" v-if="Number(item.ticket_price) > 0">¥{{ item.ticket_price }}</text>
              <text class="price free" v-else>免费</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view class="load-status">
      <text v-if="loading">加载中...</text>
      <text v-else-if="!hasMore && list.length">没有更多了</text>
      <text v-else-if="!list.length && !loading">暂无景点数据</text>
    </view>

    <!-- 自定义底部导航 -->
    <custom-tabbar :active="1"></custom-tabbar>
  </view>
</template>

<script>
import { getCategories, getAttractions } from '@/utils/api'
import { sharedState } from '@/utils/shared'
import { getImageUrl } from '@/utils/image'

export default {
  data() {
    return {
      categories: [],
      list: [],
      activeCategory: 0,
      sortType: 'default',
      page: 1,
      hasMore: true,
      loading: false,
      imgErrors: {},
    }
  },
  onLoad() {
    this.loadCategories()
    this.loadList(true)
  },
  onShow() {
    // 读取首页通过共享状态传递的分类筛选
    const filter = sharedState.pendingCategoryFilter
    if (filter && filter.categoryId) {
      this.activeCategory = filter.categoryId
      this.loadList(true)
      // 用完即清，避免重复触发
      sharedState.pendingCategoryFilter = null
    }
  },
  onReachBottom() {
    if (this.hasMore && !this.loading) {
      this.loadList(false)
    }
  },
  methods: {
    getImageUrl,
    async loadCategories() {
      try {
        const res = await getCategories()
        this.categories = res.data || []
      } catch (e) {}
    },
    async loadList(reset = false) {
      if (this.loading) return
      this.loading = true
      if (reset) {
        this.page = 1
        this.hasMore = true
      }
      try {
        const params = { page: this.page }
        if (this.activeCategory) params.category = this.activeCategory
        if (this.sortType !== 'default') params.sort = this.sortType
        const res = await getAttractions(params)
        // 兼容分页结构
        let items = []
        if (Array.isArray(res.data)) {
          items = res.data
          this.hasMore = false
        } else if (res.data && res.data.results) {
          items = res.data.results
          this.hasMore = !!res.data.next
        }
        if (reset) {
          this.list = items
        } else {
          this.list = this.list.concat(items)
        }
        if (items.length < 10) this.hasMore = false
        this.page++
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    selectCategory(id) {
      if (this.activeCategory === id) return
      this.activeCategory = id
      this.loadList(true)
    },
    changeSort(type) {
      if (this.sortType === type) return
      this.sortType = type
      this.loadList(true)
    },
    goSearch() {
      uni.navigateTo({ url: '/pages/search/search' })
    },
    onImgError(id) {
      this.$set(this.imgErrors, id, true)
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/detail/detail?id=${id}` })
    },
  },
}
</script>

<style lang="scss" scoped>
.list-page {
  min-height: 100vh;
  padding-bottom: 140rpx;
}
.search-bar {
  display: flex;
  align-items: center;
  margin: 20rpx 24rpx;
  height: 72rpx;
  padding: 0 24rpx;
  background: #fff;
  border-radius: 36rpx;
  .icon {
    font-size: 28rpx;
    margin-right: 12rpx;
  }
  .placeholder {
    color: #aaa;
    font-size: 26rpx;
  }
}
.cat-tabs {
  white-space: nowrap;
  padding: 0 24rpx 16rpx;
  .cat-tab {
    display: inline-block;
    padding: 12rpx 28rpx;
    margin-right: 16rpx;
    font-size: 26rpx;
    color: #555;
    background: #fff;
    border-radius: 30rpx;
    &.active {
      color: #fff;
      background: #1aad19;
      font-weight: 600;
    }
  }
}
.sort-bar {
  display: flex;
  padding: 16rpx 24rpx;
  background: #fff;
  margin: 0 24rpx 20rpx;
  border-radius: 16rpx;
  .sort-item {
    flex: 1;
    text-align: center;
    font-size: 26rpx;
    color: #666;
    &.active {
      color: #1aad19;
      font-weight: 600;
    }
  }
}
.attraction-list {
  padding: 0 24rpx;
  .attraction-item {
    display: flex;
    margin-bottom: 20rpx;
    overflow: hidden;
    .item-img-wrap {
      width: 220rpx;
      height: 190rpx;
      flex-shrink: 0;
      .item-img {
        width: 100%;
        height: 100%;
      }
    }
    .item-img-placeholder {
      width: 220rpx;
      height: 190rpx;
      flex-shrink: 0;
      background: #f5f5f5;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .item-info {
      flex: 1;
      padding: 18rpx 22rpx;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-width: 0;
    }
    .item-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .item-name {
        font-size: 30rpx;
        font-weight: 600;
        color: #222;
        flex: 1;
        min-width: 0;
      }
      .item-cat {
        font-size: 20rpx;
        color: #1aad19;
        background: #f0faf0;
        padding: 4rpx 14rpx;
        border-radius: 20rpx;
        margin-left: 12rpx;
        flex-shrink: 0;
      }
    }
    .item-loc {
      font-size: 24rpx;
      color: #888;
    }
    .item-bottom {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .item-tags {
        display: flex;
        .tag {
          font-size: 18rpx;
          padding: 2rpx 10rpx;
          border-radius: 6rpx;
          margin-right: 8rpx;
          &.hot {
            color: #ff5a5f;
            background: #fff0f0;
          }
          &.rec {
            color: #ff9500;
            background: #fff8eb;
          }
        }
      }
      .item-meta {
        display: flex;
        align-items: center;
        .rating {
          font-size: 24rpx;
          color: #ff9500;
          margin-right: 16rpx;
        }
        .price {
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
}
.load-status {
  text-align: center;
  padding: 30rpx 0;
  color: #aaa;
  font-size: 24rpx;
}
</style>
