# MkDocs 文档在线部署指南

## 📚 概述

您的 MkDocs 文档将部署到 **GitHub Pages**，访问地址：
```
https://centerforthebuiltenvironment.github.io/HHW_brick/
```

## ✅ 已完成的配置

### 1. 更新 mkdocs.yml
```yaml
site_url: https://centerforthebuiltenvironment.github.io/HHW_brick/
```

### 2. GitHub Actions 自动部署
文件：`.github/workflows/docs.yml`

**工作流程**：
- 每次推送到 `main` 分支时自动触发
- 自动构建 MkDocs 文档
- 自动部署到 GitHub Pages

---

## 🚀 部署步骤

### 步骤 1: 提交更改

```bash
# 添加修改的文件
git add mkdocs.yml .github/workflows/docs.yml

# 提交
git commit -m "docs: configure MkDocs for GitHub Pages deployment"

# 推送到 GitHub
git push origin main
```

### 步骤 2: 启用 GitHub Pages

1. **访问仓库设置**：
   https://github.com/CenterForTheBuiltEnvironment/HHW_brick/settings/pages

2. **配置 GitHub Pages**：
   - **Source**: 选择 `gh-pages` 分支
   - **Folder**: `/ (root)`
   - 点击 **Save**

3. **等待部署** (约 1-2 分钟)

### 步骤 3: 验证部署

访问文档网站：
```
https://centerforthebuiltenvironment.github.io/HHW_brick/
```

---

## 📋 部署检查清单

### GitHub Actions 检查
- [ ] 访问 https://github.com/CenterForTheBuiltEnvironment/HHW_brick/actions
- [ ] 确认 "Deploy Documentation" 工作流运行成功 ✅
- [ ] 查看日志确认无错误

### GitHub Pages 检查
- [ ] 访问 Settings → Pages
- [ ] 确认显示 "Your site is published at..."
- [ ] 点击链接访问文档网站
- [ ] 确认文档正常显示

---

## 🔄 自动更新流程

### 文档更新后自动发布

1. **编辑文档**：
   ```bash
   # 编辑 docs/ 下的任何 .md 文件
   vim docs/user-guide/index.md
   ```

2. **提交并推送**：
   ```bash
   git add docs/
   git commit -m "docs: update user guide"
   git push origin main
   ```

3. **自动部署**：
   - GitHub Actions 自动触发
   - 约 1-2 分钟后文档网站自动更新

### 本地预览

```bash
# 安装 MkDocs (如果还没安装)
pip install mkdocs mkdocs-material mkdocs-include-markdown-plugin

# 本地预览
mkdocs serve

# 访问 http://127.0.0.1:8000
```

---

## 🎨 自定义域名 (可选)

### 使用自定义域名

1. **添加 CNAME 文件**：
   ```bash
   # 在 docs/ 目录下创建 CNAME 文件
   echo "docs.your-domain.com" > docs/CNAME
   ```

2. **配置 DNS**：
   在您的域名提供商添加 CNAME 记录：
   ```
   docs.your-domain.com → centerforthebuiltenvironment.github.io
   ```

3. **GitHub 设置**：
   - Settings → Pages → Custom domain
   - 输入 `docs.your-domain.com`
   - 勾选 "Enforce HTTPS"

---

## 🔧 常见问题

### 问题 1: 404 错误
**原因**: GitHub Pages 未正确配置

**解决**:
1. 检查 Settings → Pages 是否选择了 `gh-pages` 分支
2. 等待 2-3 分钟让 GitHub 构建完成
3. 清除浏览器缓存

### 问题 2: 样式丢失
**原因**: `site_url` 配置错误

**解决**:
确保 `mkdocs.yml` 中：
```yaml
site_url: https://centerforthebuiltenvironment.github.io/HHW_brick/
```

### 问题 3: 部署失败
**原因**: 依赖安装失败

**解决**:
检查 `.github/workflows/docs.yml` 中的依赖版本：
```yaml
pip install mkdocs>=1.4.0 mkdocs-material>=9.0.0 mkdocs-include-markdown-plugin>=6.0.0
```

---

## 📊 部署状态徽章

在 README.md 中添加部署状态徽章：

```markdown
[![Documentation](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/actions/workflows/docs.yml/badge.svg)](https://centerforthebuiltenvironment.github.io/HHW_brick/)
```

效果：
[![Documentation](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/actions/workflows/docs.yml/badge.svg)](https://centerforthebuiltenvironment.github.io/HHW_brick/)

---

## 🎯 最佳实践

### 1. 文档结构
```
docs/
├── index.md              # 首页
├── getting-started/      # 入门指南
├── user-guide/           # 用户指南
├── api-reference/        # API 参考
└── developer-guide/      # 开发者指南
```

### 2. 版本控制
```bash
# 为文档添加版本标签
git tag -a v0.1.0-docs -m "Documentation for v0.1.0"
git push origin v0.1.0-docs
```

### 3. 定期更新
- 每次发布新版本时更新文档
- 添加 CHANGELOG 到文档
- 更新示例代码

---

## 📞 需要帮助？

### 资源链接
- **MkDocs 官方文档**: https://www.mkdocs.org/
- **Material 主题文档**: https://squidfunk.github.io/mkdocs-material/
- **GitHub Pages 文档**: https://docs.github.com/en/pages

### 快速命令

```bash
# 本地构建
mkdocs build

# 本地预览
mkdocs serve

# 手动部署 (通常不需要，GitHub Actions 会自动处理)
mkdocs gh-deploy

# 查看帮助
mkdocs --help
```

---

## ✨ 完成！

执行步骤 1（提交并推送），然后在 GitHub 设置中启用 Pages，您的文档就会上线了！

**预期地址**：
https://centerforthebuiltenvironment.github.io/HHW_brick/

**预计部署时间**: 2-3 分钟
