# FIDD-Bench 接口文档

本文档主要定义系统内部模块间的交互接口，特别是 **LLM 解析层** 与 **数据生成层** 之间的配置协议，以及 **CLI 参数** 规范。

## 1. 内部配置协议 (Internal Configuration Protocol)

这是 LLM 解析用户自然语言后，传递给 Python 生成引擎的 JSON 数据结构。

### 1.1 生成配置 (Generation Config)

*   **描述**: 定义数据集的统计特征和结构。
*   **数据结构**: JSON Object

#### 请求结构 (JSON Schema)

```json
{
  "dataset_meta": {
    "num_transactions": "Integer (Required, e.g., 10000)",
    "num_items": "Integer (Required, e.g., 500)",
    "density": "Float (Optional, 0.0-1.0, default: 0.1)",
    "avg_transaction_len": "Integer (Optional)"
  },
  "distribution_config": {
    "method": "String (Enum: 'random', 'normal', 'zipf', 'exponential')",
    "params": {
      "alpha": "Float (For zipf)",
      "mean": "Float (For normal)",
      "std": "Float (For normal)"
    }
  },
  "pattern_injection": [
    {
      "id": "String (Pattern Identifier)",
      "items": "List<Integer> (e.g., [1, 5, 10])",
      "target_support": "Float (0.0-1.0)",
      "noise_ratio": "Float (Optional, 0.0-1.0, probability of item missing in pattern instance)"
    }
  ]
}
```

#### 字段说明
*   `dataset_meta.density`: 数据集的稀疏程度。
*   `distribution_config.method`: 物品出现的频率分布。`zipf` 常用于模拟长尾分布（如真实销售数据）。
*   `pattern_injection`: 定义需要强制植入的“基准真值”。

## 2. 命令行接口 (CLI Interface)

### 2.1 主程序入口 `main.py`

#### 命令格式
```bash
python src/main.py [OPTIONS] COMMAND [ARGS]...
```

#### 常用参数 (Options)

| 参数 | 简写 | 类型 | 必填 | 说明 | 示例 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `--prompt` | `-p` | String | 是 | 自然语言描述 | `"生成超市数据"` |
| `--output` | `-o` | Path | 否 | 输出文件路径 | `./data/out.spmf` |
| `--config` | `-c` | Path | 否 | 直接使用JSON配置(跳过LLM) | `./config.json` |
| `--benchmark`| `-b` | Flag | 否 | 生成后是否立即运行基准测试 | (无值) |
| `--algo` | `-a` | String | 否 | 指定基准测试算法 | `Apriori`, `FPGrowth` |

### 2.2 状态码 (Exit Codes)

*   `0`: 成功 (Success)
*   `1`: 通用错误 (General Error)
*   `2`: 参数错误 (Invalid Arguments)
*   `3`: LLM API 连接失败 (LLM Connection Error)
*   `4`: 外部工具调用失败 (External Tool Error, e.g., Java not found)

## 3. 认证方式 (Authentication)

### 3.1 LLM API 认证
系统不应在代码中硬编码 API Key。

*   **方式**: 环境变量 (Environment Variables)
*   **变量名**:
    *   `OPENAI_API_KEY`: 用于 OpenAI 模型。
    *   `HUGGINGFACE_API_TOKEN`: 用于 HuggingFace 模型。

**配置示例 (.env 文件)**:
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
SPMF_JAR_PATH=./lib/spmf.jar
```
