---
type: concept
aliases: [Robotics Transformer X, 跨本体机器人策略]
---

# RT-X

## 定义
RT-X 是在多机器人、多数据集、多任务数据上联合训练的机器人策略族，代表性实例包括 [[RT-1]]-X 和 [[RT-2]]-X。

## 数学形式

$$
\pi_\theta(a_t \mid o_{\leq t}, l, d)
$$

## 核心要点
1. 输入通常包含视觉观测历史 $o_{\leq t}$、语言指令 $l$ 和隐式数据域/机器人信息 $d$。
2. 输出离散化末端执行器动作，可由不同机器人按各自归一化和控制接口解释。
3. 关键挑战是跨机器人本体差异、动作语义差异和数据分布不均衡。

## 代表工作
- [[RT-X]]: 基于 [[Open X-Embodiment]] 的跨机器人策略基线。

## 相关概念
- [[X-Embodiment]]
- [[RT-1]]
- [[RT-2]]
- [[Action Tokenization]]
