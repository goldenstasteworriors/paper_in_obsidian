---
type: concept
aliases: [CrossDex]
---

# CrossDex

## 定义
一类 cross-embodiment dexterous grasping 方法，通常通过中间动作目标和后续 retargeting 在不同手型间迁移抓取策略。

## 数学形式

$$
\text{intermediate target} \rightarrow \text{hand-specific retargeting} \rightarrow \text{physical joint command}
$$

## 核心要点

1. 优点是把动作语义先统一到中间空间。
2. 缺点是 retargeting 可能引入运动学不可行解。
3. 在 unseen hand 上容易因为 joint limit 和 link geometry 不匹配而掉性能。

## 代表工作

- [[DexGrasp-Zero]]: 直接对着 CrossDex 路线开刀，去掉了 trainable retargeting。

## 相关概念

- [[Motion Primitive]]
- [[URDF]]

