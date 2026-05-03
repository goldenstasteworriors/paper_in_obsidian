---
type: concept
aliases: [Kullback-Leibler Divergence, KL散度]
---

# KL Divergence

## 定义
衡量两个概率分布差异的非对称信息量，在变分推断中常用来约束近似后验逼近先验。

## 数学形式
$$
D_{\mathrm{KL}}(q(z)\|p(z)) = \int q(z)\log \frac{q(z)}{p(z)}\,dz
$$

## 核心要点
1. KL 越小，表示近似分布越接近目标分布。
2. VAE / cVAE 里常作为潜变量正则项。
3. 它约束的是分布形状，而不是单个样本点误差。

## 代表工作
- [[BiPreManip]]: 用 KL 项约束 gripper orientation 和 object pose 的 cVAE 潜变量分布。

## 相关概念
- [[cVAE]]
- [[Geodesic Loss]]
