---
title: "SayCan"
type: concept
tags: [robot-planning, language-model, affordance]
created: 2026-04-28
---

# SayCan

SayCan 是一种将语言模型规划能力和机器人 affordance 评分结合的长程任务框架。语言模型提出候选低层技能序列，机器人策略或 value/affordance 模型判断哪些技能在当前场景可执行。

## 在 RT-1 中

[[RT-1]] 被用作 SayCan 的低层 skill policy，在真实厨房长程任务中相比 [[Gato]] 和 [[BC-Z]] 有更高执行成功率。

## 代表工作

- [[RT-1]]: SayCan w/ RT-1 在 Kitchen1 和 Kitchen2 长程任务中达到 67% execution success。
