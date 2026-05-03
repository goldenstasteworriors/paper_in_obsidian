---
title: "BLIP-2"
type: concept
tags: [vision-language-model, multimodal]
created: 2026-04-29
---

# BLIP-2

BLIP-2 是一种通过 Q-Former 连接冻结视觉编码器和冻结语言模型的 [[Vision-Language Model]]。

## 在论文中的作用

- [[PaliGemma]] 在相关工作中把 BLIP-2 作为连接视觉和语言模型的代表路线。
- 与 BLIP-2 不同，PaliGemma 在多模态预训练阶段训练全部参数，并使用简单线性 connector。

## 代表工作

- [[PaliGemma]]: 对比使用 adapter/Q-Former 的 VLM 架构路线。
