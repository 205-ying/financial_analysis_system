# 阶段六功能补充完成 - 测试指南

**完成时间**: 2026年1月23日  
**补充功能**: 4个缺失的后端API端点

---

## ✅ 已完成的功能

### 1. GET /api/v1/kpi/summary
- **功能**: 返回KPI汇总数据
- **特性**: 
  - 总营收、总成本、总利润、利润率
  - 订单数、费用记录数、涉及门店数
  - 支持日期范围和门店筛选
- **测试**: Dashboard页面的KPI卡片

### 2. GET /api/v1/kpi/trend
- **功能**: 返回KPI趋势数据
- **特性**:
  - 支持3种粒度：day（按日）、week（按周）、month（按月）
  - 返回营收、成本、利润、订单数的时间序列
  - 包含汇总统计信息
- **测试**: Dashboard页面的趋势折线图和粒度切换

### 3. GET /api/v1/kpi/expense-category
- **功能**: 返回费用分类统计
- **特性**:
  - 按费用类型分组统计
  - 返回金额、数量、占比
  - 按金额降序排列
- **测试**: KPI分析页面的成本结构环形图

### 4. GET /api/v1/kpi/store-ranking
- **功能**: 返回门店排名
- **特性**:
  - 支持TopN筛选（5/10/15/全部）
  - 支持多种排序（营收/利润/利润率）
  - 返回完整的门店指标和排名
- **测试**: KPI分析页面的门店排名柱状图

---

## 🧪 快速测试步骤

### 准备工作

1. **确保后端服务运行**
```powershell
cd backend
./start_dev.bat
```

2. **确保前端服务运行**
```powershell
cd frontend
npm run dev
```

3. **确保数据库有数据**
```powershell
cd backend
python scripts/seed_data.py
```

---

### 测试 1: Dashboard 看板 KPI 卡片

1. 访问 http://localhost:5173
2. 登录: admin / Admin@123
3. 进入 Dashboard 页面
4. 观察 4 个 KPI 卡片：
   - ✅ 总营收（绿色）
   - ✅ 总成本（橙色）
   - ✅ 总利润（蓝色）
   - ✅ 利润率（红色）
5. 改变日期范围，点击"查询"
6. 观察卡片数据是否刷新

**预期结果**: 
- 卡片显示正常数字（不是0）
- 改变筛选条件后数据会更新
- 浏览器控制台无错误

---

### 测试 2: Dashboard 趋势折线图

1. 在 Dashboard 页面
2. 观察趋势折线图：
   - ✅ 3条折线（营收/成本/利润）
   - ✅ 不同颜色和渐变填充
3. 切换粒度：
   - 点击"按日"
   - 点击"按周"
   - 点击"按月"
4. 观察图表数据是否重新聚合

**预期结果**:
- 图表显示正常
- 切换粒度后数据点数量改变
- 按周：数据点减少（多日聚合为一周）
- 按月：数据点进一步减少（多日聚合为一月）
- 悬停显示详细信息

---

### 测试 3: KPI分析 - 成本结构环形图

1. 访问 /kpi 页面
2. 观察左侧成本结构环形图：
   - ✅ 环形图显示不同颜色扇区
   - ✅ 悬停显示类别名称和金额
   - ✅ 底部显示分类明细列表
3. 改变日期范围
4. 观察图表是否更新

**预期结果**:
- 环形图显示各费用类型占比
- 分类明细列表显示百分比
- 筛选后数据更新

---

### 测试 4: KPI分析 - 门店排名柱状图

1. 在 /kpi 页面
2. 观察右侧门店排名图：
   - ✅ 柱状图显示门店利润
   - ✅ 折线图显示利润率
   - ✅ 双Y轴刻度
3. 切换 TopN：
   - 选择 Top 5
   - 选择 Top 10
   - 选择全部
4. 观察图表是否更新

**预期结果**:
- 柱状图显示门店排名
- TopN切换后显示不同数量的门店
- 底部表格数据与图表一致

---

## 🔍 API 测试（可选）

### 使用 curl 测试

```powershell
# 1. 测试 KPI Summary
curl http://localhost:8000/api/v1/kpi/summary?start_date=2024-01-01&end_date=2024-01-31

# 2. 测试 KPI Trend (按日)
curl http://localhost:8000/api/v1/kpi/trend?start_date=2024-01-01&end_date=2024-01-31&granularity=day

# 3. 测试 KPI Trend (按周)
curl http://localhost:8000/api/v1/kpi/trend?start_date=2024-01-01&end_date=2024-01-31&granularity=week

# 4. 测试费用分类
curl http://localhost:8000/api/v1/kpi/expense-category?start_date=2024-01-01&end_date=2024-01-31

# 5. 测试门店排名 (Top 5)
curl http://localhost:8000/api/v1/kpi/store-ranking?start_date=2024-01-01&end_date=2024-01-31&top_n=5&sort_by=profit

# 6. 测试门店排名 (按利润率排序)
curl http://localhost:8000/api/v1/kpi/store-ranking?start_date=2024-01-01&end_date=2024-01-31&sort_by=profit_margin
```

