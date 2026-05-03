---
type: concept
aliases: [输出约束解码, constrained decoding for actions]
---

# Output-Constrained Decoding

## 定义

Output-Constrained Decoding 指在生成模型解码时限制可采样 token 集合，使输出满足任务格式或安全约束。

## 数学形式

$$
p(y_t \mid x, y_{<t}) = 0,\quad y_t \notin \mathcal{V}_{\mathrm{valid}}
$$

## 核心要点

1. 在机器人动作生成中，可将输出限制到合法 action-token vocabulary。
2. 能防止 VLM 在控制场景中输出自然语言或非法动作 token。
3. 约束集合通常随 prompt 类型变化；普通 VQA 仍可使用完整自然语言词表。

## 代表工作

- [[RT-2]]: 当 prompt 为 robot-action task 时只允许采样动作 token。

## 相关概念

- [[Action Tokenization]]
- [[Vision-Language-Action]]
- [[Behavioral Cloning]]
