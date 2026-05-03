---
type: concept
aliases: [MetaWorld, Meta-World]
---

# Meta-World

## 定义
用于评估机器人 manipulation 多任务泛化能力的经典模拟 benchmark。

## 数学形式
$$
\mathrm{SuccessRate} = \frac{\#\text{success}}{\#\text{episodes}}
$$

## 核心要点
1. 覆盖大量机械臂操作任务。
2. 常用于评估 data efficiency、multi-task learning 和 sim policy 性能。
3. 是许多 diffusion / VLA / video action model 工作的标准试验场。

## 代表工作
- [[MV-VDP]]: 在 Meta-World 上验证数据效率与鲁棒性。
- [[Diffusion Policy]]: 常见对照基线。

## 相关概念
- [[MuJoCo]]
- [[LIBERO]]
