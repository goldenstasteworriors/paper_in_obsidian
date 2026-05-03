---
title: "Action Tokenization"
type: concept
tags: [robot-action, tokenization]
created: 2026-04-28
---

# Action Tokenization

Action Tokenization 指把连续或结构化动作空间转成离散 token 序列，从而可以用序列模型和分类损失学习动作生成。

## 在 RT-1 中

[[RT-1]] 将每个连续动作维度均匀离散为 256 个 bins，并额外预测 arm/base/terminate 模式 token，使机器人控制可被 decoder-only [[Transformer]] 建模。

## 代表工作

- [[RT-1]]: 离散动作 token 的早期真机 VLA 应用。
