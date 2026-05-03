---
type: concept
aliases: [RT-1-X, Robotics Transformer 1-X]
---

# RT-1-X

## 定义

RT-1-X 是基于 Open X-Embodiment 数据训练的跨机器人操作策略，是早期开放 checkpoint 的 generalist robot policy baseline。

## 数学形式

$$
\pi_\theta(a_t \mid o_t, \ell)
$$

其中 $\ell$ 是语言指令，$o_t$ 是机器人视觉观测。

## 核心要点

1. 面向语言条件机器人操作。
2. 在多个机器人本体上进行跨数据集训练。
3. 相比 Octo，输入输出接口和新动作空间微调灵活性较弱。

## 代表工作

- [[Octo]]: 在 zero-shot 评测中以 RT-1-X 为主要开放基线。

## 相关概念

- [[Open X-Embodiment]]
- [[Generalist Robot Policy]]
