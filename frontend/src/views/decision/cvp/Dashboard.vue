<template>
  <div class="cvp-dashboard">
    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true">
        <el-form-item label="门店">
          <StoreSelect v-model="storeId" width="200px" @change="handleQuery" />
        </el-form-item>
        <el-form-item label="时间段">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DD"
            @change="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 核心指标卡片 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <el-card shadow="hover" class="metric-card bep">
          <div class="card-icon"><el-icon><TrendCharts /></el-icon></div>
          <div class="card-content">
            <div class="card-label">盈亏平衡点 (BEP)</div>
            <div class="card-value">¥{{ formatAmount(cvpData.break_even_point) }}</div>
            <div class="card-extra">当前收入的 {{ cvpData.break_even_sales_ratio.toFixed(1) }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="metric-card safety">
          <div class="card-icon"><el-icon><CircleCheckFilled /></el-icon></div>
          <div class="card-content">
            <div class="card-label">安全边际率</div>
            <div class="card-value">{{ cvpData.safety_margin_rate.toFixed(2) }}%</div>
            <div class="card-extra">安全边际: ¥{{ formatAmount(cvpData.safety_margin) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="metric-card leverage">
          <div class="card-icon"><el-icon><Opportunity /></el-icon></div>
          <div class="card-content">
            <div class="card-label">经营杠杆系数</div>
            <div class="card-value">{{ cvpData.operating_leverage.toFixed(2) }}</div>
            <div class="card-extra">利润敏感性指标</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="metric-card profit">
          <div class="card-icon"><el-icon><Money /></el-icon></div>
          <div class="card-content">
            <div class="card-label">经营利润</div>
            <div class="card-value">¥{{ formatAmount(cvpData.operating_profit) }}</div>
            <div class="card-extra">边际贡献率: {{ cvpData.contribution_margin_rate.toFixed(1) }}%</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表与模拟器 -->
    <el-row :gutter="20">
      <!-- CVP 模型图 -->
      <el-col :span="16">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <span>本量利模型图（CVP）</span>
          </template>
          <div ref="cvpChartRef" style="width: 100%; height: 450px;"></div>
        </el-card>
      </el-col>

      <!-- 敏感性分析模拟器 -->
      <el-col :span="8">
        <el-card shadow="never" class="simulator-card">
          <template #header>
            <span>敏感性分析</span>
          </template>
          
          <div class="simulator-content">
            <el-alert type="info" :closable="false" style="margin-bottom: 15px;">
              模拟成本变化对盈亏平衡点的影响
            </el-alert>

            <el-form label-width="120px" label-position="top">
              <el-form-item label="固定成本变化 (%)">
                <el-slider v-model="simulation.fixed_cost_change_rate" :min="-50" :max="50" :step="5" show-input />
              </el-form-item>
              
              <el-form-item label="变动成本变化 (%)">
                <el-slider v-model="simulation.variable_cost_change_rate" :min="-50" :max="50" :step="5" show-input />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" style="width: 100%" :loading="simulating" @click="handleSimulate">
                  <el-icon><DataAnalysis /></el-icon> 计算模拟结果
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 模拟结果 -->
            <div v-if="simulationResult" class="simulation-result">
              <el-divider>模拟结果</el-divider>
              <div class="result-item">
                <span class="label">原盈亏平衡点：</span>
                <span class="value">¥{{ formatAmount(simulationResult.original_bep) }}</span>
              </div>
              <div class="result-item">
                <span class="label">新盈亏平衡点：</span>
                <span class="value highlight">¥{{ formatAmount(simulationResult.simulated_bep) }}</span>
              </div>
              <div class="result-item">
                <span class="label">变化额：</span>
                <span class="value" :class="simulationResult.bep_change > 0 ? 'danger' : 'success'">
                  {{ simulationResult.bep_change > 0 ? '+' : '' }}¥{{ formatAmount(Math.abs(simulationResult.bep_change)) }}
                </span>
              </div>
              <div class="result-item">
                <span class="label">变化率：</span>
                <span class="value" :class="simulationResult.bep_change_rate > 0 ? 'danger' : 'success'">
                  {{ simulationResult.bep_change_rate > 0 ? '+' : '' }}{{ simulationResult.bep_change_rate.toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 成本结构展示 -->
        <el-card shadow="never" style="margin-top: 20px;">
          <template #header>
            <span>成本结构</span>
          </template>
          <div class="cost-structure">
            <div class="cost-item">
              <span class="label">总收入</span>
              <span class="value revenue">¥{{ formatAmount(cvpData.total_revenue) }}</span>
            </div>
            <div class="cost-item">
              <span class="label">变动成本</span>
              <span class="value variable">¥{{ formatAmount(cvpData.variable_cost) }}</span>
            </div>
            <div class="cost-item">
              <span class="label">固定成本</span>
              <span class="value fixed">¥{{ formatAmount(cvpData.fixed_cost) }}</span>
            </div>
            <el-divider />
            <div class="cost-item">
              <span class="label">边际贡献</span>
              <span class="value contribution">¥{{ formatAmount(cvpData.contribution_margin) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Search, TrendCharts, CircleCheckFilled, Opportunity, Money, DataAnalysis } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import StoreSelect from '@/components/StoreSelect.vue'
import { useECharts } from '@/composables/useECharts'
import { getCVPAnalysis, simulateCVP } from '@/api/cvp'
import type { CVPAnalysisResult, CVPSimulationResult } from '@/types/modules/cvp'

const storeId = ref<number>()
const dateRange = ref<[string, string]>([
  dayjs().startOf('month').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])
const loading = ref(false)
const simulating = ref(false)

const cvpData = reactive<CVPAnalysisResult>({
  total_revenue: 0,
  variable_cost: 0,
  fixed_cost: 0,
  contribution_margin: 0,
  contribution_margin_rate: 0,
  break_even_point: 0,
  break_even_sales_ratio: 0,
  safety_margin: 0,
  safety_margin_rate: 0,
  operating_leverage: 0,
  operating_profit: 0
})

const simulation = reactive({
  fixed_cost_change_rate: 0,
  variable_cost_change_rate: 0
})

const simulationResult = ref<CVPSimulationResult | null>(null)

const cvpChartRef = ref<HTMLElement | null>(null)
const { setOption } = useECharts(cvpChartRef)

function formatAmount(val: number) {
  if (val >= 10000) return (val / 10000).toFixed(2) + '万'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

async function handleQuery() {
  if (!dateRange.value || dateRange.value.length !== 2) return
  
  loading.value = true
  try {
    const res = await getCVPAnalysis({
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      store_id: storeId.value
    })
    
    if ((res.code === 0 || res.code === 200) && res.data) {
      Object.assign(cvpData, res.data)
      renderCVPChart()
      // 清空之前的模拟结果
      simulationResult.value = null
      simulation.fixed_cost_change_rate = 0
      simulation.variable_cost_change_rate = 0
    }
  } catch (error) {
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}

async function handleSimulate() {
  if (!dateRange.value) return
  
  simulating.value = true
  try {
    const res = await simulateCVP(
      {
        start_date: dateRange.value[0],
        end_date: dateRange.value[1],
        store_id: storeId.value
      },
      simulation
    )
    
    if ((res.code === 0 || res.code === 200) && res.data) {
      simulationResult.value = res.data
      ElMessage.success('模拟完成')
    }
  } catch (error) {
    ElMessage.error('模拟失败')
  } finally {
    simulating.value = false
  }
}

function renderCVPChart() {
  if (!cvpChartRef.value) return
  const maxRevenue = cvpData.total_revenue * 1.5
  const step = maxRevenue / 100

  // 生成 X 轴数据（销售额）
  const xData: number[] = []
  for (let i = 0; i <= 100; i++) {
    xData.push(i * step)
  }

  // 总收入线（斜率1）
  const revenueData = xData.map(x => x)

  // 总成本线 = 固定成本 + 变动成本
  // 变动成本率 = 变动成本 / 总收入
  const variableRate = cvpData.total_revenue > 0 ? cvpData.variable_cost / cvpData.total_revenue : 0
  const totalCostData = xData.map(x => cvpData.fixed_cost + x * variableRate)

  // 固定成本线（水平）
  const fixedCostData = xData.map(() => cvpData.fixed_cost)

  nextTick(() => {
    if (!cvpChartRef.value) return
    setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params: unknown) => {
          const list = Array.isArray(params) ? params : []
          const salesValue = (list[0] as { value?: unknown } | undefined)?.value
          const sales = typeof salesValue === 'number' ? salesValue : Number(salesValue)
          const safeSales = Number.isFinite(sales) ? sales : 0
          let html = `<div style="font-weight:bold">销售额: ¥${formatAmount(safeSales)}</div>`
          list.forEach((raw) => {
            const p = raw as { marker?: unknown; seriesName?: unknown; data?: unknown }
            const marker = typeof p.marker === 'string' ? p.marker : ''
            const seriesName = typeof p.seriesName === 'string' ? p.seriesName : ''
            const dataValue = typeof p.data === 'number' ? p.data : Number(p.data)
            const safeData = Number.isFinite(dataValue) ? dataValue : 0
            html += `<div>${marker}${seriesName}: ¥${formatAmount(safeData)}</div>`
          })
          return html
        }
      },
      legend: {
        data: ['总收入', '总成本', '固定成本'],
        top: 10
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 60,
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '销售额(元)',
        axisLabel: {
          formatter: (v: number) => v >= 10000 ? (v / 10000).toFixed(0) + 'w' : String(v)
        }
      },
      yAxis: {
        type: 'value',
        name: '金额(元)',
        axisLabel: {
          formatter: (v: number) => v >= 10000 ? (v / 10000).toFixed(0) + 'w' : String(v)
        }
      },
      series: [
        {
          name: '总收入',
          type: 'line',
          data: revenueData.map((val, idx) => [xData[idx], val]),
          smooth: true,
          lineStyle: { color: '#67c23a', width: 2 },
          itemStyle: { color: '#67c23a' },
          emphasis: { disabled: true }
        },
        {
          name: '总成本',
          type: 'line',
          data: totalCostData.map((val, idx) => [xData[idx], val]),
          smooth: true,
          lineStyle: { color: '#e6a23c', width: 2 },
          itemStyle: { color: '#e6a23c' },
          emphasis: { disabled: true }
        },
        {
          name: '固定成本',
          type: 'line',
          data: fixedCostData.map((val, idx) => [xData[idx], val]),
          lineStyle: { color: '#909399', type: 'dashed', width: 2 },
          itemStyle: { color: '#909399' },
          emphasis: { disabled: true }
        }
      ],
      // 标注盈亏平衡点
      markPoint: {
        data: [
          {
            name: '盈亏平衡点',
            coord: [cvpData.break_even_point, cvpData.break_even_point],
            value: '盈亏平衡点\n' + formatAmount(cvpData.break_even_point),
            itemStyle: { color: '#f56c6c' },
            label: {
              show: true,
              formatter: '{c}',
              fontSize: 12,
              fontWeight: 'bold'
            }
          }
        ]
      }
    }, true)
  })
}

onMounted(() => {
  handleQuery()
})
</script>

<style scoped lang="scss">
.cvp-dashboard {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.metrics-row {
  margin-bottom: 20px;
  
  .metric-card {
    display: flex;
    align-items: center;
    padding: 20px;
    transition: transform 0.3s;
    
    &:hover {
      transform: translateY(-5px);
    }
    
    .card-icon {
      width: 70px;
      height: 70px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      color: white;
      margin-right: 15px;
    }
    
    .card-content {
      flex: 1;
      
      .card-label {
        font-size: 13px;
        color: #909399;
        margin-bottom: 8px;
      }
      
      .card-value {
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 5px;
      }
      
      .card-extra {
        font-size: 12px;
        color: #c0c4cc;
      }
    }
    
    &.bep {
      .card-icon { background: linear-gradient(135deg, #409eff 0%, #79bbff 100%); }
      .card-value { color: #409eff; }
    }
    
    &.safety {
      .card-icon { background: linear-gradient(135deg, #67c23a 0%, #95d475 100%); }
      .card-value { color: #67c23a; }
    }
    
    &.leverage {
      .card-icon { background: linear-gradient(135deg, #e6a23c 0%, #f3c78e 100%); }
      .card-value { color: #e6a23c; }
    }
    
    &.profit {
      .card-icon { background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%); }
      .card-value { color: #f56c6c; }
    }
  }
}

.simulator-card {
  .simulator-content {
    :deep(.el-slider__input) {
      width: 80px;
    }
  }
  
  .simulation-result {
    .result-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;
      
      .label {
        color: #606266;
      }
      
      .value {
        font-weight: bold;
        
        &.highlight {
          color: #409eff;
          font-size: 16px;
        }
        
        &.danger {
          color: #f56c6c;
        }
        
        &.success {
          color: #67c23a;
        }
      }
    }
  }
}

.cost-structure {
  .cost-item {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    
    .label {
      color: #606266;
      font-size: 14px;
    }
    
    .value {
      font-weight: bold;
      font-size: 14px;
      
      &.revenue { color: #67c23a; }
      &.variable { color: #e6a23c; }
      &.fixed { color: #909399; }
      &.contribution { color: #409eff; font-size: 16px; }
    }
  }
}
</style>
