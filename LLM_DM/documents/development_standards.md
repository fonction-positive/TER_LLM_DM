# FIDD-Bench 开发规范文档

## 1. 界面与交互规范 (Interface & Interaction)

### 1.1 命令行界面 (CLI)
*   **参数风格**: 使用 GNU 风格参数（如 `--output`, `--verbose`）。
*   **帮助信息**: 必须提供 `-h` 或 `--help` 选项，清晰说明所有参数用途。
*   **反馈**: 长时间运行的任务（如大规模数据生成或挖掘）必须显示进度条 (推荐使用 `tqdm` 库)。
*   **错误提示**: 报错信息应友好且具体，避免直接打印 Python Traceback 给最终用户。

### 1.2 用户输入
*   **Prompt 输入**: 支持从命令行直接输入字符串，也支持从文件读取 Prompt（方便长文本输入）。
*   **默认值**: 对于非必填参数（如密度、分布类型），系统应提供合理的默认值。

## 2. 代码规范 (Code Standards)

### 2.1 命名规范 (Naming Convention)
遵循 PEP 8 标准：
*   **变量与函数**: `snake_case` (例如: `generate_data`, `transaction_count`)
*   **类名**: `CamelCase` (例如: `DataGenerator`, `SPMFRunner`)
*   **常量**: `UPPER_CASE` (例如: `DEFAULT_DENSITY`, `API_TIMEOUT`)
*   **私有成员**: 以单下划线开头 `_variable`。
*   **文件名**: `snake_case.py`。

### 2.2 注释规范 (Comments)
*   **Docstrings**: 所有公共模块、类、函数必须包含 Docstring（推荐 Google Style 或 NumPy Style）。
    ```python
    def inject_pattern(data, pattern, support):
        """
        Injects a specific pattern into the dataset.

        Args:
            data (np.array): The original binary matrix.
            pattern (list): List of item IDs to inject.
            support (float): The target support threshold (0.0 - 1.0).

        Returns:
            np.array: The modified dataset with injected patterns.
        """
        pass
    ```
*   **行内注释**: 仅在代码逻辑复杂或不直观时添加，解释“为什么”这样做，而不是“在做什么”。

### 2.3 代码格式风格 (Formatting)
*   **Formatter**: 统一使用 `Black` 进行代码格式化。
*   **Linter**: 使用 `Flake8` 或 `Ruff` 进行代码质量检查。
*   **Import 顺序**: 标准库 -> 第三方库 -> 本地模块 (推荐使用 `isort` 自动排序)。

### 2.4 提交规范 (Commit Style)
遵循 **Conventional Commits** 规范：
*   `feat`: 新功能 (feature)
*   `fix`: 修补 bug
*   `docs`: 文档改变
*   `style`: 代码格式改变 (不影响代码运行的变动)
*   `refactor`: 重构 (即不是新增功能，也不是修改 bug 的代码变动)
*   `test`: 增加测试
*   `chore`: 构建过程或辅助工具的变动

**示例**:
*   `feat: add support for zipf distribution in generator`
*   `fix: resolve memory leak in spmf runner`
*   `docs: update requirements.md with new dependencies`

## 3. 异常处理与日志
*   **日志**: 禁止使用 `print()` 进行调试或输出日志。使用 Python 标准库 `logging`。
*   **异常**: 捕获具体异常（如 `ValueError`, `FileNotFoundError`），避免使用裸露的 `except:`。

## 4. 测试规范
*   **单元测试**: 每个核心功能函数（特别是数学计算和格式转换）都必须有对应的单元测试 (`pytest`)。
*   **集成测试**: 每次提交前需跑通一个完整的 "Prompt -> 生成 -> 挖掘" 流程。
