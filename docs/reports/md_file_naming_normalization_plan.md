# Markdown 文件命名规范化方案

**执行日期**: 2026-01-27  
**目标**: 统一所有 md 文件命名为 snake_case 英文格式  
**原则**: 保持语义清晰、便于跨平台兼容、易于版本控制

---

## 📊 当前状态分析

### 命名风格统计

| 命名风格 | 文件数 | 示例 |
|---------|--------|------|
| **snake_case (标准)** | ~20个 | development_guide.md, backend_structure.md |
| **中文命名 (非标准)** | ~15个 | second_structure_optimization_delivery.md, frontend_cleanup_completion_report.md |

### 存在的问题

1. ❌ **跨平台兼容性差** - 中文文件名在某些系统可能显示乱码
2. ❌ **Git 操作不便** - 中文路径在命令行需要转义
3. ❌ **搜索效率低** - 英文关键词搜索无法匹配中文文件名
4. ❌ **IDE 支持差** - 某些编辑器对中文文件名支持不佳
5. ❌ **命名不一致** - 同一项目混用两种风格

---

## 🎯 重命名映射表

### docs/reports/ 目录（核心报告）

| 当前文件名（中文） | 新文件名（snake_case） | 说明 |
|------------------|----------------------|------|
| `second_structure_optimization_diagnosis.md` | `second_structure_optimization_diagnosis.md` | 诊断报告 |
| `second_structure_optimization_delivery.md` | `second_structure_optimization_delivery.md` | 最终交付 |
| `backend_second_convergence_report.md` | `backend_second_convergence_report.md` | 后端收敛 |
| `frontend_second_optimization_report.md` | `frontend_second_optimization_report.md` | 前端优化 |
| `documentation_second_governance_report.md` | `documentation_second_governance_report.md` | 文档治理 |
| `script_entry_unification_report.md` | `script_entry_unification_report.md` | 脚本统一 |
| `restrained_structure_optimization_report.md` | `restrained_structure_optimization_report.md` | 克制优化 |
| `repository_cleanup_report.md` | `repository_cleanup_report.md` | 仓库清理 |
| `repository_cleanup_changelog.md` | `repository_cleanup_changelog.md` | 变更清单 |
| `same_function_file_integration_analysis.md` | `same_function_file_integration_analysis.md` | 功能整合 |
| `cross_platform_consistency_audit.md` | `cross_platform_consistency_audit.md` | 一致性审计 |
| `code_slimming_redundancy_cleanup.md` | `code_slimming_redundancy_cleanup.md` | 代码瘦身 |
| `代码重复分析.md` | `code_duplication_analysis.md` | 重复分析 |
| `type_constant_deduplication_analysis.md` | `type_constant_deduplication_analysis.md` | 类型去重 |
| `frontend_cleanup_completion_report.md` | `frontend_cleanup_completion_report.md` | 前端清理 |
| `page_permission_mapping.md` | `page_permission_mapping.md` | 权限映射 |
| `project_complete_directory_tree.md` | `project_complete_directory_tree.md` | 完整目录树 |

### 已符合规范的文件（保持不变）

| 文件名 | 状态 |
|-------|------|
| `file_naming_normalization_report.md` | ✅ 保持 |
| `frontend_optimization_report.md` | ✅ 保持 |
| `project_structure_optimization_report.md` | ✅ 保持 |
| `INDEX.md` | ✅ 保持 |

---

## 🔄 执行步骤

### 阶段1: 批量重命名（Git方式）

