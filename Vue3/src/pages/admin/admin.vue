<template>
  <view class="admin-container">
    <!-- 顶部统计卡片 -->
    <view class="stats-header">
      <view class="stat-card" v-for="(item, idx) in statsCards" :key="idx">
        <view class="stat-value">{{ stats[item.key] || 0 }}</view>
        <view class="stat-label">{{ item.label }}</view>
      </view>
    </view>

    <!-- Tab 切换 -->
    <view class="tab-bar">
      <view
        class="tab-item"
        :class="{ active: currentTab === tab.key }"
        v-for="tab in tabs"
        :key="tab.key"
        @click="switchTab(tab.key)"
      >
        <uni-icons :type="tab.icon" size="20" :color="currentTab === tab.key ? '#1aad19' : '#666'"></uni-icons>
        <text>{{ tab.label }}</text>
      </view>
    </view>

    <!-- 景点管理 -->
    <view class="tab-content" v-if="currentTab === 'attractions'">
      <!-- 搜索和添加 -->
      <view class="toolbar">
        <view class="search-box">
          <input v-model="searchKeyword" placeholder="搜索景点名称" @confirm="loadAttractions" />
        </view>
        <view class="btn btn-primary" @click="openEditDialog(null)">
          <uni-icons type="plus" size="16" color="#fff"></uni-icons>
          <text>添加景点</text>
        </view>
      </view>

      <!-- 景点列表 -->
      <view class="list">
        <view class="list-item" v-for="item in attractions" :key="item.id">
          <image class="item-cover" :src="getImageUrl(item.cover)" mode="aspectFill" />
          <view class="item-info">
            <view class="item-name">{{ item.name }}</view>
            <view class="item-meta">
              <text class="tag">{{ item.category_name || '未分类' }}</text>
              <text class="view-count">👁 {{ item.view_count }}</text>
            </view>
            <view class="item-desc">{{ truncateText(item.description, 30) }}</view>
          </view>
          <view class="item-actions">
            <view class="action-btn edit" @click="openEditDialog(item)">
              <uni-icons type="compose" size="18" color="#1aad19"></uni-icons>
            </view>
            <view class="action-btn delete" @click="deleteAttraction(item.id)">
              <uni-icons type="trash" size="18" color="#e53935"></uni-icons>
            </view>
          </view>
        </view>
        <view class="empty" v-if="attractions.length === 0 && !loading">
          <text>暂无景点数据</text>
        </view>
      </view>
      <!-- 加载更多 -->
      <view class="load-more" v-if="attractions.length > 0">
        <text @click="loadMoreAttractions">加载更多</text>
      </view>
    </view>

    <!-- 分类管理 -->
    <view class="tab-content" v-if="currentTab === 'categories'">
      <view class="toolbar">
        <view class="btn btn-primary" @click="openCategoryDialog(null)">
          <uni-icons type="plus" size="16" color="#fff"></uni-icons>
          <text>添加分类</text>
        </view>
      </view>
      <view class="list">
        <view class="list-item category-item" v-for="item in categories" :key="item.id">
          <view class="item-info">
            <view class="item-name">{{ item.name }}</view>
            <view class="item-desc">{{ item.description || '无描述' }}</view>
          </view>
          <view class="item-actions">
            <view class="action-btn edit" @click="openCategoryDialog(item)">
              <uni-icons type="compose" size="18" color="#1aad19"></uni-icons>
            </view>
            <view class="action-btn delete" @click="deleteCategory(item.id)">
              <uni-icons type="trash" size="18" color="#e53935"></uni-icons>
            </view>
          </view>
        </view>
        <view class="empty" v-if="categories.length === 0">
          <text>暂无分类数据</text>
        </view>
      </view>
    </view>

    <!-- 轮播图管理 -->
    <view class="tab-content" v-if="currentTab === 'banners'">
      <view class="toolbar">
        <view class="btn btn-primary" @click="openBannerDialog(null)">
          <uni-icons type="plus" size="16" color="#fff"></uni-icons>
          <text>添加轮播图</text>
        </view>
      </view>

      <view class="list">
        <view class="list-item banner-item" v-for="item in banners" :key="item.id">
          <image class="banner-cover" :src="getImageUrl(item.image)" mode="aspectFill" />
          <view class="item-info">
            <view class="item-name">{{ item.title || '无标题' }}</view>
            <view class="item-meta">
              <text class="tag">{{ item.is_active ? '启用' : '禁用' }}</text>
              <text class="sort">排序: {{ item.sort }}</text>
            </view>
          </view>
          <view class="item-actions">
            <view class="action-btn edit" @click="openBannerDialog(item)">
              <uni-icons type="compose" size="18" color="#1aad19"></uni-icons>
            </view>
            <view class="action-btn delete" @click="deleteBanner(item.id)">
              <uni-icons type="trash" size="18" color="#e53935"></uni-icons>
            </view>
          </view>
        </view>
        <view class="empty" v-if="banners.length === 0">
          <text>暂无轮播图数据</text>
        </view>
      </view>
    </view>

    <!-- 景点编辑弹窗（页面内展开显示） -->
    <view class="dialog-mask" v-if="showEditDialog" @click="closeEditDialog">
      <view class="dialog" @click.stop>
        <view class="dialog-header">
          <text class="dialog-title">{{ editingItem ? '编辑景点' : '添加景点' }}</text>
          <view class="close-btn" @click="closeEditDialog">
            <uni-icons type="closeempty" size="20" color="#999"></uni-icons>
          </view>
        </view>
        <scroll-view class="dialog-body" scroll-y>
          <view class="form-group">
            <text class="form-label">景点名称</text>
            <input class="form-input" v-model="formData.name" placeholder="请输入景点名称" />
          </view>
          <view class="form-group">
            <text class="form-label">所属分类</text>
            <view class="custom-select" @click.stop="showCategoryDropdown = !showCategoryDropdown">
              <view class="form-picker">
                <text :class="{ placeholder: !formData.category_name }">{{ formData.category_name || '请选择分类' }}</text>
                <uni-icons :type="showCategoryDropdown ? 'top' : 'bottom'" size="16" color="#999"></uni-icons>
              </view>
              <view class="dropdown-list" v-if="showCategoryDropdown">
                <view
                  class="dropdown-item"
                  :class="{ active: formData.category === cat.id }"
                  v-for="cat in categories"
                  :key="cat.id"
                  @click.stop="selectCategory(cat)"
                >
                  <text>{{ cat.name }}</text>
                  <uni-icons v-if="formData.category === cat.id" type="checkmarkempty" size="16" color="#1aad19"></uni-icons>
                </view>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">封面图片</text>
            <view class="image-upload">
              <image v-if="formData.cover" class="preview" :src="getImageUrl(formData.cover)" mode="aspectFill" @click="previewImage(formData.cover)" />
              <view class="upload-btn" @click="chooseImage" v-else>
                <uni-icons type="camera" size="32" color="#999"></uni-icons>
                <text>上传图片</text>
              </view>
              <view class="replace-btn" @click="chooseImage" v-if="formData.cover">
                <uni-icons type="camera" size="16" color="#1aad19"></uni-icons>
                <text>更换</text>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">描述</text>
            <textarea class="form-textarea" v-model="formData.description" placeholder="请输入景点描述" />
          </view>
          <view class="form-row">
            <view class="form-group half">
              <text class="form-label">门票价格</text>
              <input class="form-input" v-model="formData.price" type="digit" placeholder="0.00" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">地址</text>
            <input class="form-input" v-model="formData.address" placeholder="请输入地址" />
          </view>
          <view class="form-group">
            <text class="form-label">开放时间</text>
            <input class="form-input" v-model="formData.opening_hours" placeholder="例如: 08:00-18:00" />
          </view>
          <view class="form-row">
            <view class="form-group half">
              <view class="checkbox-row" @click="toggleHot">
                <view class="checkbox" :class="{ checked: formData.is_hot }"></view>
                <text>热门景点</text>
              </view>
            </view>
            <view class="form-group half">
              <view class="checkbox-row" @click="toggleRecommended">
                <view class="checkbox" :class="{ checked: formData.is_recommended }"></view>
                <text>推荐景点</text>
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="dialog-footer">
          <view class="btn btn-cancel" @click="closeEditDialog">取消</view>
          <view class="btn btn-primary" :class="{ disabled: saving }" @click="saveAttraction">{{ saving ? '保存中...' : '保存' }}</view>
        </view>
      </view>
    </view>

    <!-- 分类编辑弹窗 -->
    <view class="dialog-mask" v-if="showCategoryDialog" @click="closeCategoryDialog">
      <view class="dialog" @click.stop>
        <view class="dialog-header">
          <text class="dialog-title">{{ editingCategory ? '编辑分类' : '添加分类' }}</text>
          <view class="close-btn" @click="closeCategoryDialog">
            <uni-icons type="closeempty" size="20" color="#999"></uni-icons>
          </view>
        </view>
        <scroll-view class="dialog-body" scroll-y>
          <view class="form-group">
            <text class="form-label">分类名称</text>
            <input class="form-input" v-model="categoryForm.name" placeholder="请输入分类名称" />
          </view>
          <view class="form-group">
            <text class="form-label">分类描述</text>
            <textarea class="form-textarea" v-model="categoryForm.description" placeholder="请输入分类描述" />
          </view>
          <view class="form-group">
            <text class="form-label">分类图标</text>
            <input class="form-input" v-model="categoryForm.icon" placeholder="请输入图标名称" />
          </view>
          <view class="form-group">
            <text class="form-label">排序</text>
            <input class="form-input" v-model="categoryForm.sort" type="number" placeholder="0" />
          </view>
        </scroll-view>
        <view class="dialog-footer">
          <view class="btn btn-cancel" @click="closeCategoryDialog">取消</view>
          <view class="btn btn-primary" @click="saveCategory">保存</view>
        </view>
      </view>
    </view>

    <!-- 轮播图编辑弹窗 -->
    <view class="dialog-mask" v-if="showBannerDialog" @click="closeBannerDialog">
      <view class="dialog" @click.stop>
        <view class="dialog-header">
          <text class="dialog-title">{{ editingBanner ? '编辑轮播图' : '添加轮播图' }}</text>
          <view class="close-btn" @click="closeBannerDialog">
            <uni-icons type="closeempty" size="20" color="#999"></uni-icons>
          </view>
        </view>
        <scroll-view class="dialog-body" scroll-y>
          <view class="form-group">
            <text class="form-label">轮播图片</text>
            <view class="image-upload">
              <image v-if="bannerForm.image" class="preview" :src="getImageUrl(bannerForm.image)" mode="aspectFill" />
              <view class="upload-btn" @click="chooseBannerImage" v-else>
                <uni-icons type="camera" size="32" color="#999"></uni-icons>
                <text>上传图片</text>
              </view>
              <view class="replace-btn" @click="chooseBannerImage" v-if="bannerForm.image">
                <uni-icons type="camera" size="16" color="#1aad19"></uni-icons>
                <text>更换</text>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">标题</text>
            <input class="form-input" v-model="bannerForm.title" placeholder="请输入标题" />
          </view>
          <view class="form-group">
            <text class="form-label">关联景点</text>
            <view class="custom-select" @click.stop="showAttractionDropdown = !showAttractionDropdown">
              <view class="form-picker">
                <text :class="{ placeholder: !bannerForm.attraction_name }">{{ bannerForm.attraction_name || '请选择关联景点' }}</text>
                <uni-icons :type="showAttractionDropdown ? 'top' : 'bottom'" size="16" color="#999"></uni-icons>
              </view>
              <view class="dropdown-list" v-if="showAttractionDropdown">
                <view
                  class="dropdown-item"
                  :class="{ active: bannerForm.attraction === attr.id }"
                  v-for="attr in attractions"
                  :key="attr.id"
                  @click.stop="selectBannerAttraction(attr)"
                >
                  <text>{{ attr.name }}</text>
                  <uni-icons v-if="bannerForm.attraction === attr.id" type="checkmarkempty" size="16" color="#1aad19"></uni-icons>
                </view>
              </view>
            </view>
          </view>
          <view class="form-row">
            <view class="form-group half">
              <text class="form-label">排序</text>
              <input class="form-input" v-model="bannerForm.sort" type="number" placeholder="0" />
            </view>
            <view class="form-group half">
              <view class="checkbox-row" @click="toggleBannerActive">
                <view class="checkbox" :class="{ checked: bannerForm.is_active }"></view>
                <text>启用</text>
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="dialog-footer">
          <view class="btn btn-cancel" @click="closeBannerDialog">取消</view>
          <view class="btn btn-primary" @click="saveBanner">保存</view>
        </view>
      </view>
    </view>

  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getAdminStats, getAttractions, createAttraction, updateAttraction, deleteAttraction as deleteAttractionApi,
  getCategories, createCategory, updateCategory, deleteCategory as deleteCategoryApi,
  getBanners, createBanner, updateBanner, deleteBanner as deleteBannerApi,
} from '@/utils/api'
import { getImageUrl, FULL_BASE } from '@/utils/image'

