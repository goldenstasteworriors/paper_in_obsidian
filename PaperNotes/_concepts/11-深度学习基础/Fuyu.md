---
title: "Fuyu"
type: concept
tags: [vision-language-model, decoder-only-transformer]
created: 2026-04-29
---

# Fuyu

Fuyu 是一种不使用显式视觉编码器、直接把图像 patch 投影进 decoder-only 模型的 VLM 架构路线。

## 在论文中的作用

- [[PaliGemma]] 用 Fuyu-style 设置做消融：移除 [[SigLIP]]，把 RGB patch 线性投影给 [[Gemma]]。
- 结果显示这种路线可行但样本效率明显低于复用预训练视觉编码器。

## 代表工作

- [[PaliGemma]]: 用 Fuyu-style ablation 分析视觉编码器的重要性。
