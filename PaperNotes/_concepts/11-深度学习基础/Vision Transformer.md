---
type: concept
aliases: [ViT, Vision Transformer, 视觉Transformer]
---

# Vision Transformer

## 定义

Vision Transformer 将图像切分为 patch token，并用 Transformer 进行视觉表征学习。

## 数学形式

$$
z_0 = [x_{\text{patch}}^1 E; x_{\text{patch}}^2 E; \ldots; x_{\text{patch}}^N E] + E_{\text{pos}}
$$

## 核心要点

1. 用 patch token 替代传统 CNN 的 dense feature map。
2. 训练规模足够大时，ViT-style 架构通常更容易从数据规模中获益。
3. 在机器人策略中可以把相机观测与语言、状态 token 放进统一序列。

## 代表工作

- [[Octo]]: 采用 transformer-first 架构，把大部分参数和 FLOPs 放在 transformer backbone。

## 相关概念

- [[Transformer]]
- [[Generalist Robot Policy]]
