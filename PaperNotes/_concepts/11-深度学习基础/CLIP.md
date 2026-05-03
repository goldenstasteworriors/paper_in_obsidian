---
type: concept
aliases: [Contrastive Language-Image Pretraining]
---

# CLIP

## 定义
通过对比学习把图像和文本嵌入到同一语义空间的视觉语言预训练模型。

## 数学形式
$$
\mathcal{L}_{\text{clip}} = - \log \frac{\exp(\langle v_i, t_i \rangle / \tau)}{\sum_j \exp(\langle v_i, t_j \rangle / \tau)}
$$

## 核心要点
1. 文本编码器可直接为下游任务提供语义条件。
2. 常用于 zero-shot 分类、检索和机器人任务条件编码。
3. 在机器人里常作为语言 backbone，而不是直接负责动作预测。

## 代表工作
- [[BiPreManip]]: 用 CLIP 文本特征条件化 goal / preparatory affordance 预测。

## 相关概念
- [[Vision-Language Model]]
- [[Affordance]]
