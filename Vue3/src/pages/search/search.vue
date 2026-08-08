<template>
  <view class="search-page">
    <view class="search-box">
      <text class="icon">🔍</text>
      <input class="input" v-model="keyword" placeholder="搜索兴宁景点" confirm-type="search"
             @confirm="doSearch" focus />
      <text class="btn" @click="doSearch">搜索</text>
    </view>

    <!-- 搜索历史 -->
    <view class="history" v-if="!searched">
      <view class="history-title" v-if="history.length">
        <text>搜索历史</text>
        <text class="clear" @click="clearHistory">清空</text>
      </view>
      <view class="history-tags" v-if="history.length">
        <view class="history-tag" v-for="(h, i) in history" :key="i" @click="searchByTag(h)">{{ h }}</view>
      </view>
      <view class="hot-search">
        <view class="history-title"><text>热门搜索</text></view>
        <view class="history-tags">
          <view class="history-tag" v-for="h in hotWords" :key="h" @click="searchByTag(h)">{{ h }}</view>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <view class="result-list" v-if="searched">
      <view class="result-count" v-if="list.length">共找到 {{ list.length }} 个景点</view>
      <view class="attraction-item card" v-for="item in list" :key="item.id" @click="goDetail(item.id)">
        <view class="item-img-wrap" v-if="item.cover && !imgErrors[item.id]">
          <image class="item-img" :src="getImageUrl(item.cover)" mode="aspectFill" @error="onImgError(item.id)" />
        </view>
        <view class="item-img-placeholder" v-else>
          <uni-icons type="images" size="40" color="#ccc"></uni-icons>
        </view>
        <view class="item-info">
          <text class="item-name ellipsis-1">{{ item.name }}</text>
          <text class="item-loc ellipsis-1">📍 {{ item.location }}</text>
          <view class="item-bottom">
            <text class="rating">⭐ {{ item.rating }}</text>
            <text class="price" v-if="Number(item.ticket_price) > 0">¥{{ item.ticket_price }}</text>
            <text class="price free" v-else>免费</text>
          </view>
        </view>
      </view>
      <view class="empty" v-if="!list.length">
        <text>😢 没有找到相关景点</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getAttractions } from '@/utils/api'
import { getImageUrl } from '@/utils/image'

export default {
  data() {
    return {
      keyword: '',
      list: [],
      searched: false,
      history: [],
      hotWords: ['神光山', '温泉', '围龙屋', '合水水库', '学宫'],
      imgErrors: {},
    }
  },
  onLoad() {
    // 读取本地存储时做安全类型校验，避免旧缓存为字符串/null导致 filter 报错
    const saved = uni.getStorageSync('searchHistory')
    this.history = Array.isArray(saved) ? saved : []
  },
  methods: {
    getImageUrl,
    async doSearch() {
      const kw = this.keyword.trim()
      if (!kw) {
        uni.showToast({ title: '请输入关键词', icon: 'none' })
        return
      }
      this.saveHistory(kw)
      try {
        uni.showLoading({ title: '搜索中' })
        const res = await getAttractions({ keyword: kw })
        this.list = Array.isArray(res.data) ? res.data : (res.data.results || [])
        this.searched = true
      } catch (e) {
        uni.showToast({ title: '搜索失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    searchByTag(kw) {
      this.keyword = kw
      this.doSearch()
    },
    saveHistory(kw) {
      const arr = Array.isArray(this.history) ? this.history : []
      const h = arr.filter((x) => x !== kw)
      h.unshift(kw)
      this.history = h.slice(0, 10)
      uni.setStorageSync('searchHistory', this.history)
    },
    clearHistory() {
      this.history = []
      uni.removeStorageSync('searchHistory')
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
.search-page {
  min-height: 100vh;
}
.search-box {
  display: flex;
  align-items: center;
  margin: 20rpx 24rpx;
  height: 76rpx;
  padding: 0 20rpx;
  background: #fff;
  border-radius: 38rpx;
  .icon {
    font-size: 30rpx;
    margin-right: 12rpx;
  }
  .input {
    flex: 1;
    height: 76rpx;
    font-size: 28rpx;
  }
  .btn {
    color: #1aad19;
    font-size: 28rpx;
    font-weight: 600;
    padding-left: 16rpx;
  }
}
.history {
  padding: 20rpx 24rpx;
  .history-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 28rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
    .clear {
      font-size: 24rpx;
      color: #999;
      font-weight: normal;
    }
  }
  .history-tags {
    display: flex;
    flex-wrap: wrap;
    .history-tag {
      padding: 12rpx 28rpx;
      background: #fff;
      border-radius: 30rpx;
      font-size: 26rpx;
      color: #555;
      margin: 0 16rpx 16rpx 0;
    }
  }
  .hot-search {
    margin-top: 40rpx;
  }
}
.result-list {
  padding: 0 24rpx;
  .result-count {
    font-size: 24rpx;
    color: #888;
    margin-bottom: 16rpx;
  }
  .attraction-item {
    display: flex;
    margin-bottom: 20rpx;
    overflow: hidden;
    .item-img-wrap {
      width: 200rpx;
      height: 170rpx;
      flex-shrink: 0;
      .item-img {
        width: 100%;
        height: 100%;
      }
    }
    .item-img-placeholder {
      width: 200rpx;
      height: 170rpx;
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
    .item-name {
      font-size: 30rpx;
      font-weight: 600;
      color: #222;
    }
    .item-loc {
      font-size: 24rpx;
      color: #888;
    }
    .item-bottom {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .rating {
        font-size: 24rpx;
        color: #ff9500;
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
  .empty {
    text-align: center;
    padding: 100rpx 0;
    color: #aaa;
    font-size: 28rpx;
  }
}
</style>