```bash
cd c:\Users\29624\Desktop\financial_analysis_system

# 重命名 docs/reports/ 核心报告（保留Git历史）
git mv "docs/reports/second_structure_optimization_diagnosis.md" "docs/reports/second_structure_optimization_diagnosis.md"
git mv "docs/reports/second_structure_optimization_delivery.md" "docs/reports/second_structure_optimization_delivery.md"
git mv "docs/reports/backend_second_convergence_report.md" "docs/reports/backend_second_convergence_report.md"
git mv "docs/reports/frontend_second_optimization_report.md" "docs/reports/frontend_second_optimization_report.md"
git mv "docs/reports/documentation_second_governance_report.md" "docs/reports/documentation_second_governance_report.md"
git mv "docs/reports/script_entry_unification_report.md" "docs/reports/script_entry_unification_report.md"
git mv "docs/reports/restrained_structure_optimization_report.md" "docs/reports/restrained_structure_optimization_report.md"
git mv "docs/reports/repository_cleanup_report.md" "docs/reports/repository_cleanup_report.md"
git mv "docs/reports/repository_cleanup_changelog.md" "docs/reports/repository_cleanup_changelog.md"
git mv "docs/reports/same_function_file_integration_analysis.md" "docs/reports/same_function_file_integration_analysis.md"
git mv "docs/reports/cross_platform_consistency_audit.md" "docs/reports/cross_platform_consistency_audit.md"
git mv "docs/reports/code_slimming_redundancy_cleanup.md" "docs/reports/code_slimming_redundancy_cleanup.md"
git mv "docs/reports/代码重复分析.md" "docs/reports/code_duplication_analysis.md"
git mv "docs/reports/type_constant_deduplication_analysis.md" "docs/reports/type_constant_deduplication_analysis.md"
git mv "docs/reports/frontend_cleanup_completion_report.md" "docs/reports/frontend_cleanup_completion_report.md"
git mv "docs/reports/page_permission_mapping.md" "docs/reports/page_permission_mapping.md"
git mv "docs/reports/project_complete_directory_tree.md" "docs/reports/project_complete_directory_tree.md"
```

### 阶段2: 更新所有引用

需要更新引用这些文件的文档：

**受影响的文件**:
- `docs/reports/INDEX.md` - 报告索引
- `docs/README.md` - 文档入口
- `README.md` - 项目根README
- 其他报告文件中的交叉引用

**批量更新命令** (PowerShell):

```powershell
# 更新所有md文件中的引用
$replacements = @{
    "second_structure_optimization_diagnosis.md" = "second_structure_optimization_diagnosis.md"
    "second_structure_optimization_delivery.md" = "second_structure_optimization_delivery.md"
    "backend_second_convergence_report.md" = "backend_second_convergence_report.md"
    "frontend_second_optimization_report.md" = "frontend_second_optimization_report.md"
    "documentation_second_governance_report.md" = "documentation_second_governance_report.md"
    "script_entry_unification_report.md" = "script_entry_unification_report.md"
    "restrained_structure_optimization_report.md" = "restrained_structure_optimization_report.md"
    "repository_cleanup_report.md" = "repository_cleanup_report.md"
    "repository_cleanup_changelog.md" = "repository_cleanup_changelog.md"
    "same_function_file_integration_analysis.md" = "same_function_file_integration_analysis.md"
    "cross_platform_consistency_audit.md" = "cross_platform_consistency_audit.md"
    "code_slimming_redundancy_cleanup.md" = "code_slimming_redundancy_cleanup.md"
    "代码重复分析.md" = "code_duplication_analysis.md"
    "type_constant_deduplication_analysis.md" = "type_constant_deduplication_analysis.md"
    "frontend_cleanup_completion_report.md" = "frontend_cleanup_completion_report.md"
    "page_permission_mapping.md" = "page_permission_mapping.md"
    "project_complete_directory_tree.md" = "project_complete_directory_tree.md"
}

# 遍历所有md文件并替换
Get-ChildItem -Path . -Recurse -Filter *.md | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    $modified = $false
    
    foreach ($old in $replacements.Keys) {
        $new = $replacements[$old]
        if ($content -match [regex]::Escape($old)) {
            $content = $content -replace [regex]::Escape($old), $new
            $modified = $true
        }
    }
    
    if ($modified) {
        Set-Content -Path $_.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "Updated: $($_.FullName)"
    }
}
```

---

## ✅ 验证清单

### 重命名后验证

