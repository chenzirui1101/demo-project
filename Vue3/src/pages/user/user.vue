<template>
  <view class="user-page">
    <!-- 用户信息头部 -->
    <view class="user-header">
      <view class="header-bg"></view>
      <view class="user-card">
        <block v-if="isLogin">
          <view class="avatar-wrap" v-if="userInfo.avatar">
            <image class="avatar" :src="userInfo.avatar" mode="aspectFill" />
          </view>
          <view class="avatar-icon" v-else>
            <uni-icons type="person-filled" size="56" color="#1aad19"></uni-icons>
          </view>
          <view class="user-meta">
            <text class="nickname">{{ userInfo.nickname || userInfo.username || '游客' }}</text>
            <text class="username">账号：{{ userInfo.username }}</text>
          </view>
          <text class="edit-btn" @click="goEdit">编辑</text>
        </block>
        <block v-else>
          <view class="avatar-icon">
            <uni-icons type="person-filled" size="56" color="#bbb"></uni-icons>
          </view>
          <view class="user-meta">
            <text class="nickname login-tip" @click="goLogin">点击登录</text>
            <text class="username">登录后享受更多服务</text>
          </view>
        </block>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-group card">
      <view class="menu-item" v-if="userInfo.is_staff" @click="goAdmin">
        <uni-icons type="settings" size="22" color="#ff9500"></uni-icons>
        <text class="menu-text">管理员后台</text>
        <text class="admin-badge">ADMIN</text>
        <uni-icons type="right" size="16" color="#ccc"></uni-icons>
      </view>
      <view class="menu-item" @click="goFavorites">
        <uni-icons type="heart" size="22" color="#1aad19"></uni-icons>
        <text class="menu-text">我的收藏</text>
        <uni-icons type="right" size="16" color="#ccc"></uni-icons>
      </view>
      <view class="menu-item" @click="toggleHistory">
        <uni-icons type="location" size="22" color="#1aad19"></uni-icons>
        <text class="menu-text">浏览景点</text>
        <text class="history-count" v-if="historyList.length">{{ historyList.length }}</text>
        <uni-icons :type="showHistory ? 'up' : 'right'" size="16" color="#ccc"></uni-icons>
      </view>
      <view class="menu-item" @click="goSearch">
        <uni-icons type="search" size="22" color="#1aad19"></uni-icons>
        <text class="menu-text">搜索景点</text>
        <uni-icons type="right" size="16" color="#ccc"></uni-icons>
      </view>
    </view>

    <!-- 浏览历史 -->
    <view class="history-section card" v-if="showHistory && isLogin">
      <view class="history-header">
        <text class="history-title">最近浏览</text>
        <text class="history-clear" @click="clearHistory" v-if="historyList.length">清空</text>
      </view>
      <view class="history-list" v-if="historyList.length">
        <view class="history-item" v-for="item in historyList" :key="item.id" @click="goDetail(item.attraction_id)">
          <image class="history-img" :src="getImageUrl(item.attraction_cover)" mode="aspectFill" />
          <view class="history-info">
            <text class="history-name">{{ item.attraction_name }}</text>
            <text class="history-meta">
              <text class="history-cat">{{ item.category_name }}</text>
              <text class="history-loc">{{ item.location }}</text>
            </text>
            <text class="history-time">{{ formatTime(item.viewed_at) }}</text>
          </view>
          <uni-icons type="right" size="14" color="#ccc"></uni-icons>
        </view>
      </view>
      <view class="history-empty" v-else>
        <text class="empty-icon">📭</text>
        <text>暂无浏览记录</text>
      </view>
      <!-- 简化版功能菜单 -->
    </view>

    <view class="menu-group card">
      <view class="menu-item" @click="aboutUs">
        <uni-icons type="info" size="22" color="#1aad19"></uni-icons>
        <text class="menu-text">关于我们</text>
        <uni-icons type="right" size="16" color="#ccc"></uni-icons>
      </view>
      <view class="menu-item" v-if="isLogin" @click="doLogout">
        <uni-icons type="undo" size="22" color="#ff5a5f"></uni-icons>
        <text class="menu-text">退出登录</text>
        <uni-icons type="right" size="16" color="#ccc"></uni-icons>
      </view>
    </view>

    <view class="footer-info">
      <text>兴宁旅游 v1.0.0</text>
      <text>梅州市兴宁市旅游景点推荐</text>
    </view>

    <!-- 自定义底部导航 -->
    <custom-tabbar :active="3"></custom-tabbar>

    <!-- 编辑资料弹窗 -->
    <view class="edit-mask" v-if="showEdit" @click="showEdit = false">
      <view class="edit-box" @click.stop>
        <view class="edit-title">编辑资料</view>
        <view class="edit-row">
          <text class="label">昵称</text>
          <input class="edit-input" v-model="editForm.nickname" placeholder="请输入昵称" />
        </view>
        <view class="edit-row">
          <text class="label">手机号</text>
          <input class="edit-input" v-model="editForm.phone" placeholder="请输入手机号" />
        </view>
        <view class="edit-actions">
          <text class="cancel" @click="showEdit = false">取消</text>
          <text class="save" @click="saveProfile">保存</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getUserInfo, updateUserInfo, logout, getBrowsingHistory, clearBrowsingHistory } from '@/utils/api'
