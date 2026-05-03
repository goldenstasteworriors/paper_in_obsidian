---
type: concept
aliases: [Low-Rank Adaptation, 低秩适配, A-LoRA, T-LoRA]
---

# LoRA

## 定义
LoRA 是一种参数高效微调方法，通过给大模型权重更新加入低秩分解矩阵，在少量可训练参数下适配新任务。

## 数学形式

$$
W' = W + \Delta W, \quad \Delta W = BA
$$

其中 $A$ 和 $B$ 是低秩可训练矩阵。

## 核心要点
1. 冻结或基本保持原模型参数，只训练低秩增量。
2. 适合将通用模型适配到具体技能或输出格式。
3. RoboBrain 中 A-LoRA 学 affordance，T-LoRA 学 trajectory。

## 代表工作
- [[RoboBrain]]: 在 Stage 4 使用 LoRA 训练具体机器人技能。

## 相关概念
- [[Multimodal Large Language Model]]
- [[RoboBrain]]
