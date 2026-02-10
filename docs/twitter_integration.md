# Twitter AI 资讯功能使用说明

## 功能概述

GitHubSentinel 现在支持从 Twitter 获取最新的 AI 相关资讯。系统会自动抓取与人工智能相关的推文，并使用大语言模型生成分析报告，帮助您快速了解 AI 领域的最新动态和趋势。

## 配置说明

### 1. 获取 Twitter API Bearer Token

要使用 Twitter API，您需要：

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/)
2. 创建一个新的应用或使用现有应用
3. 在应用的 "Keys and tokens" 页面中获取 Bearer Token

### 2. 配置 config.json

在 `config.json` 文件中添加 Twitter 配置：

```json
{
    "twitter": {
        "bearer_token": "your_twitter_bearer_token"
    },
    "report_types": [
        "github",
        "hacker_news_hours_topic",
        "hacker_news_daily_report",
        "twitter_ai_news"
    ]
}
```

**出于安全考虑**：推荐使用环境变量配置 Twitter Bearer Token：

```bash
export TWITTER_BEARER_TOKEN="your_bearer_token_here"
```

## 使用方法

### 1. 通过 Gradio Web 界面使用

启动 Gradio 服务器：

```bash
python src/gradio_server.py
```

在浏览器中访问 `http://localhost:7860`，选择 "Twitter AI 资讯" 标签页：

1. 选择模型类型（OpenAI 或 Ollama）
2. 选择具体的模型名称
3. 设置要获取的推文数量（10-100条）
4. 点击 "生成AI资讯报告" 按钮

系统将自动：
- 从 Twitter 获取最新的 AI 相关推文
- 使用 LLM 分析并生成报告
- 显示报告内容并提供下载

### 2. 直接使用 Python 代码

```python
from src.twitter_client import TwitterClient
from src.config import Config
from src.llm import LLM
from src.report_generator import ReportGenerator

# 初始化配置和客户端
config = Config()
twitter_client = TwitterClient(config.twitter_bearer_token)

# 获取 AI 推文并导出
markdown_file = twitter_client.export_ai_tweets(max_results=50)

# 生成报告
llm = LLM(config)
report_generator = ReportGenerator(llm, config.report_types)
report, report_file = report_generator.generate_twitter_ai_report(markdown_file)

print(f"报告已生成：{report_file}")
```

## 功能特点

### 搜索关键词

系统会搜索包含以下关键词的推文：
- AI
- Artificial Intelligence
- Machine Learning
- Deep Learning
- LLM
- GPT
- 人工智能
- 机器学习
- 深度学习

### 推文过滤

- 排除转发（Retweet）内容
- 支持英文和中文推文
- 按相关性排序

### 报告内容

生成的报告包含：
- 5个最重要的 AI 热点话题或趋势
- 每个话题的详细分析
- 相关推文的原始链接
- 推文互动数据（点赞、回复、转发）

## 文件组织

Twitter AI 资讯相关文件按以下结构组织：

```
twitter_ai_news/
├── 2024-01-01/
│   ├── 12.md          # 原始推文数据
│   └── 12_report.md   # 生成的分析报告
├── 2024-01-02/
│   ├── 14.md
│   └── 14_report.md
...
```

## 注意事项

1. **API 限制**：Twitter API 有速率限制，请合理控制请求频率
2. **Token 安全**：不要将 Bearer Token 提交到代码仓库，使用环境变量或安全存储
3. **网络连接**：需要稳定的网络连接才能访问 Twitter API
4. **语言模型**：报告质量取决于所选的语言模型性能

## 故障排查

### 无法获取推文

- 检查 Bearer Token 是否正确配置
- 确认网络连接正常
- 查看日志文件了解详细错误信息

### 报告生成失败

- 确认 LLM 配置正确（OpenAI API Key 或 Ollama 服务）
- 检查 prompt 文件是否存在
- 查看日志了解具体错误

## 扩展与自定义

您可以通过修改以下文件来自定义功能：

1. **搜索查询**：编辑 `src/twitter_client.py` 中的 `fetch_ai_tweets` 方法
2. **报告模板**：编辑 `prompts/twitter_ai_news_ollama_prompt.txt` 和 `prompts/twitter_ai_news_openai_prompt.txt`
3. **推文数量**：在调用时设置 `max_results` 参数（最大 100）
