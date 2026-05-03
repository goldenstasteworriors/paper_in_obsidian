---
type: concept
aliases: [MPM, 物质点法]
---

# Material Point Method

## 定义

一种同时结合粒子表示与背景网格计算的数值方法，常用于可变形体、接触和连续介质模拟；在机器人里也可以借来做形态离散表示。

## 数学形式

$$
m_p \frac{d\mathbf{v}_p}{dt} = \mathbf{f}_p,\qquad
\mathbf{x}_p^{t+1}=\mathbf{x}_p^{t}+\Delta t\,\mathbf{v}_p^{t+1}
$$

## 核心要点

1. 物体由一组 material points 承载质量、速度和状态。
2. 计算时常借助背景网格做力和动量更新。
3. 对接触、形变和复杂拓扑变化比较友好。

## 代表工作

- [[MorphoGuard]]: 借用 material point 思路表示机器人 morphology，并学习从形态到关节命令的映射。

## 相关概念

- [[Whole-Body Controller]]
- [[SE(3)]]
