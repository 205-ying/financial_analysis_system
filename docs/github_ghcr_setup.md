# GitHub 与 GHCR 发布检查清单

本文档用于确保首次发布 GHCR 镜像时一次成功。

## 当前仓库信息

- GitHub 仓库: 205-ying/financial_analysis_system
- 默认发布分支: main
- 默认镜像名:
  - ghcr.io/205-ying/financial-analysis-system-backend:latest
  - ghcr.io/205-ying/financial-analysis-system-frontend:latest

## 已完成的仓库内配置

- 已新增 GHCR 发布工作流 [publish-images.yml](../.github/workflows/publish-images.yml)
- 发布流程改为在 [CI 工作流](../.github/workflows/ci.yml) 成功后自动触发
- 手动触发 workflow_dispatch 仍可保留
- 镜像标签包含 latest 和 commit sha
- 镜像附带 OCI source label，便于 GHCR 关联源码仓库

## 需要在 GitHub 仓库网页检查的设置

### 1. Actions 权限

进入仓库：

- Settings
- Actions
- General

检查以下项：

- Allow all actions and reusable workflows 已开启
- Workflow permissions 设为 Read and write permissions
- Allow GitHub Actions to create and approve pull requests 可不开启，与 GHCR 无关

说明：

- 如果 Workflow permissions 仍是只读，工作流即使声明了 packages: write，也可能无法把镜像推到 GHCR。

### 2. Packages 权限

如果仓库属于个人账号，通常无需额外配置，只要 GITHUB_TOKEN 有 packages: write 即可。

如果仓库属于组织，需要额外确认：

- 组织允许 Actions 发布 package
- 组织允许仓库使用 GITHUB_TOKEN 写入 GHCR

### 3. 主分支确认

确认默认分支为 main。

说明：

- 当前工作流会在 main 上的 CI 成功后自动发布 latest。
- 其他分支只会在你手动触发时发布 sha 标签，不建议作为稳定发布来源。

### 4. 仓库可见性与镜像可见性

如果希望目标机器无需登录 GHCR 就能 docker pull，需要把 GHCR 包设为 public。

检查路径：

- GitHub 主页右上角头像
- Your packages
- 选择对应 package
- Package settings
- Change visibility

说明：

- private package 需要 docker login ghcr.io 才能拉取
- public package 可直接拉取，更适合部署机使用

## 首次发布推荐流程

1. 先把当前改动合并到 main
2. 在 GitHub 网页检查上面的 Actions 与 Packages 设置
3. 推送一个小提交到 main，触发 CI
4. 等待 CI 成功后自动触发 Publish Docker Images
5. 在 GHCR 中确认出现两个包：
   - financial-analysis-system-backend
   - financial-analysis-system-frontend
6. 复制镜像地址填入 [.env.images.example](../.env.images.example) 对应环境变量
7. 在目标机器执行 docker compose -f docker-compose.images.yml pull

## 首次发布后的验证命令

本地或部署机可执行：

```bash
docker pull ghcr.io/205-ying/financial-analysis-system-backend:latest
docker pull ghcr.io/205-ying/financial-analysis-system-frontend:latest
```

如果镜像是私有的：

```bash
docker login ghcr.io
docker pull ghcr.io/205-ying/financial-analysis-system-backend:latest
docker pull ghcr.io/205-ying/financial-analysis-system-frontend:latest
```

## 常见失败点

- Workflow permissions 仍是只读，导致 denied: permission_denied: write_package
- 包是私有的，但部署机没有先 docker login ghcr.io
- 触发分支不是 main，结果没有生成 latest 标签
- 使用了旧的镜像名，例如 your-org 占位值
- 组织策略禁止 Actions 发布 package