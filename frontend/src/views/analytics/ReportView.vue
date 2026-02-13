/**
 * 报表中心页面
 * 包含日报、月报、门店对比、费用结构四个Tab
 */
<template>
  <div class="report-container">
    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" :inline="true" label-width="80px">
        <el-form-item label="门店">
          <StoreSelect v-model="queryForm.store_id" width="200px" />
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
            @change="handleDateChange"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button
            v-permission="PERMISSIONS.REPORT_EXPORT"
            type="success"
            :icon="Download"
            :loading="exportLoading"
            @click="handleExport"
          >
            导出Excel
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Tab切换 -->
    <el-card class="content-card" shadow="never">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- Tab1: 日报 -->
        <el-tab-pane label="日报" name="daily">
          <el-row v-loading="dailyLoading" :gutter="20">
            <el-col :span="24">
              <div class="chart-title">营收与利润趋势</div>
              <LineChart
                v-if="dailyChartData.xAxisData.length > 0"
                :x-axis-data="dailyChartData.xAxisData"
                :series="dailyChartData.series"
                y-axis-name="金额（元）"
                height="350px"
              />
              <el-empty v-else description="暂无数据" />
            </el-col>
          </el-row>
          
          <div class="table-title">日汇总明细</div>
          <el-table :data="dailySummaryData" stripe border>
            <el-table-column prop="biz_date" label="日期" width="120" align="center" />
            <el-table-column prop="store_name" label="门店" min-width="120" />
            <el-table-column label="营收" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text success">¥{{ formatNumber(row.revenue) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="成本" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text warning">¥{{ formatNumber(row.cost_total) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="费用" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text danger">¥{{ formatNumber(row.expense_total) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="毛利" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text primary">¥{{ formatNumber(row.gross_profit) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="营业利润" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text" :class="(row.operating_profit ?? 0) >= 0 ? 'success' : 'danger'">
                  ￥{{ formatNumber(row.operating_profit) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="毛利率" width="100" align="center">
              <template #default="{ row }">
                {{ row.gross_profit_rate?.toFixed(2) ?? '0.00' }}%
              </template>
            </el-table-column>
            <el-table-column label="营业利润率" width="100" align="center">
              <template #default="{ row }">
                <span :class="(row.operating_profit_rate ?? 0) >= 0 ? 'text-success' : 'text-danger'">
                  {{ row.operating_profit_rate?.toFixed(2) ?? '0.00' }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="order_count" label="订单数" width="100" align="center" />
          </el-table>
        </el-tab-pane>

        <!-- Tab2: 月报 -->
        <el-tab-pane label="月报" name="monthly">
          <el-row v-loading="monthlyLoading" :gutter="20">
            <el-col :span="24">
              <div class="chart-title">月度营收对比</div>
              <BarChart
                v-if="monthlyChartData.xAxisData.length > 0"
                :x-axis-data="monthlyChartData.xAxisData"
                :series="monthlyChartData.series"
                y-axis-name="金额（元）"
                height="350px"
              />
              <el-empty v-else description="暂无数据" />
            </el-col>
          </el-row>

          <div class="table-title">月汇总明细</div>
          <el-table :data="monthlySummaryData" stripe border>
            <el-table-column label="年月" width="120" align="center">
              <template #default="{ row }">
                {{ row.year }}-{{ String(row.month).padStart(2, '0') }}
              </template>
            </el-table-column>
            <el-table-column prop="store_name" label="门店" min-width="120" />
            <el-table-column label="营收" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text success">¥{{ formatNumber(row.revenue) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="成本" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text warning">¥{{ formatNumber(row.cost_total) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="营业利润" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text" :class="(row.operating_profit ?? 0) >= 0 ? 'success' : 'danger'">
                  ¥{{ formatNumber(row.operating_profit) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="日均营收" width="130" align="right">
              <template #default="{ row }">
                ¥{{ formatNumber(row.avg_daily_revenue) }}
              </template>
            </el-table-column>
            <el-table-column label="日均订单" width="100" align="center">
              <template #default="{ row }">
                {{ row.avg_daily_order_count.toFixed(1) }}
              </template>
            </el-table-column>
            <el-table-column prop="order_count" label="总订单数" width="110" align="center" />
            <el-table-column prop="day_count" label="天数" width="80" align="center" />
          </el-table>
        </el-tab-pane>

        <!-- Tab3: 门店对比 -->
        <el-tab-pane label="门店对比" name="store">
          <el-row :gutter="20">
            <el-col :span="24">
              <div class="filter-row">
                <span class="filter-label">排行数量:</span>
                <el-select v-model="topN" size="small" style="width: 120px" @change="handleQuery">
                  <el-option label="Top 5" :value="5" />
                  <el-option label="Top 10" :value="10" />
                  <el-option label="Top 15" :value="15" />
                  <el-option label="全部" :value="999" />
                </el-select>
              </div>
            </el-col>
          </el-row>

          <el-row v-loading="storeLoading" :gutter="20">
            <el-col :span="24">
              <div class="chart-title">门店营收排行</div>
              <BarChart
                v-if="storeChartData.xAxisData.length > 0"
                :x-axis-data="storeChartData.xAxisData"
                :series="storeChartData.series"
                y-axis-name="金额（元）"
                :horizontal="true"
                height="400px"
              />
              <el-empty v-else description="暂无数据" />
            </el-col>
          </el-row>

          <div class="table-title">门店绩效明细</div>
          <el-table :data="storePerformanceData" stripe border>
            <el-table-column type="index" label="排名" width="80" align="center" />
            <el-table-column prop="store_name" label="门店名称" min-width="150" />
            <el-table-column label="营收" width="130" align="right" sortable>
              <template #default="{ row }">
                <span class="amount-text success">¥{{ formatNumber(row.revenue) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="营业利润" width="130" align="right" sortable>
              <template #default="{ row }">
                <span class="amount-text" :class="(row.operating_profit ?? 0) >= 0 ? 'success' : 'danger'">
                  ￥{{ formatNumber(row.operating_profit) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="order_count" label="订单数" width="100" align="center" sortable />
            <el-table-column label="平均订单金额" width="130" align="right" sortable>
              <template #default="{ row }">
                ¥{{ formatNumber(row.avg_order_amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="revenue_rank" label="营收排名" width="100" align="center" />
            <el-table-column prop="profit_rank" label="利润排名" width="100" align="center" />
          </el-table>
        </el-tab-pane>

        <!-- Tab4: 费用结构 -->
        <el-tab-pane label="费用结构" name="expense">
          <el-row :gutter="20">
            <el-col :span="24">
              <div class="filter-row">
                <span class="filter-label">显示数量:</span>
                <el-select v-model="expenseTopN" size="small" style="width: 120px" @change="handleQuery">
                  <el-option label="Top 5" :value="5" />
                  <el-option label="Top 10" :value="10" />
                  <el-option label="Top 15" :value="15" />
                  <el-option label="全部" :value="999" />
                </el-select>
              </div>
            </el-col>
          </el-row>

          <el-row v-loading="expenseLoading" :gutter="20">
            <el-col :span="24">
              <div class="chart-title">费用结构分析</div>
              <PieChart
                v-if="expenseChartData.length > 0"
                :data="expenseChartData"
                :is-donut="true"
                height="400px"
              />
              <el-empty v-else description="暂无数据" />
            </el-col>
          </el-row>

          <div class="table-title">费用明细</div>
          <el-table :data="expenseBreakdownData" stripe border>
            <el-table-column type="index" label="排名" width="80" align="center" />
            <el-table-column prop="type_code" label="科目代码" width="120" />
            <el-table-column prop="type_name" label="科目名称" min-width="150" />
            <el-table-column prop="category" label="类别" width="120" />
            <el-table-column label="总金额" width="150" align="right" sortable>
              <template #default="{ row }">
                <span class="amount-text danger">¥{{ formatNumber(row.total_amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="占比" width="100" align="center" sortable>
              <template #default="{ row }">
                <el-tag type="warning">{{ row.percentage.toFixed(2) }}%</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="record_count" label="记录数" width="100" align="center" sortable />
            <el-table-column label="平均金额" width="130" align="right">
              <template #default="{ row }">
                ¥{{ formatNumber(row.avg_amount) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import StoreSelect from '@/components/StoreSelect.vue'
import {
  getDailySummary,
  getMonthlySummary,
  getStorePerformance,
  getExpenseBreakdown,
  exportReport
} from '@/api/reports'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import type {
  ReportQuery,
  DailySummaryRow,
  MonthlySummaryRow,
  StorePerformanceRow,
  ExpenseBreakdownRow
} from '@/types'
import { PERMISSIONS } from '@/config'
import dayjs from 'dayjs'

// 筛选表单
const queryForm = reactive<ReportQuery>({
  start_date: '',
  end_date: '',
  store_id: undefined,
  top_n: undefined
})

// 日期范围
const dateRange = ref<[string, string]>([
  dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近7天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近30天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '本月',
    value: () => {
      const start = dayjs().startOf('month').toDate()
      const end = new Date()
      return [start, end]
    }
  },
  {
    text: '上月',
    value: () => {
      const start = dayjs().subtract(1, 'month').startOf('month').toDate()
      const end = dayjs().subtract(1, 'month').endOf('month').toDate()
      return [start, end]
    }
  }
]

// Tab状态
const activeTab = ref('daily')

// TOP N
const topN = ref(10)
const expenseTopN = ref(10)

// 加载状态
const dailyLoading = ref(false)
const monthlyLoading = ref(false)
const storeLoading = ref(false)
const expenseLoading = ref(false)
const exportLoading = ref(false)

// 数据
const dailySummaryData = ref<DailySummaryRow[]>([])
const monthlySummaryData = ref<MonthlySummaryRow[]>([])
const storePerformanceData = ref<StorePerformanceRow[]>([])
const expenseBreakdownData = ref<ExpenseBreakdownRow[]>([])

// 图表数据
const dailyChartData = computed(() => {
  if (dailySummaryData.value.length === 0) {
    return { xAxisData: [], series: [] }
  }

  return {
    xAxisData: dailySummaryData.value.map(item => item.biz_date),
    series: [
      {
        name: '营收',
        data: dailySummaryData.value.map(item => item.revenue),
        color: '#67c23a'
      },
      {
        name: '毛利',
        data: dailySummaryData.value.map(item => item.gross_profit),
        color: '#409eff'
      },
      {
        name: '营业利润',
        data: dailySummaryData.value.map(item => item.operating_profit),
        color: '#f56c6c'
      }
    ]
  }
})

const monthlyChartData = computed(() => {
  if (monthlySummaryData.value.length === 0) {
    return { xAxisData: [], series: [] }
  }

  return {
    xAxisData: monthlySummaryData.value.map(
      item => `${item.year}-${String(item.month).padStart(2, '0')}`
    ),
    series: [
      {
        name: '营收',
        data: monthlySummaryData.value.map(item => item.revenue),
        color: '#67c23a'
      },
      {
        name: '营业利润',
        data: monthlySummaryData.value.map(item => item.operating_profit),
        color: '#409eff'
      }
    ]
  }
})

const storeChartData = computed(() => {
  if (storePerformanceData.value.length === 0) {
    return { xAxisData: [], series: [] }
  }

  // 取前10个门店展示
  const top10 = storePerformanceData.value.slice(0, 10)

  return {
    xAxisData: top10.map(item => item.store_name),
    series: [
      {
        name: '营收',
        data: top10.map(item => item.revenue),
        color: '#67c23a'
      }
    ]
  }
})

const expenseChartData = computed(() => {
  return expenseBreakdownData.value.map(item => ({
    name: item.type_name,
    value: item.total_amount
  }))
})

// 格式化数字
const formatNumber = (value: number | null | undefined) => {
  if (value === null || value === undefined || isNaN(value)) {
    return '0.00'
  }
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

// 日期变化
const handleDateChange = (value: unknown) => {
  if (Array.isArray(value) && value.length === 2 && typeof value[0] === 'string' && typeof value[1] === 'string') {
    queryForm.start_date = value[0]
    queryForm.end_date = value[1]
  } else {
    queryForm.start_date = ''
    queryForm.end_date = ''
  }
}

// 查询
const handleQuery = async () => {
  if (!queryForm.start_date || !queryForm.end_date) {
    ElMessage.warning('请选择日期范围')
    return
  }

  switch (activeTab.value) {
    case 'daily':
      await loadDailySummary()
      break
    case 'monthly':
      await loadMonthlySummary()
      break
    case 'store':
      await loadStorePerformance()
      break
    case 'expense':
      await loadExpenseBreakdown()
      break
  }
}

// 重置
const handleReset = () => {
  queryForm.store_id = undefined
  dateRange.value = [
    dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
    dayjs().format('YYYY-MM-DD')
  ]
  queryForm.start_date = dateRange.value[0]
  queryForm.end_date = dateRange.value[1]
  handleQuery()
}

// Tab切换
const handleTabChange = (_tabName: string) => {
  handleQuery()
}

// 转换数字字段（处理后端Decimal序列化为字符串的情况）
const convertToNumber = (value: unknown): number => {
  if (value === null || value === undefined) return 0
  if (typeof value === 'number') return value
  if (typeof value === 'string') {
    const num = parseFloat(value)
    return isNaN(num) ? 0 : num
  }
  return 0
}

const convertToInt = (value: unknown): number => {
  if (typeof value === 'number') return Number.isFinite(value) ? Math.trunc(value) : 0
  if (typeof value === 'string') {
    const num = parseInt(value, 10)
    return Number.isFinite(num) ? num : 0
  }
  return 0
}

// 转换日汇总数据
const convertDailySummaryData = (data: Array<Record<string, unknown>>): DailySummaryRow[] => {
  return data.map((item) => ({
    ...(item as Record<string, unknown>),
    revenue: convertToNumber(item['revenue']),
    net_revenue: convertToNumber(item['net_revenue']),
    cost_total: convertToNumber(item['cost_total']),
    cost_material: convertToNumber(item['cost_material']),
    cost_labor: convertToNumber(item['cost_labor']),
    expense_total: convertToNumber(item['expense_total']),
    gross_profit: convertToNumber(item['gross_profit']),
    operating_profit: convertToNumber(item['operating_profit']),
    gross_profit_rate: item['gross_profit_rate'] !== null ? convertToNumber(item['gross_profit_rate']) : null,
    operating_profit_rate: item['operating_profit_rate'] !== null ? convertToNumber(item['operating_profit_rate']) : null,
    discount_amount: convertToNumber(item['discount_amount']),
    refund_amount: convertToNumber(item['refund_amount']),
    order_count: convertToInt(item['order_count'])
  })) as unknown as DailySummaryRow[]
}

// 加载日汇总
const loadDailySummary = async () => {
  dailyLoading.value = true
  try {
    const params: ReportQuery = {
      start_date: queryForm.start_date,
      end_date: queryForm.end_date,
      store_id: queryForm.store_id
    }
    const response = await getDailySummary(params)
    // 转换数据类型
    dailySummaryData.value = convertDailySummaryData((response.data || []) as unknown as Array<Record<string, unknown>>)
  } catch {
    ElMessage.error('加载日汇总失败，请稍后重试')
    dailySummaryData.value = []
  } finally {
    dailyLoading.value = false
  }
}

// 转换月汇总数据
const convertMonthlySummaryData = (data: Array<Record<string, unknown>>): MonthlySummaryRow[] => {
  return data.map((item) => ({
    ...(item as Record<string, unknown>),
    revenue: convertToNumber(item['revenue']),
    net_revenue: convertToNumber(item['net_revenue']),
    cost_total: convertToNumber(item['cost_total']),
    expense_total: convertToNumber(item['expense_total']),
    gross_profit: convertToNumber(item['gross_profit']),
    operating_profit: convertToNumber(item['operating_profit']),
    gross_profit_rate: item['gross_profit_rate'] !== null ? convertToNumber(item['gross_profit_rate']) : null,
    operating_profit_rate: item['operating_profit_rate'] !== null ? convertToNumber(item['operating_profit_rate']) : null,
    discount_amount: convertToNumber(item['discount_amount']),
    refund_amount: convertToNumber(item['refund_amount']),
    avg_daily_revenue: convertToNumber(item['avg_daily_revenue']),
    avg_daily_order_count: convertToNumber(item['avg_daily_order_count']),
    order_count: convertToInt(item['order_count']),
    day_count: convertToInt(item['day_count'])
  })) as unknown as MonthlySummaryRow[]
}

// 加载月汇总
const loadMonthlySummary = async () => {
  monthlyLoading.value = true
  try {
    const params: ReportQuery = {
      start_date: queryForm.start_date,
      end_date: queryForm.end_date,
      store_id: queryForm.store_id
    }
    const response = await getMonthlySummary(params)
    monthlySummaryData.value = convertMonthlySummaryData((response.data || []) as unknown as Array<Record<string, unknown>>)
  } catch {
    ElMessage.error('加载月汇总失败')
  } finally {
    monthlyLoading.value = false
  }
}

// 转换门店绩效数据
const convertStorePerformanceData = (data: Array<Record<string, unknown>>): StorePerformanceRow[] => {
  return data.map((item) => ({
    ...(item as Record<string, unknown>),
    revenue: convertToNumber(item['revenue']),
    net_revenue: convertToNumber(item['net_revenue']),
    gross_profit: convertToNumber(item['gross_profit']),
    operating_profit: convertToNumber(item['operating_profit']),
    gross_profit_rate: item['gross_profit_rate'] !== null ? convertToNumber(item['gross_profit_rate']) : null,
    operating_profit_rate: item['operating_profit_rate'] !== null ? convertToNumber(item['operating_profit_rate']) : null,
    avg_order_amount: convertToNumber(item['avg_order_amount']),
    order_count: convertToInt(item['order_count']),
    revenue_rank: convertToInt(item['revenue_rank']),
    profit_rank: convertToInt(item['profit_rank'])
  })) as unknown as StorePerformanceRow[]
}

// 加载门店绩效
const loadStorePerformance = async () => {
  storeLoading.value = true
  try {
    const params: ReportQuery = {
      start_date: queryForm.start_date,
      end_date: queryForm.end_date,
      store_id: queryForm.store_id,
      top_n: topN.value
    }
    const response = await getStorePerformance(params)
    storePerformanceData.value = convertStorePerformanceData((response.data || []) as unknown as Array<Record<string, unknown>>)
  } catch {
    ElMessage.error('加载门店绩效失败')
  } finally {
    storeLoading.value = false
  }
}

// 转换费用明细数据
const convertExpenseBreakdownData = (data: Array<Record<string, unknown>>): ExpenseBreakdownRow[] => {
  return data.map((item) => ({
    ...(item as Record<string, unknown>),
    total_amount: convertToNumber(item['total_amount']),
    avg_amount: convertToNumber(item['avg_amount']),
    percentage: convertToNumber(item['percentage']),
    record_count: convertToInt(item['record_count'])
  })) as unknown as ExpenseBreakdownRow[]
}

// 加载费用明细
const loadExpenseBreakdown = async () => {
  expenseLoading.value = true
  try {
    const params: ReportQuery = {
      start_date: queryForm.start_date,
      end_date: queryForm.end_date,
      store_id: queryForm.store_id,
      top_n: expenseTopN.value
    }
    const response = await getExpenseBreakdown(params)
    expenseBreakdownData.value = convertExpenseBreakdownData((response.data || []) as unknown as Array<Record<string, unknown>>)
  } catch {
    ElMessage.error('加载费用明细失败')
  } finally {
    expenseLoading.value = false
  }
}

// 导出Excel
const handleExport = async () => {
  if (!queryForm.start_date || !queryForm.end_date) {
    ElMessage.warning('请选择日期范围')
    return
  }

  exportLoading.value = true
  try {
    const params: ReportQuery = {
      start_date: queryForm.start_date,
      end_date: queryForm.end_date,
      store_id: queryForm.store_id
    }
    const blob = await exportReport(params)

    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `报表_${queryForm.start_date}_${queryForm.end_date}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '导出失败'
    ElMessage.error(message)
  } finally {
    exportLoading.value = false
  }
}

// 初始化
onMounted(() => {
  // 设置初始日期
  queryForm.start_date = dateRange.value[0]
  queryForm.end_date = dateRange.value[1]

  // 加载默认Tab数据
  loadDailySummary()
})
</script>

<style scoped lang="scss">
.report-container {
  padding: 20px;

  .filter-card {
    margin-bottom: 20px;
  }

  .content-card {
    :deep(.el-tabs__header) {
      margin-bottom: 20px;
    }
  }

  .filter-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;

    .filter-label {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
    }
  }

  .chart-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 4px solid #409eff;
  }

  .table-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin: 30px 0 15px;
    padding-left: 10px;
    border-left: 4px solid #67c23a;
  }

  .amount-text {
    font-weight: 600;

    &.success {
      color: #67c23a;
    }

    &.warning {
      color: #e6a23c;
    }

    &.danger {
      color: #f56c6c;
    }

    &.primary {
      color: #409eff;
    }
  }

  .text-success {
    color: #67c23a;
  }

  .text-danger {
    color: #f56c6c;
  }

  :deep(.el-table) {
    margin-top: 10px;

    .el-table__header th {
      background-color: #f5f7fa;
      color: #606266;
      font-weight: 600;
    }
  }
}
</style>
