---
type: concept
aliases: [R3M, Reusable Representations for Robotic Manipulation]
---

# R3M

## 定义

R3M 是从大规模人类活动视频中学习可复用机器人视觉表征的方法，用于提升下游操作策略的数据效率。

## 数学形式

$$
a_t = \pi_\theta(f_{\mathrm{R3M}}(I_t), l)
$$

## 核心要点

1. 关注从人类视频中学习通用视觉表征。
2. 下游机器人策略通常在冻结或微调表征的基础上训练动作头。
3. 与 VLA 不同，R3M 本身不是自然语言生成模型，也不直接输出动作 token。

## 代表工作

- [[RT-2]]: 使用 R3M 作为预训练视觉表征基线。

## 相关概念

- [[Vision-Language Model]]
- [[Behavioral Cloning]]
- [[RT-1]]
