# FIDD-Bench 技术文档

## 1. 技术栈 (Technology Stack)

*   **核心编程语言**: Python 3.9+ (负责逻辑编排、数据生成、接口处理)
*   **辅助编程语言**: Java 8+ (用于运行 SPMF 和 Choco-Mining 库)
*   **大语言模型 (LLM)**:
    *   API 接入: OpenAI GPT-3.5/4o (推荐，开发便捷)
    *   本地部署 (可选): Llama 3 / Mistral (通过 HuggingFace / Ollama)
*   **核心库**:
    *   数据处理: `numpy`, `pandas`, `scipy` (高效数值计算与分布生成)
    *   LLM 集成: `langchain` (可选，用于 Prompt 管理), `openai` SDK
    *   可视化: `matplotlib`, `seaborn`
*   **工具与环境**:
    *   版本控制: Git
    *   容器化: Docker (可选，用于统一运行环境)

## 2. 架构设计 (Architecture)

本项目采用 **"LLM 作为编排者 (LLM as Orchestrator)"** 的架构模式。

```mermaid
graph TD
    User[用户 (User)] -->|自然语言指令| Frontend[前端交互层 (CLI/UI)]
    Frontend -->|Prompt + Context| LLM_Brain[LLM 解析引擎 (The Brain)]
    LLM_Brain -->|生成参数 (JSON)| Gen_Engine[数据生成核心 (Generation Engine)]
    Gen_Engine -->|原始数据| Data_Files[数据文件 (.spmf / .txt)]
    Data_Files --> Bench_Module[评估与基准测试模块 (Benchmarking)]
    Bench_Module -->|调用| SPMF[SPMF (Java)]
    Bench_Module -->|调用| Choco[Choco-Mining (Java)]
    SPMF -->|挖掘结果| Metrics[指标计算]
    Choco -->|挖掘结果| Metrics
    Metrics -->|报告| User
```

### 核心层级
1.  **交互层**: 负责接收用户输入和展示结果。
2.  **智能层 (Brain)**: 负责理解语义，将非结构化需求转换为结构化参数。
3.  **执行层 (Core)**: 负责高性能的数据生成和模式注入，不依赖 LLM 进行计算。
4.  **评估层**: 负责外部工具调用和结果分析。

## 3. 模块划分 (Module Design)

### 3.1 `llm_processor` (LLM 处理模块)
*   **功能**: 管理 System Prompt，与 LLM API 交互。
*   **输入**: 用户自然语言字符串。
*   **输出**: 标准化 JSON 配置对象。
*   **关键类**: `PromptManager`, `LLMClient`。

### 3.2 `data_generator` (数据生成模块)
*   **功能**: 接收 JSON 配置，生成合成数据。
*   **子模块**:
    *   `distribution_engine`: 处理统计分布（Zipf, Gaussian 等）。
    *   `pattern_injector`: 负责在背景噪声中植入频繁项集。
    *   `format_converter`: 将内部矩阵转换为 SPMF 格式。
*   **关键类**: `TransactionGenerator`, `PatternInjector`。

### 3.3 `benchmarker` (基准测试模块)
*   **功能**: 运行外部挖掘算法并收集指标。
*   **实现**: 使用 Python `subprocess` 调用 Java jar 包。
*   **关键类**: `SPMFRunner`, `ChocoRunner`, `MetricCalculator`。

## 4. 数据结构 (Data Structure)

### 4.1 生成配置对象 (Generation Config JSON)
LLM 输出的中间格式，用于驱动生成引擎。

```json
{
  "meta": {
    "description": "超市周末销售数据",
    "num_transactions": 10000,
    "num_items": 500
  },
  "distribution": {
    "type": "zipf",
    "alpha": 1.2
  },
  "constraints": {
    "avg_transaction_length": 10,
    "density": 0.05
  },
  "injected_patterns": [
    {
      "items": [1, 5, 10],
      "support": 0.02,
      "noise_level": 0.1
    },
    {
      "items": [99, 100],
      "support": 0.05
    }
  ]
}
```

### 4.2 内部数据表示
*   **Transaction Matrix**: 使用 `scipy.sparse.csr_matrix` 或 `List[List[int]]` 存储，以节省内存。

### 4.3 输出文件格式 (.spmf)
文本文件，每行代表一个事务，数字代表 Item ID，以空格分隔，-1 或 -2 作为结束符（视具体 SPMF 算法要求而定，通常标准格式仅需空格分隔，行尾无特殊符号或以 -1 结尾）。

示例：
```text
1 3 5
2 4
1 3 5 8
```

## 5. 接口规范概要 (API Specs Summary)

*   **CLI 入口**: `python main.py --prompt "..." --output "data.spmf"`
*   **Python 内部接口**:
    *   `generate_config(prompt: str) -> dict`
    *   `generate_dataset(config: dict) -> str (filepath)`
    *   `run_benchmark(filepath: str, algorithm: str) -> dict (metrics)`
