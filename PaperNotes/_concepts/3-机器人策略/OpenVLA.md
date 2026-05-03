---
tags: [concept, robotics]
created: 2026-03-12
---

# OpenVLA

`OpenVLA` 是开源的 `Vision-Language-Action` 基线之一，常被用来评估通用机器人操作能力。

## 为什么重要

- 它提供了一个相对统一的 VLA 起点。
- 很多后续工作都把它当作性能、延迟或训练配方的对比基线。
- 在 [[FutureVLA]] 和 [[DepthCache]] 这类论文里，OpenVLA 经常作为直接参照。

## 代表工作

- [[OpenVLA]]: 7B 参数开源 VLA，基于 Llama 2、DINOv2、SigLIP 和 Open X-Embodiment 970k 真实机器人 episode 训练。
