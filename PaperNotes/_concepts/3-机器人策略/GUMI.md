---
type: concept
aliases: [GUI Manipulation Interface, 图形化机器人操纵接口]
created: 2026-09-11
---

# GUMI

## 定义

Show-Harness中的GUI Manipulation Interface：让人和智能体通过同一离散控制界面采集机器人示范。

## 数学形式

$$
\mathcal D=\{(o_t,a_t)\}_{t=1}^{N}.
$$

o为动作前观测，a为语义动作，N为样本数；还可同时保存低层状态与命令以转换监督。

## 核心要点

1. 支持按钮、键盘、排队动作和人介入纠错，不要求专用主从遥操设备。
2. 同一接口可覆盖仿真、真机、单臂和双臂，依赖正确的机器人解释器。
3. 按键采集的轨迹可能偏向离散策略，比较连续策略时应审查监督转换及采数偏置。

## 代表工作

- [[Show-Harness]]：真实164条及仿真230条示范。

## 相关概念

- [[Semantic Action Interface]]
- [[Embodied Harness]]
