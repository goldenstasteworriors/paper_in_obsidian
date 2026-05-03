---
type: concept
aliases: [本体感觉, Proprioception]
---

# Proprioception

## 定义
机器人对自身状态的内部感知，通常包括关节位置、速度、加速度、IMU 和触觉等信号。

## 数学形式
$$
s_t = [q_t, \dot{q}_t, \ddot{q}_t, \mathrm{imu}_t, \tau_t]
$$

## 核心要点
1. 它决定控制器是否知道“自己现在在哪、动得多快、受了什么力”。
2. whole-body 控制尤其依赖结构化 proprioception，而不只是末端状态。
3. 跨 embodiment 学习时，本体感觉维度和语义往往不一致。

## 代表工作
- [[HEX]]: 把异构 proprioceptive 信号映射到 canonical body-part latent slots。

## 相关概念
- [[Cross-Embodiment]]
- [[Whole-Body Controller]]
