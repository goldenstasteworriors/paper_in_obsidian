---
title: "Multimodal Pretraining"
type: concept
tags: [multimodal, pretraining, vision-language-model]
created: 2026-04-29
---

# Multimodal Pretraining

Multimodal Pretraining 指在图像、文本、视频、结构化视觉标注等多模态数据上预训练模型，让模型获得跨模态表示和任务能力。

## 在论文中的作用

- [[PaliGemma]] 的 Stage1 使用 caption、OCR、VQA、detection、segmentation、grounded captioning 等任务做长时间多模态预训练。
- 目标是获得便于 [[Transfer Learning]] 的基座模型，而不是直接训练聊天模型。

## 代表工作

- [[PaliGemma]]: 面向迁移的多模态预训练基座。
