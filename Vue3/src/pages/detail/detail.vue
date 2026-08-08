<template>
  <view class="detail-page" v-if="info">
    <!-- 图片轮播 -->
    <swiper class="cover-swiper" v-if="imgList.length" circular :indicator-dots="imgList.length > 1"
            indicator-color="rgba(255,255,255,0.4)" indicator-active-color="#fff">
      <swiper-item v-for="(img, idx) in imgList" :key="idx">
        <image class="cover-img" :src="img" mode="aspectFill" @click="previewImage(idx)" />
      </swiper-item>
    </swiper>
    <view class="cover-placeholder" v-else>
      <uni-icons type="image" size="60" color="#ccc"></uni-icons>
      <text class="placeholder-text">暂无图片</text>
    </view>

    <!-- 基础信息 -->
    <view class="info-card card">
      <view class="info-top">
        <text class="info-name">{{ info.name }}</text>
        <view class="info-tags">
          <text class="tag hot" v-if="info.is_hot">热门</text>
          <text class="tag rec" v-if="info.is_recommended">精选</text>
        </view>
      </view>
      <view class="info-meta">
        <text class="meta-rating">⭐ {{ info.rating }}分</text>
        <text class="meta-views">{{ formatViews(info.view_count) }}人浏览</text>
        <text class="meta-cat" v-if="info.category_name">{{ info.category_name }}</text>
      </view>
      <view class="info-row">
        <text class="row-label">📍 位置</text>
        <text class="row-value">{{ info.location || '暂无' }}</text>
      </view>
      <view class="info-row">
        <text class="row-label">🎫 门票</text>
        <text class="row-value price" v-if="Number(info.ticket_price) > 0">¥{{ info.ticket_price }}</text>
        <text class="row-value free" v-else>免费开放</text>
      </view>
      <view class="info-row">
        <text class="row-label">🕐 开放</text>
        <text class="row-value">{{ info.open_time || '全天' }}</text>
      </view>
    </view>

    <!-- 景点介绍 -->
    <view class="desc-card card">
      <view class="card-title">景点介绍</view>
      <text class="desc-text">{{ info.description }}</text>
    </view>

    <!-- 评论区 -->
    <view class="review-card card">
      <view class="card-title">
        <text>游客评价</text>
        <text class="review-count">({{ reviewList.length }}条)</text>
      </view>
      <view class="review-list" v-if="reviewList.length">
        <view class="review-item" v-for="item in reviewList" :key="item.id">
          <image class="review-avatar" v-if="item.avatar" :src="item.avatar" mode="aspectFill" />
          <view class="review-avatar review-avatar-icon" v-else>
            <uni-icons type="person-filled" size="28" color="#bbb"></uni-icons>
          </view>
          <view class="review-content">
            <view class="review-head">
              <text class="review-user">{{ item.nickname || item.username }}</text>
              <text class="review-stars">{{ '⭐'.repeat(item.rating) }}</text>
            </view>
            <text class="review-text">{{ item.content }}</text>
            <text class="review-time">{{ formatTime(item.created_at) }}</text>
          </view>
        </view>
      </view>
      <view class="empty-review" v-else>
        <text>暂无评价，快来抢沙发吧~</text>
      </view>
    </view>

    <view style="height: 140rpx;"></view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="bar-icon" @click="toggleFavorite">
        <text class="icon">{{ isFavorite ? '❤️' : '🤍' }}</text>
        <text class="icon-text">{{ isFavorite ? '已收藏' : '收藏' }}</text>
      </view>
      <view class="bar-btn comment-btn" @click="showReviewInput = true">
        <text>写评价</text>
      </view>
    </view>

    <!-- 评论输入弹窗 -->
    <view class="review-mask" v-if="showReviewInput" @click="showReviewInput = false">
      <view class="review-box" @click.stop>
        <view class="review-box-title">
          <text>发表评价</text>
          <text class="close" @click="showReviewInput = false">✕</text>
        </view>
        <view class="rating-select">
          <text class="rating-label">评分：</text>
          <text class="star" v-for="n in 5" :key="n" @click="reviewRating = n"
                :class="{ active: n <= reviewRating }">★</text>
        </view>
        <textarea class="review-input" v-model="reviewContent" placeholder="说说你的游玩体验吧..."
                  maxlength="200" />
        <view class="review-submit" @click="submitReview">发表</view>
      </view>
    </view>
  </view>