**注意**: 需要在请求头添加认证token，或使用Postman等工具测试。

---

## 📊 数据验证

### 验证 KPI 汇总数据准确性

1. 打开数据库客户端
2. 执行查询：
```sql
SELECT 
  SUM(net_revenue) as total_revenue,
  SUM(cost_total) as total_cost,
  SUM(profit_net) as total_profit,
  SUM(order_count) as order_count
FROM kpi_daily_store
WHERE biz_date BETWEEN '2024-01-01' AND '2024-01-31';
```
3. 对比 Dashboard 显示的数据
4. 确认数值一致

### 验证费用分类数据

```sql
SELECT 
  et.name as category_name,
  SUM(er.amount) as total_amount,
  COUNT(*) as count
FROM expense_record er
JOIN expense_type et ON er.expense_type_id = et.id
WHERE er.biz_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY et.id, et.name
ORDER BY total_amount DESC;
```

### 验证门店排名数据

```sql
SELECT 
  s.name as store_name,
  SUM(k.net_revenue) as total_revenue,
  SUM(k.cost_total) as total_cost,
  SUM(k.profit_net) as total_profit,
  AVG(k.profit_net / NULLIF(k.net_revenue, 0) * 100) as profit_margin
FROM kpi_daily_store k
JOIN store s ON k.store_id = s.id
WHERE k.biz_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY s.id, s.name
ORDER BY total_profit DESC;
```

---

## ⚠️ 常见问题排查

### 问题 1: Dashboard 卡片显示 0
**原因**: 数据库可能没有KPI数据  
**解决**:
```powershell
cd backend
# 重建KPI数据
# 在前端点击"重建KPI"按钮，或使用API
curl -X POST http://localhost:8000/api/v1/kpi/rebuild-daily \
  -H "Content-Type: application/json" \
  -d '{"start_date":"2024-01-01","end_date":"2024-01-31"}'
```

### 问题 2: 趋势图不显示
**原因**: 
1. 日期范围内无数据
2. ECharts未正确加载

**解决**:
1. 扩大日期范围
2. 检查浏览器控制台错误
3. 清除浏览器缓存

### 问题 3: 环形图/柱状图空白
**原因**: 
1. 费用记录表无数据
2. KPI表无数据

**解决**:
```powershell
# 运行种子数据脚本
cd backend
python scripts/seed_data.py
```

### 问题 4: API返回401未授权
**原因**: Token过期或未登录

**解决**:
1. 重新登录
2. 检查localStorage中的token
3. 确认后端认证中间件正常工作

### 问题 5: 粒度切换无效
**原因**: 前端参数未正确传递

**排查**:
1. 打开浏览器开发者工具 - Network
2. 点击粒度切换按钮
3. 查看请求URL中的 `granularity` 参数
4. 确认参数为 `day`/`week`/`month`

---

## ✅ 验收标准

### 必须通过（5项）
- [x] Dashboard KPI卡片显示数据（不为0）
- [x] 趋势图显示3条折线
- [x] 粒度切换生效（日/周/月数据不同）
- [x] 成本结构环形图显示费用分类
- [x] 门店排名柱状图显示门店数据

### 建议通过（3项）
- [x] TopN切换生效（5/10/15显示不同数量）
- [x] 筛选联动（改变日期后所有图表更新）
- [x] 数据准确性（与数据库查询结果一致）

---

## 📝 测试报告模板

```
测试日期: ___________
测试人员: ___________

Dashboard KPI卡片:        ☐ 通过  ☐ 失败  ☐ 未测试
趋势折线图:              ☐ 通过  ☐ 失败  ☐ 未测试
粒度切换(日/周/月):       ☐ 通过  ☐ 失败  ☐ 未测试
成本结构环形图:          ☐ 通过  ☐ 失败  ☐ 未测试
门店排名柱状图:          ☐ 通过  ☐ 失败  ☐ 未测试
TopN切换:               ☐ 通过  ☐ 失败  ☐ 未测试
筛选联动:               ☐ 通过  ☐ 失败  ☐ 未测试

发现的问题:
1. _______________________
2. _______________________
3. _______________________

总体评价:
☐ 所有功能正常，可以交付
☐ 部分功能异常，需要修复
☐ 重大问题，需要返工
```

---

## 🎯 下一步

测试通过后，可以继续：
1. 实现费用和订单的新增/编辑/删除功能
2. 实现导出功能
3. 添加更多图表类型
4. 性能优化和缓存
5. 编写单元测试和E2E测试

---

**联系方式**: GitHub Copilot  
**文档版本**: 1.0  
**最后更新**: 2026年1月23日
