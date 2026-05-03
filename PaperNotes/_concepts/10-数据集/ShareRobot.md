---
type: concept
aliases: [ShareRobot Dataset, ShareRobot 数据集]
---

# ShareRobot

## 定义
ShareRobot 是用于机器人操作的异构数据集，标注 task planning、object affordance 和 end-effector trajectory，用来训练从抽象指令到具体动作表达的机器人模型。

## 数学形式
affordance 标注为 bounding box：

$$
A = \{l(x), l(y), r(x), r(y)\}
$$

trajectory 标注为 2D waypoint 序列：

$$
P_{t:N} = \{(x_i, y_i) \mid i=t,\ldots,N\}
$$

## 核心要点
1. 从 [[Open X-Embodiment]] 中筛选高质量成功 demonstrations。
2. 使用 Gemini 生成低层任务分解，再由人工审查。
3. 包含约 1,028,060 个 planning QA pairs，并额外标注 affordance 与 trajectory。

## 代表工作
- [[RoboBrain]]: 提出并使用 ShareRobot 训练机器人脑模型。

## 相关概念
- [[Open X-Embodiment]]
- [[RoboVQA]]
- [[Affordance]]
- [[Trajectory Prediction]]
