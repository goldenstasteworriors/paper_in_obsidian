---
type: concept
aliases: [合成交互数据, Synthetic User Interaction Data]
---

# Synthetic Interaction Data

## 定义

Synthetic Interaction Data 是由模型自动生成的人类指令、用户插话、机器人回应等交互监督，用于扩展真实示范中稀缺的语言交互覆盖。

## 数学形式

$$
p_{gen}(\ell_t,u_t|I_t^1,\ldots,I_t^n,\hat{\ell}_0,\ldots,\hat{\ell}_{t-1},\hat{\ell}_t,P)
$$

## 核心要点

1. 可以从真实机器人技能反推合理的人类 prompt。
2. 相比纯文本生成，更容易保持与机器人 affordance 一致。
3. 质量依赖生成 prompt、场景类别和过滤策略。

## 代表工作

- [[HiRobot]]: 使用 VLM 根据视觉上下文和技能标签生成开放式用户指令与机器人回应。

## 相关概念

- [[Vision-Language Model]]
- [[Teleoperation]]
- [[Hierarchical VLA]]
