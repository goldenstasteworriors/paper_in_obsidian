---
title: "Gato"
type: concept
tags: [generalist-agent, transformer, robot-policy]
created: 2026-04-28
---

# Gato

Gato 是 DeepMind 提出的 generalist agent，用单一 Transformer 处理文本、图像、游戏和机器人等多种序列任务。

## 与 RT-1 的关系

[[RT-1]] 将 Gato 风格的序列建模思想用于真实机器人控制，但加入语言早融合、[[TokenLearner]]、离散动作设计和实时推理约束。在 RT-1 论文中，Gato 架构被重训为同规模 baseline。

## 代表工作

- [[RT-1]]: Gato baseline 在 seen/unseen/distractor/background 上均低于 RT-1。
