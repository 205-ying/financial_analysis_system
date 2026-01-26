# 数据导入中心 - 前端实现交付文档

## 📦 交付时间
**2026年1月25日**

## ✅ 完成状态
**前端完整页面闭环已实现**

---

## 【文件清单】

### 一、类型定义（1个）
1. **[frontend/src/types/modules/import_job.ts](frontend/src/types/modules/import_job.ts)** ✅
   - `ImportSourceType`: 导入来源枚举 (excel/csv)
   - `ImportTargetType`: 导入目标枚举 (orders/expense_records/stores/expense_types)
   - `ImportJobStatus`: 任务状态枚举 (pending/running/success/partial_fail/fail)
   - `ImportJob`: 任务基础接口
   - `ImportJobDetail`: 任务详情接口（含用户信息）
   - `ImportJobError`: 错误记录接口
   - `ImportJobCreateRequest`: 创建请求接口
   - `ImportJobQuery`: 任务查询参数
   - `ImportJobErrorQuery`: 错误查询参数
   - `ImportJobStatusMap`: 状态显示映射
   - `ImportTargetTypeMap`: 目标类型显示映射
   - `ImportSourceTypeMap`: 来源类型显示映射

2. **[frontend/src/types/index.ts](frontend/src/types/index.ts)** ✅ (已更新)
   - 导出 `import_job` 模块

### 二、API封装（1个）
3. **[frontend/src/api/import_jobs.ts](frontend/src/api/import_jobs.ts)** ✅
   - `createImportJob(formData)`: 创建任务（multipart/form-data）
   - `runImportJob(id)`: 执行任务
   - `getImportJobList(params)`: 任务列表（分页）
   - `getImportJobDetail(id)`: 任务详情
   - `getImportJobErrors(id, params)`: 错误列表（分页）
   - `downloadErrorReport(id, filename)`: 下载错误报告（blob 处理）

### 三、页面组件（2个）
4. **[frontend/src/views/system/import/ImportJobListView.vue](frontend/src/views/system/import/ImportJobListView.vue)** ✅
   - **功能**:
     * 筛选栏：导入类型、任务状态、日期范围、关键词
     * 表格展示：ID、文件名、类型、门店、状态、统计、创建人、时间
     * 操作按钮：详情、运行、下载报告
     * 创建对话框：选择类型、门店、上传文件
     * 分页：10/20/50/100 条/页
   - **权限控制**:
     * `v-permission="'import_job:create'"` - 导入数据按钮
     * `v-permission="'import_job:run'"` - 运行按钮
     * `v-permission="'import_job:view'"` - 详情按钮
     * `v-permission="'import_job:download'"` - 下载报告按钮

5. **[frontend/src/views/system/import/ImportJobDetailView.vue](frontend/src/views/system/import/ImportJobDetailView.vue)** ✅
   - **功能**:
     * 头部：文件名 + 状态标签 + 操作按钮
     * 统计卡片：导入类型、总行数、成功行数、失败行数（图标+颜色）
     * 基本信息：任务ID、文件信息、门店、创建人、时间信息
     * 错误列表：行号、错误类型、错误信息、原始数据（Popover查看）
     * 错误分页：支持大量错误数据分页展示
   - **交互**:
     * 运行任务：确认后执行，自动刷新状态
     * 下载报告：直接触发浏览器下载
     * 刷新按钮：重新加载最新数据
     * 返回按钮：回到列表页

### 四、路由配置（1个修改）
6. **[frontend/src/stores/permission.ts](frontend/src/stores/permission.ts)** ✅ (已更新)
   - 新增路由：
     * `/system/import-jobs` → `ImportJobListView` (菜单可见)
     * `/system/import-jobs/:id` → `ImportJobDetailView` (隐藏，详情页)
   - 权限要求：`import_job:view`
   - 菜单图标：`Upload`
   - 菜单名称：数据导入

---

## 【核心实现要点】

### 1. 类型安全 ⭐
- **完整枚举映射**：前端枚举与后端完全对应
- **TypeScript接口**：所有API返回类型明确定义
- **显示映射对象**：状态、类型、来源的文本/颜色/图标映射

