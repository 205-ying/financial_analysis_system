<!--
  可访问门店选择器
  根据用户的数据权限自动过滤门店列表
-->
<template>
  <el-select
    v-model="localValue"
    placeholder="请选择门店"
    clearable
    :style="{ width: width }"
    :disabled="disabled"
    :loading="storeStore.loading"
    @change="handleChange"
  >
    <el-option label="全部门店" :value="undefined" />
    <el-option
      v-for="store in storeStore.accessibleStoreList"
      :key="store.id"
      :label="store.name"
      :value="store.id"
    />
  </el-select>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useStoreStore } from '@/stores/store'

interface Props {
  modelValue?: number | undefined
  width?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: undefined,
  width: '200px',
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: number | undefined]
  'change': [value: number | undefined]
}>()

const storeStore = useStoreStore()
const localValue = ref<number | undefined>(props.modelValue)

// 监听 props 变化
watch(
  () => props.modelValue,
  (newValue) => {
    localValue.value = newValue
  }
)

// 监听本地值变化
watch(localValue, (newValue) => {
  emit('update:modelValue', newValue)
})

// 处理选择变化
const handleChange = (value: number | undefined) => {
  emit('change', value)
}

// 组件挂载时加载门店列表
onMounted(async () => {
  if (storeStore.allStores.length === 0) {
    await storeStore.fetchAllStores()
  }
})
</script>
