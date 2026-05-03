---
title: "Universal Sentence Encoder"
type: concept
tags: [language-embedding, representation-learning]
created: 2026-04-28
---

# Universal Sentence Encoder

Universal Sentence Encoder, USE, 是一种句子级文本 embedding 模型，用于把自然语言句子映射为固定维度向量表示。

## 在 RT-1 中

[[RT-1]] 使用 USE 编码机器人自然语言指令，再将该 embedding 输入 [[FiLM]] 层，调制 [[EfficientNet]] 的视觉特征抽取。

## 代表工作

- [[RT-1]]: 使用 USE 作为语言条件输入。
