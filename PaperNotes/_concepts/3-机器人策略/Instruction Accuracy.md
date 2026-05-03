---
type: concept
aliases: [指令准确率, IA]
---

# Instruction Accuracy

## 定义

Instruction Accuracy 是机器人高层策略输出是否符合用户意图和当前视觉观察的人工评估指标。

## 数学形式

$$
\mathrm{IA}=\frac{\#\text{correct high-level predictions}}{\#\text{all high-level predictions}}
$$

## 核心要点

1. 评估的是高层命令与人类意图的对齐，而不是最终物理成功率。
2. 对 flat 策略可由评估者根据行为意图近似打分。
3. 常与任务进度一起报告，区分“想对了”和“做成了”。

## 代表工作

- [[HiRobot]]: 用 IA 衡量高层策略是否正确理解复杂 prompt 和实时反馈。

## 相关概念

- [[Task Progress]]
- [[Hierarchical VLA]]
- [[Robot Policy]]