import { getImageUrl } from '@/utils/image'

export default {
  data() {
    return {
      isLogin: false,
      userInfo: {},
      showEdit: false,
      editForm: { nickname: '', phone: '' },
      showHistory: false,
      historyList: [],
    }
  },
  onShow() {
    this.checkLogin()
    if (this.isLogin) {
      this.loadHistory()
    }
  },
  methods: {
    getImageUrl,
    async loadHistory() {
      try {
        const res = await getBrowsingHistory()
        this.historyList = res.data || []
      } catch (e) {}
    },
    toggleHistory() {
      if (!this.isLogin) {
        this.goLogin()
        return
      }
      this.showHistory = !this.showHistory
      if (this.showHistory) {
        this.loadHistory()
      }
    },
    async clearHistory() {
      uni.showModal({
        title: '提示',
        content: '确定清空浏览记录吗？',
        success: async (r) => {
          if (r.confirm) {
            try {
              await clearBrowsingHistory()
              this.historyList = []
              uni.showToast({ title: '已清空', icon: 'none' })
            } catch (e) {}
          }
        },
      })
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/detail/detail?id=${id}` })
    },
    formatTime(t) {
      if (!t) return ''
      const d = new Date(t)
      const now = new Date()
      const diff = (now - d) / 1000
      if (diff < 60) return '刚刚'
      if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
      if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
      if (diff < 604800) return Math.floor(diff / 86400) + '天前'
      return String(t).substring(0, 16).replace('T', ' ')
    },
    async checkLogin() {
      const token = uni.getStorageSync('token')
      if (!token) {
        this.isLogin = false
        return
      }
      try {
        const res = await getUserInfo()
        if (res.code === 0 && res.data) {
          this.userInfo = res.data
          this.isLogin = true
        }
      } catch (e) {
        this.isLogin = false
      }
    },
    goLogin() {
      uni.navigateTo({ url: '/pages/login/login' })
    },
    goFavorites() {
      if (!this.isLogin) {
        this.goLogin()
        return
      }
      uni.switchTab({ url: '/pages/favorites/favorites' })
    },
    goAdmin() {
      uni.navigateTo({ url: '/pages/admin/admin' })
    },
    goSearch() {
      uni.navigateTo({ url: '/pages/search/search' })
    },
    goEdit() {
      this.editForm.nickname = this.userInfo.nickname || ''
      this.editForm.phone = this.userInfo.phone || ''
      this.showEdit = true
    },
    async saveProfile() {
      try {
        await updateUserInfo(this.editForm)
        uni.showToast({ title: '保存成功', icon: 'success' })
        this.showEdit = false
        this.checkLogin()
      } catch (e) {}
    },
    doLogout() {
      uni.showModal({
        title: '提示',
        content: '确定退出登录吗？',
        success: async (r) => {
          if (r.confirm) {
            try {
              await logout()
            } catch (e) {}
            uni.removeStorageSync('token')
            this.isLogin = false
            this.userInfo = {}
            uni.showToast({ title: '已退出', icon: 'none' })
          }
        },
      })
    },
    aboutUs() {
      uni.showModal({
        title: '关于我们',
        content: '兴宁旅游APP，为您推荐梅州市兴宁市精彩旅游景点，发现客家文化之美。',
        showCancel: false,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.user-page {
  min-height: 100vh;
  padding-bottom: 140rpx;
}
.user-header {
  position: relative;
  .header-bg {
    height: 240rpx;
    background: linear-gradient(135deg, #1aad19, #4ecdc4);
  }
  .user-card {
    position: relative;
    margin: -100rpx 24rpx 0;
    background: #fff;
    border-radius: 20rpx;
    padding: 30rpx;
    display: flex;
    align-items: center;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
    .avatar-wrap {
      width: 120rpx;
      height: 120rpx;
      border-radius: 50%;
      overflow: hidden;
      border: 4rpx solid #fff;
      box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
      .avatar {
        width: 100%;
        height: 100%;
      }
    }
    .avatar-icon {
      width: 120rpx;
      height: 120rpx;
      border-radius: 50%;
      background: #f0faf0;
      border: 4rpx solid #fff;
      box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .user-meta {
      flex: 1;
      margin-left: 24rpx;
      display: flex;
      flex-direction: column;
      .nickname {
        font-size: 34rpx;
        font-weight: bold;
        color: #222;
      }
      .nickname.login-tip {
        color: #1aad19;
      }
      .username {
        font-size: 24rpx;
        color: #999;
        margin-top: 8rpx;
      }
    }
    .edit-btn {
      font-size: 26rpx;
      color: #1aad19;
      padding: 8rpx 24rpx;
      border: 1rpx solid #1aad19;
      border-radius: 30rpx;
    }
  }
}
.menu-group {
  margin: 20rpx 24rpx;
  padding: 0 30rpx;
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  .menu-item {
    display: flex;
    align-items: center;
    height: 100rpx;
    border-bottom: 1rpx solid #f5f5f5;
    &:last-child {
      border-bottom: none;
    }
    /* uni-icons 第一个图标 */
    .uni-icons:first-child {
      margin-right: 20rpx;
    }
    .menu-text {
      flex: 1;
      font-size: 28rpx;
      color: #333;
    }
  }
}
.admin-badge {
  font-size: 20rpx;
  color: #fff;
  background: linear-gradient(135deg, #ff9500, #ff5a5f);
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  margin-right: 12rpx;
  font-weight: 600;
  letter-spacing: 1rpx;
}
.footer-info {
  text-align: center;
  margin-top: 60rpx;
  text {
    display: block;
    color: #bbb;
    font-size: 22rpx;
    line-height: 1.8;
  }
}
/* 浏览历史相关 */
.history-count {
  background: #1aad19;
  color: #fff;
  font-size: 22rpx;
  min-width: 36rpx;
  height: 36rpx;
  padding: 0 10rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12rpx;
}
.history-section {
  margin: 20rpx 24rpx;
  padding: 30rpx;
  background: #fff;
  border-radius: 20rpx;
  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    .history-title {
      font-size: 30rpx;
      font-weight: bold;
      color: #222;
    }
    .history-clear {
      font-size: 24rpx;
      color: #ff5a5f;
    }
  }
  .history-list {
    .history-item {
      display: flex;
      align-items: center;
      padding: 20rpx 0;
      border-top: 1rpx solid #f5f5f5;
      &:first-child {
        border-top: none;
      }
      .history-img {
        width: 140rpx;
        height: 100rpx;
        border-radius: 12rpx;
        flex-shrink: 0;
        background: #eee;
      }
      .history-info {
        flex: 1;
        margin-left: 20rpx;
        min-width: 0;
        .history-name {
          font-size: 28rpx;
          font-weight: 600;
          color: #222;
          display: block;
        }
        .history-meta {
          display: flex;
          align-items: center;
          margin-top: 8rpx;
          .history-cat {
            font-size: 20rpx;
            color: #1aad19;
            background: #f0faf0;
            padding: 2rpx 12rpx;
            border-radius: 8rpx;
            margin-right: 12rpx;
          }
          .history-loc {
            font-size: 22rpx;
            color: #999;
          }
        }
        .history-time {
          display: block;
          font-size: 22rpx;
          color: #bbb;
          margin-top: 6rpx;
        }
      }
    }
  }
  .history-empty {
    text-align: center;
    padding: 40rpx 0;
    color: #aaa;
    font-size: 26rpx;
    .empty-icon {
      display: block;
      font-size: 60rpx;
      margin-bottom: 16rpx;
    }
  }
}
/* 编辑弹窗 */
.edit-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  .edit-box {
    width: 600rpx;
    background: #fff;
    border-radius: 20rpx;
    padding: 40rpx;
    .edit-title {
      font-size: 34rpx;
      font-weight: bold;
      text-align: center;
      margin-bottom: 30rpx;
    }
    .edit-row {
      display: flex;
      align-items: center;
      margin-bottom: 24rpx;
      .label {
        width: 120rpx;
        font-size: 28rpx;
        color: #555;
      }
      .edit-input {
        flex: 1;
        height: 72rpx;
        padding: 0 20rpx;
        background: #f8f8f8;
        border-radius: 12rpx;
        font-size: 28rpx;
      }
    }
    .edit-actions {
      display: flex;
      margin-top: 30rpx;
      .cancel, .save {
        flex: 1;
        height: 80rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 40rpx;
        font-size: 30rpx;
      }
      .cancel {
        color: #888;
        background: #f5f5f5;
        margin-right: 20rpx;
      }
      .save {
        color: #fff;
        background: #1aad19;
      }
    }
  }
}
</style>
