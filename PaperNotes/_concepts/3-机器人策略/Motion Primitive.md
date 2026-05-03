---
type: concept
aliases: [动作原语, Motion Primitive]
---

# Motion Primitive

## 定义
对复杂动作空间做更小、更稳定的语义分解，用少量可解释原语描述控制命令。

## 数学形式

$$
\boldsymbol{\alpha}_{i} = [\Delta_{\text{flex}}, \Delta_{\text{abd}}, \Delta_{\text{rot}}]^{\top}
$$

## 核心要点

1. 可以把不同 embodiment 的动作统一到共同语义空间。
2. 比直接回归 raw joint action 更利于结构对齐。
3. 需要配合 hand-specific mapping 才能真正执行。

## 代表工作

- [[DexGrasp-Zero]]: 把 grasp 控制统一到 flexion / abduction / axial rotation 三轴原语。

## 相关概念

- [[MAGCN]]
- [[URDF]]

