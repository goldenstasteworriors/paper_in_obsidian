---
tags: [concept, generative-model]
created: 2026-03-11
---

# VQ-VAE

`VQ-VAE` 是 `Vector Quantized Variational Autoencoder`，核心作用是把连续表示压成离散 codebook token。

## 为什么重要

- 适合把连续动作、图像 patch 或语音特征变成可自回归建模的离散序列。
- 在 motion token、图像 tokenizer、离散 world model 里很常见。
- 对 [[ZeroWBC]] 这类方法，它解决的是“怎么把连续人体动作交给大语言/视觉语言模型生成”。

## 相关概念

- [[Vision-Language Model]]
- [[MotionGPT]]

