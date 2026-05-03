---
tags: [concept, 3d-vision]
created: 2026-03-12
---

# RANSAC

`RANSAC` 是 `Random Sample Consensus`，一种通过随机采样剔除离群点并估计模型参数的经典鲁棒算法。

## 为什么重要

- 在 3D 配准、位姿估计和几何拟合里几乎无处不在。
- 它通常作为传统几何管线中的稳定基线。
- 在 [[TacLoc]] 这样的触觉配准任务里，RANSAC 代表最经典的鲁棒拟合思路。
