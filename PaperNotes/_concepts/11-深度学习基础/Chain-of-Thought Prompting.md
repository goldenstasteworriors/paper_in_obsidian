---
type: concept
aliases: [CoT, 思维链提示, chain of thought]
---

# Chain-of-Thought Prompting

## 定义

Chain-of-Thought Prompting 是让语言模型在给出最终答案前先生成中间推理步骤的提示或训练方式。

## 数学形式

$$
p(a \mid x) = \sum_r p(a \mid r, x)p(r \mid x)
$$

## 核心要点

1. 中间推理 $r$ 可显式承载分解、选择、计算和语义判断。
2. 在 embodied control 中，CoT 可作为高层自然语言 plan 与低层动作之间的桥。
3. 生成推理并不保证真实因果推理，需要结合行为结果评估。

## 代表工作

- [[RT-2]]: 让模型先生成 `Plan`，再生成动作 token，展示多阶段语义控制能力。

## 相关概念

- [[Vision-Language Model]]
- [[Vision-Language-Action]]
- [[PaLM-E]]
