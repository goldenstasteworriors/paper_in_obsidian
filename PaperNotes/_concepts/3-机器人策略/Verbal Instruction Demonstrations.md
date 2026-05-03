---
title: "Verbal Instruction Demonstrations"
tags: [concept, robotics, language-supervision]
created: 2026-04-30
---

# Verbal Instruction Demonstrations

## 定义

[[Verbal Instruction Demonstrations]] 指人类专家不直接遥操作关节或末端执行器，而是用一系列语言子任务实时指导机器人低层策略完成任务，从而形成高层策略训练数据。

## 作用

- 提供“当前场景下下一步该做什么”的监督。
- 比低层遥操作更贴近高层规划和任务分解。
- 能让高层策略学习与已有低层策略相匹配的子任务分布。

## 代表工作

- [[Pi05]]: post-training 中加入 VI 数据，论文消融显示去掉 VI 会明显削弱高层推理表现。

## 相关概念

- [[Teleoperation]]
- [[Semantic Subtask Prediction]]
- [[Hierarchical VLA]]
- [[Vision-Language-Action Model]]
