---
type: concept
aliases: [Motion Latent Diffusion, MLD]
---

# MLD

## 定义
面向人体动作生成的 latent diffusion 模型，通常用于 text-to-motion 或 motion prior 学习。

## 数学形式

$$
\mathbf{z}_{0} = f_{\theta}(\mathbf{z}_{k}, c, k)
$$

## 核心要点

1. 在 latent 空间里做扩散，比直接在高维动作空间去噪更稳定。
2. 常被用于 text-conditioned human motion generation。
3. 落到 humanoid 执行时，常需要额外物理约束或 tracking policy。

## 代表工作

- [[RoboForge]]: 以 MLD 类 motion generator 为基础，再用物理优化闭环强化执行性。

## 相关概念

- [[Motion Primitive]]
