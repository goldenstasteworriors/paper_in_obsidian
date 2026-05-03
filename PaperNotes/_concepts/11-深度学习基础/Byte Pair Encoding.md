---
title: "Byte Pair Encoding"
aliases: [BPE, 字节对编码]
tags: [concept, tokenization, compression]
created: 2026-04-29
---

# Byte Pair Encoding

Byte Pair Encoding（BPE）是一种基于频繁相邻符号合并的子词/序列压缩方法。它从基础符号序列开始，反复把数据中最常见的相邻符号对合并为新 token，从而得到固定大小词表。

## 在机器人策略中的作用

在 [[FAST]] 中，BPE 不直接处理文本，而是处理 [[Discrete Cosine Transform]] 后的量化频域系数序列。由于 DCT 系数矩阵通常稀疏，BPE 可以合并常见的零值片段和跨动作维度的常见频域模式，把长整数序列压缩成更短的动作 token。

## 代表工作

- [[FAST]]: 用 BPE 压缩 DCT 量化后的动作频域系数，是 FAST tokenizer 中唯一需要从数据中学习的组件。
