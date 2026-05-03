---
title: "Transfer Learning"
type: concept
tags: [fine-tuning, pretraining]
created: 2026-04-29
---

# Transfer Learning

Transfer Learning 指先在大规模通用数据上预训练模型，再把模型迁移到具体下游任务上的学习范式。

## 在论文中的作用

- [[PaliGemma]] 明确把自身定位为 transfer-friendly base VLM。
- Stage3 对每个下游任务全参数 fine-tune，并研究超参敏感性和少样本迁移。

## 代表工作

- [[PaliGemma]]: 系统评估 VLM 基座在近 40 个任务上的迁移能力。
