---
type: concept
aliases: [ShapeNet Dataset]
---

# ShapeNet

## 定义
一个大规模 3D CAD 模型数据集，覆盖多类日常物体和丰富的几何变化。

## 数学形式
$$
\mathcal{D} = \{S_i\}_{i=1}^{N}
$$

## 核心要点
1. 提供对象级几何多样性，适合做 seen / unseen split。
2. 常用作仿真对象库或 3D 表征学习的数据源。
3. 在机器人操作中常和 part-level 标注数据配合使用。

## 代表工作
- [[BiPreManip]]: 用于构造具有形状变化的训练对象和 unseen 测试对象。

## 相关概念
- [[PartNet]]
- [[PointNet++]]
