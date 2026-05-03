---
type: concept
aliases: [Special Euclidean Group, 刚体位姿群]
---

# SE(3)

## 定义
三维空间中刚体的旋转和平移组成的李群，是机器人位姿与动作最常见的表示空间。

## 数学形式
$$
SE(3) = \left\{
\begin{bmatrix}
R & t \\
0 & 1
\end{bmatrix}
\;\middle|\;
R \in SO(3),\; t \in \mathbb{R}^3
\right\}
$$

## 核心要点
1. 同时表示位置和平移，适合抓手动作和物体位姿。
2. 组合运算天然对应刚体变换叠加。
3. 机器人抓取、位姿估计和重定位问题都会落到这个空间里。

## 代表工作
- [[BiPreManip]]: 主臂动作、辅臂动作和物体重定位都在 SE(3) 中表示与监督。

## 相关概念
- [[Geodesic Loss]]
- [[PointNet++]]
