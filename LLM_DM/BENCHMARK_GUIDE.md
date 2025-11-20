# 基准测试快速指南

## 📊 已生成的数据

你已经成功生成了数据集：
- **文件位置**: `data/processed/dataset.spmf`
- **事务数**: 1000 条
- **查看数据**: `head data/processed/dataset.spmf`

## 🧪 基准测试方法

### 方法 1: 单个算法测试

```bash
python src/main.py benchmark \
  --input data/processed/dataset.spmf \
  --algorithm Apriori \
  --min-support 0.05 \
  --output data/benchmarks/apriori_results.txt
```

**支持的算法**:
- `Apriori` - 经典 Apriori 算法
- `FPGrowth` - FP-Growth 算法（通常更快）
- `Eclat` - Eclat 算法
- `LCM` - LCM 算法
- `CHARM` - CHARM 算法

### 方法 2: 测试多个算法

```bash
# 测试 Apriori
python src/main.py benchmark \
  -i data/processed/dataset.spmf \
  -a Apriori \
  -s 0.05 \
  -o data/benchmarks/apriori.txt

# 测试 FPGrowth
python src/main.py benchmark \
  -i data/processed/dataset.spmf \
  -a FPGrowth \
  -s 0.05 \
  -o data/benchmarks/fpgrowth.txt

# 测试 Eclat
python src/main.py benchmark \
  -i data/processed/dataset.spmf \
  -a Eclat \
  -s 0.05 \
  -o data/benchmarks/eclat.txt
```

### 方法 3: 使用完整流程（推荐用于新数据）

如果你想生成新数据并立即测试：

```bash
python src/main.py full-pipeline \
  --config-json examples/supermarket_config.json \
  --dataset data/processed/new_dataset.spmf \
  --algorithms Apriori FPGrowth \
  --min-support 0.05
```

### 方法 4: 使用脚本批量测试

```bash
# 给脚本添加执行权限
chmod +x run_benchmark.sh

# 运行批量测试
./run_benchmark.sh
```

## 📈 查看测试结果

### 查看找到的模式

```bash
# 查看 Apriori 找到的前 20 个模式
head -20 data/benchmarks/apriori_results.txt

# 统计找到的模式数量
wc -l data/benchmarks/apriori_results.txt
```

### 模式格式说明

SPMF 输出格式：`items #SUP: support`

例如：
```
0 1 5 #SUP: 120
```
表示物品 {0, 1, 5} 在 120 个事务中同时出现。

## 🔍 不同支持度阈值测试

测试不同的最小支持度来观察性能差异：

```bash
# 高支持度（更快，模式更少）
python src/main.py benchmark \
  -i data/processed/dataset.spmf \
  -a Apriori -s 0.1 \
  -o data/benchmarks/apriori_s10.txt

# 中等支持度
python src/main.py benchmark \
  -i data/processed/dataset.spmf \
  -a Apriori -s 0.05 \
  -o data/benchmarks/apriori_s05.txt

# 低支持度（更慢，模式更多）
python src/main.py benchmark \
  -i data/processed/dataset.spmf \
  -a Apriori -s 0.02 \
  -o data/benchmarks/apriori_s02.txt
```

## 📊 性能对比示例

```bash
# 创建对比测试脚本
cat > compare_algorithms.sh << 'EOF'
#!/bin/bash
echo "算法性能对比测试"
echo "数据集: data/processed/dataset.spmf"
echo "最小支持度: 0.05"
echo ""

for algo in Apriori FPGrowth Eclat; do
    echo "测试 $algo..."
    time python src/main.py benchmark \
        -i data/processed/dataset.spmf \
        -a $algo -s 0.05 \
        -o data/benchmarks/${algo}_compare.txt 2>&1 | grep "Execution Time"
    echo ""
done
EOF

chmod +x compare_algorithms.sh
./compare_algorithms.sh
```

## 🎯 验证注入的模式（如果有 Ground Truth）

如果你的数据集注入了已知模式，可以验证算法是否找到它们：

```bash
# 使用带 ground truth 的配置生成数据
python src/main.py generate \
  --config-json examples/supermarket_config.json \
  --output data/processed/gt_dataset.spmf \
  --save-config data/processed/gt_config.json

# 运行测试并验证准确率
python src/main.py benchmark \
  -i data/processed/gt_dataset.spmf \
  -a Apriori -s 0.05 \
  --ground-truth data/processed/gt_config.json \
  -o data/benchmarks/apriori_with_gt.txt
```

## 📝 常用命令速查

| 操作 | 命令 |
|------|------|
| 查看数据 | `head -n 10 data/processed/dataset.spmf` |
| 统计事务数 | `wc -l data/processed/dataset.spmf` |
| 查看结果 | `cat data/benchmarks/apriori_results.txt` |
| 统计模式数 | `wc -l data/benchmarks/apriori_results.txt` |
| 查找高频模式 | `grep "#SUP: [2-9][0-9][0-9]" data/benchmarks/apriori_results.txt` |

## 🐛 故障排查

### Java 相关错误

```bash
# 检查 Java 版本
java -version

# 检查 SPMF jar 路径
ls -lh lib/spmf.jar
```

### 内存不足

编辑 `.env` 文件增加内存：
```
JAVA_MEMORY_MAX=8g
```

### 执行超时

增加超时时间（编辑 `config/settings.yaml`）：
```yaml
benchmark:
  timeout: 600  # 10分钟
```

## 💡 实用技巧

1. **先用小数据测试**: 用少量数据（100-500 事务）快速验证流程
2. **调整支持度**: 从高支持度开始（0.1），逐步降低
3. **比较算法**: FPGrowth 通常比 Apriori 快，特别是在大数据集上
4. **保存日志**: 使用 `2>&1 | tee benchmark.log` 保存完整输出

---

**现在就开始测试吧！** 🚀
