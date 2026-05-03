---
title: "Finite Scalar Quantization"
aliases: [FSQ]
tags: [concept, quantization, tokenizer]
created: 2026-04-29
---

# Finite Scalar Quantization

Finite Scalar Quantization（FSQ）是一类将连续 latent 表示按有限标量级别量化的方法，可作为 VQ 类离散表示学习的简化替代。

## 在机器人策略中的作用

在动作 tokenization 中，FSQ 可以学习压缩动作序列的离散 latent。[[FAST]] 将 FSQ 作为对比 tokenizer，发现 FSQ 在较低重建保真度下压缩能力较强，但在高精度、细粒度控制所需的重建质量上不如 FAST 稳定。

## 代表工作

- [[FAST]]: 在 action tokenizer 对比中把 FSQ 作为 learned compression baseline。
