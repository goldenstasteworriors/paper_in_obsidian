---
type: concept
aliases: [层级视觉语言动作模型, Hierarchical Vision-Language-Action Model]
---

# Hierarchical VLA

## 定义

Hierarchical VLA 是把机器人策略拆成高层视觉语言推理策略和低层视觉语言动作策略的架构，高层输出当前应执行的语言技能，低层把该技能转成连续动作。

## 数学形式

$$
p_{hi}(\hat{\ell}_t|I_t^1,\ldots,I_t^n,\ell_t),\qquad
p_{lo}(\mathbf{A}_t|I_t^1,\ldots,I_t^n,\hat{\ell}_t,q_t)
$$

## 核心要点

1. 高层负责开放式指令、用户反馈和视觉上下文理解。
2. 低层负责原子技能执行和动作生成。
3. 语言技能 $\hat{\ell}_t$ 是高低层之间的可解释接口。

## 代表工作

- [[HiRobot]]: 用高层 VLM 和低层 Pi0 VLA 处理复杂机器人指令与实时反馈。

## 相关概念

- [[Vision-Language-Action Model]]
- [[Vision-Language Model]]
- [[Action Chunking]]
