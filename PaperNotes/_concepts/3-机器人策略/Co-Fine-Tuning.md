---
type: concept
aliases: [共同微调, mixed fine-tuning, co-training with fine-tuning]
---

# Co-Fine-Tuning

## 定义

Co-Fine-Tuning 指在下游任务数据微调时同时保留原始预训练任务数据，以降低灾难性遗忘并保留预训练模型的通用能力。

## 数学形式

$$
\mathcal{L}_{\mathrm{mix}}
= \lambda_{\mathrm{task}}\mathcal{L}_{\mathrm{task}}
+ \lambda_{\mathrm{pretrain}}\mathcal{L}_{\mathrm{pretrain}}
$$

## 核心要点

1. 通过 batch mixture 控制下游数据和原始数据比例。
2. 适合将大规模 foundation model 改造成专用策略，同时保留原有语义知识。
3. 在机器人 VLA 中可缓解只用机器人轨迹微调导致的视觉语言能力遗忘。

## 代表工作

- [[RT-2]]: 将机器人轨迹数据与 web-scale vision-language 数据共同微调。

## 相关概念

- [[Vision-Language-Action]]
- [[Behavioral Cloning]]
- [[Vision-Language Model]]
