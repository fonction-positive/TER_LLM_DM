# 数据生成示例

## 示例 1：超市早餐购物规律分析

### 场景描述
模拟超市早餐时段的购物行为，包含以下购买规律：

1. **早餐经典组合**（60% 支持度）
   - 牛奶 (ID:0) + 面包 (ID:1) + 鸡蛋 (ID:2)
   - 这是最常见的早餐组合

2. **咖啡爱好者组合**（40% 支持度）
   - 咖啡 (ID:5) + 糖 (ID:6) + 奶油 (ID:7)
   - 喜欢喝咖啡的顾客通常会买齐配料

3. **健康早餐组合**（35% 支持度）
   - 酸奶 (ID:10) + 水果 (ID:11)
   - 注重健康的顾客偏好

4. **西式早餐组合**（25% 支持度）
   - 培根 (ID:15) + 香肠 (ID:16) + 番茄 (ID:17) + 蘑菇 (ID:18)
   - 完整的英式早餐

### 使用方法

#### 方法 1：使用配置文件（推荐，无需 API）
```bash
# 生成数据
python src/main.py generate \
  --config-json examples/breakfast_shopping_config.json \
  --output data/processed/breakfast_shopping.spmf \
  --stats

# 运行基准测试
python src/main.py benchmark \
  --input data/processed/breakfast_shopping.spmf \
  --algorithm Apriori \
  --min-support 0.20 \
  --output data/benchmarks/breakfast_apriori.txt

# 验证规律（使用真实值对比）
python src/main.py benchmark \
  --input data/processed/breakfast_shopping.spmf \
  --algorithm FPGrowth \
  --min-support 0.20 \
  --ground-truth examples/breakfast_shopping_config.json \
  --output data/benchmarks/breakfast_fpgrowth.txt
```

#### 方法 2：使用 LLM 提示词（需要 API）
```bash
python src/main.py generate \
  --prompt "生成1000条超市早餐购物记录，包含50种商品。重要规律：60%的交易包含牛奶+面包+鸡蛋组合(商品ID 0,1,2)，支持度0.60；40%包含咖啡+糖+奶油组合(商品ID 5,6,7)，支持度0.40；35%包含酸奶+水果组合(商品ID 10,11)，支持度0.35。每条交易平均6-8个商品，适度稀疏，添加10%噪声。" \
  --output data/processed/breakfast_shopping.spmf \
  --stats
```

### 预期结果

运行 Apriori 算法后，应该能发现：

```
频繁模式（min_support = 0.20）:
- {0, 1, 2} #SUP: ~600     # 牛奶+面包+鸡蛋（60%）
- {5, 6, 7} #SUP: ~400     # 咖啡+糖+奶油（40%）
- {10, 11}  #SUP: ~350     # 酸奶+水果（35%）
- {15, 16, 17, 18} #SUP: ~250  # 西式早餐（25%）
```

### 验证规律准确性

```bash
# 查看生成的规律是否符合预期
head -50 data/benchmarks/breakfast_apriori.txt

# 统计包含核心组合的交易数量
grep -E "^0 1 2( |$)" data/processed/breakfast_shopping.spmf | wc -l
# 应该接近 600 条（60% of 1000）
```

---

## 示例 2：电商用户行为规律

### 场景描述
模拟电商平台的用户浏览和购买行为：

1. **手机配件组合**（70% 支持度）
   - 手机壳 + 钢化膜 + 数据线
   
2. **游戏玩家组合**（50% 支持度）
   - 鼠标 + 键盘 + 鼠标垫

3. **办公文具组合**（40% 支持度）
   - 笔记本 + 签字笔 + 橡皮

配置文件：`examples/ecommerce_config.json`

---

## 示例 3：图书馆借阅规律

### 场景描述
分析学生借书行为：

1. **考研学生组合**（55% 支持度）
   - 数学教材 + 英语词汇 + 政治复习资料

2. **编程学习组合**（45% 支持度）
   - Python 入门 + 算法导论 + 数据结构

3. **文学爱好者组合**（30% 支持度）
   - 小说 + 诗歌 + 散文

配置文件：`examples/library_config.json`

---

## 如何创建自定义规律

### 步骤 1：定义商品映射
```json
"item_mapping": {
  "0": "商品A名称",
  "1": "商品B名称",
  ...
}
```

### 步骤 2：设计规律模式
```json
"pattern_injection": [
  {
    "items": [0, 1, 2],           // 商品ID组合
    "target_support": 0.60,       // 目标支持度（60%）
    "noise_ratio": 0.10,          // 噪声比例（10%）
    "description": "规律描述"
  }
]
```

### 步骤 3：选择分布类型
- **zipf**: 幂律分布（少数热门商品，多数冷门商品）- 适合电商
- **normal**: 正态分布（商品受欢迎程度均匀）- 适合超市
- **exponential**: 指数分布（衰减型）- 适合新品推广
- **random**: 均匀分布 - 适合测试

### 步骤 4：调整参数
```json
"dataset_meta": {
  "num_transactions": 1000,      // 交易数量
  "num_items": 50,               // 商品种类
  "avg_transaction_length": 7    // 平均每笔交易商品数
}
```

---

## 常见问题

### Q: 如何查看生成数据中的具体商品名称？

A: 使用配置文件中的 `item_mapping` 字段，手动对照 ID：
```bash
# 查看前 10 条交易
head -10 data/processed/breakfast_shopping.spmf

# 输出示例：
# 0 1 2 5 12 24    → 牛奶 面包 鸡蛋 咖啡 麦片 可乐
```

### Q: 为什么实际支持度和目标支持度不完全一致？

A: 因为添加了 `noise_ratio` 噪声，使数据更真实。如果 `target_support=0.60` 且 `noise_ratio=0.10`，实际支持度约在 54%-66% 之间。

### Q: 如何提高规律的明显程度？

A: 降低 `noise_ratio`，例如从 0.10 改为 0.05 或 0.02。

### Q: 如何生成更稀疏的数据？

A: 减少 `avg_transaction_length`，例如从 7 改为 4 或 5。

---

## 下一步

1. 复制 `examples/breakfast_shopping_config.json` 并修改为你的场景
2. 运行数据生成命令
3. 使用 benchmark 测试挖掘效果
4. 调整参数优化结果
