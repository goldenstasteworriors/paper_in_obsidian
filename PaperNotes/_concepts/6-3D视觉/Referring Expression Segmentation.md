---
title: "Referring Expression Segmentation"
type: concept
tags: [segmentation, grounding, vision-language]
created: 2026-04-29
---

# Referring Expression Segmentation

Referring Expression Segmentation 是根据自然语言指代表达在图像中分割对应目标的任务。

## 在论文中的作用

- [[PaliGemma]] 通过新增 `<seg>` tokens 和位置 tokens，把分割输出文本化。
- 在 RefCOCO、RefCOCO+、RefCOCOg 上评估不同分辨率和数据增强策略。

## 代表工作

- [[PaliGemma]]: 使用通用 VLM 架构完成指代表达分割迁移。
