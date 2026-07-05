# Tooling

本目录统一承载项目脚本，替代旧的 `scripts/` 与 `qa_scripts/` 双目录。

```text
tooling/
├─ dev/                    # 本地开发启动脚本
├─ qa/                     # 检查、诊断、冒烟和验收脚本
└─ api/                    # 后端数据初始化、维护、归档工具
```

常用命令：

```bash
python tooling/qa/verifications/system/verify_system_integrity.py
python tooling/api/seed_data.py
python tooling/api/generate_bulk_data.py
python tooling/api/clean_bulk_data.py
```

完整说明见 `docs/qa/scripts.md`。
