# CI/CD 自动发布配置

本项目已配置 GitHub Actions 实现自动化测试和发布。

## 🚀 自动发布流程

### 1. 配置 PyPI API Token

在 GitHub 仓库中设置 Secret：

1. 访问 https://pypi.org/manage/account/token/
2. 创建新的 API token，scope 设为 "Entire account"
3. 复制生成的 token（格式：`pypi-...`）
4. 在 GitHub 仓库中：
   - 点击 Settings -> Secrets and variables -> Actions
   - 点击 "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: 粘贴你的 PyPI token
   - 点击 "Add secret"

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
4. 🚀 自动发布到 PyPI

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
