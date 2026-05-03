---
title: "PaliGemma"
type: concept
tags: [vision-language-model, multimodal, robotics]
created: 2026-04-28
---

# PaliGemma

PaliGemma 是 Google 的轻量级预训练 [[Vision-Language Model]]，由视觉编码器和 Gemma 语言模型组成，常被用作较小规模 VLM backbone。

## 在论文中的作用

- [[Pi0]] 使用 PaliGemma 作为视觉-语言 backbone，以继承互联网尺度语义知识。
- 机器人状态和动作不直接交给原 VLM 权重，而是交给单独的 action expert。

## 代表工作

- [[PaliGemma]]: 原始 PaliGemma 技术报告，系统介绍架构、训练阶段、transfer 评估和消融。
- [[Pi0]]: 使用 PaliGemma + [[Flow Matching]] action expert 构成通用机器人策略。
