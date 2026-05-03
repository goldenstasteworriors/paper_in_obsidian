---
type: concept
aliases: [PointNet Plus Plus]
---

# PointNet++

## 定义
一种分层点云编码网络，通过局部邻域采样和特征聚合学习 3D 点集的几何表示。

## 数学形式
$$
f_{\text{local}} = \operatorname{Pool}\left(\phi\left(\mathcal{N}(p_i)\right)\right)
$$

## 核心要点
1. 通过 set abstraction 逐层扩大感受野。
2. 同时支持 per-point feature 和 global feature。
3. 在点云分类、分割和操作策略中都很常见。

## 代表工作
- [[BiPreManip]]: 用于提取物体点云的局部与全局几何特征。

## 相关概念
- [[Affordance]]
- [[SE(3)]]
