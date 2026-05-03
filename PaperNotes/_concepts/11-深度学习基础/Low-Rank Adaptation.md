---
title: "Low-Rank Adaptation"
type: concept
tags: [parameter-efficient-finetuning, lora]
created: 2026-04-28
---

# Low-Rank Adaptation

Low-Rank Adaptation, LoRA, 是一种参数高效微调方法，通过给线性层加入低秩增量矩阵来适配新任务，而不是更新全部模型参数。

## 为什么重要

- LoRA 显著降低大模型微调的显存和可训练参数数量。
- 在机器人 VLA 中，LoRA 使研究者可以用单张高端 GPU 微调大模型策略，而不必完整更新 7B 参数。

## 代表工作

- [[OpenVLA]]: LoRA rank 32/64 接近 full fine-tuning 成功率，只训练约 1.4% 参数。