// ============ 统计数据 ============
const stats = reactive({
  attractions: 0,
  categories: 0,
  banners: 0,
  users: 0,
  favorites: 0,
  reviews: 0,
})

const statsCards = [
  { key: 'attractions', label: '景点', color: '#1aad19' },
  { key: 'categories', label: '分类', color: '#ff9500' },
  { key: 'banners', label: '轮播图', color: '#007aff' },
  { key: 'users', label: '用户', color: '#5856d6' },
  { key: 'favorites', label: '收藏', color: '#e53935' },
  { key: 'reviews', label: '评论', color: '#00bcd4' },
]

// ============ Tab 切换 ============
const tabs = [
  { key: 'attractions', label: '景点', icon: 'location' },
  { key: 'categories', label: '分类', icon: 'grid' },
  { key: 'banners', label: '轮播图', icon: 'image' },
]

const currentTab = ref('attractions')
const switchTab = (tab) => {
  currentTab.value = tab
  if (tab === 'attractions') loadAttractions()
  if (tab === 'categories') loadCategories()
  if (tab === 'banners') loadBanners()
}

// ============ 图片 URL 处理已迁移至 @/utils/image ============

// ============ 景点管理 ============
const attractions = ref([])
const attractionsTotal = ref(0)
const attractionsPage = ref(1)
const loading = ref(false)
const searchKeyword = ref('')
const editingItem = ref(null)
const showEditDialog = ref(false)
const categoryIndex = ref(-1)
const showCategoryDropdown = ref(false)
const saving = ref(false)

