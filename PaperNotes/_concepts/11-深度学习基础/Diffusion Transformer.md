---
type: concept
aliases: [DiT, 扩散 Transformer]
---

# Diffusion Transformer

## 定义
用 Transformer 作为去噪网络的扩散模型架构，常用于图像、视频和机器人动作生成。

## 数学形式
$$
\epsilon_\theta(x_t, t, c)
$$

## 核心要点
1. 用自注意力建模长程依赖，适合时空序列。
2. 可作为图像、视频、动作扩散模型的统一骨干。
3. 在机器人中常与条件观测、语言或未来视频预测结合。

## 代表工作
- [[MV-VDP]]: 用于多视角视频扩散建模。
- [[GigaWorld-Policy]]: 依赖视频生成预训练骨干提供动态先验。

## 相关概念
- [[Diffusion Policy]]
- [[Vision-Language-Action]]
