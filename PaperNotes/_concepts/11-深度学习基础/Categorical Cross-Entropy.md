---
title: "Categorical Cross-Entropy"
type: concept
tags: [loss-function, classification]
created: 2026-04-28
---

# Categorical Cross-Entropy

Categorical Cross-Entropy 是多类别分类常用损失，用于最大化正确类别的预测概率。

$$
\mathcal{L} = - \sum_k y_k \log p_k
$$

## 在 RT-1 中

[[RT-1]] 将连续动作分量离散为 256 个 bins，每个动作维度作为分类问题训练，因此使用分类交叉熵作为动作 token 预测损失。

## 代表工作

- [[RT-1]]: 离散动作 token 预测。
