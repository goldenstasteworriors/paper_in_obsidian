---
title: "Open-World Generalization"
tags: [concept, robotics, generalization]
created: 2026-04-30
---

# Open-World Generalization

## 定义

[[Open-World Generalization]] 指机器人或具身智能系统在训练分布之外的真实环境中仍能完成任务的能力，通常包含新场景、新布局、新物体、新任务组合和意外物理条件。

## 关键点

- 不只是 zero-shot object recognition，而是感知、语义推理、动作执行和失败恢复的联合泛化。
- 在机器人中尤其困难，因为环境变化会同时改变视觉输入、可操作物体、接触动力学和任务阶段结构。
- 常见评估方式包括未见家庭、未见房间、未见物体类别和长程任务。

## 代表工作

- [[Pi05]]: 通过异质数据共训和高层子任务预测，在未见真实家庭中执行厨房和卧室清理任务。

## 相关概念

- [[Vision-Language-Action Model]]
- [[Co-training]]
- [[Cross-Embodiment]]
- [[Mobile Manipulator]]
