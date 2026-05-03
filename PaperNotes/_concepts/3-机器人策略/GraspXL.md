---
type: concept
aliases: [GraspXL]
---

# GraspXL

## 定义
面向单手型 dexterous grasping 的训练与评测基线，常被用来测试单手训练后对目标手型内任务的抓取能力。

## 数学形式

$$
\pi_{\theta}: o_t \mapsto a_t
$$

## 核心要点

1. 更偏 single-hand specialist baseline。
2. 不以跨 hand zero-shot transfer 为主要目标。
3. 经常作为 cross-embodiment 方法的对照组。

## 代表工作

- [[DexGrasp-Zero]]: 在单手训练协议下仍拿 GraspXL 作参照。

## 相关概念

- [[CrossDex]]
- [[YCB]]

