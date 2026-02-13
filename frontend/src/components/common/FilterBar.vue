<template>
  <el-card class="filter-card" shadow="never">
    <el-form :model="filterForm" :inline="true" label-width="80px">
      <el-form-item label="门店">
        <StoreSelect v-model="filterForm.store_id" width="200px" />
      </el-form-item>

      <el-form-item label="日期范围">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          :shortcuts="dateShortcuts"
          style="width: 360px"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        <slot name="extra-buttons"></slot>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import StoreSelect from '@/components/StoreSelect.vue'
import dayjs from 'dayjs'

interface FilterForm {
  store_id?: number
  start_date?: string
  end_date?: string
}

interface Props {
  defaultDays?: number // 默认查询最近多少天
}

const props = withDefaults(defineProps<Props>(), {
  defaultDays: 30
})

const emit = defineEmits<{
  query: [filters: FilterForm]
  reset: []
}>()

// 筛选表单
const filterForm = reactive<FilterForm>({
  store_id: undefined,
  start_date: undefined,
  end_date: undefined
})

// 日期范围
const dateRange = ref<[string, string]>()

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  }
]

/**
 * 处理查询
 */
const handleQuery = () => {
  if (dateRange.value) {
    filterForm.start_date = dateRange.value[0]
    filterForm.end_date = dateRange.value[1]
  } else {
    filterForm.start_date = undefined
    filterForm.end_date = undefined
  }

  emit('query', { ...filterForm })
}

/**
 * 处理重置
 */
const handleReset = () => {
  filterForm.store_id = undefined
  filterForm.start_date = undefined
  filterForm.end_date = undefined
  
  // 重置为默认日期范围
  const end = dayjs()
  const start = end.subtract(props.defaultDays, 'day')
  dateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
  filterForm.start_date = dateRange.value[0]
  filterForm.end_date = dateRange.value[1]

  emit('reset')
  emit('query', { ...filterForm })
}

/**
 * 初始化默认日期范围
 */
const initDefaultDateRange = () => {
  const end = dayjs()
  const start = end.subtract(props.defaultDays, 'day')
  dateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
  filterForm.start_date = dateRange.value[0]
  filterForm.end_date = dateRange.value[1]
}

onMounted(() => {
  initDefaultDateRange()
  // 自动触发一次查询
  handleQuery()
})

// 暴露方法给父组件
defineExpose({
  handleQuery,
  handleReset,
  filterForm
})
</script>

<style scoped lang="scss">
.filter-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 20px;
  }

  .el-form {
    margin: 0;
  }
}
</style>
