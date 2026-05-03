---
type: concept
aliases: [遥操作, Teleoperation]
---

# Teleoperation

## 定义
由人类远程提供动作、姿态或目标指令，驱动机器人执行任务或采集示教数据的交互范式。

## 数学形式
$$
a_t = \pi_{\text{teleop}}(u_t^{\text{human}}, o_t)
$$

## 核心要点
1. 常用于 demonstration collection、在线纠错和安全接管。
2. 关键问题包括操作负担、延迟、映射方式和 replay feasibility。
3. 对 humanoid 和 contact-rich manipulation，teleop 仍然是高质量数据主来源。

## 代表工作
- [[HEX]]: 通过真实机器人 teleoperation 采集 whole-body humanoid 数据。

## 相关概念
- [[Cross-Embodiment]]
- [[Vision-Language-Action]]
