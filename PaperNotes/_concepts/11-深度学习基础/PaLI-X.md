---
type: concept
aliases: [Pathways Language and Image X, PaLI X]
---

# PaLI-X

## 定义

PaLI-X 是 Google 提出的超大规模视觉语言模型系列，使用 ViT 视觉编码器和 encoder-decoder 文本生成骨干处理图像-文本任务。

## 数学形式

$$
p_\theta(y \mid I, x)=\prod_t p_\theta(y_t \mid I, x, y_{<t})
$$

## 核心要点

1. 面向 captioning、VQA、多语言视觉语言理解等任务。
2. RT-2 使用 5B 和 55B PaLI-X 作为 VLA backbone。
3. 其 tokenizer 中整数 token 可直接映射到离散动作 bin。

## 代表工作

- [[RT-2]]: 构建 RT-2-PaLI-X-5B / 55B。

## 相关概念

- [[Vision-Language Model]]
- [[Vision-Language-Action]]
- [[Action Tokenization]]
