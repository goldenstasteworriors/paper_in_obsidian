---
title: "FSDP"
type: concept
tags: [distributed-training, sharding]
created: 2026-04-29
---

# FSDP

FSDP 是 Fully Sharded Data Parallel 的简称，用于把模型参数、梯度和优化器状态切分到多设备上，以降低单设备内存压力。

## 在论文中的作用

- [[PaliGemma]] 训练时使用类似 Zero-DP/FSDP 的 sharding 策略。
- 论文附录还比较了 FSDP 和 Megatron-style sharding 在推理时的 walltime、吞吐和内存。

## 代表工作

- [[PaliGemma]]: 在 VLM 训练和推理测量中使用/评估 FSDP。
