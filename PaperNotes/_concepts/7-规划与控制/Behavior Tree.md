---
type: concept
aliases: [BT, 行为树]
---

# Behavior Tree

## 定义
用树形结构组织条件判断与动作执行的任务规划表示，强调模块化、可解释和可回退。

## 数学形式
$$
\pi(s) = \mathrm{Traverse}(T, s)
$$

## 核心要点
1. 将复杂任务拆成 selector、sequence、condition、action 等节点。
2. 比端到端黑箱策略更容易检查和调试。
3. 适合与符号规划、VLM 生成和安全约束结合。

## 代表工作
- [[Structured Robot Policies]]: 用 VLM 从多模态输入直接生成可执行行为树。

## 相关概念
- [[Vision-Language-Action]]
- [[Differentiable SpaTiaL]]