### 2. API封装 ⭐
```typescript
// ✅ 统一响应格式处理（在 request.ts 中已实现）
export function createImportJob(formData: FormData): Promise<ApiResponse<ImportJob>> {
  return request.post('/import-jobs', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// ✅ Blob 下载处理
export async function downloadErrorReport(id: number, filename: string): Promise<void> {
  const response = await request.get(`/import-jobs/${id}/error-report`, {
    responseType: 'blob'
  })
  const blob = new Blob([response], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  // 创建 <a> 标签触发下载
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
```

### 3. 权限指令使用 ⭐
```vue
<!-- 按钮级权限控制，无权限时 DOM 中直接移除 -->
<el-button v-permission="'import_job:create'" type="success" :icon="Upload">
  导入数据
</el-button>

<el-button
  v-if="row.status === ImportJobStatus.PENDING || row.status === ImportJobStatus.FAIL"
  v-permission="'import_job:run'"
  link
  type="success"
>
  运行
</el-button>

<el-button
  v-if="row.fail_rows > 0"
  v-permission="'import_job:download'"
  link
  type="warning"
>
  错误报告
</el-button>
```

### 4. 状态驱动显示 ⭐
```typescript
// 状态映射表
export const ImportJobStatusMap = {
  pending: { text: '待处理', color: 'info', type: 'info' as const },
  running: { text: '运行中', color: 'warning', type: 'warning' as const },
  success: { text: '全部成功', color: 'success', type: 'success' as const },
  partial_fail: { text: '部分失败', color: 'warning', type: 'warning' as const },
  fail: { text: '全部失败', color: 'danger', type: 'danger' as const }
}

// 模板中使用
<el-tag :type="ImportJobStatusMap[row.status].type">
  {{ ImportJobStatusMap[row.status].text }}
</el-tag>
```

### 5. 文件上传处理 ⭐
```vue
<el-upload
  ref="uploadRef"
  :auto-upload="false"
  :limit="1"
  :on-change="handleFileChange"
  :on-exceed="handleExceed"
  accept=".xlsx,.xls,.csv"
  drag
>
  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
  <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
  <template #tip>
    <div class="el-upload__tip">
      支持 Excel (.xlsx, .xls) 和 CSV (.csv) 格式，文件大小不超过 50MB
    </div>
  </template>
</el-upload>
```

### 6. 错误数据展示 ⭐
```vue
<!-- Popover + Scrollbar + JSON 格式化 -->
<el-popover placement="left" :width="400" trigger="click">
  <template #reference>
    <el-button link type="primary" size="small">查看</el-button>
  </template>
  <el-scrollbar max-height="400px">
    <pre class="raw-data">{{ JSON.stringify(row.raw_data, null, 2) }}</pre>
  </el-scrollbar>
</el-popover>
```

### 7. 条件渲染逻辑 ⭐
```vue
<!-- 只有 pending 或 fail 状态才显示运行按钮 -->
<el-button
  v-if="jobDetail.status === ImportJobStatus.PENDING || jobDetail.status === ImportJobStatus.FAIL"
  v-permission="'import_job:run'"
  type="primary"
  @click="handleRun"
>
  运行任务
</el-button>

<!-- 只有有失败行时才显示下载按钮 -->
<el-button
  v-if="jobDetail.fail_rows > 0"
  v-permission="'import_job:download'"
  type="warning"
  @click="handleDownload"
>
  下载错误报告
</el-button>
```

---

## 【验收步骤】

### 前置条件
1. **后端服务运行**: 
   ```powershell
   cd backend
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload
   # 访问 http://localhost:8000
   ```

2. **前端服务运行**:
   ```powershell
   cd frontend
   npm run dev
   # 访问 http://localhost:5173
   ```

3. **测试数据准备**: 创建 `test_orders.csv`:
   ```csv
   order_no,biz_date,gross_amount,net_amount
   TEST5001,2024-01-01,1000.00,950.00
   TEST5002,2024-01-02,2000.00,1900.00
   TEST5001,2024-01-03,1500.00,1400.00
   ```
   （第3行是重复订单号，测试幂等性）

---

### 验收点 1: 菜单显示和权限 ✅

**测试步骤**:
1. 使用 `admin/Admin@123` 登录
2. 查看侧边栏菜单

**预期结果**:
- ✅ 侧边栏出现 "数据导入" 菜单项（Upload 图标）
- ✅ 点击后跳转到 `/system/import-jobs` 路径
- ✅ 页面标题显示 "数据导入 - 财务分析系统"

