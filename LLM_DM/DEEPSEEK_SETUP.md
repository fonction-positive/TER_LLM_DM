# 使用 DeepSeek API 指南

## 为什么选择 DeepSeek？

- 💰 **性价比高**：比 OpenAI 便宜很多
- 🇨🇳 **中文友好**：对中文支持更好
- ⚡ **速度快**：响应速度较快
- 🔌 **兼容性好**：使用 OpenAI 兼容的 API 接口

## 配置步骤

### 1. 获取 DeepSeek API Key

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册账号并登录
3. 进入 API Keys 页面创建新的 API Key
4. 复制你的 API Key

### 2. 配置环境变量

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```bash
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your-actual-deepseek-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 更新配置文件（可选）

如果你想默认使用 DeepSeek，编辑 `config/settings.yaml`：

```yaml
llm:
  provider: "deepseek"  # 使用 deepseek
  model: "deepseek-chat"
  temperature: 0.3
  max_tokens: 2000
  timeout: 30
```

## 使用方式

### 方式 1：通过配置文件（推荐）

如果已经在 `config/settings.yaml` 中设置了 `provider: "deepseek"`，直接运行：

```bash
python src/main.py generate \
  --prompt "生成1000条超市交易记录" \
  --output data/processed/dataset.spmf
```

### 方式 2：通过代码指定

在 Python 代码中明确指定使用 DeepSeek：

```python
from llm.client import LLMClient

# 使用 DeepSeek
client = LLMClient(
    provider="deepseek",
    model="deepseek-chat",
    temperature=0.3
)

config = client.generate_config("生成1000条交易记录，100种商品")
print(config)
```

### 方式 3：临时切换

你也可以保持配置文件不变，通过环境变量临时切换：

```bash
# 临时使用 DeepSeek
export LLM_PROVIDER=deepseek
python src/main.py generate --prompt "..." --output data.spmf
```

## DeepSeek 模型选择

DeepSeek 提供多个模型：

| 模型名称 | 说明 | 适用场景 |
|---------|------|---------|
| `deepseek-chat` | 通用对话模型 | 本项目推荐使用 |
| `deepseek-coder` | 代码生成模型 | 如果生成代码配置 |

## 价格对比（仅供参考）

| 提供商 | 输入价格 | 输出价格 |
|-------|---------|---------|
| OpenAI GPT-4o-mini | $0.15/1M tokens | $0.60/1M tokens |
| DeepSeek Chat | ¥1/1M tokens | ¥2/1M tokens |

💡 **DeepSeek 约为 OpenAI 价格的 1/10**

## 完整示例

### 1. 配置 .env

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 2. 生成数据集

```bash
python src/main.py generate \
  --prompt "生成2000条零售交易数据，包含150种商品，使用Zipf分布，注入3个频繁模式" \
  --output data/processed/retail_deepseek.spmf \
  --stats
```

### 3. 运行基准测试

```bash
python src/main.py full-pipeline \
  --prompt "稀疏型电商数据，1000笔交易" \
  --algorithms Apriori FPGrowth \
  --min-support 0.05
```

## 注意事项

1. **JSON 格式输出**：DeepSeek 支持 OpenAI 的 `response_format` 参数，可以强制返回 JSON
2. **速率限制**：注意 API 的速率限制，避免请求过快
3. **兼容性**：由于使用 OpenAI 兼容接口，所有 OpenAI 的功能都支持

## 故障排查

### 问题 1: API Key 无效

```
ValueError: DEEPSEEK_API_KEY not found in environment variables
```

**解决方案**：
- 检查 `.env` 文件是否正确配置
- 确保 API Key 没有多余的空格
- 重新加载环境变量

### 问题 2: 连接失败

```
Exception: LLM API call failed: Connection error
```

**解决方案**：
- 检查网络连接
- 确认 `DEEPSEEK_BASE_URL` 是否正确
- 检查是否需要代理

### 问题 3: 响应格式错误

```
ValueError: LLM returned invalid JSON
```

**解决方案**：
- DeepSeek 已支持 JSON 模式，但偶尔可能失败
- 可以降低 `temperature` 参数（更确定性）
- 检查 Prompt 是否清晰

## 性能优化建议

1. **调整温度**：`temperature=0.2` 可以获得更稳定的结果
2. **减少 tokens**：`max_tokens=1500` 对于配置生成已足够
3. **批量处理**：如果需要生成多个数据集，可以批量请求

## 与 OpenAI 切换

如果需要切换回 OpenAI，只需修改 `config/settings.yaml`：

```yaml
llm:
  provider: "openai"
  model: "gpt-4o-mini"
```

或在代码中指定：

```python
client = LLMClient(provider="openai")
```

---

**Happy Data Mining with DeepSeek! 🚀**
