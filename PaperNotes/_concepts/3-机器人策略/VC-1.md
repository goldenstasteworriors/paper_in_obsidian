---
type: concept
aliases: [VC-1, visual cortex foundation model]
---

# VC-1

## 定义

VC-1 是面向机器人控制的视觉 foundation model，提供预训练视觉表征供下游机器人策略使用。

## 数学形式

$$
a_t = \pi_\theta(f_{\mathrm{VC1}}(I_t), e(l))
$$

## 核心要点

1. 作为视觉表征模型，它主要增强感知，不原生建模语言到动作的 token 生成。
2. 在语言条件控制中通常需要额外的语言 embedding 与视觉 token 融合。
3. 常作为检验视觉预训练是否足以带来机器人泛化的基线。

## 代表工作

- [[RT-2]]: 将 VC-1 与 RT-1 风格 decoder 结合，作为 real-world 泛化和 emergent evaluation 基线。

## 相关概念

- [[Vision-Language Model]]
- [[Behavioral Cloning]]
- [[RT-1]]