```bash
# 1. 验证所有文件已重命名
ls docs/reports/*.md | Select-String "[\u4e00-\u9fa5]"
# 预期输出: 无结果（无中文文件名）

# 2. 验证Git历史保留
git log --follow docs/reports/second_structure_optimization_diagnosis.md
# 预期输出: 包含原文件的完整提交历史

# 3. 验证链接可达性
# 检查所有md文件中的链接
Get-ChildItem -Path docs -Recurse -Filter *.md | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $links = [regex]::Matches($content, '\[.*?\]\((.*?\.md)\)')
    foreach ($link in $links) {
        $target = $link.Groups[1].Value
        if (-not (Test-Path (Join-Path (Split-Path $_.FullName) $target))) {
            Write-Host "Broken link in $($_.Name): $target"
        }
    }
}
# 预期输出: 无断链

# 4. 构建测试（确保没有引用错误）
cd backend && python -c "import app.main; print('OK')"
cd frontend && npm run build
```

---

## 🔄 回滚方案

如果重命名后出现问题，可以快速回滚：

```bash
# 方法1: 使用Git回退单个commit
git log --oneline -1  # 获取最新提交哈希
git revert <commit_hash>

# 方法2: 重置到重命名前
git reset --hard HEAD~1

# 方法3: 手动恢复单个文件
git checkout HEAD~1 -- "docs/reports/second_structure_optimization_diagnosis.md"
```

---

## 📊 影响范围评估

### 受影响的文件统计

| 类型 | 数量 | 说明 |
|-----|------|------|
| **需重命名** | 17个 | docs/reports/中的中文文件名 |
| **需更新引用** | ~30个 | 包含这些文件链接的md文件 |
| **外部引用** | 0个 | 无外部系统依赖这些文件名 |

### 风险评估

| 风险项 | 等级 | 缓解措施 |
|--------|------|---------|
| **断链风险** | 🟡 中 | 批量更新所有引用 + 验证脚本 |
| **Git历史丢失** | 🟢 低 | 使用`git mv`保留历史 |
| **IDE缓存问题** | 🟢 低 | 重启IDE即可 |
| **回滚复杂度** | 🟢 低 | 单个commit可快速回退 |

---

## 📝 命名规范指引（未来参考）

### 推荐命名格式

```
{类型}_{主题}_{子类型}.md

类型:
  - report: 报告
  - guide: 指南
  - analysis: 分析
  - reference: 参考
  - changelog: 变更日志

主题:
  - backend: 后端
  - frontend: 前端
  - documentation: 文档
  - structure: 结构
  - optimization: 优化

示例:
  - report_backend_optimization.md
  - guide_development_setup.md
  - analysis_code_duplication.md
```

### 避免的命名方式

- ❌ 中文文件名
- ❌ 空格 (使用下划线代替)
- ❌ 特殊字符 (仅使用 a-z, 0-9, _, -)
- ❌ 过长文件名 (建议 < 50 字符)
- ❌ 大写字母 (统一小写)

---

## 🎯 执行时机建议

**推荐时机**: 
- ✅ 在无活跃开发分支时执行
- ✅ 所有团队成员同步后执行
- ✅ 提前通知团队成员即将重命名

**不推荐时机**:
- ❌ 有未合并的PR时
- ❌ 正在进行大型功能开发时
- ❌ 临近重要发布节点时

---

## ✅ 批准检查表

执行前确认：

- [ ] 所有团队成员已提交本地更改
- [ ] 无未合并的PR引用这些文件
- [ ] 已备份当前分支（创建备份标签）
- [ ] 已准备好回滚方案
- [ ] 已测试批量替换脚本
- [ ] 已通知所有团队成员

---

**准备就绪后，执行以下命令开始重命名**:

```bash
# 1. 创建备份标签
git tag -a backup-before-rename -m "Backup before md file renaming"

# 2. 执行重命名脚本（见阶段1）

# 3. 执行引用更新脚本（见阶段2）

# 4. 验证（见验证清单）

# 5. 提交变更
git add -A
git commit -m "docs: 规范化所有md文件命名为snake_case英文格式

- 重命名17个中文命名的md文件为snake_case英文格式
- 更新所有文档中的交叉引用
- 保留Git历史（使用git mv）
- 提升跨平台兼容性和可维护性"

# 6. 推送（谨慎）
git push origin main
git push origin backup-before-rename
```

---

**报告结束**
