<template>
  <view class="custom-tabbar">
    <view class="tabbar-item" v-for="(item, index) in tabs" :key="index" @click="switchTab(item)">
      <uni-icons
        :type="active === index ? item.iconActive : item.icon"
        :size="24"
        :color="active === index ? '#1aad19' : '#999'"
        class="tabbar-icon"
      ></uni-icons>
      <text class="tabbar-text" :class="{ active: active === index }">{{ item.text }}</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CustomTabBar',
  data() {
    return {
      tabs: [
        { text: '首页', icon: 'home', iconActive: 'home-filled', path: '/pages/index/index' },
        { text: '发现', icon: 'search', iconActive: 'search-filled', path: '/pages/list/list' },
        { text: '收藏', icon: 'heart', iconActive: 'heart-filled', path: '/pages/favorites/favorites' },
        { text: '我的', icon: 'person', iconActive: 'person-filled', path: '/pages/user/user' },
      ],
    }
  },
  props: {
    active: {
      type: Number,
      default: 0,
    },
  },
  methods: {
    switchTab(item) {
      uni.switchTab({ url: item.path })
    },
  },
}
</script>

<style lang="scss" scoped>
.custom-tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 998;
  height: calc(110rpx + env(safe-area-inset-bottom));
  box-sizing: border-box;
  display: flex;
  align-items: center;
  background: #fff;
  border-top: 1rpx solid #eee;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);
  padding-bottom: env(safe-area-inset-bottom);
  .tabbar-item {
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6rpx;
    overflow: hidden;
    .tabbar-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }
    .tabbar-text {
      font-size: 20rpx;
      color: #999;
      line-height: 1;
      transition: all 0.2s ease;
      &.active {
        color: #1aad19;
        font-weight: 600;
      }
    }
    &:active .tabbar-icon {
      transform: scale(1.1);
    }
  }
}
</style>
