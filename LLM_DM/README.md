# FIDD-Bench

**Flexible & Intelligent Data Generator for Data Mining Benchmarking**

一个基于大语言模型（LLM）的智能合成数据生成系统，用于评估和基准测试模式挖掘算法。

## 项目概述

FIDD-Bench 是 TER 集体项目（2025/2026）的一部分，旨在解决传统模式挖掘算法测试中的三大痛点：

1. **数据集陈旧**：传统数据集（如 FIMI Repository）大多来自20年前，缺乏多样性
2. **生成器简单**：现有随机生成器无法捕捉真实世界数据的复杂分布
3. **缺乏真值**：难以验证算法的准确率（Precision/Recall）

通过 FIDD-Bench，用户可以用自然语言描述数据集需求，系统将自动生成符合要求的合成数据，并提供基准测试功能。

## 核心特性

- 🤖 **自然语言驱动**：使用自然语言描述数据集特征
- 📊 **多种分布支持**：支持 Zipf、正态、指数等多种统计分布
- 🎯 **模式注入**：可在数据中"埋藏"特定模式作为基准真值（Ground Truth）
- ⚡ **高性能生成**：使用 NumPy/SciPy 实现高效大规模数据生成
- 🔧 **算法集成**：自动调用 SPMF 和 Choco-Mining 进行基准测试
- 📈 **完整评估**：提供运行时间、内存、准确率等多维度指标

## 快速开始

### 安装

1. 克隆项目：
```bash
git clone <repository-url>
cd LLM_DM
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OPENAI_API_KEY
```

4. 下载 SPMF：
```bash
# 访问 https://www.philippe-fournier-viger.com/spmf/
# 下载 spmf.jar 并放入 lib/ 目录
```

### 基本使用

#### 1. 生成数据集

使用自然语言生成数据集：

```bash
python src/main.py generate \
  --prompt "生成1000条交易记录，模拟小型超市销售，包含100种商品，数据稀疏" \
  --output data/processed/supermarket.spmf \
  --stats
```

使用配置文件生成：

```bash
python src/main.py generate \
  --config-json examples/config.json \
  --output data/processed/custom.spmf
```

#### 2. 运行基准测试

```bash
python src/main.py benchmark \
  --input data/processed/supermarket.spmf \
  --algorithm Apriori \
  --min-support 0.05 \
  --output results/apriori_results.txt
```

#### 3. 完整流程

一键运行生成+测试：

```bash
python src/main.py full-pipeline \
  --prompt "密集型零售数据，1000笔交易" \
  --algorithms Apriori FPGrowth \
  --min-support 0.03
```

## 项目结构

```
LLM_DM/
├── config/                 # 配置文件
│   ├── settings.yaml       # 全局配置
│   └── prompts/            # LLM 提示词模板
├── data/                   # 数据目录
│   ├── raw/                # 原始生成数据
│   ├── processed/          # 处理后的数据（.spmf格式）
│   └── benchmarks/         # 基准测试结果
├── documents/              # 项目文档
├── lib/                    # 外部库（SPMF jar）
├── src/                    # 源代码
│   ├── llm/                # LLM 处理模块
│   ├── generator/          # 数据生成核心
│   ├── benchmark/          # 基准测试模块
│   ├── utils/              # 工具函数
│   └── main.py             # CLI 入口
├── tests/                  # 单元测试
└── notebooks/              # Jupyter 示例
```

## 模块说明

### LLM 处理模块 (`src/llm/`)

- `client.py`: LLM API 客户端，支持 Deepseek，OpenAI
- `parser.py`: 配置解析和验证

### 数据生成核心 (`src/generator/`)

- `core.py`: 主生成引擎
- `distributions.py`: 统计分布生成（Zipf、正态、指数等）
- `injector.py`: 模式注入逻辑

### 基准测试模块 (`src/benchmark/`)

- `spmf_runner.py`: SPMF 算法执行器
- `metrics.py`: 性能指标计算

## 配置示例

生成配置 JSON 格式：

```json
{
  "dataset_meta": {
    "num_transactions": 1000,
    "num_items": 100,
    "density": 0.1,
    "avg_transaction_len": 10
  },
  "distribution_config": {
    "method": "zipf",
    "params": {
      "alpha": 1.2
    }
  },
  "pattern_injection": [
    {
      "id": "coffee_croissant",
      "items": [1, 5, 10],
      "target_support": 0.08,
      "noise_ratio": 0.05
    }
  ]
}
```

## 测试

运行单元测试：

```bash
pytest tests/ -v
```

运行特定测试：

```bash
pytest tests/test_generator.py -v
```

## 技术栈

- **Python 3.9+**: 主要编程语言
- **NumPy/SciPy**: 高效数值计算
- **OpenAI API**: LLM 集成
- **Click**: CLI 框架
- **Pytest**: 测试框架
- **Java 8+**: 运行 SPMF

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 标准
- 使用 Black 格式化代码
- 所有公共函数必须包含 Docstring
- 提交信息遵循 Conventional Commits

## 许可证

MIT License

## 联系方式

- **指导老师**: Nadjib Lazaar (lazaar@lisn.fr)
- **项目年度**: 2025/2026

## 致谢

- SPMF Library by Philippe Fournier-Viger
- OpenAI GPT Models
- Deepseek Models
- TER Project Team

## 路线图

- [x] 基础数据生成功能
- [x] LLM 集成
- [x] 模式注入
- [x] SPMF 集成
- [ ] Choco-Mining 集成
- [ ] 序列数据支持
- [ ] Web UI 界面
- [ ] 更多分布类型

---

**Made with ❤️ for Data Mining Research**
