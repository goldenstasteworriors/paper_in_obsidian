---
tags: [concept, human-motion]
created: 2026-03-11
---

# MotionGPT

`MotionGPT` 是把人体动作序列表示成离散 token，再用类 GPT 自回归模型生成动作的路线。

## 为什么重要

- 它证明了 motion token 化之后，语言模型范式可以迁移到动作生成。
- 在 text-to-motion 里是很常见的基线。
- [[ZeroWBC]] 在实验里用 MotionGPT 作为纯 text-to-motion 对照，展示视觉模态的增益。

## 相关概念

- [[VQ-VAE]]
- [[HumanML3D]]
