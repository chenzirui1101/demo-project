<template>
  <view class="fav-page">
    <view class="fav-list" v-if="validList.length">
      <view class="fav-item card" v-for="item in validList" :key="item.id" @click="goDetail(item.attraction.id)">
        <image class="fav-img" :src="getImageUrl(item.attraction.cover)" mode="aspectFill" />
        <view class="fav-info">
          <text class="fav-name ellipsis-1">{{ item.attraction.name }}</text>
          <text class="fav-loc ellipsis-1">📍 {{ item.attraction.location }}</text>
          <view class="fav-bottom">
            <text class="rating">⭐ {{ item.attraction.rating }}</text>
            <text class="remove" @click.stop="removeFav(item.id, item.attraction.id, item.attraction.name)">取消收藏</text>
          </view>
        </view>
      </view>
    </view>
    <view class="empty" v-else-if="!loading">
      <uni-icons type="heart" size="80" color="#ddd"></uni-icons>
      <text class="empty-text">还没有收藏景点</text>
      <text class="empty-btn" @click="goList">去逛逛</text>
    </view>

    <!-- 自定义底部导航 -->
    <custom-tabbar :active="2"></custom-tabbar>
  </view>
</template>

<script>
import { getFavorites, removeFavorite } from '@/utils/api'
import { getImageUrl } from '@/utils/image'

export default {
  data() {
    return {
      list: [],
      loading: true,
    }
  },
  computed: {
    validList() {
      return this.list.filter(item => item.attraction)
    },
  },
  onShow() {
    this.loadList()
  },
  methods: {
    getImageUrl,
    async loadList() {
      const token = uni.getStorageSync('token')
      if (!token) {
        this.list = []
        this.loading = false
        this.showLoginTip()
        return
      }
      this.loading = true
      try {
        const res = await getFavorites()
        this.list = res.data || []
      } catch (e) {
        this.list = []
      } finally {
        this.loading = false
      }
    },
    showLoginTip() {
      uni.showModal({
        title: '提示',
        content: '请先登录后查看收藏',
        showCancel: false,
        success: (r) => {
          if (r.confirm) uni.navigateTo({ url: '/pages/login/login' })
        },
      })
    },
    removeFav(favoriteId, attractionId, name) {
      uni.showModal({
        title: '提示',
        content: `确定取消收藏「${name}」吗？`,
        success: async (r) => {
          if (r.confirm) {
            try {
              await removeFavorite(attractionId)
              uni.showToast({ title: '已取消', icon: 'none' })
              await this.loadList()
            } catch (e) {}
          }
        },
      })
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/detail/detail?id=${id}` })
    },
    goList() {
      uni.switchTab({ url: '/pages/list/list' })
    },
  },
}
</script>

<style lang="scss" scoped>
.fav-page {
  min-height: 100vh;
  padding: 20rpx 24rpx 140rpx;
}
.fav-list {
  .fav-item {
    display: flex;
    margin-bottom: 20rpx;
    overflow: hidden;
    .fav-img {
      width: 200rpx;
      height: 170rpx;
      flex-shrink: 0;
    }
    .fav-info {
      flex: 1;
      padding: 18rpx 22rpx;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-width: 0;
    }
    .fav-name {
      font-size: 30rpx;
      font-weight: 600;
      color: #222;
    }
    .fav-loc {
      font-size: 24rpx;
      color: #888;
    }
    .fav-bottom {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .rating {
        font-size: 24rpx;
        color: #ff9500;
      }
      .remove {
        font-size: 24rpx;
        color: #ff5a5f;
      }
    }
  }
}
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;
  .empty-text {
    color: #999;
    font-size: 28rpx;
    margin: 20rpx 0 40rpx;
  }
  .empty-btn {
    padding: 16rpx 50rpx;
    background: #1aad19;
    color: #fff;
    border-radius: 40rpx;
    font-size: 28rpx;
  }
}
</style>
