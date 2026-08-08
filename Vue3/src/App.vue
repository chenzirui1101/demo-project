<script>
export default {
  onLaunch() {
    console.log('兴宁旅游APP启动')
  },
  onShow() {},
  onHide() {},
}
</script>

<style lang="scss">
/* 全局样式 */
page {
  background-color: #f5f6f8;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #333;
  font-size: 28rpx;
}
view, text, image, navigator {
  box-sizing: border-box;
}
/* 清除默认样式 */
button::after {
  border: none;
}
/* 通用容器 */
.container {
  padding: 24rpx;
}
/* 卡片 */
.card {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}
/* 文本省略 */
.ellipsis-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ellipsis-2 {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
/* 主色调 */
.primary-color {
  color: #1aad19;
}
</style>
