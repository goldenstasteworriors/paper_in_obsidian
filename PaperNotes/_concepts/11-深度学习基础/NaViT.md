---
title: "NaViT"
type: concept
tags: [vision-transformer, variable-resolution]
created: 2026-04-29
---

# NaViT

NaViT 是支持原生可变分辨率和可变长 patch 序列处理的 Vision Transformer 路线。

## 在论文中的作用

- [[PaliGemma]] 没有使用 NaViT/FlexiViT 一类可变分辨率机制，而是发布 224/448/896 三个固定分辨率 checkpoint。
- 论文认为未来可用可变分辨率建模减少多 checkpoint 维护成本。

## 代表工作

- [[PaliGemma]]: 在分辨率消融中讨论 NaViT 类方法可能的替代价值。
