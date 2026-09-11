---
type: concept
aliases: [具身智能体运行框架]
created: 2026-09-11
---

# Embodied Harness

## 定义

围绕基础模型组织机器人观测、任务上下文、动作执行、历史和失败恢复的运行系统。

## 数学形式

$$
c_t=\Phi_{\mathcal P}(\ell,o_t,h_t),\qquad a_t=\pi(c_t).
$$

P为插件集合，ℓ为任务，o为观测，h为历史，c为上下文，π为决策模型。

## 核心要点

1. harness的规则、额外观测、执行器都可能贡献性能，不能仅归因于模型。
2. 闭环反馈的时机很重要，动作分块会暂时放弃逐步观察。
3. 插件消融要区分输入信息变化与推理结构变化。

## 代表工作

- [[Show-Harness]]：多视角、状态、规划、历史和恢复组成机器人控制循环。

## 相关概念

- [[Semantic Action Interface]]
- [[Action Chunking]]
