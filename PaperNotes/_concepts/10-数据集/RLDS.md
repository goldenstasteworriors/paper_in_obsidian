---
type: concept
aliases: [Reinforcement Learning Datasets, tfrecord robot dataset format]
---

# RLDS

## 定义
RLDS 是一种用于存储和共享强化学习/机器人学习 episode 数据的数据格式，常以 tfrecord 序列化保存。

## 数学形式

$$
\mathcal{D} = \{\tau_i\}_{i=1}^{N},\quad \tau_i = \{(o_t, a_t, r_t, d_t)\}_{t=1}^{T_i}
$$

## 核心要点
1. 以 episode/trajectory 为基本单位保存观测、动作、奖励、终止标记和元数据。
2. 支持多模态观测，例如 RGB、深度、点云和语言标注。
3. 适合将不同实验室的数据统一到可批量加载的训练管线。

## 代表工作
- [[RT-X]]: 使用 RLDS 统一 [[Open X-Embodiment]] 数据集。

## 相关概念
- [[Open X-Embodiment]]
- [[Imitation Learning]]
