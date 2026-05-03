---
title: "Semantic Subtask Prediction"
tags: [concept, robotics, planning]
created: 2026-04-30
---

# Semantic Subtask Prediction

## 定义

[[Semantic Subtask Prediction]] 指机器人策略根据当前观测和高层任务命令，预测下一步应执行的短语义子任务，例如 "pick up the plate" 或 "open the drawer"。

## 作用

- 把长程任务拆成更短、更可执行的局部目标。
- 为低层策略提供比原始高层命令更具体的条件。
- 让模型在推理时形成类似 [[Chain-of-Thought Prompting]] 的中间语义步骤。

## 代表工作

- [[Pi05]]: 用人工标注子任务、bounding box 和语言指导示教训练同一个 VLA 同时做高层和低层推理。

## 相关概念

- [[Hierarchical VLA]]
- [[Vision-Language-Action Model]]
- [[Action Chunking]]
- [[Verbal Instruction Demonstrations]]
