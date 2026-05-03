---
type: concept
aliases: [MoE, Mixture of Experts]
---

# Mixture of Experts

## 定义
通过路由器把不同 token 或样本分配给不同 expert 子网络处理的条件计算架构。

## 数学形式
$$
y = \sum_{i=1}^{K} g_i(x) E_i(x)
$$

## 核心要点
1. 目标是在不线性增加计算量的前提下提升模型容量。
2. 路由器通常使用 top-k gating，并配合负载均衡损失避免 expert 塌缩。
3. 适合 token 异质性明显的场景，比如多模态输入或不同身体部位动力学。

## 代表工作
- [[HEX]]: 在 UPP 输入和输出边界使用 morphology-aware MoE 处理不同 body-part token。

## 相关概念
- [[Flow Matching]]
- [[Vision-Language Model]]