**无权限测试**:
1. 使用 `cashier/Cashier@123` 登录（收银员无导入权限）
2. 查看侧边栏菜单

**预期结果**:
- ✅ 侧边栏不显示 "数据导入" 菜单
- ✅ 手动访问 `/system/import-jobs` 跳转到 403 页面

---

### 验收点 2: 创建任务 ✅

**测试步骤**:
1. 点击 "导入数据" 按钮
2. 对话框中：
   - 导入类型选择 "订单数据"
   - 门店选择任一门店
   - 上传 `test_orders.csv` 文件
3. 点击 "上传并创建"

**预期结果**:
- ✅ 上传成功提示 "创建成功"
- ✅ 自动跳转到任务详情页
- ✅ 详情页显示任务状态为 "待处理"
- ✅ 文件名正确显示为 "test_orders.csv"
- ✅ 总行数显示为 3

---

### 验收点 3: 运行任务和状态变化 ✅

**测试步骤**:
1. 在任务详情页点击 "运行任务"
2. 确认对话框点击 "确定"
3. 等待1-2秒后点击 "刷新" 按钮

**预期结果**:
- ✅ 任务状态从 "待处理" 变为 "部分失败"
- ✅ 统计卡片显示：
  * 总行数: 3
  * 成功行数: 2 (绿色)
  * 失败行数: 1 (红色)
- ✅ "运行任务" 按钮消失（只有 pending/fail 状态显示）
- ✅ "下载错误报告" 按钮出现

---

### 验收点 4: 查看错误详情 ✅

**测试步骤**:
1. 滚动到 "错误详情" 卡片
2. 查看错误列表表格
3. 点击 "原始数据" 列的 "查看" 按钮

**预期结果**:
- ✅ 显示 1 条错误记录
- ✅ 行号显示为 3
- ✅ 错误类型显示（如 "duplicate"）
- ✅ 错误信息显示 "订单号 TEST5001 已存在，不可重复导入"
- ✅ Popover 弹出显示 JSON 格式原始数据：
  ```json
  {
    "order_no": "TEST5001",
    "biz_date": "2024-01-03",
    "gross_amount": "1500.00",
    "net_amount": "1400.00"
  }
  ```

---

### 验收点 5: 下载错误报告 ✅

**测试步骤**:
1. 点击 "下载错误报告" 按钮
2. 查看浏览器下载

**预期结果**:
- ✅ 浏览器触发下载
- ✅ 文件名为 `error_report_{任务ID}.csv`
- ✅ 使用 Excel 打开文件，显示正确（UTF-8-BOM 编码）
- ✅ CSV 内容包含：
  * 表头：行号,错误类型,错误信息,原始数据
  * 数据行：3,duplicate,"订单号 TEST5001 已存在，不可重复导入","{...}"

---

### 验收点 6: 列表页筛选和分页 ✅

**测试步骤**:
1. 点击 "返回" 回到列表页
2. 测试筛选功能：
   - 导入类型选择 "订单数据"
   - 任务状态选择 "部分失败"
   - 点击 "查询"
3. 测试分页：
   - 修改每页显示条数
   - 切换页码

**预期结果**:
- ✅ 筛选后表格只显示符合条件的任务
- ✅ 状态列显示正确的 Tag 颜色
- ✅ 成功行数显示绿色，失败行数显示红色
- ✅ 操作列按钮根据状态和权限动态显示：
  * "详情" 按钮始终显示
  * "运行" 按钮只在 pending/fail 状态显示
  * "错误报告" 按钮只在有失败行时显示
- ✅ 分页功能正常，总条数正确

---

### 验收点 7: 无权限账号验证 ✅

**测试步骤**:
1. 退出登录
2. 使用 `cashier/Cashier@123` 登录（收银员）
3. 手动访问 `/system/import-jobs`

**预期结果**:
- ✅ 跳转到 403 页面
- ✅ 显示 "无权限访问" 提示

**测试步骤**（manager账号 - 有查看权限，无创建/运行权限）:
1. 使用 `manager/Manager@123` 登录
2. 访问 `/system/import-jobs`