const formData = reactive({
  name: '',
  category: null,
  category_name: '',
  cover: '',
  description: '',
  price: '',
  address: '',
  opening_hours: '',
  is_hot: false,
  is_recommended: false,
})

const loadStats = async () => {
  try {
    const res = await getAdminStats()
    if (res.code === 0) {
      Object.assign(stats, res.data)
    }
  } catch (e) { console.error(e) }
}

const loadAttractions = async (reset = false) => {
  if (reset) {
    attractionsPage.value = 1
    attractions.value = []
    attractionsTotal.value = 0
  }
  loading.value = true
  try {
    const params = { page: attractionsPage.value, page_size: 20 }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    const res = await getAttractions(params)
    if (res.code === 0) {
      const data = res.data
      attractions.value = data.results || []
      attractionsTotal.value = data.count || 0
    }
  } catch (e) { console.error(e) }
  loading.value = false
}

const loadMoreAttractions = () => {
  const totalPages = Math.ceil(attractionsTotal.value / 20)
  if (attractionsPage.value < totalPages) {
    attractionsPage.value++
    loadAttractions()
  }
}

const openEditDialog = (item) => {
  editingItem.value = item
  if (item) {
    Object.assign(formData, {
      name: item.name || '',
      category: item.category || null,
      category_name: item.category_name || '',
      cover: item.cover || '',
      description: item.description || '',
      price: item.ticket_price || '',
      address: item.location || '',
      opening_hours: item.open_time || '',
      is_hot: item.is_hot || false,
      is_recommended: item.is_recommended || false,
    })
  } else {
    Object.assign(formData, {
      name: '',
      category: null,
      category_name: '',
      cover: '',
      description: '',
      price: '',
      address: '',
      opening_hours: '',
      is_hot: false,
      is_recommended: false,
    })
  }
  showEditDialog.value = true
}

