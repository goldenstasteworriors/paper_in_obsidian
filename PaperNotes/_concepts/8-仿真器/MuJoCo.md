---
type: concept
aliases: [MuJoCo, Multi-Joint dynamics with Contact]
---

# MuJoCo

## 定义
广泛用于机器人控制与 manipulation 研究的物理仿真器。

## 数学形式
$$
M(q)\ddot{q} + C(q,\dot{q})\dot{q} + g(q) = \tau + J^\top f
$$

## 核心要点
1. 支持刚体动力学与接触模拟。
2. 是 manipulation、强化学习和控制论文常见底座。
3. 许多 benchmark，如 Meta-World，都依赖 MuJoCo。

## 代表工作
- [[MV-VDP]]: manipulation 实验生态的重要基础。
- [[SV-VLA]]: 相关操控评测环境通常依托 MuJoCo 类仿真。

## 相关概念
- [[Meta-World]]
- [[Diffusion Policy]]
