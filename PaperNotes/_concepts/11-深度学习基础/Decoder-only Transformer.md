---
title: "Decoder-only Transformer"
type: concept
tags: [transformer, language-model]
created: 2026-04-29
---

# Decoder-only Transformer

Decoder-only Transformer 是只使用 Transformer decoder block 的自回归语言模型架构，通常通过 causal attention 逐 token 生成文本。

## 在论文中的作用

- [[PaliGemma]] 使用 [[Gemma]]-2B 作为 decoder-only language model。
- 图像 token、prefix token 和 suffix token 被组织成统一序列，suffix 部分自回归生成。

## 代表工作

- [[PaliGemma]]: 将 decoder-only LM 扩展为视觉语言模型。
