---
type: concept
aliases: [Sigmoid Loss for Language Image Pre-training]
---

# SigLIP

## 定义
SigLIP 是一种图文预训练视觉编码器，用 sigmoid loss 替代 CLIP 式 softmax 对比学习，常作为多模态模型的 vision tower。

## 数学形式

$$
\mathcal{L}_{sigmoid} = \sum_{i,j} \log(1 + \exp(-z_{ij} s_i t_j))
$$

## 核心要点
1. 输出图像特征供 projector 对齐到 LLM token 空间。
2. 在 [[RoboBrain]] 中作为视觉编码器。
3. 适合高分辨率图像和多图/视频帧输入的特征抽取。

## 代表工作
- [[RoboBrain]]: 使用 SigLIP 作为 vision encoder。

## 相关概念
- [[Vision-Language Model]]
- [[LLaVA]]
