---
type: concept
aliases: [实时动作分块, RTC]
---

# Real-Time Chunking

## 定义

用已执行或即将执行的动作作为新动作块前缀来条件化预测，从而掩蔽策略推理延迟并保持连续控制。

## 核心要点

1. 训练时模拟部署延迟。
2. 推理期间机器人执行已知前缀，新动作只替换后缀。

## 代表工作

- [[EgoSteer]]：32 步预测保留 12 步，其中 4 步覆盖延迟、8 步为新动作。

## 相关概念

- [[Action Chunking]]
- [[Conditional Flow Matching]]
