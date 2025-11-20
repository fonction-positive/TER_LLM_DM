# FIDD-Bench 快速入门指南

## 安装步骤

### 1. 环境要求

- Python 3.9 或更高版本
- Java 8 或更高版本（用于运行 SPMF）
- Git

### 2. 克隆项目

```bash
git clone <repository-url>
cd LLM_DM
```

### 3. 创建虚拟环境（推荐）

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini

# SPMF 配置
SPMF_JAR_PATH=./lib/spmf.jar

# Java 配置
JAVA_MEMORY_MAX=4g

# 日志级别
LOG_LEVEL=INFO
```

### 6. 下载 SPMF

访问 [SPMF 官网](https://www.philippe-fournier-viger.com/spmf/) 下载 `spmf.jar`，并放入 `lib/` 目录。

或使用命令下载：

```bash
cd lib
# 下载链接可能需要更新
wget https://www.philippe-fournier-viger.com/spmf/download.php
cd ..
```

### 7. 验证安装

运行测试：

```bash
pytest tests/ -v
```

## 基本使用

### 示例 1: 生成简单数据集

```bash
python src/main.py generate \
  --prompt "生成500条零售交易记录，包含80种商品，数据稀疏" \
  --output data/processed/retail.spmf \
  --stats
```

### 示例 2: 使用配置文件

创建配置文件 `my_config.json`：

```json
{
  "dataset_meta": {
    "num_transactions": 1000,
    "num_items": 100,
    "density": 0.12
  },
  "distribution_config": {
    "method": "zipf",
    "params": {"alpha": 1.2}
  },
  "pattern_injection": [
    {
      "items": [5, 10, 15],
      "target_support": 0.08
    }
  ]
}
```

生成数据：

```bash
python src/main.py generate \
  --config-json my_config.json \
  --output data/processed/custom.spmf
```

### 示例 3: 运行基准测试

```bash
python src/main.py benchmark \
  --input data/processed/retail.spmf \
  --algorithm Apriori \
  --min-support 0.05
```

### 示例 4: 完整流程

```bash
python src/main.py full-pipeline \
  --prompt "密集型超市数据，2000笔交易，150种商品" \
  --algorithms Apriori FPGrowth \
  --min-support 0.03
```

## 常见问题

### Q: 如何获取 OpenAI API Key？

访问 [OpenAI Platform](https://platform.openai.com/) 注册并创建 API Key。

### Q: 没有 OpenAI API Key 怎么办？

可以直接使用配置文件跳过 LLM：

```bash
python src/main.py generate --config-json config.json --output data.spmf
```

### Q: SPMF 执行失败

检查：
1. Java 是否已安装：`java -version`
2. `spmf.jar` 路径是否正确
3. `.env` 中的 `SPMF_JAR_PATH` 配置

### Q: 如何使用 Jupyter Notebook？

```bash
cd notebooks
jupyter notebook demo_generation.ipynb
```

## 下一步

- 查看 [完整文档](../documents/README_DOCS.md)
- 运行 [示例 Notebook](../notebooks/demo_generation.ipynb)
- 阅读 [技术设计文档](../documents/technical_design.md)

## 获取帮助

如有问题，请联系：
- 指导老师：Nadjib Lazaar (lazaar@lisn.fr)
- 查看 [Issues](https://github.com/your-repo/fidd-bench/issues)
