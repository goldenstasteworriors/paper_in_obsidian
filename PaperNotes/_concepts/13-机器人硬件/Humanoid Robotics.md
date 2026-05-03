---
type: concept
aliases: [人形机器人, Humanoid Robotics]
---

# Humanoid Robotics

## 定义
以接近人体形态的多自由度机器人为载体，研究其感知、控制、运动与操作能力的方向。

## 数学形式
$$
x_t = [q_t^{body}, q_t^{hands}, q_t^{head}, c_t]
$$

## 核心要点
1. 核心难点是高自由度、接触切换、平衡约束和多部位协同。
2. 与固定基座 manipulation 相比，whole-body coordination 是本质增量。
3. 真实落地往往需要高层策略与低层稳定控制共同工作。

## 代表工作
- [[HEX]]: 面向 full-sized bipedal humanoid 的 whole-body VLA 框架。

## 相关概念
- [[Whole-Body Controller]]
- [[Cross-Embodiment]]
