#!/bin/bash
# 自动化发布脚本

set -e

# 检查是否有未提交的更改
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ 有未提交的更改，请先提交所有更改"
    exit 1
fi

# 获取当前版本
current_version=$(python -c "import tomllib; f=open('pyproject.toml','rb'); data=tomllib.load(f); f.close(); print(data['project']['version'])")
echo "当前版本: $current_version"

# 询问新版本
read -p "输入新版本号 (当前: $current_version): " new_version

if [[ -z "$new_version" ]]; then
    echo "❌ 版本号不能为空"
    exit 1
fi

# 更新 pyproject.toml 中的版本号
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i "" "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml
else
    # Linux
    sed -i "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml
fi

echo "✅ 版本号已更新为: $new_version"

# 提交版本更改
git add pyproject.toml
git commit -m "🔖 Bump version to $new_version"

# 创建并推送标签
git tag "v$new_version"
git push origin main
git push origin "v$new_version"

echo "🚀 版本 $new_version 发布流程已启动！"
echo "   GitHub Actions 将自动构建并发布到 PyPI"
echo "   查看进度: https://github.com/langlink-localization/xliff-mcp-server/actions"