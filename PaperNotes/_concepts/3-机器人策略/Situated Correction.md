---
type: concept
aliases: [情境化纠错, 具身纠错, Situated Feedback]
---

# Situated Correction

## 定义

Situated Correction 指用户在机器人执行过程中基于当前场景和动作给出的纠正或约束，例如 “that's not trash” 或 “leave it alone”。

## 数学形式

$$
\hat{\ell}_t \sim p_{hi}(\hat{\ell}_t|I_t^1,\ldots,I_t^n,\ell_t)
$$

其中 $\ell_t$ 包含用户的实时纠错语言，$I_t$ 提供当前视觉情境。

## 核心要点

1. 纠错语义依赖当前观察，不能只靠语言理解。
2. 系统需要立即触发高层重新规划。
3. 纠错可能要求停止、撤销、补充或改变目标。

## 代表工作

- [[HiRobot]]: 通过高层 VLM 把实时用户纠错转成新的低层技能命令。

## 相关概念

- [[Human-Robot Interaction]]
- [[Hierarchical VLA]]
- [[Vision-Language Model]]
