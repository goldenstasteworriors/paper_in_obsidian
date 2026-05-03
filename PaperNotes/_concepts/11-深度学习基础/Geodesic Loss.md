---
type: concept
aliases: [测地损失, rotation geodesic loss]
---

# Geodesic Loss

## 定义
在旋转流形上衡量两个旋转矩阵之间最短角距离的损失函数。

## 数学形式
$$
\mathcal{L}_{\mathrm{geo}}(R, R^*)=
\arccos\!\left(\frac{\operatorname{Tr}(R^\top R^*)-1}{2}\right)
$$

## 核心要点
1. 比欧氏距离更适合监督姿态和旋转。
2. 与 SO(3) / SE(3) 表示天然兼容。
3. 常用于 6D pose estimation、gripper orientation prediction 和 rigid body control。

## 代表工作
- [[BiPreManip]]: 用 geodesic loss 监督主臂和辅臂的抓手姿态。

## 相关概念
- [[SE(3)]]
- [[KL Divergence]]
