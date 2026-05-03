---
title: "RT-1"
type: concept
tags: [robot-policy, vision-language-action, transformer]
created: 2026-04-28
---

# RT-1

RT-1 是 Google 提出的 Robotics Transformer 1，一种面向真实机器人控制的语言条件 [[Vision-Language-Action]] 策略。它用 [[FiLM]] 条件化 [[EfficientNet]] 编码图像和指令，用 [[TokenLearner]] 压缩视觉 token，再用 [[Transformer]] 输出离散化动作。

## 关键点

- 训练数据为 13 台真实机器人采集的约 130k 演示，覆盖 744 条指令。
- 设计重点是同时满足高容量、多任务泛化和 3 Hz 真机闭环控制。
- 代表了后续 [[RT-1-X]]、[[RT-2-X]] 等大规模机器人策略路线的起点。

## 代表工作

- [[RT-1]]: Robotics Transformer for Real-World Control at Scale.
