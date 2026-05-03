---
type: concept
aliases: [Unified Robot Description Format, URDF]
---

# URDF

## 定义
机器人结构描述格式，用于表示 link、joint、轴向、限制和几何层级关系。

## 数学形式

$$
\mathcal{R} = (\mathcal{L}, \mathcal{J}, \mathcal{T}, \mathcal{C})
$$

## 核心要点

1. 提供 link length、joint limit、axis direction 等结构先验。
2. 常用于仿真、运动学求解和机器人模型解析。
3. 在 DexGrasp-Zero 中直接转成 physical graph features。

## 代表工作

- [[DexGrasp-Zero]]: 用 URDF 派生的 physical priors 约束跨手型策略。

## 相关概念

- [[MAGCN]]
- [[Motion Primitive]]

