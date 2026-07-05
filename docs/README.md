# 文档中心

本目录是项目级说明文档的统一入口。根目录 `README.md` 只保留快速开始和常用导航，具体开发、架构、API 和 QA 说明集中放在这里。

## 文档地图

### 架构

- `architecture/project-structure.md`：项目目录、前后端分层、文档和脚本归位规则

### 开发

- `development.md`：本地开发、依赖、运行时文件、启动、迁移、测试、排障和提交前检查

### 业务扩展

- `finance-expansion-roadmap.md`：财务系统扩展功能清单、成熟度与下一阶段建设建议

### API

- `api/backend-api.md`：后端 API 导出文档
- `api/openapi-baseline.json`：OpenAPI 基线快照

### QA

- `qa.md`：QA 脚本分类、命名规则、运行方式和性能基线采集说明

## 维护规则

- 项目级长期文档放在 `docs/`。
- 业务模块附近只保留必要的短 README，并链接回文档中心。
- 自动生成文档需要在文件顶部注明生成方式。
- 文档路径调整后，同步更新根 `README.md` 和 `tooling/qa/verifications/system/verify_system_integrity.py`。
