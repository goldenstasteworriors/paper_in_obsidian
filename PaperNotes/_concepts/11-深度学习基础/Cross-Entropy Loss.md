---
type: concept
aliases: [交叉熵损失, CE loss]
---

# Cross-Entropy Loss

## 定义
Cross-Entropy Loss 衡量真实离散标签分布与模型预测概率分布之间的差异，是分类和 token 预测任务的常用训练目标。

## 数学形式

$$
\mathcal{L}_{CE} = -\sum_i y_i \log p_i
$$

## 核心要点
1. 当真实标签为 one-hot 时，损失等价于负对数似然。
2. 可用于图像分类、语言建模和离散化动作预测。
3. 在机器人策略中常用于 imitation learning 的 action token classification。

## 代表工作
- [[RT-X]]: 用交叉熵训练 RT-1-X 和 RT-2-X 的离散动作输出。

## 相关概念
- [[Action Tokenization]]
- [[Imitation Learning]]
