FIDD-Bench: 基于LLM的模式挖掘合成数据生成项目指南

项目名称: FIDD-Bench (Flexible & Intelligent Data Generator for Data Mining Benchmarking)
适用对象: TER 集体项目 (2025/2026)
指导老师: Nadjib Lazaar (lazaar@lisn.fr)
核心目标: 利用LLM根据自然语言指令生成高质量、可控的合成数据集，用于评估模式挖掘算法（如SPMF, Choco-Mining）的性能。

1. 项目愿景与核心价值

1.1 痛点分析

传统的模式挖掘算法测试通常依赖于：

FIMI Repository 等老旧数据集: 很多是20年前的数据，缺乏多样性。

简单的随机生成器: 往往无法捕捉现实世界数据的复杂分布（如长尾分布、特定的序列模式）。

缺乏基准真值 (Ground Truth): 在真实数据中，我们不知道“正确”的模式是什么，因此很难验证算法的准确率（Precision/Recall）。

1.2 解决方案

通过 FIDD-Bench，用户可以说：“生成一个模拟小型超市一周销售记录的数据集，包含1000笔交易，商品总数500，大部分交易很短，但周末有明显的啤酒和尿布共现模式。”
系统将自动生成符合描述的结构化数据，供研究人员测试算法。

2. 系统架构设计 (Technical Architecture)

建议采用 "LLM 作为 编排者 (Orchestrator)" 的架构，而不是让 LLM 逐行生成数据（因为 LLM 生成大量数据太慢且昂贵）。

核心模块划分

前端交互层 (Prompt Interface):

接受用户的自然语言描述。

接受硬性约束参数（如：密度=15%，事务数=10k）。

LLM 解析引擎 (The Brain):

任务: 将自然语言转换为数据生成配置文件 (JSON) 或 Python 生成脚本。

Prompt 策略: "你是一个数据科学家。根据用户的描述，推断出数据的统计特征（分布类型、平均长度、标准差、特定的频繁项集种子）。"

数据生成核心 (Generation Engine):

这是一个基于 Python 的脚本执行环境。

它接收 LLM 输出的参数，使用 numpy / scipy 高效生成大规模数据。

功能: 注入特定的模式（Pattern Injection）作为基准真值（Ground Truth）。

评估与基准测试模块 (Benchmarking Module):

连接器: 自动调用 SPMF (Java) 和 Choco-Mining (Java)。

格式转换: 将生成的数据转换为 SPMF 格式 (.spmf) 或 Choco-Mining 支持的格式。

指标计算: 运行时间、内存消耗、挖掘出的模式数量、准确率（是否找回了注入的模式）。

3. 功能需求规格 (Functional Requirements)

第一阶段：基础事务数据 (Transactional Data)

输入: 事务数 ($|T|$), 项目数 ($|I|$), 密度 (Density).

输出: 二进制矩阵或项集列表 (Itemsets).

LLM 能力: 理解“稀疏”、“密集”、“长尾分布”等词汇对应的数学参数。

第二阶段：模式注入 (Pattern Injection)

需求: 用户要求“埋藏”特定的模式。

实现: 在随机噪声中，强制插入某些项集组合，使其支持度 (Support) 高于特定阈值。

目的: 验证算法是否能把这些“埋”进去的模式挖出来。

第三阶段：序列数据 (Sequential Data) (扩展目标)

支持时间序列或事件序列 (A -> B -> C)。

增加时间戳或顺序约束。

4. 实施路线图 (Roadmap)

假设项目周期为一学期（约12-14周），建议如下安排：

Phase 1: 启动与调研 (第1-3周)

Week 1: 团队组建，GitLab 仓库初始化。阅读 SPMF 文档，跑通一个简单的 Apriori 算法 Demo。

Week 2: 调研现有的合成数据生成器（IBM Quest Data Generator 等）。

Week 3: 确定 LLM 接口（使用 OpenAI API, HuggingFace 本地模型, 或 Mistral 等）。设计 Prompt 原型。

Phase 2: 核心开发 (第4-8周)

Week 4: LLM 模块开发。编写 Prompt，让 LLM 能输出 JSON 格式的生成参数（如 {"num_transactions": 1000, "distribution": "exponential"}）。

Week 5-6: 生成器后端开发。编写 Python 代码，读取 JSON 参数并生成 .txt 或 .spmf 文件。实现“模式注入”逻辑。

Week 7: 基准测试集成。编写脚本自动调用 SPMF 的 spmf.jar。

Week 8: 中期整合。能够通过简单的文本指令生成文件并跑通 SPMF。

Phase 3: 评估与优化 (第9-11周)

Week 9: 集成 Choco-Mining。

Week 10: 大规模实验。生成不同特征的数据集，对比声明式方法与命令式方法的优劣。

Week 11: UI/CLI 优化，确保工具易用。

Phase 4: 交付与文档 (第12-14周)

Week 12: 撰写 TER 报告，整理实验图表。

Week 13: 准备 PPT，制作 Demo 视频。

Week 14: 最终答辩排练。

5. 团队分工建议 (Team Roles)

如果是 4-6 人的团队，建议如下分工：

PM & 架构师 (1人):

负责整体进度把控，Git 分支管理。

定义模块间的接口（JSON 结构）。

撰写最终报告的统筹部分。

LLM & Prompt 工程师 (1-2人):

设计 System Prompt。

负责与 LLM API 对接。

测试 LLM 对不同自然语言指令的理解能力（Prompt Engineering）。

后端/算法工程师 (1-2人):

实现 Python 数据生成逻辑（核心难点：如何高效生成并注入模式）。

确保生成的统计分布符合数学定义。

基准测试与评估员 (1-2人):

负责集成 SPMF 和 Choco-Mining。

设计实验表格，运行实验，绘制 matplotlib 图表。

负责数据格式转换。

6. 技术栈推荐

编程语言: Python (主逻辑), Java (运行 SPMF/Choco 必需)。

LLM: OpenAI GPT-3.5/4o (API调用最简单) 或 Llama 3 (本地部署，免费)。

库: numpy, pandas (数据处理), langchain (可选，用于管理 LLM 流程).

数据格式: SPMF 标准格式 (每行代表一个事务，数字代表物品 ID，空格分隔)。

例如: 1 3 5 (代表该交易购买了物品1, 3, 5)。

7. 参考文献与资源

SPMF 格式说明: SPMF Format definition

IBM Quest Data Generator: 数据挖掘领域最经典的生成器逻辑，值得参考。

Python subprocess 模块: 用于在 Python 中调用 Java jar 包。

8. 报告与交付物清单

代码库: 结构清晰，包含 README.md, requirements.txt, dockerfile (可选)。

数据集: datasets/ 目录下存放生成的典型数据集（稀疏、密集、长序列等）。

实验报告:

Q1: LLM 是否能准确理解复杂的分布要求？

Q2: 在生成的数据集上，SPMF 和 Choco-Mining 谁更快？

Q3: 生成的数据质量是否通过了统计检验？

祝你们项目顺利！这是一个非常适合写在简历上的 AI + 工程化项目。