---
type: concept
aliases: [Open X-Embodiment, Open-X, OXE, Open X-Embodiment Dataset]
---

# Open X-Embodiment

## 定义

Open X-Embodiment 是一个聚合多机器人、多任务、多场景操作数据的大规模机器人学习数据集。

## 数学形式

$$
\mathcal{D}=\{(o_t, a_t, c)_t\}_{i=1}^{N}
$$

其中 $o_t$ 为观测，$a_t$ 为动作，$c$ 为语言、目标图像或任务条件。

## 核心要点

1. 汇集来自多个机构和机器人平台的 demonstration 数据。
2. 数据异质性包括相机配置、语言标注、动作空间和机器人本体。
3. 适合训练跨本体的通用机器人策略，但需要处理数据质量和采样权重。

## 代表工作

- [[Octo]]: 从 Open X-Embodiment 中筛选 25 个子数据集、800k episodes 用于预训练。

## 相关概念

- [[Generalist Robot Policy]]
- [[RT-1-X]]
