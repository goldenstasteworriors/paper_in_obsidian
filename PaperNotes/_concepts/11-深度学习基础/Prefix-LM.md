---
title: "Prefix-LM"
type: concept
tags: [attention-mask, language-model, multimodal]
created: 2026-04-29
---

# Prefix-LM

Prefix-LM 是一种把输入 prefix 作为双向可见上下文、把输出 suffix 作为自回归生成目标的训练方式。

## 在论文中的作用

- [[PaliGemma]] 让 image tokens 和 prefix tokens 互相全注意力，suffix tokens 只看过去 token。
- 论文消融显示，相比让 prefix 或 image 也受 causal mask 约束，Prefix-LM 设定在 VLM transfer 上更好。

## 代表工作

- [[PaliGemma]]: 使用 Prefix-LM masking 预训练视觉语言模型。
