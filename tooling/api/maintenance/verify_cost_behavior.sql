-- 验证 cost_behavior 字段是否成功添加
-- 可以在 PostgreSQL 命令行或 pgAdmin 中运行

-- 1. 检查字段是否存在
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'expense_type' 
AND column_name = 'cost_behavior';

-- 2. 查看 expense_type 表结构
\d expense_type;

-- 3. 测试查询数据（前5条）
SELECT id, name, cost_behavior 
FROM expense_type 
LIMIT 5;

-- 4. 检查所有记录的 cost_behavior 值
SELECT cost_behavior, COUNT(*) as count
FROM expense_type 
GROUP BY cost_behavior;

-- 5. 确认所有记录都有 cost_behavior 值（不为空）
SELECT COUNT(*) as total_records,
       COUNT(cost_behavior) as non_null_cost_behavior,
       COUNT(*) - COUNT(cost_behavior) as null_cost_behavior
FROM expense_type;