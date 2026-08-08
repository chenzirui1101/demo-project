<template>
  <view class="register-page">
    <view class="logo-area">
      <text class="logo">📝</text>
      <text class="title">注册账号</text>
      <text class="subtitle">加入兴宁旅游，发现更多精彩</text>
    </view>

    <view class="form-card">
      <view class="form-item">
        <text class="form-icon">👤</text>
        <input class="form-input" v-model="form.username" placeholder="请输入用户名" />
      </view>
      <view class="form-item">
        <text class="form-icon">📛</text>
        <input class="form-input" v-model="form.nickname" placeholder="请输入昵称" />
      </view>
      <view class="form-item">
        <text class="form-icon">🔒</text>
        <input class="form-input" v-model="form.password" placeholder="请输入密码(至少6位)" password />
      </view>
      <view class="form-item">
        <text class="form-icon">🔒</text>
        <input class="form-input" v-model="form.confirmPassword" placeholder="请确认密码" password />
      </view>

      <view class="submit-btn" :class="{ disabled: loading }" @click="doRegister">
        <text>{{ loading ? '注册中...' : '注 册' }}</text>
      </view>

      <view class="form-footer">
        <text class="tip">已有账号？</text>
        <text class="link" @click="goLogin">去登录</text>
      </view>
    </view>
  </view>
</template>

<script>
import { register } from '@/utils/api'

export default {
  data() {
    return {
      form: { username: '', nickname: '', password: '', confirmPassword: '' },
      loading: false,
    }
  },
  methods: {
    async doRegister() {
      if (this.loading) return
      if (!this.form.username || !this.form.password) {
        uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
        return
      }
      if (this.form.password.length < 6) {
        uni.showToast({ title: '密码至少6位', icon: 'none' })
        return
      }
      if (this.form.password !== this.form.confirmPassword) {
        uni.showToast({ title: '两次密码不一致', icon: 'none' })
        return
      }
      this.loading = true
      try {
        const res = await register({
          username: this.form.username,
          password: this.form.password,
          nickname: this.form.nickname,
        })
        if (res.code === 0) {
          // 存储后端返回的真实 token
          if (res.data && res.data.token) {
            uni.setStorageSync('token', res.data.token)
          }
          uni.setStorageSync('userInfo', res.data)
          uni.showToast({ title: '注册成功', icon: 'success' })
          setTimeout(() => {
            // 有上一页则返回，否则跳转到"我的"tabBar页
            const pages = getCurrentPages()
            if (pages.length > 1) {
              uni.navigateBack()
            } else {
              uni.switchTab({ url: '/pages/user/user' })
            }
          }, 1000)
        } else {
          uni.showToast({ title: res.msg || '注册失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '注册失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    goLogin() {
      uni.navigateBack()
    },
  },
}
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #e8f7e8, #f5f6f8 300rpx);
}
.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 70rpx 0 50rpx;
  .logo {
    font-size: 90rpx;
  }
  .title {
    font-size: 40rpx;
    font-weight: bold;
    color: #1aad19;
    margin-top: 20rpx;
  }
  .subtitle {
    font-size: 24rpx;
    color: #888;
    margin-top: 10rpx;
  }
}
.form-card {
  margin: 0 40rpx;
  padding: 40rpx;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.06);
  .form-item {
    display: flex;
    align-items: center;
    height: 90rpx;
    border-bottom: 1rpx solid #f0f0f0;
    margin-bottom: 16rpx;
    .form-icon {
      font-size: 36rpx;
      margin-right: 20rpx;
    }
    .form-input {
      flex: 1;
      height: 90rpx;
      font-size: 30rpx;
    }
  }
  .submit-btn {
    margin-top: 36rpx;
    height: 90rpx;
    background: linear-gradient(135deg, #1aad19, #4ecdc4);
    border-radius: 45rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 32rpx;
    font-weight: 600;
    &.disabled {
      opacity: 0.6;
    }
  }
  .form-footer {
    text-align: center;
    margin-top: 30rpx;
    .tip {
      font-size: 26rpx;
      color: #999;
    }
    .link {
      font-size: 26rpx;
      color: #1aad19;
      margin-left: 8rpx;
    }
  }
}
</style>
