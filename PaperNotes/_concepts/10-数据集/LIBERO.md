---
type: concept
aliases: [LIBERO benchmark]
---

# LIBERO

## 定义
机器人 manipulation 常用 benchmark，用于评估多任务学习、泛化和语言条件控制能力。

## 数学形式
$$
\mathrm{AvgSuccess} = \frac{1}{N}\sum_{i=1}^{N} \mathrm{SuccessRate}_i
$$

## 核心要点
1. 是 VLA、Diffusion Policy 和 WAM 路线常见对比平台。
2. 适合分析 encoder、action representation 和泛化能力。
3. 经常与 RoboTwin、Meta-World 一起构成对比矩阵。

## 代表工作
- [[The Compression Gap]]: 用于分析离散 action token 的压缩瓶颈。
- [[SV-VLA]]: 作为 VLA 控制实验数据集之一。

## 相关概念
- [[RoboTwin]]
- [[Meta-World]]
