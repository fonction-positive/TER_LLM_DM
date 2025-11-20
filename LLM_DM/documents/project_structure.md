# FIDD-Bench 项目结构文档

本项目的推荐目录结构如下，旨在保持模块化、清晰且符合 Python 最佳实践。

```text
FIDD-Bench/
├── .gitignore               # Git 忽略文件配置
├── README.md                # 项目主文档
├── requirements.txt         # Python 依赖列表
├── setup.py                 # (可选) 安装脚本
├── config/                  # 配置文件目录
│   ├── settings.yaml        # 全局配置 (API Keys, 路径等)
│   └── prompts/             # 存放 LLM 的 System Prompts
│       ├── generation.txt
│       └── validation.txt
├── data/                    # 数据存储目录
│   ├── raw/                 # 原始生成数据
│   ├── processed/           # 转换格式后的数据 (.spmf)
│   └── benchmarks/          # 基准测试结果日志
├── docs/                    # 项目文档
│   ├── requirements.md
│   ├── technical_design.md
│   ├── api_specs.md
│   └── ...
├── lib/                     # 外部依赖库 (非 Python 包)
│   ├── spmf.jar             # SPMF 算法库
│   └── choco-mining.jar     # Choco-Mining 算法库
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── main.py              # 程序主入口
│   ├── llm/                 # LLM 相关模块
│   │   ├── __init__.py
│   │   ├── client.py        # LLM API 客户端
│   │   └── parser.py        # JSON 解析与校验
│   ├── generator/           # 数据生成核心模块
│   │   ├── __init__.py
│   │   ├── core.py          # 生成逻辑主类
│   │   ├── distributions.py # 统计分布函数
│   │   └── injector.py      # 模式注入逻辑
│   ├── benchmark/           # 基准测试模块
│   │   ├── __init__.py
│   │   ├── spmf_runner.py   # 调用 SPMF
│   │   └── metrics.py       # 指标计算
│   └── utils/               # 通用工具模块
│       ├── __init__.py
│       ├── file_io.py       # 文件读写
│       └── logger.py        # 日志记录
├── tests/                   # 测试代码目录
│   ├── __init__.py
│   ├── test_generator.py
│   ├── test_llm_parser.py
│   └── test_integration.py
└── notebooks/               # Jupyter Notebooks (用于实验和演示)
    ├── demo_generation.ipynb
    └── analysis_results.ipynb
```

## 关键目录说明

*   **`src/llm/`**: 包含所有与大模型交互的代码。Prompt 的构建和 API 的调用应封装在此处，与业务逻辑解耦。
*   **`src/generator/`**: 这是项目的核心引擎。应包含纯数学/统计学的生成逻辑，不应包含任何 LLM 调用代码。
*   **`lib/`**: 存放 Java 的 jar 包。确保在代码中通过相对路径正确引用这些 jar 包。
*   **`data/`**: 生成的数据文件不应提交到 Git 仓库（除了少量的样例数据），应在 `.gitignore` 中配置忽略。
