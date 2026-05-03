---
title: "Llama 2"
type: concept
tags: [language-model, transformer]
created: 2026-04-28
---

# Llama 2

Llama 2 是 Meta 发布的开源权重大语言模型系列，常作为多模态模型的语言主干。

## 为什么重要

- 它提供了成熟的 autoregressive token prediction 接口，可以把非文本 token 也接入同一序列建模框架。
- 在 [[OpenVLA]] 中，Llama 2 7B 作为语言主干，通过覆盖低频 vocabulary token 来生成动作 token。

## 代表工作

- [[OpenVLA]]: 使用 Llama 2 7B 作为 VLA 的动作生成主干。