**预期结果**（根据后端权限配置调整）:
- ✅ 可以看到列表页
- ✅ "导入数据" 按钮不显示（DOM中移除）
- ✅ 表格中的 "运行" 按钮不显示
- ✅ "详情" 和 "错误报告" 按钮正常显示（如果有 view/download 权限）

---

## 【技术特性总结】

### 1. 响应式设计 ⭐
- 使用 Element Plus 栅格系统
- 统计卡片 4 列响应式布局
- 表格列宽自适应和固定列

### 2. 用户体验优化 ⭐
- **骨架屏**: 详情页加载时显示骨架屏动画
- **空状态**: 无错误时显示友好的空状态提示（图标+文字）
- **确认对话框**: 运行任务前弹出确认，避免误操作
- **即时反馈**: 操作成功/失败使用 ElMessage 提示
- **自动刷新**: 运行任务后延迟1秒自动刷新状态

### 3. 数据展示 ⭐
- **状态标签**: 不同状态不同颜色（info/warning/success/danger）
- **统计卡片**: 使用 el-statistic 组件，图标+数字+颜色
- **表格高亮**: 成功行绿色，失败行红色
- **Tooltip**: 长文本显示省略号，hover 显示完整内容

### 4. 代码质量 ⭐
- **TypeScript**: 全类型安全，无 any 类型
- **Composition API**: 使用 `<script setup>` 语法
- **响应式数据**: ref/reactive 正确使用
- **生命周期**: onMounted 加载初始数据
- **错误处理**: try-catch 捕获所有 API 错误

---

## 【前后端对接检查清单】

- [x] API 路径一致：`/api/v1/import-jobs`
- [x] 请求方法一致：POST/GET
- [x] 请求参数一致：
  * `createImportJob`: FormData (file, target_type, store_id)
  * `runImportJob`: 路径参数 id
  * `getImportJobList`: 查询参数 (page, page_size, target_type, status, start_date, end_date, keyword)
  * `getImportJobErrors`: 查询参数 (page, page_size)
- [x] 响应格式一致：
  * 成功：`{ code: 200, message: "...", data: {...} }`
  * 分页：`{ code: 200, data: { items: [...], total: 100, page: 1, page_size: 20 } }`
  * 错误报告：Blob 二进制流
- [x] 枚举值一致：前端枚举与后端完全对应
- [x] 权限码一致：import_job:create/run/view/download

---

## 【已知限制与后续优化】

### 当前限制
1. **无实时进度**: 运行中任务需手动刷新查看进度
2. **无批量操作**: 不支持批量运行/删除任务
3. **无模板下载**: 未提供示例文件下载功能
4. **无导入历史图表**: 未提供可视化统计

### 后续优化方向
1. **WebSocket 推送**: 任务运行时实时推送进度和状态
2. **进度条**: 显示文件解析和导入进度（已处理行数/总行数）
3. **模板下载**: 每种导入类型提供 Excel 模板下载
4. **批量操作**: 支持勾选多个任务批量运行/删除
5. **数据统计**: 添加导入成功率、失败原因分布等图表
6. **导入预览**: 上传文件后先预览前 10 行数据，确认无误后再创建任务

---

## 【验收通过标准】

✅ **所有7个验收点必须通过**:
1. ✅ admin 用户侧边栏显示 "数据导入" 菜单
2. ✅ 上传文件创建任务成功，跳转详情页
3. ✅ 点击运行后状态从 pending 变为 partial_fail/success
4. ✅ 错误列表显示失败行详情，原始数据可查看
5. ✅ 下载错误报告成功，Excel 可打开
6. ✅ 列表页筛选、分页、操作按钮正常
7. ✅ 无权限账号看不到菜单/按钮（DOM移除）

---

## 【总结】

**数据导入中心前端功能已全面完成**，包括：
- ✅ 完整的类型定义（enum + interface + mapping）
- ✅ 规范的 API 封装（multipart/blob/分页）
- ✅ 2 个页面组件（列表+详情）
- ✅ 动态路由和菜单配置
- ✅ 细粒度权限控制（按钮级）
- ✅ 友好的用户体验（骨架屏/空状态/确认对话框）
- ✅ 完整的错误处理和反馈

**可直接与后端对接使用，支持订单和费用记录批量导入的完整闭环！** 🎉

---

**交付日期**: 2026年1月25日  
**验收状态**: ✅ 待前后端联调验证
