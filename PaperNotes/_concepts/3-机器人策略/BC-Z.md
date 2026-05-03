---
title: "BC-Z"
type: concept
tags: [imitation-learning, robot-policy]
created: 2026-04-28
---

# BC-Z

BC-Z 是一种语言条件行为克隆机器人策略，曾作为 SayCan 系统中的低层操作策略。

## 与 RT-1 的关系

[[RT-1]] 将 BC-Z 作为主要 baseline。BC-Z 使用 ResNet 风格前馈策略和连续动作，不使用历史帧 Transformer 序列建模，也没有 RT-1 的离散动作 token 设计。

## 代表工作

- [[RT-1]]: BC-Z baseline 在 seen task 上为 72%，RT-1 为 97%。