const closeEditDialog = () => {
  showEditDialog.value = false
  editingItem.value = null
}

const categoryOptions = computed(() => categories.value.map(c => c.name))

const selectCategory = (cat) => {
  formData.category = cat.id
  formData.category_name = cat.name
  showCategoryDropdown.value = false
}

const toggleHot = () => { formData.is_hot = !formData.is_hot }
const toggleRecommended = () => { formData.is_recommended = !formData.is_recommended }

const chooseImage = () => {
  uni.chooseImage({
    count: 1,
    success: async (res) => {
      const tempPath = res.tempFilePaths[0]
      uni.showLoading({ title: '上传中...' })
      try {
        const uploadRes = await uploadImageFromPath(tempPath, 'attractions')
        if (uploadRes.code === 0) {
          formData.cover = uploadRes.data.url
        }
      } catch (e) { console.error(e) }
      uni.hideLoading()
    },
  })
}

const uploadImageFromPath = (filePath, subdir) => {
  return new Promise((resolve, reject) => {
    const uploadUrl = FULL_BASE + '/api/admin/upload/'
    const token = uni.getStorageSync('token') || ''
    uni.uploadFile({
      url: uploadUrl,
      filePath,
      name: 'file',
      formData: { subdir },
      header: token ? { 'Authorization': 'Token ' + token } : {},
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          resolve(data)
        } catch (e) {
          reject(e)
        }
      },
      fail: reject,
    })
  })
}

