---
type: concept
aliases: [Conditional Variational Autoencoder, 条件变分自编码器]
---

# cVAE

## 定义
在变分自编码器中加入条件变量的生成模型，用于在给定上下文时学习多模态输出分布。

## 数学形式
$$
\mathcal{L}_{\text{cVAE}} =
\mathbb{E}_{q_\phi(z \mid x, c)}[\log p_\theta(x \mid z, c)] -
D_{\mathrm{KL}}(q_\phi(z \mid x, c)\|p(z))
$$

## 核心要点
1. 适合一个输入对应多个合理输出的场景。
2. 常用于姿态预测、动作生成和多模态策略建模。
3. KL 项保证训练和推理时潜变量分布一致。

## 代表工作
- [[BiPreManip]]: 用 cVAE 为主臂和辅臂采样 gripper orientation。

## 相关概念
- [[KL Divergence]]
- [[Geodesic Loss]]
