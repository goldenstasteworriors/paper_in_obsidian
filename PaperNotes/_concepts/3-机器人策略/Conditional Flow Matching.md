---
type: concept
aliases: [条件流匹配, CFM]
---

# Conditional Flow Matching

## 定义

通过条件上下文监督概率路径上的速度场，使模型可由噪声积分生成连续动作或数据。

## 数学形式

$$
\mathcal L_{\mathrm{CFM}}=\mathbb E\|v_\theta(x_t\mid c,t)-u_t(x_t\mid x_1)\|_2^2
$$

## 核心要点

1. 不需要显式求解数据分布的 score。
2. VLA 中常用于生成连续动作块。

## 代表工作

- [[EgoSteer]]：结合 RTC 前缀条件生成双手动作后缀。

## 相关概念

- [[Flow Matching]]
- [[Action Chunking]]
