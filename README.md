# 涩涩-collector

一个涩涩采集器，支持图片和小说两种采集模式，并提供每日模式选项。

## 功能特性

### 采集模式
- **图片模式**：采集指定版块的图片内容，支持子版块：
  - gif動圖 (ID: 33)
  - 亞洲激情 (ID: 29)
  - 露出清纯 (ID: 30)
  - 歐美性愛 (ID: 31)
  - 卡通動漫 (ID: 32)

- **小说模式**：采集指定版块的小说内容，支持子版块：
  - 人妻熟女 (ID: 24)
  - 經典激情 (ID: 28)
  - 家庭亂倫 (ID: 26)
  - 武俠玄幻 (ID: 35)
  - 學生校園 (ID: 27)

### 每日模式
- 支持 `--daily` 选项，仅采集当日发布的内容
- 当日数据保存在 `./picture/daily_YYYY-MM-DD/` 和 `./novel/daily_YYYY-MM-DD/` 目录
- 自动根据帖子标题中的日期标识 `[MM-DD]` 进行筛选

### 配置灵活性
- 支持通过 `config.yaml` 本地配置
- 支持通过 GitHub Workflow 输入参数配置
- 支持多个备选域名配置 (`site_domain.yaml`)
- 可配置请求头、超时、延迟和重试次数

## 安装依赖

```bash
pip install requests beautifulsoup4 pyyaml
```

## 使用方法

### 命令行运行

```bash
# 运行图片采集模式
python main.py --mode picture

# 运行小说采集模式
python main.py --mode novel

# 运行每日图片采集模式
python main.py --mode picture --daily

# 运行每日小说采集模式
python main.py --mode novel --daily

# 指定配置文件
python main.py --mode picture --config my_config.yaml
```

### 配置文件说明

#### config.yaml

```yaml
crawl:
  max_pages: 10         # 每个版块最大爬取页数
  retry_times: 3        # 请求失败重试次数
crawl_mode: picture     # 默认采集模式

# 小说版块配置
novel_forums:
- id: 24
  name: 人妻熟女
- id: 28
  name: 經典激情
- id: 26
  name: 家庭亂倫
- id: 35
  name: 武俠玄幻
- id: 27
  name: 學生校園

# 图片版块配置
picture_forums:
- id: 33
  name: gif動圖
- id: 29
  name: 亞洲激情
- id: 30
  name: 露出清纯
- id: 31
  name: 歐美性愛
- id: 32
  name: 卡通動漫

request:
  delay: 1              # 请求延迟（秒）
  headers:              # 请求头
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
  proxies:              # 代理配置
    http: null
    https: null
  timeout: 10           # 请求超时（秒）

save_paths:
  novel: ./novel        # 小说保存路径
  picture: ./picture    # 图片保存路径

site_domain: wm.wmhuu.com  # 网站域名
```

#### site_domain.yaml（可选）

```yaml
site_domains:
  - wm.wmhuu.com
  - backup.wmhuu.com
```

## GitHub Actions 工作流

### 手动触发

通过 GitHub Actions 手动触发工作流时，可以选择以下参数：

- **crawl_mode**：采集模式，可选值：picture、novel
- **daily_mode**：是否仅采集当日数据，默认值：true

### 定时执行

工作流配置了每日凌晨自动执行，默认使用每日模式采集图片。

## 项目结构

```
getSeSe/
├── main.py                # 主程序入口
├── config.yaml            # 主配置文件
├── site_domain.yaml       # 域名配置文件
├── .github/workflows/
│   └── crawler.yml        # GitHub Actions 工作流
├── utils/
│   ├── request.py         # 请求处理模块
│   ├── parser.py          # HTML 解析模块
│   └── saver.py           # 内容保存模块
├── picture/               # 图片保存目录
├── novel/                 # 小说保存目录
└── README.md              # 项目说明文档
```

## 注意事项

1. 请遵守网站的 robots.txt 规则，合理设置爬取间隔
2. 大量爬取可能导致 IP 被封禁，建议使用代理
3. 本程序仅供学习和研究使用，请勿用于商业用途
4. 定期检查并更新域名配置，以确保爬虫正常运行

## 许可证

MIT License
