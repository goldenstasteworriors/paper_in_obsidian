---
type: concept
aliases: [Diffusion Policy]
---

# Diffusion Policy

## 定义
把机器人动作生成建模为扩散 / 去噪过程的策略学习方法。

## 数学形式

$$
\mathbf{a}_{t}^{0} = f_{\theta}(\mathbf{o}, \mathbf{a}_{t}^{k}, k)
$$

## 核心要点

1. 擅长建模多模态动作分布。
2. 在 manipulation imitation learning 中很常见。
3. 推理延迟和多步去噪是部署时的主要痛点。

## 代表工作

- [[VolumeDP]]: 与 Diffusion Policy 类方法对比 3D 空间表征的收益。

## 相关概念

- [[Vision-Language-Action]]

