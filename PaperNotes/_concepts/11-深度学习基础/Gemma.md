---
title: "Gemma"
type: concept
tags: [language-model, decoder-only-transformer]
created: 2026-04-29
---

# Gemma

Gemma 是 Google 发布的开放权重 [[Decoder-only Transformer]] 语言模型家族，源自 Gemini 相关技术栈。[[PaliGemma]] 使用 Gemma-2B raw pretrained checkpoint 作为语言生成 backbone。

## 在论文中的作用

- [[PaliGemma]] 将 [[SigLIP]] image tokens 线性投影到 Gemma token embedding 维度后，与文本 token 拼接输入 Gemma decoder。
- Gemma 负责根据图像 token 和任务 prefix 自回归生成 suffix。

## 代表工作

- [[PaliGemma]]: 使用 Gemma-2B 构成 3B 级 VLM。
