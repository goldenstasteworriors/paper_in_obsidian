---
title: "DINOv2"
type: concept
tags: [vision-backbone, self-supervised-learning]
created: 2026-04-28
---

# DINOv2

DINOv2 是 Meta 提出的自监督视觉表征模型，常用作无需人工标注即可获得强空间表征的视觉 backbone。

## 为什么重要

- 对机器人策略而言，DINOv2 的局部空间特征有助于定位物体、末端执行器和接触区域。
- 在 [[OpenVLA]] 中，DINOv2 与 [[SigLIP]] 特征拼接，用来同时保留空间细节和语义信息。

## 代表工作

- [[OpenVLA]]: 使用 DINOv2 + SigLIP 双视觉编码器构建 VLA backbone。
