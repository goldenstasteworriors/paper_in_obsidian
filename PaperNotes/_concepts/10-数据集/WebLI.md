---
type: concept
aliases: [WebLI dataset, web-scale image-text data]
---

# WebLI

## 定义

WebLI 是用于训练视觉语言模型的大规模网页图文数据集，包含多语言 image-text pairs。

## 数学形式

$$
\mathcal{D}_{\mathrm{WebLI}} = \{(I_i, x_i)\}_{i=1}^{N}
$$

## 核心要点

1. 数据来自 web-scale 图文配对，并经过跨模态相似度过滤。
2. 支撑 PaLI / PaLI-X 等视觉语言模型的语义理解能力。
3. 在 RT-2 中，WebLI 相关视觉语言数据用于 co-fine-tuning，帮助保留 web 语义知识。

## 代表工作

- [[RT-2]]: 与机器人轨迹数据混合微调，提升语义泛化。

## 相关概念

- [[Vision-Language Model]]
- [[PaLI-X]]
- [[Co-Fine-Tuning]]
