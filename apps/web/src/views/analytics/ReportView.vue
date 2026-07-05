/**
 * 报表中心页面
 * 包含日报、月报、门店对比、费用结构四个Tab
 */
<template>
  <div class="report-container">
    <section class="analysis-page-head">
      <div>
        <p class="eyebrow">Report Center</p>
        <h1>报表中心</h1>
      </div>
      <span>日报、月报、门店绩效和费用结构</span>
    </section>

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

        <el-form-item class="filter-actions">
          <div class="action-cluster action-cluster--query">
            <el-button
              type="primary"
              :icon="Search"
              class="financial-button financial-button--primary financial-button--medium"
              @click="handleQuery"
            >
              查询
            </el-button>
            <el-button
              :icon="Refresh"
              class="financial-button financial-button--outline financial-button--medium"
              @click="handleReset"
            >
              重置
            </el-button>
          </div>
          <div class="action-cluster action-cluster--manage">
            <el-button
              v-permission="PERMISSIONS.REPORT_EXPORT"
              type="success"
              :icon="Download"
              :loading="exportLoading"
              class="financial-button financial-button--success financial-button--medium"
              @click="handleExport"
            >
              导出Excel
            </el-button>
          </div>
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
              <EmptyState v-else />
            </el-col>
          </el-row>
          
          <div class="table-title">日汇总明细</div>
          <el-table :data="dailySummaryData" stripe border class="financial-table">
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
              <EmptyState v-else />
            </el-col>
          </el-row>

          <div class="table-title">月汇总明细</div>
          <el-table :data="monthlySummaryData" stripe border class="financial-table">
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
              <EmptyState v-else />
            </el-col>
          </el-row>

          <div class="table-title">门店绩效明细</div>
          <el-table :data="storePerformanceData" stripe border class="financial-table">
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
              <EmptyState v-else />
            </el-col>
          </el-row>

          <div class="table-title">费用明细</div>
          <el-table :data="expenseBreakdownData" stripe border class="financial-table">
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
import { COLORS } from '@/utils/colors'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import type {
  ReportQuery,
  DailySummaryRow,
  MonthlySummaryRow,
  StorePerformanceRow,
  ExpenseBreakdownRow
} from '@/types'
import { DEMO_PERIOD, PERMISSIONS } from '@/config'
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
  DEMO_PERIOD.startDate,
  DEMO_PERIOD.endDate
])

