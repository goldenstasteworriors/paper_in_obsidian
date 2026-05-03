---
title: "FAST+"
aliases: [FAST Plus, Universal Robot Action Tokenizer]
tags: [concept, action-tokenization, robot-policy]
created: 2026-04-29
---

# FAST+

FAST+ 是 [[FAST]] 论文提出的通用机器人动作 tokenizer。它基于 FAST 的 DCT + BPE 框架，在约 1M 条真实机器人动作轨迹上训练 BPE 字典，目标是在不同机器人形态、动作空间、动作维度和控制频率之间复用。

## 关键特点

- 支持单臂、双臂、移动平台、灵巧手、humanoid 等多种 embodiment。
- 覆盖关节空间、末端执行器空间、相机坐标系动作等多种 action space。
- 作为黑盒 tokenizer 接入 [[Vision-Language-Action Model]]，不需要修改自回归 VLA backbone。

## 代表工作

- [[FAST]]: 提出 FAST+ 并验证其在未见机器人数据集上的压缩泛化能力。
