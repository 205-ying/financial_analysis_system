# 项目文档索引

本目录包含财务分析系统的核心文档。

> 📁 **历史文档已归档**: 各阶段交付文档已移至 [archive/](archive/) 目录

---

## 📁 核心文档

### 🏗️ 架构设计
- [backend_structure.md](backend_structure.md) - **后端架构说明** ⭐
- [frontend_structure.md](frontend_structure.md) - **前端架构说明** ⭐
- [naming_conventions.md](naming_conventions.md) - 命名规范
- [backend_refactoring_guide.md](backend_refactoring_guide.md) - Backend重构指南

### 📖 开发指南
- [development_guide.md](development_guide.md) - **开发指南** ⭐ （包含启动说明）
- [development_roadmap.md](development_roadmap.md) - 开发路线图
- [dependency_guide.md](dependency_guide.md) - 依赖管理指南

### 📚 项目历程
- [project_history.md](project_history.md) - **项目开发历程** ⭐
  - Stage 2-11 各阶段技术总结
  - 完整技术栈说明
  - 核心功能实现要点

### ✅ 验证报告
- [system_verification_report_final.md](system_verification_report_final.md) - **系统最终验证报告** ⭐
  - 57/57 项测试通过（100%）
  - 生产就绪状态确认

### 📊 优化报告
- [optimization_complete.md](optimization_complete.md) - **项目整体优化完成总结** ⭐
- [file_naming_normalization_report.md](file_naming_normalization_report.md) - **文件命名规范化与引用修复报告** ⭐
- [project_structure_optimization_report.md](project_structure_optimization_report.md) - 整体结构优化详细报告（含后端、前端、整体三阶段）
- [frontend_optimization_report.md](frontend_optimization_report.md) - 前端优化详细报告

### 📄 最新功能交付（已归档）
详细的功能交付文档已移至 [archive/](archive/) 目录：
- Stage 9: 门店级数据权限 ([store_level_data_scope_delivery.md](archive/store_level_data_scope_delivery.md))
- Stage 10: 数据导入中心 ([data_import_*.md](archive/))
- Stage 11: 报表中心 ([reports_*.md](archive/))

---

## 📦 归档文档

### [archive/](archive/) 目录内容

包含各开发阶段的详细交付文档：

#### 阶段交付文档（26个）
- **交付文档**: stage2-8_delivery.md - 各阶段功能交付说明
- **测试文档**: stage3-7_test.md - 阶段测试计划和用例
- **验证文档**: stage6_verification_report.md, stage6_final_verification.md
- **部署文档**: stage7_deployment.md - 生产部署指南
- **Stage 9-11 交付**: 门店数据权限、数据导入中心、报表中心完整交付文档

详细的阶段技术总结请查看 [project_history.md](project_history.md)。

> 💡 **提示**: 归档文档主要用于历史参考，新开发者关注核心文档即可。

---

## 📋 文档命名规范

### 核心文档
- **小写字母** + **下划线分隔**
- 描述性命名：`{功能}_{类型}.md`
- 示例：`backend_structure.md`, `development_guide.md`

### 归档文档
- 保持原有命名
- 阶段文档：`stage{N}_{type}.md`

---

## 📌 快速导航

### 新手入门
1. 阅读 [development_guide.md](development_guide.md) 了解项目启动和开发流程
2. 查看 [project_history.md](project_history.md) 了解项目发展历程
3. 参考 [naming_conventions.md](naming_conventions.md) 了解代码规范

### 架构了解
1. [backend_structure.md](backend_structure.md) - 后端分层架构
2. [frontend_structure.md](frontend_structure.md) - 前端组件结构

### 系统验证
- [system_verification_report_final.md](system_verification_report_final.md) - 完整的系统验证报告

---

**最后更新**: 2026年1月24日