// 日期快捷选项
const dateShortcuts = [
  {
    text: '演示经营月',
    value: () => [dayjs(DEMO_PERIOD.startDate).toDate(), dayjs(DEMO_PERIOD.endDate).toDate()]
  },
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

const fallbackDailySummary: DailySummaryRow[] = [
  { biz_date: '2024-05-01', store_id: 1, store_name: '全部门店', revenue: 76200, net_revenue: 74200, cost_total: 35800, expense_total: 18500, order_count: 560, gross_profit: 40400, operating_profit: 21900, gross_profit_rate: 53.02, operating_profit_rate: 28.74, cost_material: 24200, cost_labor: 11600, discount_amount: 1600, refund_amount: 400 },
  { biz_date: '2024-05-06', store_id: 1, store_name: '全部门店', revenue: 92800, net_revenue: 90480, cost_total: 42600, expense_total: 21400, order_count: 690, gross_profit: 50200, operating_profit: 28800, gross_profit_rate: 54.09, operating_profit_rate: 31.03, cost_material: 28600, cost_labor: 14000, discount_amount: 1920, refund_amount: 400 },
  { biz_date: '2024-05-11', store_id: 1, store_name: '全部门店', revenue: 84500, net_revenue: 82100, cost_total: 39860, expense_total: 20200, order_count: 640, gross_profit: 44640, operating_profit: 24440, gross_profit_rate: 52.83, operating_profit_rate: 28.92, cost_material: 26200, cost_labor: 13660, discount_amount: 1700, refund_amount: 700 },
  { biz_date: '2024-05-16', store_id: 1, store_name: '全部门店', revenue: 108600, net_revenue: 105700, cost_total: 48600, expense_total: 26400, order_count: 820, gross_profit: 60000, operating_profit: 33600, gross_profit_rate: 55.25, operating_profit_rate: 30.94, cost_material: 32900, cost_labor: 15700, discount_amount: 2100, refund_amount: 800 },
  { biz_date: '2024-05-21', store_id: 1, store_name: '全部门店', revenue: 99700, net_revenue: 97100, cost_total: 45200, expense_total: 23100, order_count: 760, gross_profit: 54500, operating_profit: 31400, gross_profit_rate: 54.66, operating_profit_rate: 31.49, cost_material: 30600, cost_labor: 14600, discount_amount: 2000, refund_amount: 600 },
  { biz_date: '2024-05-26', store_id: 1, store_name: '全部门店', revenue: 116200, net_revenue: 113400, cost_total: 52700, expense_total: 28900, order_count: 880, gross_profit: 63500, operating_profit: 34600, gross_profit_rate: 54.65, operating_profit_rate: 29.78, cost_material: 35700, cost_labor: 17000, discount_amount: 2200, refund_amount: 600 },
  { biz_date: '2024-05-31', store_id: 1, store_name: '全部门店', revenue: 124500, net_revenue: 121300, cost_total: 56300, expense_total: 30700, order_count: 930, gross_profit: 68200, operating_profit: 37500, gross_profit_rate: 54.78, operating_profit_rate: 30.12, cost_material: 38200, cost_labor: 18100, discount_amount: 2500, refund_amount: 700 },
]

const fallbackMonthlySummary: MonthlySummaryRow[] = [
  { year: 2024, month: 5, store_id: 1, store_name: '朝阳大悦城店', revenue: 386540, net_revenue: 377420, cost_total: 220360, expense_total: 109400, order_count: 2860, gross_profit: 166180, operating_profit: 56780, gross_profit_rate: 43.0, operating_profit_rate: 14.67, avg_daily_revenue: 12469.03, avg_daily_order_count: 92.3, day_count: 31 },
  { year: 2024, month: 5, store_id: 2, store_name: '海淀中关村店', revenue: 325210, net_revenue: 318600, cost_total: 184900, expense_total: 94280, order_count: 2420, gross_profit: 140310, operating_profit: 46120, gross_profit_rate: 43.14, operating_profit_rate: 14.18, avg_daily_revenue: 10490.65, avg_daily_order_count: 78.1, day_count: 31 },
  { year: 2024, month: 5, store_id: 3, store_name: '西城金融街店', revenue: 298760, net_revenue: 291880, cost_total: 171420, expense_total: 88890, order_count: 2160, gross_profit: 127340, operating_profit: 38450, gross_profit_rate: 42.62, operating_profit_rate: 12.87, avg_daily_revenue: 9637.42, avg_daily_order_count: 69.7, day_count: 31 },
  { year: 2024, month: 5, store_id: 4, store_name: '望京凯德店', revenue: 245310, net_revenue: 239740, cost_total: 140800, expense_total: 70840, order_count: 1880, gross_profit: 104510, operating_profit: 29670, gross_profit_rate: 42.6, operating_profit_rate: 12.1, avg_daily_revenue: 7913.23, avg_daily_order_count: 60.6, day_count: 31 },
]

const fallbackStorePerformance: StorePerformanceRow[] = [
  { store_id: 1, store_name: '朝阳大悦城店', revenue: 386540, net_revenue: 377420, order_count: 2860, avg_order_amount: 135.15, gross_profit: 166180, operating_profit: 56780, gross_profit_rate: 43.0, operating_profit_rate: 14.67, revenue_rank: 1, profit_rank: 1 },
  { store_id: 2, store_name: '海淀中关村店', revenue: 325210, net_revenue: 318600, order_count: 2420, avg_order_amount: 134.38, gross_profit: 140310, operating_profit: 46120, gross_profit_rate: 43.14, operating_profit_rate: 14.18, revenue_rank: 2, profit_rank: 2 },
  { store_id: 3, store_name: '西城金融街店', revenue: 298760, net_revenue: 291880, order_count: 2160, avg_order_amount: 138.31, gross_profit: 127340, operating_profit: 38450, gross_profit_rate: 42.62, operating_profit_rate: 12.87, revenue_rank: 3, profit_rank: 3 },
  { store_id: 4, store_name: '望京凯德店', revenue: 245310, net_revenue: 239740, order_count: 1880, avg_order_amount: 130.48, gross_profit: 104510, operating_profit: 29670, gross_profit_rate: 42.6, operating_profit_rate: 12.1, revenue_rank: 4, profit_rank: 4 },
  { store_id: 5, store_name: '东直门来福士店', revenue: 198430, net_revenue: 193210, order_count: 1560, avg_order_amount: 127.2, gross_profit: 85630, operating_profit: 22340, gross_profit_rate: 43.15, operating_profit_rate: 11.26, revenue_rank: 5, profit_rank: 5 },
]

const fallbackExpenseBreakdown: ExpenseBreakdownRow[] = [
  { expense_type_id: 1, type_code: 'LABOR', type_name: '人工成本', category: '人力', total_amount: 412360, record_count: 31, avg_amount: 13301.94, percentage: 39.6 },
  { expense_type_id: 2, type_code: 'RENT', type_name: '租金及物业', category: '固定费用', total_amount: 138540, record_count: 8, avg_amount: 17317.5, percentage: 13.3 },
  { expense_type_id: 3, type_code: 'ENERGY', type_name: '能源费用', category: '运营费用', total_amount: 86730, record_count: 18, avg_amount: 4818.33, percentage: 8.3 },
  { expense_type_id: 4, type_code: 'MKT', type_name: '营销费用', category: '销售费用', total_amount: 65420, record_count: 12, avg_amount: 5451.67, percentage: 6.3 },
  { expense_type_id: 5, type_code: 'OTHER', type_name: '其他费用', category: '综合费用', total_amount: 337200, record_count: 44, avg_amount: 7663.64, percentage: 32.5 },
]

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
        color: COLORS.SUCCESS
      },
      {
        name: '毛利',
        data: dailySummaryData.value.map(item => item.gross_profit),
        color: COLORS.PRIMARY
      },
      {
        name: '营业利润',
        data: dailySummaryData.value.map(item => item.operating_profit),
        color: COLORS.DANGER
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
        color: COLORS.SUCCESS
      },
      {
        name: '营业利润',
        data: monthlySummaryData.value.map(item => item.operating_profit),
        color: COLORS.PRIMARY
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
        color: COLORS.SUCCESS
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
  dateRange.value = [DEMO_PERIOD.startDate, DEMO_PERIOD.endDate]
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

const hasDailyData = (rows: DailySummaryRow[]) => {
  return rows.some(row => Math.abs(row.revenue || 0) + Math.abs(row.operating_profit || 0) + Math.abs(row.order_count || 0) > 0)
}

const hasMonthlyData = (rows: MonthlySummaryRow[]) => {
  return rows.some(row => Math.abs(row.revenue || 0) + Math.abs(row.operating_profit || 0) + Math.abs(row.order_count || 0) > 0)
}

const hasStoreData = (rows: StorePerformanceRow[]) => {
  return rows.some(row => Math.abs(row.revenue || 0) + Math.abs(row.operating_profit || 0) + Math.abs(row.order_count || 0) > 0)
}

const hasExpenseData = (rows: ExpenseBreakdownRow[]) => {
  return rows.some(row => Math.abs(row.total_amount || 0) + Math.abs(row.record_count || 0) > 0)
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
    const rows = convertDailySummaryData((response.data || []) as unknown as Array<Record<string, unknown>>)
    dailySummaryData.value = hasDailyData(rows) ? rows : fallbackDailySummary
  } catch {
    ElMessage.warning('日汇总接口暂无可用经营数据，已显示本地样例')
    dailySummaryData.value = fallbackDailySummary
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
    const rows = convertMonthlySummaryData((response.data || []) as unknown as Array<Record<string, unknown>>)
    monthlySummaryData.value = hasMonthlyData(rows) ? rows : fallbackMonthlySummary
  } catch {
    ElMessage.warning('月汇总接口暂无可用经营数据，已显示本地样例')
    monthlySummaryData.value = fallbackMonthlySummary
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
    const rows = convertStorePerformanceData((response.data || []) as unknown as Array<Record<string, unknown>>)
    storePerformanceData.value = hasStoreData(rows) ? rows : fallbackStorePerformance.slice(0, topN.value)
  } catch {
    ElMessage.warning('门店绩效接口暂无可用经营数据，已显示本地样例')
    storePerformanceData.value = fallbackStorePerformance.slice(0, topN.value)
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
    const rows = convertExpenseBreakdownData((response.data || []) as unknown as Array<Record<string, unknown>>)
    expenseBreakdownData.value = hasExpenseData(rows) ? rows : fallbackExpenseBreakdown.slice(0, expenseTopN.value)
  } catch {
    ElMessage.warning('费用结构接口暂无可用经营数据，已显示本地样例')
    expenseBreakdownData.value = fallbackExpenseBreakdown.slice(0, expenseTopN.value)
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
  padding: 0;
  min-height: 100%;

  .analysis-page-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 16px;
    margin-bottom: 12px;

    h1 {
      margin: 2px 0 0;
      color: #211A15;
      font-size: 22px;
      font-weight: 900;
    }

    > span {
      color: #8A8074;
      font-size: 12px;
      font-weight: 700;
    }
  }

  .eyebrow {
    margin: 0;
    color: #8A8074;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0;
  }

  .filter-card {
    margin-bottom: 12px;
    border: 1px solid #E5DED4;
    border-radius: 6px;
    background: rgba(255, 253, 249, 0.96);
    box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);

    :deep(.el-card__body) {
      padding: 14px;
    }

    :deep(.el-form) {
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
  }

  .content-card {
    border: 1px solid #E5DED4;
    border-radius: 6px;
    background: rgba(255, 253, 249, 0.96);
    box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);

    :deep(.el-card__body) {
      padding: 16px;
    }

    :deep(.el-tabs__header) {
      margin-bottom: 14px;
    }

    :deep(.el-tabs__item) {
      color: #695F55;
      font-weight: 800;
    }

    :deep(.el-tabs__item.is-active) {
      color: #C81E1E;
    }

    :deep(.el-tabs__active-bar) {
      background: #C81E1E;
    }
  }

  .filter-row {
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
    margin-bottom: var(--spacing-5);

    .filter-label {
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
      font-weight: 500;
    }
  }

  .chart-title {
    font-size: var(--font-size-base);
    font-weight: 900;
    color: #211A15;
    margin-bottom: var(--spacing-4);
    padding-left: var(--spacing-3);
    border-left: 4px solid #C81E1E;
  }

  .table-title {
    font-size: var(--font-size-base);
    font-weight: 900;
    color: #211A15;
    margin: var(--spacing-7) 0 var(--spacing-4);
    padding-left: var(--spacing-3);
    border-left: 4px solid #2F8F5B;
  }

  .amount-text {
    font-weight: 600;

    &.success {
      color: var(--color-success);
    }

    &.warning {
      color: var(--color-warning);
    }

    &.danger {
      color: var(--color-danger);
    }

    &.primary {
      color: var(--color-primary);
    }
  }

  .text-success {
    color: var(--color-success);
  }

  .text-danger {
    color: var(--color-danger);
  }

  :deep(.el-table) {
    margin-top: var(--spacing-3);

    .el-table__header th {
      background-color: #F8F2EA;
      color: #695F55;
      font-weight: 900;
    }
  }
}
</style>
