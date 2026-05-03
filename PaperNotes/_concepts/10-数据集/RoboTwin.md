---
type: concept
aliases: [RoboTwin 2.0, RoboTwin]
---

# RoboTwin

## 定义
面向机器人操控与泛化评测的 benchmark / 数据集，用于比较策略在多任务场景中的表现。

## 数学形式
$$
\mathrm{SuccessRate} = \frac{\#\text{successful trials}}{\#\text{all trials}}
$$

## 核心要点
1. 常用于比较 WAM、VLA 和 manipulation policy。
2. 关注多任务成功率和泛化表现。
3. 经常出现在数据效率与鲁棒性实验中。

## 代表工作
- [[GigaWorld-Policy]]: 在 RoboTwin 2.0 上报告显著提升。
- [[The Compression Gap]]: 用 manipulation benchmark 分析表征瓶颈。

## 相关概念
- [[LIBERO]]
- [[Vision-Language-Action]]