</template>

<script>
import {
  getAttractionDetail, getReviews, addReview,
  checkFavorite, addFavorite, removeFavorite,
  recordBrowsing,
} from '@/utils/api'
import { getImageUrl } from '@/utils/image'

export default {
  data() {
    return {
      id: null,
      info: null,
      imgList: [],
      reviewList: [],
      isFavorite: false,
      favoriteId: null,
      showReviewInput: false,
      reviewContent: '',
      reviewRating: 5,
    }
  },
  onLoad(options) {
    this.id = options.id
    this.loadDetail()
    this.loadReviews()
    this.checkFav()
  },
  methods: {
    getImageUrl,
    async loadDetail() {
      try {
        const res = await getAttractionDetail(this.id)
        this.info = res.data
        const imgs = (res.data.image_list || []).filter((u) => u).map(u => getImageUrl(u))
        const cover = res.data.cover ? getImageUrl(res.data.cover) : ''
        this.imgList = imgs.length ? imgs : (cover ? [cover] : [])
        uni.setNavigationBarTitle({ title: res.data.name || '景点详情' })
        this.reportBrowsing()
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    async reportBrowsing() {
      const token = uni.getStorageSync('token')
      if (!token) return
      try {
        await recordBrowsing(this.id)
      } catch (e) {}
    },
    async loadReviews() {
      try {
        const res = await getReviews(this.id)
        this.reviewList = res.data || []
      } catch (e) {}
    },
    async checkFav() {
      const token = uni.getStorageSync('token')
      if (!token) return
      try {
        const res = await checkFavorite(this.id)
        this.isFavorite = res.data.is_favorite
        this.favoriteId = res.data.id || null
      } catch (e) {}
    },
    async toggleFavorite() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showModal({
          title: '提示',
          content: '请先登录后再收藏',
          success: (r) => {
            if (r.confirm) uni.navigateTo({ url: '/pages/login/login' })
          },
        })
        return
      }
      try {
        if (this.isFavorite) {
          await removeFavorite(this.id)
          this.isFavorite = false
          this.favoriteId = null
          uni.showToast({ title: '已取消收藏', icon: 'none' })
        } else {
          const res = await addFavorite(this.id)
          this.isFavorite = true
          uni.showToast({ title: '收藏成功', icon: 'success' })
        }
      } catch (e) {}
    },
    async submitReview() {
      if (!this.reviewContent.trim()) {
        uni.showToast({ title: '请输入评价内容', icon: 'none' })
        return
      }
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showModal({
          title: '提示',
          content: '请先登录后再评论',
          success: (r) => {
            if (r.confirm) uni.navigateTo({ url: '/pages/login/login' })
          },
        })
        return
      }
      try {
        await addReview({
          attraction: this.id,
          content: this.reviewContent,
          rating: this.reviewRating,
        })
        uni.showToast({ title: '评价成功', icon: 'success' })
        this.reviewContent = ''
        this.reviewRating = 5
        this.showReviewInput = false
        this.loadReviews()
      } catch (e) {}
    },
    previewImage(idx) {
      uni.previewImage({ current: idx, urls: this.imgList })
    },
    formatViews(n) {
      if (!n) return '0'
      if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
      return n + ''
    },
    formatTime(t) {
      if (!t) return ''
      return String(t).substring(0, 16).replace('T', ' ')
    },
  },
}
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  padding-bottom: 40rpx;
}
.cover-swiper {
  width: 100%;
  height: 460rpx;
  .cover-img {
    width: 100%;
    height: 100%;
  }
}
.cover-placeholder {
  width: 100%;
  height: 460rpx;
  background: #f0f0f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  .placeholder-text {
    color: #aaa;
    font-size: 26rpx;
    margin-top: 16rpx;
  }
}
/* 卡片通用 */
.card {
  margin: 20rpx 24rpx;
  padding: 30rpx;
  background: #fff;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}
.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #222;
  margin-bottom: 20rpx;
  .review-count {
    font-size: 24rpx;
    color: #999;
    font-weight: normal;
    margin-left: 8rpx;
  }
}
/* 基础信息 */
.info-card {
  .info-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    .info-name {
      font-size: 38rpx;
      font-weight: bold;
      color: #222;
      flex: 1;
    }
    .info-tags {
      display: flex;
      .tag {
        font-size: 20rpx;
        padding: 4rpx 12rpx;
        border-radius: 6rpx;
        margin-left: 8rpx;
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
  }
  .info-meta {
    display: flex;
    align-items: center;
    margin: 16rpx 0 24rpx;
    .meta-rating {
      color: #ff9500;
      font-size: 26rpx;
      font-weight: 600;
      margin-right: 20rpx;
    }
    .meta-views {
      color: #aaa;
      font-size: 24rpx;
      margin-right: 20rpx;
    }
    .meta-cat {
      font-size: 22rpx;
      color: #1aad19;
      background: #f0faf0;
      padding: 4rpx 16rpx;
      border-radius: 20rpx;
    }
  }
  .info-row {
    display: flex;
    align-items: center;
    padding: 14rpx 0;
    border-top: 1rpx solid #f5f5f5;
    .row-label {
      width: 140rpx;
      font-size: 26rpx;
      color: #888;
    }
    .row-value {
      flex: 1;
      font-size: 26rpx;
      color: #333;
      &.price {
        color: #ff5a5f;
        font-weight: bold;
      }
      &.free {
        color: #1aad19;
        font-weight: 600;
      }
    }
  }
}
.desc-text {
  font-size: 28rpx;
  color: #555;
  line-height: 1.8;
}
/* 评论 */
.review-list {
  .review-item {
    display: flex;
    padding: 20rpx 0;
    border-top: 1rpx solid #f5f5f5;
    .review-avatar {
      width: 72rpx;
      height: 72rpx;
      border-radius: 50%;
      flex-shrink: 0;
      background: #eee;
      &.review-avatar-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f0f0f0;
      }
    }
    .review-content {
      flex: 1;
      margin-left: 20rpx;
      min-width: 0;
    }
    .review-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .review-user {
        font-size: 26rpx;
        font-weight: 600;
        color: #333;
      }
      .review-stars {
        font-size: 22rpx;
        color: #ff9500;
      }
    }
    .review-text {
      display: block;
      font-size: 26rpx;
      color: #555;
      line-height: 1.6;
      margin: 8rpx 0;
    }
    .review-time {
      font-size: 22rpx;
      color: #bbb;
    }
  }
}
.empty-review {
  text-align: center;
  padding: 40rpx 0;
  color: #aaa;
  font-size: 26rpx;
}
/* 底部栏 */
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 110rpx;
  background: #fff;
  border-top: 1rpx solid #eee;
  display: flex;
  align-items: center;
  padding: 0 30rpx;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
  .bar-icon {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 120rpx;
    .icon {
      font-size: 40rpx;
    }
    .icon-text {
      font-size: 20rpx;
      color: #888;
      margin-top: 4rpx;
    }
  }
  .bar-btn {
    flex: 1;
    height: 76rpx;
    margin-left: 30rpx;
    background: linear-gradient(135deg, #1aad19, #4ecdc4);
    border-radius: 38rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 30rpx;
    font-weight: 600;
  }
}
/* 评论弹窗 */
.review-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  .review-box {
    width: 100%;
    background: #fff;
    border-radius: 30rpx 30rpx 0 0;
    padding: 30rpx;
    .review-box-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 32rpx;
      font-weight: bold;
      margin-bottom: 24rpx;
      .close {
        color: #999;
        font-size: 36rpx;
      }
    }
    .rating-select {
      display: flex;
      align-items: center;
      margin-bottom: 20rpx;
      .rating-label {
        font-size: 28rpx;
        color: #555;
        margin-right: 12rpx;
      }
      .star {
        font-size: 44rpx;
        color: #ddd;
        margin-right: 10rpx;
        &.active {
          color: #ff9500;
        }
      }
    }
    .review-input {
      width: 100%;
      height: 200rpx;
      padding: 20rpx;
      background: #f8f8f8;
      border-radius: 16rpx;
      font-size: 28rpx;
      box-sizing: border-box;
    }
    .review-submit {
      margin-top: 24rpx;
      height: 80rpx;
      background: linear-gradient(135deg, #1aad19, #4ecdc4);
      border-radius: 40rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 30rpx;
      font-weight: 600;
    }
  }
}
</style>
