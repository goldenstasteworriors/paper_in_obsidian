---
type: concept
aliases: [Transformer, 自注意力网络]
---

# Transformer

## 定义

Transformer 是基于自注意力机制的序列建模架构，可将输入 token 之间的依赖关系显式建模。

## 数学形式

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d}}\right)V
$$

## 核心要点

1. 将输入表示为 token 序列，并通过 attention 建模 token 间关系。
2. 可通过 mask 控制信息流，例如 causal mask 或 block-wise mask。
3. 在机器人策略中可统一处理语言、图像 patch、状态和 readout token。

## 代表工作

- [[Octo]]: 使用 block-wise masked transformer 统一处理任务 token、观测 token 和 readout token。

## 相关概念

- [[Vision Transformer]]
- [[Generalist Robot Policy]]
