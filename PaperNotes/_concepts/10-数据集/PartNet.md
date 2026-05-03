---
type: concept
aliases: [PartNet Dataset]
---

# PartNet

## 定义
一个提供细粒度物体部件分解与层级标注的大规模 3D 对象数据集。

## 数学形式
$$
\mathcal{O} = \{(S_i, P_i)\}_{i=1}^{N}
$$

其中 $S_i$ 表示对象形状，$P_i$ 表示其部件层级与语义标注。

## 核心要点
1. 强调对象的 part structure，而不只是整体几何。
2. 对 articulation、功能部件定位和机器人操作任务很有用。
3. 常被用来构造可交互对象类别。

## 代表工作
- [[BiPreManip]]: 利用具有明确功能部件的对象类别构造双臂 preparatory manipulation 任务。

## 相关概念
- [[ShapeNet]]
- [[Affordance]]
