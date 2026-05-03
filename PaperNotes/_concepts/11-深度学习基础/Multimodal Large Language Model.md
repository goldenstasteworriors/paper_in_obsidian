---
type: concept
aliases: [MLLM, 多模态大语言模型, Multimodal LLM]
---

# Multimodal Large Language Model

## 定义
Multimodal Large Language Model 是把图像、视频、文本等多模态输入映射到统一语义空间，并由大语言模型进行推理和生成的模型。

## 数学形式

$$
H_v = h(g(X_v)), \quad y_t \sim p_\theta(y_t \mid y_{<t}, H_v, X_t)
$$

## 核心要点
1. 通常包含视觉编码器、跨模态 projector 和 LLM。
2. 可用于 VQA、图像描述、视频理解和具身任务规划。
3. 直接迁移到机器人时通常缺少动作、接触和轨迹监督。

## 代表工作
- [[RoboBrain]]: 将 MLLM 扩展到机器人规划、affordance 和轨迹预测。

## 相关概念
- [[Vision-Language Model]]
- [[LLaVA]]
- [[Multimodal Pretraining]]
