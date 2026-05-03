---
type: concept
aliases: [动作块, Action Chunking]
---

# Action Chunking

## 定义
一次性预测未来多个控制步的动作序列，而不是逐步只预测下一个动作的策略建模方式。

## 数学形式
$$
a_{t:t+k} = \pi_\theta(o_t, l_t, s_t)
$$

## 核心要点
1. 能减少决策频率和累计误差，也便于生成式策略建模。
2. chunk 太长会牺牲反应速度，太短又学不到长时程结构。
3. 常和 diffusion 或 flow-matching 动作头一起出现。

## 代表工作
- [[ACT]]: 经典 action chunking imitation baseline。
- [[HEX]]: 以 flow matching 方式预测 high-level action chunks。

## 相关概念
- [[Flow Matching]]
- [[ACT]]
