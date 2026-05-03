---
title: "FiLM"
type: concept
tags: [conditioning, multimodal-learning]
created: 2026-04-28
---

# FiLM

FiLM, Feature-wise Linear Modulation, 是一种条件化特征调制方法。它用条件输入生成缩放参数 $\gamma$ 和平移参数 $\beta$，对中间特征做逐通道或逐元素仿射变换。

$$
\mathrm{FiLM}(h; \gamma, \beta) = \gamma \odot h + \beta
$$

## 在 RT-1 中

[[RT-1]] 用语言 embedding 生成 FiLM 参数，插入 [[EfficientNet]] 内部，使视觉特征抽取从早期就受语言任务条件影响。

## 代表工作

- [[RT-1]]: identity-initialized FiLM-conditioned EfficientNet.
