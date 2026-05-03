---
type: concept
aliases: [Yale-CMU-Berkeley Objects, YCB]
---

# YCB

## 定义
机器人操作领域常用的标准物体集合与 benchmark，覆盖大量日常抓取对象。

## 数学形式

$$
\mathcal{D}_{\text{YCB}} = \{o_1, o_2, \dots, o_N\}
$$

## 核心要点

1. 物体多样性高，适合评测 grasp 和 manipulation 泛化。
2. 常被用于 sim-to-real 和 cross-embodiment grasp benchmark。
3. DexGrasp-Zero 在 45-object YCB split 上报告主结果。

## 代表工作

- [[DexGrasp-Zero]]: 使用 45-object YCB split 验证 seen / unseen hand transfer。

## 相关概念

- [[GraspXL]]
- [[DexGrasp-Zero]]

