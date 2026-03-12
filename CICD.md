# CI/CD 自动发布配置

本项目已配置 GitHub Actions 实现自动化测试和发布。

## 🚀 自动发布流程

### 1. 配置 PyPI Trusted Publishing

本仓库使用 **PyPI Trusted Publishing**，不再需要长期保存的 `PYPI_API_TOKEN`。

首次配置时，在 PyPI 项目页中添加一个 Trusted Publisher：

1. 打开 PyPI 项目设置中的 Publishing 配置
2. 添加 GitHub Actions publisher
3. 填写：
   - **Owner**: `langlink-localization`
   - **Repository name**: `xliff-mcp-server`
   - **Workflow name**: `publish-to-pypi.yml`
   - **Environment name**: `pypi`
4. 保存后，GitHub Actions 即可通过 OIDC 发布，无需仓库 secret

### 2. 发布新版本

使用自动化脚本发布：

```bash
./release.sh
```

或手动步骤：

```bash
# 1. 更新版本号（在 pyproject.toml 中）
# 2. 提交更改
git add .
git commit -m "🔖 Bump version to x.y.z"

# 3. 创建版本标签
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

### 3. 自动化流程说明

**触发条件**: 推送版本标签（如 `v1.0.0`）

**自动执行**:
1. ✅ 运行测试
2. 🏗️ 构建 Python 包
3. ✅ 验证包格式
4. 🚀 使用 Trusted Publishing 自动发布到 PyPI

## 🧪 持续测试

每次推送到 `main` 分支或创建 PR 时自动运行：

- 多 Python 版本测试 (3.10, 3.11, 3.12)
- 包构建测试
- 安装测试

## 📦 发布后

发布成功后，用户可以通过以下方式使用：

### Claude Desktop MCP 配置

```json
{
  "mcpServers": {
    "xliff-mcp": {
      "command": "uvx",
      "args": ["xliff-mcp-server"]
    }
  }
}
```

### 或使用 pipx

```json
{
  "mcpServers": {
    "xliff-mcp": {
      "command": "pipx",
      "args": ["run", "xliff-mcp-server"]
    }
  }
}
```

## 🔧 本地开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 本地 lint
ruff check .

# 本地测试
python -m pytest

# 冒烟验证
python test_server.py

# 本地构建
python -m build
```

## 📊 监控发布

- GitHub Actions: https://github.com/langlink-localization/xliff-mcp-server/actions
- PyPI 包页面: https://pypi.org/project/xliff-mcp-server/
- PyPI Trusted Publishing 文档: https://docs.pypi.org/trusted-publishers/using-a-publisher/
