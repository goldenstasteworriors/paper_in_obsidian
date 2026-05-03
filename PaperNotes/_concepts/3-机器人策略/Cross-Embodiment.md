---
type: concept
aliases: [跨构型学习, Cross-Embodiment]
---

# Cross-Embodiment

## 定义
让策略、表示或控制模型在不同机器人形态之间共享知识并迁移能力的方法。

## 数学形式
$$
z = f_\theta(s^{(e)}, m^{(e)})
$$

## 核心要点
1. 关键在于把不同 embodiment 的状态、动作或身体部件映射到共享空间。
2. 难点是形态差异、传感器差异和控制接口差异同时存在。
3. 常见路线包括统一 body-part token、latent action 对齐和人到机器人 retargeting。

## 代表工作
- [[HEX]]: 用 canonical body-part slots 和共享 latent space 做 humanoid cross-embodiment 预训练。

## 相关概念
- [[Proprioception]]
- [[Whole-Body Controller]]
