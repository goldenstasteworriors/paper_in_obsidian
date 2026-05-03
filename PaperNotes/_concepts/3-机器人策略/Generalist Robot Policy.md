---
type: concept
aliases: [通用机器人策略, GRP, Generalist Robot Policy]
---

# Generalist Robot Policy

## 定义

Generalist Robot Policy 指在多任务、多环境、多机器人本体数据上训练，能够直接控制或快速适配不同机器人设置的低层视觉运动策略。

## 数学形式

$$
\pi_\theta(a_t \mid o_{\le t}, c)
$$

其中 $o_{\le t}$ 是观测历史，$c$ 是语言、目标图像或其他任务条件。

## 核心要点

1. 目标是复用跨任务和跨本体数据，而不是为每个机器人从头训练。
2. 难点在于统一不同传感器、动作空间、控制频率和任务条件。
3. 常见做法包括 transformer policy、动作块预测、语言/目标图像条件和大规模机器人数据预训练。

## 代表工作

- [[Octo]]: 开源通用机器人操作策略，支持新观测和新动作空间微调。

## 相关概念

- [[Open X-Embodiment]]
- [[Action Chunking]]
- [[Diffusion Policy]]
