---
title: "Behavioral Cloning"
type: concept
tags: [imitation-learning, policy-learning]
created: 2026-04-28
---

# Behavioral Cloning

Behavioral Cloning 是 [[Imitation Learning]] 中最直接的方法：把专家演示中的状态到动作映射视为监督学习问题，训练策略最大化专家动作的似然。

$$
\mathcal{L}_{BC} = - \sum_t \log \pi(a_t \mid o_{\le t}, i)
$$

## 在 RT-1 中

[[RT-1]] 在成功演示数据上使用行为克隆训练，动作被离散化为 token 后用分类交叉熵优化。

## 代表工作

- [[RT-1]]: 大规模真机演示上的语言条件行为克隆。
