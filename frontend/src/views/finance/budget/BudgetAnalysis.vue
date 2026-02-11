<template>
  <div class="budget-analysis">
    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true">
        <el-form-item label="门店">
          <StoreSelect v-model="storeId" width="200px" @change="handleQuery" />
        </el-form-item>
        <el-form-item label="月份">
          <el-date-picker
            v-model="monthDate"
            type="month"
            placeholder="选择月份"
            format="YYYY年MM月"
            value-format="YYYY-MM-DD"
            :clearable="false"
            @change="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 概览卡片 -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="8">
        <el-card shadow="hover" class="summary-card budget">
          <div class="card-title">总预算</div>
          <div class="card-value">¥{{ formatAmount(summary.total_budget) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="summary-card actual">
          <div class="card-title">实际支出</div>
          <div class="card-value">¥{{ formatAmount(summary.total_actual) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="summary-card variance" :class="{ negative: summary.total_actual > summary.total_budget }">
          <div class="card-title">预算差异</div>
          <div class="card-value">
            {{ summary.total_actual > summary.total_budget ? '+' : '' }}¥{{ formatAmount(summary.total_actual - summary.total_budget) }}
            <el-tag :type="summary.total_actual > summary.total_budget ? 'danger' : 'success'" size="small" class="rate-tag">
               执行率 {{ summary.total_budget > 0 ? ((summary.total_actual / summary.total_budget) * 100).toFixed(1) : 0 }}%
            </el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表与明细 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 柱状图 -->
      <el-col :span="24" style="margin-bottom: 20px">
         <el-card shadow="never">
           <template #header>
             <span>预算执行对比</span>
           </template>
           <div ref="chartRef" style="width: 100%; height: 350px;"></div>
         </el-card>
      </el-col>
      
      <!-- 明细表格 -->
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>
            <span>科目明细</span>
          </template>
          <el-table v-loading="loading" :data="tableData" border style="width: 100%">
            <el-table-column prop="expense_type_name" label="费用科目" />
            <el-table-column prop="budget_amount" label="预算金额" sortable>
              <template #default="{ row }">¥{{ formatAmount(row.budget_amount) }}</template>
            </el-table-column>
            <el-table-column prop="actual_amount" label="实际支出" sortable>
              <template #default="{ row }">¥{{ formatAmount(row.actual_amount) }}</template>
            </el-table-column>
            <el-table-column label="差异额" sortable :sort-method="(a, b) => a.variance - b.variance">
              <template #default="{ row }">
                <span :class="row.variance > 0 ? 'text-danger' : 'text-success'">
                  {{ row.variance > 0 ? '+' : '' }}{{ formatAmount(row.variance) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="执行率/进度" width="200">
               <template #default="{ row }">
                 <el-progress 
                   :percentage="Math.min(calcRate(row), 100)" 
                   :status="row.is_over_budget ? 'exception' : 'success'"
                   :format="() => calcRate(row).toFixed(1) + '%'"
                 />
               </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.is_over_budget" type="danger">超支</el-tag>
                <el-tag v-else type="success">正常</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import StoreSelect from '@/components/StoreSelect.vue'
import { getBudgetAnalysis } from '@/api/budget'
import { useECharts } from '@/composables/useECharts'
import type { BudgetAnalysisItem } from '@/types/modules/budget'

const storeId = ref<number>()
const monthDate = ref(dayjs().format('YYYY-MM-01'))
const loading = ref(false)

const summary = reactive({
  total_budget: 0,
  total_actual: 0,
  total_variance: 0
})

const tableData = ref<BudgetAnalysisItem[]>([])

const chartRef = ref<HTMLElement | null>(null)
const { setOption } = useECharts(chartRef)

const year = computed(() => dayjs(monthDate.value).year())
const month = computed(() => dayjs(monthDate.value).month() + 1)

function formatAmount(val: number) {
  return val ? val.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) : '0.00'
}

function calcRate(row: BudgetAnalysisItem) {
  if (row.budget_amount === 0) return row.actual_amount > 0 ? 100 : 0
  return (row.actual_amount / row.budget_amount) * 100
}

async function handleQuery() {
  if (!storeId.value) return
  
  loading.value = true
  try {
    const res = await getBudgetAnalysis({
      store_id: storeId.value,
      year: year.value,
      month: month.value
    })
    
    if ((res.code === 0 || res.code === 200) && res.data) {
      summary.total_budget = res.data.total_budget
      summary.total_actual = res.data.total_actual
      summary.total_variance = res.data.total_variance
      
      tableData.value = res.data.items || []
      renderChart()
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}

function renderChart() {
  const names = tableData.value.map(item => item.expense_type_name)
  const budgets = tableData.value.map(item => item.budget_amount)
  const actuals = tableData.value.map(item => item.actual_amount)
  
  setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['预算', '实际']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { interval: 0, rotate: 30 }
    },
    yAxis: {
      type: 'value',
      name: '金额(元)'
    },
    series: [
      {
        name: '预算',
        type: 'bar',
        data: budgets,
        itemStyle: { color: '#409eff' }
      },
      {
        name: '实际',
        type: 'bar',
        data: actuals,
        itemStyle: { color: '#67c23a' } // 可以在这里针对超支变色, ECharts support callback in itemStyle.color
      }
    ]
  }, true)
}
</script>

<style scoped lang="scss">
.budget-analysis {
  padding: 20px;
}
.filter-card {
  margin-bottom: 20px;
}
.summary-card {
  text-align: center;
  margin-bottom: 20px;
  .card-title {
    color: #909399;
    font-size: 14px;
    margin-bottom: 10px;
  }
  .card-value {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
  }
  &.budget .card-value { color: #409eff; }
  &.actual .card-value { color: #67c23a; }
  &.variance.negative .card-value { color: #f56c6c; }
}
.text-danger { color: #f56c6c; font-weight: bold; }
.text-success { color: #67c23a; }
</style>
