-- 预算管理模块权限添加脚本
-- 直接在数据库中执行此SQL即可启用预算管理功能

-- 1. 添加预算管理权限（如果不存在）
INSERT INTO permission (code, name, description, created_at, updated_at)
SELECT 'budget:view', '预算查看', '查看预算数据和差异分析', NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM permission WHERE code = 'budget:view'
);

INSERT INTO permission (code, name, description, created_at, updated_at)
SELECT 'budget:manage', '预算管理', '创建和修改预算设置', NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM permission WHERE code = 'budget:manage'
);

-- 2. 将预算权限分配给admin角色（如果未分配）
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
CROSS JOIN permission p
WHERE r.code = 'admin' 
  AND p.code IN ('budget:view', 'budget:manage')
  AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- 3. 验证权限已添加
SELECT 
    p.code,
    p.name,
    p.description,
    COUNT(rp.role_id) as assigned_roles
FROM permission p
LEFT JOIN role_permission rp ON p.id = rp.permission_id
WHERE p.code LIKE 'budget:%'
GROUP BY p.id, p.code, p.name, p.description
ORDER BY p.code;

-- 4. 验证admin角色拥有预算权限
SELECT 
    r.name as role_name,
    p.code as permission_code,
    p.name as permission_name
FROM role r
JOIN role_permission rp ON r.id = rp.role_id
JOIN permission p ON rp.permission_id = p.id
WHERE r.code = 'admin' AND p.code LIKE 'budget:%'
ORDER BY p.code;
