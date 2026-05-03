---
title: "Quantization"
type: concept
tags: [model-compression, inference]
created: 2026-04-28
---

# Quantization

Quantization 指把模型权重或激活从高精度浮点表示压缩到低比特表示，以减少显存占用并可能提高推理吞吐。

## 为什么重要

- 大 VLA 模型需要实时闭环控制，推理显存和延迟都会直接影响真机成功率。
- 量化可以让大模型策略运行在更常见的消费级 GPU 上。

## 代表工作

- [[OpenVLA]]: 4-bit 量化把推理显存降到约 7GB，并在 BridgeData V2 上基本保持 bfloat16 成功率。
