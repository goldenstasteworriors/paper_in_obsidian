---
type: concept
aliases: [Dataset Aggregation]
---

# DAgger

## 定义

一种通过反复收集策略访问到的状态并让专家纠正标签，来缓解模仿学习 compounding error 的数据聚合算法。

## 数学形式

$$
\mathcal{D}_{k+1} = \mathcal{D}_k \cup \{(s, \pi^\*(s))\}
$$

## 核心要点

1. 目标是修复行为克隆在分布外状态上的崩溃。
2. 关键代价是持续依赖专家在线标注。
3. 常用于机器人模仿学习和 sequential decision making。

## 代表工作

- [[WM-DAgger]]: 用 world model 替代部分人工纠错数据。

## 相关概念

- [[Imitation Learning]]

