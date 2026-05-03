---
title: "EfficientNet"
type: concept
tags: [cnn, image-encoder]
created: 2026-04-28
---

# EfficientNet

EfficientNet 是一种卷积神经网络家族，通过复合缩放统一调整网络深度、宽度和分辨率，在图像识别中具有较好的参数效率。

## 在 RT-1 中

[[RT-1]] 使用 ImageNet 预训练 EfficientNet-B3 作为图像 tokenizer，并通过 [[FiLM]] 加入语言条件。每帧图像输出 $9 \times 9$ 空间特征，形成 81 个视觉-语言 token。

## 代表工作

- [[RT-1]]: FiLM-conditioned EfficientNet-B3.
