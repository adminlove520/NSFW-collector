# 更新日志

## [v1.0.0] - 2025-12-15

### 新增功能

1. **基础爬虫功能**
   - 实现了 wm.wmhuu.com 网站的爬虫框架
   - 支持图片和小说两种采集模式
   - 支持多个子版块的并行爬取

2. **每日模式**
   - 添加了 `--daily` 命令行参数，支持仅采集当日数据
   - 当日数据保存到 `./picture/daily_YYYY-MM-DD/` 和 `./novel/daily_YYYY-MM-DD/` 目录
   - 通过正则表达式 `\[(\d{2}-\d{2})\]` 匹配帖子标题中的日期

3. **配置管理**
   - 支持通过 `config.yaml` 进行本地配置
   - 支持通过 GitHub Workflow 输入参数进行配置
   - 支持 `site_domain.yaml` 配置多个备选域名

4. **GitHub Actions 工作流**
   - 实现了手动触发和定时执行的工作流
   - 支持选择采集模式和每日模式
   - 默认每日模式为 true
   - 配置了每日凌晨自动执行

5. **健壮性设计**
   - 实现了请求重试机制
   - 支持代理配置和自动禁用
   - 完善的错误处理和日志输出

### 修复的问题

1. **代理错误处理**
   - 修复了 `ProxyError` 引用错误（`requests.ProxyError` → `requests.exceptions.ProxyError`）
   - 添加了代理自动禁用逻辑

2. **域名配置**
   - 实现了简化的域名选择逻辑，避免复杂的测速问题
   - 支持从 `site_domain.yaml` 读取多个备选域名

3. **路径处理**
   - 修复了保存路径的构建问题
   - 支持 Windows 和 Linux 路径格式

### 技术栈

- Python 3.10+
- requests 库用于网络请求
- BeautifulSoup4 用于 HTML 解析
- PyYAML 用于配置文件处理
- argparse 用于命令行参数解析
- GitHub Actions 用于持续集成

## 后续计划

1. 实现分布式爬取
2. 添加更多的内容类型支持
3. 实现数据去重功能
4. 添加更详细的日志记录
5. 支持更多的配置选项
6. 实现 GUI 界面
