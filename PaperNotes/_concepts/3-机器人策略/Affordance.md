---
type: concept
aliases: [可供性, 功能可操作性]
---

# Affordance

## 定义
描述物体某个区域在当前任务和交互主体下“适合被如何作用”的功能性表征。

## 数学形式
$$
a(p, l) \rightarrow s_p
$$

其中 $p$ 是物体上的点，$l$ 是任务条件，$s_p$ 表示该点作为接触或操作区域的适用程度。

## 核心要点
1. 不是纯几何属性，而是几何、任务和执行体共同决定的交互可能性。
2. 在机器人操作里常表现为 per-point score map 或 contact region heatmap。
3. 可以同时服务 grasp planning、tool use 和 preparatory manipulation。

## 代表工作
- [[BiPreManip]]: 把 goal affordance 和 preparatory affordance 分成两个阶段来预测。

## 相关概念
- [[PointNet++]]
- [[SE(3)]]
- [[cVAE]]
