---
type: concept
aliases: [RT-2-X, Robotics Transformer 2-X]
---

# RT-2-X

## 定义

RT-2-X 是将大规模视觉语言模型与机器人动作预测结合的跨机器人策略，用于语言条件操作控制。

## 数学形式

$$
\pi_\theta(a_t \mid I_t, \ell)
$$

其中 $I_t$ 是图像观测，$\ell$ 是语言指令。

## 核心要点

1. 模型规模远大于 RT-1-X 和 Octo。
2. 强项是借助 vision-language pretraining 提升语义泛化。
3. 公开可用性和可微调接口不如 Octo 直接。

## 代表工作

- [[Octo]]: 报告在 WidowX 和 RT-1 Robot 上接近 RT-2-X 的 zero-shot 表现。

## 相关概念

- [[Generalist Robot Policy]]
- [[RT-1-X]]
