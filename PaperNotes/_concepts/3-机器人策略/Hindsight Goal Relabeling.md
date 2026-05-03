---
type: concept
aliases: [Hindsight Goal Relabeling, 事后目标重标注, hindsight goal relabeling]
---

# Hindsight Goal Relabeling

## 定义

Hindsight Goal Relabeling 是把轨迹未来某个状态重新标为目标，从而构造目标条件学习样本的方法。

## 数学形式

$$
g \sim \operatorname{Uniform}(\{o_{t+1},\ldots,o_T\})
$$

## 核心要点

1. 可在缺少人工语言标注时生成目标图像条件。
2. 常用于 goal-conditioned imitation learning 或 reinforcement learning。
3. 对机器人数据尤其有用，因为很多 demonstration 轨迹天然包含成功后的目标状态。

## 代表工作

- [[Octo]]: 从未来状态均匀采样目标图像，并随机 drop language/goal，使模型同时支持语言和目标图像条件。

## 相关概念

- [[Generalist Robot Policy]]
- [[Open X-Embodiment]]
