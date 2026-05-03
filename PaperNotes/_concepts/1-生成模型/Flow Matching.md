---
type: concept
aliases: [流匹配, Flow Matching]
---

# Flow Matching

## 定义
一种通过学习连续时间速度场来把噪声分布映射到目标分布的生成建模方法。

## 数学形式
$$
\mathcal{L} = \lVert v_\theta(x_\lambda, \lambda) - (x_1 - x_0) \rVert_2^2
$$

## 核心要点
1. 训练时直接监督速度场，而不是显式逆扩散每一步噪声。
2. 常用于图像、视频和动作序列生成。
3. 在机器人里常被拿来做 action chunk 的去噪或连续轨迹生成。

## 代表工作
- [[HEX]]: 用 flow-matching action head 预测 high-level whole-body manipulation 动作块。

## 相关概念
- [[Diffusion Policy]]
- [[Action Chunking]]
