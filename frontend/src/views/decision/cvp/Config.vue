<template>
  <div class="cvp-config">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">成本习性配置</span>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
        </div>
      </template>

      <el-alert
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <div>请为每个费用科目设置成本习性：</div>
        <ul style="margin: 5px 0 0 20px;">
          <li><strong>固定成本</strong>：不随营业额变化而变化的成本（如房租、折旧、管理人员工资等）</li>
          <li><strong>变动成本</strong>：随营业额变化而变化的成本（如采购提成、配送费、营销费等）</li>
        </ul>
      </el-alert>

      <el-table v-loading="loading" :data="expenseTypes" border style="width: 100%">
        <el-table-column prop="type_code" label="科目编码" width="150" />
        <el-table-column prop="name" label="科目名称" min-width="200" />
        <el-table-column prop="category" label="类别" width="150">
          <template #default="{ row }">
            <el-tag size="small">{{ getCategoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="成本习性" width="200" align="center">
          <template #default="{ row }">
            <el-select v-model="row.cost_behavior" placeholder="选择" size="small" style="width: 140px">
              <el-option label="固定成本" value="fixed">
                <el-icon style="margin-right: 5px"><Lock /></el-icon>固定成本
              </el-option>
              <el-option label="变动成本" value="variable">
                <el-icon style="margin-right: 5px"><TrendCharts /></el-icon>变动成本
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="说明" min-width="250">
          <template #default="{ row }">
            <span v-if="row.cost_behavior === 'fixed'" class="info-text">
              <el-icon><InfoFilled /></el-icon> 
              不随销售额变化
            </span>
            <span v-else class="info-text success">
              <el-icon><InfoFilled /></el-icon> 
              随销售额变化
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Lock, TrendCharts, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getExpenseTypeList } from '@/api/expense'
import { updateCostBehavior } from '@/api/cvp'
import type { ExpenseTypeInfo } from '@/types'

const loading = ref(false)
const saving = ref(false)
const expenseTypes = ref<ExpenseTypeInfo[]>([])
const originalData = ref<Record<number, string>>({})

const categoryLabels: Record<string, string> = {
  operating: '运营成本',
  marketing: '营销费用',
  administrative: '管理费用',
  other: '其他',
  cost: '成本',
  expense: '费用'
}

function getCategoryLabel(category: string) {
  return categoryLabels[category] || category
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getExpenseTypeList()
    if ((res.code === 0 || res.code === 200) && res.data) {
      const normalized = res.data.map(item => ({
        ...item,
        cost_behavior: item.cost_behavior || 'variable'
      }))
      expenseTypes.value = normalized
      // 保存原始数据用于对比变化
      originalData.value = {}
      normalized.forEach(item => {
        originalData.value[item.id] = item.cost_behavior
      })
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  // 找出有变化的项
  const changedItems = expenseTypes.value.filter(item => {
    const behavior = item.cost_behavior || 'variable'
    if (item.cost_behavior !== behavior) {
      item.cost_behavior = behavior
    }
    return behavior !== originalData.value[item.id]
  })

  if (changedItems.length === 0) {
    ElMessage.info('没有修改内容')
    return
  }

  saving.value = true
  try {
    // 逐个更新
    const promises = changedItems.map(item => {
      const behavior = (item.cost_behavior || 'variable') as 'fixed' | 'variable'
      return updateCostBehavior({
        expense_type_id: item.id,
        cost_behavior: behavior
      })
    })
    await Promise.all(promises)
    
    ElMessage.success(`成功更新 ${changedItems.length} 个科目的成本习性`)
    await fetchData() // 重新加载
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.cvp-config {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .title {
      font-size: 16px;
      font-weight: 600;
    }
  }
  
  .info-text {
    color: #909399;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    
    &.success {
      color: #67c23a;
    }
  }
}
</style>
