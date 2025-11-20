#!/bin/bash

# FIDD-Bench 基准测试示例脚本

echo "=========================================="
echo "FIDD-Bench 基准测试"
echo "=========================================="
echo ""

# 激活虚拟环境
# source /Users/jinzhuoyuan/King/Saclay/Course/TER/.venv/bin/activate

# 数据文件
DATA_FILE="data/processed/dataset.spmf"
MIN_SUPPORT=0.05

echo "📊 数据文件: $DATA_FILE"
echo "🎯 最小支持度: $MIN_SUPPORT"
echo ""

# 测试 1: Apriori 算法
echo "-------------------------------------------"
echo "测试 1: Apriori 算法"
echo "-------------------------------------------"
python src/main.py benchmark \
  --input $DATA_FILE \
  --algorithm Apriori \
  --min-support $MIN_SUPPORT \
  --output data/benchmarks/apriori_results.txt

echo ""
echo "✅ Apriori 测试完成"
echo ""

# 测试 2: FPGrowth 算法
echo "-------------------------------------------"
echo "测试 2: FPGrowth 算法"
echo "-------------------------------------------"
python src/main.py benchmark \
  --input $DATA_FILE \
  --algorithm FPGrowth \
  --min-support $MIN_SUPPORT \
  --output data/benchmarks/fpgrowth_results.txt

echo ""
echo "✅ FPGrowth 测试完成"
echo ""

# 测试 3: Eclat 算法
echo "-------------------------------------------"
echo "测试 3: Eclat 算法"
echo "-------------------------------------------"
python src/main.py benchmark \
  --input $DATA_FILE \
  --algorithm Eclat \
  --min-support $MIN_SUPPORT \
  --output data/benchmarks/eclat_results.txt

echo ""
echo "✅ Eclat 测试完成"
echo ""

echo "=========================================="
echo "所有测试完成！"
echo "=========================================="
echo ""
echo "查看结果文件："
echo "  - data/benchmarks/apriori_results.txt"
echo "  - data/benchmarks/fpgrowth_results.txt"
echo "  - data/benchmarks/eclat_results.txt"
