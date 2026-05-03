---
type: concept
aliases: [Teacher-Student Distillation for Sim-to-Real, Privileged Distillation]
---

# Privileged Distillation

## 定义
先让 teacher 在仿真中使用真机不可见的 privileged state，再把行为蒸馏给只依赖可观测量的 student。

## 数学形式

$$
\mathcal{L}_{\text{distill}} = \|\pi_{\text{student}}(o_t)-\pi_{\text{teacher}}(o_t, z_t^{\text{priv}})\|_2^2
$$

## 核心要点

1. teacher 可以使用 contact、force、state 等 privileged signals。
2. student 只看部署时真实可用的观测。
3. 常用于 sim-to-real，特别适合 tactile / contact 不可直接测量的任务。

## 代表工作

- [[DexGrasp-Zero]]: 用 privileged teacher 的 contact / force 信息蒸馏 student。

## 相关概念

- [[MAGCN]]
- [[URDF]]

