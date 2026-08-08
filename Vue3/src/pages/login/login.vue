<template>
  <view class="login-page">
    <view class="logo-area">
      <text class="logo">🏞️</text>
      <text class="title">兴宁旅游</text>
      <text class="subtitle">梅州市兴宁市景点推荐</text>
    </view>

    <view class="form-card">
      <view class="form-item">
        <text class="form-icon">👤</text>
        <input class="form-input" v-model="form.username" placeholder="请输入用户名" />
      </view>
      <view class="form-item">
        <text class="form-icon">🔒</text>
        <input class="form-input" v-model="form.password" placeholder="请输入密码" password />
      </view>

      <view class="submit-btn" :class="{ disabled: loading }" @click="doLogin">
        <text>{{ loading ? '登录中...' : '登 录' }}</text>
      </view>

      <view class="form-footer">
        <text class="tip">还没有账号？</text>
        <text class="link" @click="goRegister">立即注册</text>
      </view>

      <view class="test-tip">
        <text>测试账号：admin / admin123</text>
      </view>
    </view>
  </view>
</template>

<script>
import { login } from '@/utils/api'

export default {
  data() {
    return {
      form: { username: '', password: '' },
      loading: false,
    }
  },
  methods: {
    async doLogin() {
      if (this.loading) return
      if (!this.form.username || !this.form.password) {
        uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
        return
      }
      this.loading = true
      try {
        const res = await login(this.form)
        if (res.code === 0) {
          // 存储后端返回的真实 token
          if (res.data && res.data.token) {
            uni.setStorageSync('token', res.data.token)
          }
          uni.setStorageSync('userInfo', res.data)
          uni.showToast({ title: '登录成功', icon: 'success' })
          setTimeout(() => {
            const pages = getCurrentPages()
            if (pages.length > 1) {
              uni.navigateBack()
            } else {
              uni.switchTab({ url: '/pages/user/user' })
            }
          }, 1000)
        } else {
          uni.showToast({ title: res.msg || '登录失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '登录失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    goRegister() {
      uni.navigateTo({ url: '/pages/register/register' })
    },
  },
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #e8f7e8, #f5f6f8 300rpx);
}
.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0 60rpx;
  .logo {
    font-size: 100rpx;
  }
  .title {
    font-size: 44rpx;
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
  padding: 50rpx 40rpx;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.06);
  .form-item {
    display: flex;
    align-items: center;
    height: 90rpx;
    border-bottom: 1rpx solid #f0f0f0;
    margin-bottom: 20rpx;
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
    margin-top: 40rpx;
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
  .test-tip {
    text-align: center;
    margin-top: 24rpx;
    padding: 16rpx;
    background: #f8f8f8;
    border-radius: 12rpx;
    text {
      font-size: 22rpx;
      color: #aaa;
    }
  }
}
</style>