const previewImage = (url) => {
  uni.previewImage({ urls: [getImageUrl(url)] })
}

const saveAttraction = async () => {
  if (saving.value) return
  if (!formData.name) {
    uni.showToast({ title: '请输入景点名称', icon: 'none' })
    return
  }
  if (!formData.category) {
    uni.showToast({ title: '请选择分类', icon: 'none' })
    return
  }
  saving.value = true
  const payload = {
    name: formData.name,
    category: formData.category,
    cover: formData.cover || '',
    description: formData.description || '',
    ticket_price: formData.price ? parseFloat(formData.price) : 0,
    location: formData.address || '',
    open_time: formData.opening_hours || '',
    is_hot: formData.is_hot,
    is_recommended: formData.is_recommended,
  }
  try {
    let res
    if (editingItem.value) {
      res = await updateAttraction(editingItem.value.id, payload)
    } else {
      res = await createAttraction(payload)
    }
    if (res.code === 0) {
      uni.showToast({ title: '保存成功', icon: 'success' })
      closeEditDialog()
      loadAttractions(true)
      loadStats()
    } else {
      uni.showToast({ title: res.msg || '保存失败', icon: 'none' })
    }
  } catch (e) {
    console.error(e)
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}

const deleteAttraction = (id) => {
  uni.showModal({
    title: '确认删除',
    content: '删除后无法恢复，是否继续？',
    success: async (res) => {
      if (res.confirm) {
        try {
          const result = await deleteAttractionApi(id)
          if (result.code === 0) {
            uni.showToast({ title: '删除成功', icon: 'success' })
            loadAttractions(true)
            loadStats()
          }
        } catch (e) { console.error(e) }
      }
    },
  })
}

const truncateText = (text, maxLen) => {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

// ============ 分类管理 ============
const categories = ref([])
const editingCategory = ref(null)
const showCategoryDialog = ref(false)

const categoryForm = reactive({
  name: '',
  description: '',
  icon: '',
  sort: '0',
})

const loadCategories = async () => {
  try {
    const res = await getCategories()
    if (res.code === 0) {
      categories.value = res.data || []
    }
  } catch (e) { console.error(e) }
}

const openCategoryDialog = (item) => {
  editingCategory.value = item
  if (item) {
    Object.assign(categoryForm, {
      name: item.name || '',
      description: item.description || '',
      icon: item.icon || '',
      sort: item.sort ? String(item.sort) : '0',
    })
  } else {
    Object.assign(categoryForm, { name: '', description: '', icon: '', sort: '0' })
  }
  showCategoryDialog.value = true
}

const closeCategoryDialog = () => {
  showCategoryDialog.value = false
  editingCategory.value = null
}

const saveCategory = async () => {
  if (!categoryForm.name) {
    uni.showToast({ title: '请输入分类名称', icon: 'none' })
    return
  }
  const payload = {
    name: categoryForm.name,
    description: categoryForm.description,
    icon: categoryForm.icon,
    sort: parseInt(categoryForm.sort) || 0,
  }
  try {
    let res
    if (editingCategory.value) {
      res = await updateCategory(editingCategory.value.id, payload)
    } else {
      res = await createCategory(payload)
    }
    if (res.code === 0) {
      uni.showToast({ title: '保存成功', icon: 'success' })
      closeCategoryDialog()
      loadCategories()
      loadStats()
    } else {
      uni.showToast({ title: res.msg || '保存失败', icon: 'none' })
    }
  } catch (e) { console.error(e) }
}

const deleteCategory = (id) => {
  uni.showModal({
    title: '确认删除',
    content: '删除后无法恢复，是否继续？',
    success: async (res) => {
      if (res.confirm) {
        try {
          const result = await deleteCategoryApi(id)
          if (result.code === 0) {
            uni.showToast({ title: '删除成功', icon: 'success' })
            loadCategories()
            loadStats()
          }
        } catch (e) { console.error(e) }
      }
    },
  })
}

// ============ 轮播图管理 ============
const banners = ref([])
const editingBanner = ref(null)
const showBannerDialog = ref(false)
const bannerAttractionIndex = ref(-1)
const showAttractionDropdown = ref(false)

const bannerForm = reactive({
  image: '',
  title: '',
  attraction: null,
  attraction_name: '',
  sort: '0',
  is_active: true,
})

const loadBanners = async () => {
  try {
    const res = await getBanners()
    if (res.code === 0) {
      banners.value = res.data || []
    }
  } catch (e) { console.error(e) }
}

const openBannerDialog = (item) => {
  editingBanner.value = item
  if (item) {
    Object.assign(bannerForm, {
      image: item.image || '',
      title: item.title || '',
      attraction: item.attraction || null,
      attraction_name: item.attraction?.name || '',
      sort: item.sort ? String(item.sort) : '0',
      is_active: item.is_active !== false,
    })
    bannerAttractionIndex.value = attractions.value.findIndex(a => a.id === item.attraction)
  } else {
    Object.assign(bannerForm, { image: '', title: '', attraction: null, attraction_name: '', sort: '0', is_active: true })
    bannerAttractionIndex.value = -1
  }
  showBannerDialog.value = true
}

const closeBannerDialog = () => {
  showBannerDialog.value = false
  editingBanner.value = null
}

const attractionOptions = computed(() => attractions.value.map(a => a.name))

const selectBannerAttraction = (attr) => {
  bannerForm.attraction = attr.id
  bannerForm.attraction_name = attr.name
  showAttractionDropdown.value = false
}

const chooseBannerImage = () => {
  uni.chooseImage({
    count: 1,
    success: async (res) => {
      const tempPath = res.tempFilePaths[0]
      uni.showLoading({ title: '上传中...' })
      try {
        const uploadRes = await uploadImageFromPath(tempPath, 'banners')
        if (uploadRes.code === 0) {
          bannerForm.image = uploadRes.data.url
        }
      } catch (e) { console.error(e) }
      uni.hideLoading()
    },
  })
}

const toggleBannerActive = () => { bannerForm.is_active = !bannerForm.is_active }

const saveBanner = async () => {
  if (!bannerForm.image) {
    uni.showToast({ title: '请上传轮播图片', icon: 'none' })
    return
  }
  const payload = {
    image: bannerForm.image,
    title: bannerForm.title,
    attraction: bannerForm.attraction,
    sort: parseInt(bannerForm.sort) || 0,
    is_active: bannerForm.is_active,
  }
  try {
    let res
    if (editingBanner.value) {
      res = await updateBanner(editingBanner.value.id, payload)
    } else {
      res = await createBanner(payload)
    }
    if (res.code === 0) {
      uni.showToast({ title: '保存成功', icon: 'success' })
      closeBannerDialog()
      loadBanners()
      loadStats()
    } else {
      uni.showToast({ title: res.msg || '保存失败', icon: 'none' })
    }
  } catch (e) { console.error(e) }
}

const deleteBanner = (id) => {
  uni.showModal({
    title: '确认删除',
    content: '删除后无法恢复，是否继续？',
    success: async (res) => {
      if (res.confirm) {
        try {
          const result = await deleteBannerApi(id)
          if (result.code === 0) {
            uni.showToast({ title: '删除成功', icon: 'success' })
            loadBanners()
            loadStats()
          }
        } catch (e) { console.error(e) }
      }
    },
  })
}

// ============ 初始化 ============
onMounted(async () => {
  uni.showLoading({ title: '加载中...' })
  await Promise.all([loadStats(), loadCategories(), loadAttractions(true)])
  uni.hideLoading()
})
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: #f5f6f8;
  padding-bottom: 40rpx;
}

/* 统计卡片 */
.stats-header {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  padding: 24rpx;
  background: linear-gradient(135deg, #1aad19, #0d7a14);
}

.stat-card {
  flex: 1;
  min-width: 140rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
  padding: 24rpx 16rpx;
  text-align: center;
  backdrop-filter: blur(10px);
}

.stat-value {
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
  line-height: 1.2;
}

.stat-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8rpx;
}

/* Tab 栏 */
.tab-bar {
  display: flex;
  background: #fff;
  padding: 16rpx 24rpx;
  border-bottom: 1rpx solid #eee;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 16rpx 0;
  font-size: 28rpx;
  color: #666;
  border-bottom: 4rpx solid transparent;
  transition: all 0.3s;
}

.tab-item.active {
  color: #1aad19;
  border-bottom-color: #1aad19;
  font-weight: 600;
}

/* Tab 内容 */
.tab-content {
  padding: 24rpx;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.search-box {
  flex: 1;
  background: #fff;
  border-radius: 12rpx;
  padding: 16rpx 24rpx;
}

.search-box input {
  font-size: 28rpx;
}

/* 按钮 */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 16rpx 32rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  white-space: nowrap;
}

.btn-primary {
  background: #1aad19;
  color: #fff;
}

.btn-primary.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

/* 列表 */
.list {
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.list-item:last-child {
  border-bottom: none;
}

.item-cover {
  width: 160rpx;
  height: 120rpx;
  border-radius: 12rpx;
  flex-shrink: 0;
  background: #f5f5f5;
}

.item-info {
  flex: 1;
  margin-left: 24rpx;
  min-width: 0;
}

.item-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 8rpx;
  font-size: 24rpx;
  color: #999;
}

.tag {
  background: #e8f5e9;
  color: #1aad19;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
}

.view-count, .sort {
  font-size: 24rpx;
}

.item-desc {
  font-size: 26rpx;
  color: #999;
  line-height: 1.4;
}

.category-item .item-desc {
  margin-top: 8rpx;
}

/* 轮播图列表 */
.banner-cover {
  width: 200rpx;
  height: 120rpx;
  border-radius: 12rpx;
  flex-shrink: 0;
  background: #f5f5f5;
}

/* 操作按钮 */
.item-actions {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-left: 16rpx;
  flex-shrink: 0;
}

.action-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f8f8f8;
}

