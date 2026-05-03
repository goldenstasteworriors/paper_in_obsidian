---
type: concept
aliases: [Qwen2.5, Qwen2.5-7B-Instruct]
---

# Qwen2.5

## 定义
Qwen2.5 是 Qwen 系列大语言模型，RoboBrain 使用 Qwen2.5-7B-Instruct 作为语言模型主干。

## 数学形式

$$
y_t \sim p_\theta(y_t \mid y_{<t}, X_t, H_v)
$$

## 核心要点
1. 在多模态框架中负责语言理解、推理和自回归生成。
2. RoboBrain 用它生成任务规划、affordance 坐标和 trajectory 坐标。
3. 配合视觉 token 后成为具身多模态推理模型的核心。

## 代表工作
- [[RoboBrain]]: 使用 Qwen2.5-7B-Instruct 作为 LLM backbone。

## 相关概念
- [[Multimodal Large Language Model]]
- [[Vision-Language Model]]
