---
type: concept
aliases: [任务进度, TP]
---

# Task Progress

## 定义

Task Progress 是长程机器人任务中已正确完成对象或子目标所占比例，用于比二值成功率更细粒度地衡量完成程度。

## 数学形式

$$
\mathrm{TP}=\frac{\#\text{objects correctly placed or configured}}{\#\text{target objects or configurations}}
$$

## 核心要点

1. 适合清理、装配、购物等多对象长程任务。
2. 可反映部分完成，即使最终任务未完全成功。
3. 需要明确定义每个对象或配置的正确终态。

## 代表工作

- [[HiRobot]]: 用 TP 评估 table bussing、sandwich making 和 grocery shopping 的长程完成度。

## 相关概念

- [[Instruction Accuracy]]
- [[Robot Policy]]
- [[Hierarchical VLA]]
