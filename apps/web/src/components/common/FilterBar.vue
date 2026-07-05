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
import { DEMO_PERIOD } from '@/config'

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
    text: '演示经营月',
    value: () => [dayjs(DEMO_PERIOD.startDate).toDate(), dayjs(DEMO_PERIOD.endDate).toDate()]
  },
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
  dateRange.value = [DEMO_PERIOD.startDate, DEMO_PERIOD.endDate]
  filterForm.start_date = dateRange.value[0]
  filterForm.end_date = dateRange.value[1]

  emit('reset')
  emit('query', { ...filterForm })
}

/**
 * 初始化默认日期范围
 */
const initDefaultDateRange = () => {
  if (props.defaultDays !== 30) {
    const end = dayjs()
    const start = end.subtract(props.defaultDays, 'day')
    dateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
  } else {
    dateRange.value = [DEMO_PERIOD.startDate, DEMO_PERIOD.endDate]
  }
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
  margin-bottom: 12px;
  border: 1px solid #E5DED4;
  border-radius: 6px;
  background: rgba(255, 253, 249, 0.96);
  box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);

  :deep(.el-card__body) {
    padding: 14px;
  }

  .el-form {
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }

  :deep(.el-form-item) {
    margin: 0;
  }

  :deep(.el-input__wrapper) {
    min-height: 36px;
    border-radius: 6px;
    background: #FFFDF9;
    border: 1px solid #D7CEC2;
    box-shadow: none;
  }

  :deep(.el-button) {
    border-radius: 6px;
    font-weight: 800;
  }
}
</style>
