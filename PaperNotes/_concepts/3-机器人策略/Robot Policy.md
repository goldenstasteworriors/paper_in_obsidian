---
title: "Robot Policy"
type: concept
tags: [robot-policy, policy-learning]
created: 2026-04-28
---

# Robot Policy

Robot Policy 指机器人在给定观测、目标或语言指令条件下选择动作的函数或概率分布。它可以是显式控制器、学习到的神经网络策略，或两者的组合。

$$
a_t \sim \pi(\cdot \mid o_{\le t}, g)
$$

## 在 RT-1 中

[[RT-1]] 将机器人策略建模为语言条件视觉策略：输入自然语言指令和图像历史，输出离散化手臂、底盘和终止动作 token。

## 代表工作

- [[RT-1]]: 用 [[Transformer]] 参数化大规模语言条件 robot policy。
