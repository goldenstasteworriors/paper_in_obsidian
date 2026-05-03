---
title: "Co-training"
tags: [concept, training, multimodal-learning]
created: 2026-04-30
---

# Co-training

## 定义

[[Co-training]] 在这里指把不同来源、不同模态或不同任务形式的数据放入同一个模型训练流程中，使模型从异质监督中学习可迁移能力。

## 在 VLA 中的作用

- 机器人动作数据提供低层控制能力。
- Web 图文数据提供物体、场景和语言语义。
- 高层子任务标注提供长程任务分解能力。
- 跨 embodiment 数据提供动作和技能迁移。

## 代表工作

- [[Pi05]]: 同时使用 MM、ME、CE、HL、WD 和 VI 数据源训练一个统一 [[Vision-Language-Action Model]]。

## 相关概念

- [[Multimodal Pretraining]]
- [[Transfer Learning]]
- [[Cross-Embodiment]]
- [[Vision-Language-Action Model]]
