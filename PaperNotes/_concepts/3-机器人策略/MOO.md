---
type: concept
aliases: [MOO, object-centric VLM policy]
---

# MOO

## 定义

MOO 是一种物体中心的机器人策略基线，使用视觉语言模型提供物体语义信息，再将其接入低层策略进行动作预测。

## 数学形式

$$
a_t = \pi_\theta(o_t, l, \phi_{\mathrm{VLM}}(o_t, l))
$$

## 核心要点

1. 通过 VLM 提供物体级语义，而不是端到端共享全部视觉语言参数。
2. 可测试“外部语义模块 + 机器人策略”是否足以带来泛化。
3. 与 VLA 相比，语义和动作学习的耦合更弱。

## 代表工作

- [[RT-2]]: 将 MOO 作为 real-world manipulation 泛化基线。

## 相关概念

- [[Vision-Language Model]]
- [[Vision-Language-Action]]
- [[RT-1]]
