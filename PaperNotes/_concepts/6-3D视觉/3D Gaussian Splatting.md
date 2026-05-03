---
type: concept
aliases: [3DGS]
---

# 3D Gaussian Splatting

## 定义

一种用大量带位置、尺度、方向、颜色和透明度参数的 3D Gaussian 来表示场景并进行实时可微渲染的方法。

## 数学形式

$$
I(\mathbf{r}) = \sum_{i} T_i \alpha_i G_i(\mathbf{r})
$$

## 核心要点

1. 用显式高斯基元表示三维场景，比 NeRF 类隐式体渲染更易实时。
2. 适合做视角合成、视觉 sim-to-real 和可微渲染。
3. 可以在表示空间直接做数据增强和随机化。

## 代表工作

- [[ViserDex]]: 用 3DGS 做视觉 sim-to-real 与高斯空间随机化。

## 相关概念

- [[6-3D视觉]]

