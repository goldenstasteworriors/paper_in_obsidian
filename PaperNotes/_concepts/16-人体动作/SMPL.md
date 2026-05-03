---
tags: [concept, human-motion]
created: 2026-03-11
---

# SMPL

`SMPL` 是一种参数化 3D 人体模型，用统一的姿态和形状参数表示全身动作。

## 为什么重要

- 它让不同数据源的人体动作能落到同一种表示里。
- 很多 humanoid imitation、motion generation、retargeting 工作都基于它。
- 在 [[ZeroWBC]] 中，SMPL 动作先被离散成 motion tokens，再 retarget 到机器人。

## 相关概念

- [[MoCap]]
- [[HumanML3D]]

