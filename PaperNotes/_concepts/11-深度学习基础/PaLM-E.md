---
type: concept
aliases: [PaLM-E, embodied multimodal language model]
---

# PaLM-E

## 定义

PaLM-E 是将视觉、语言和机器人状态等多模态输入投影到语言 token 空间中的 embodied multimodal language model。

## 数学形式

$$
z = [E_{\mathrm{text}}(x), P_{\mathrm{vision}}(I), P_{\mathrm{robot}}(s)]
$$

## 核心要点

1. 基于 decoder-only LLM，可接收图像、语言、机器人状态等输入。
2. 常用于 embodied planning、VQA 和机器人高层推理。
3. RT-2 使用 PaLM-E-12B，并将最低频 token 覆盖为动作 token。

## 代表工作

- [[RT-2]]: 构建 RT-2-PaLM-E-12B，并探索 Chain-of-Thought 动作生成。

## 相关概念

- [[Vision-Language Model]]
- [[Vision-Language-Action]]
- [[Chain-of-Thought Prompting]]