.action-btn:active {
  background: #eee;
}

/* 空状态 */
.empty {
  padding: 80rpx 0;
  text-align: center;
  color: #999;
  font-size: 28rpx;
}

/* 加载更多 */
.load-more {
  text-align: center;
  padding: 32rpx;
  color: #1aad19;
  font-size: 28rpx;
}

/* 弹窗遮罩 */
.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.dialog {
  width: 100%;
  max-height: 85vh;
  background: #fff;
  border-radius: 24rpx 24rpx 0 0;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.dialog-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
}

.close-btn {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-body {
  flex: 1;
  padding: 24rpx 32rpx;
  max-height: 65vh;
  overflow-y: auto;
  position: relative;
}

.dialog-footer {
  display: flex;
  gap: 24rpx;
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid #f0f0f0;
}

.dialog-footer .btn {
  flex: 1;
  padding: 24rpx;
  font-size: 32rpx;
}

/* 表单 */
.form-group {
  margin-bottom: 32rpx;
}

.form-group.half {
  flex: 1;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 16rpx;
}

.form-input {
  width: 100%;
  height: 80rpx;
  background: #f5f6f8;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 30rpx;
  box-sizing: border-box;
}

.form-textarea {
  width: 100%;
  height: 200rpx;
  background: #f5f6f8;
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  font-size: 30rpx;
  box-sizing: border-box;
}

.form-picker {
  height: 80rpx;
  background: #f5f6f8;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 30rpx;
  line-height: 80rpx;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.form-picker .placeholder {
  color: #999;
}

/* 自定义下拉选择 */
.custom-select {
  position: relative;
}

.dropdown-list {
  position: absolute;
  top: calc(100% + 8rpx);
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 12rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.12);
  z-index: 100;
  max-height: 400rpx;
  overflow-y: auto;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  font-size: 30rpx;
  color: #333;
  border-bottom: 1rpx solid #f5f5f5;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:active {
  background: #f5f6f8;
}

.dropdown-item.active {
  color: #1aad19;
  font-weight: 600;
}

.form-row {
  display: flex;
  gap: 24rpx;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-top: 16rpx;
  font-size: 28rpx;
  color: #333;
}

.checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid #ddd;
  border-radius: 8rpx;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox.checked {
  background: #1aad19;
  border-color: #1aad19;
}

.checkbox.checked::after {
  content: '✓';
  color: #fff;
  font-size: 24rpx;
}

/* 图片上传 */
.image-upload {
  position: relative;
}

.preview {
  width: 100%;
  height: 300rpx;
  border-radius: 12rpx;
  background: #f5f5f5;
}

.upload-btn {
  width: 240rpx;
  height: 240rpx;
  background: #f5f6f8;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  color: #999;
}

.upload-btn text {
  font-size: 26rpx;
}

.replace-btn {
  position: absolute;
  right: 16rpx;
  bottom: 16rpx;
  background: rgba(255, 255, 255, 0.9);
  padding: 8rpx 16rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #1aad19;
}
</style>
