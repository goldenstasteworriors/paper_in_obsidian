---
type: concept
aliases: [联合注意力, Cross-stream Joint Attention]
---

# Joint Attention

## 定义

将多个信息流的 key/value 拼接，使一个模块的 query 同时访问自身 token 与外部主干表征。

## 核心要点

1. 可通过线性投影对齐不同模块的语义空间。
2. 比复制完整 backbone 更节省参数。

## 代表工作

- [[EgoSteer]]：动作专家和世界模型专家分别读取 Qwen3-VL 的 KV cache。

## 相关概念

- [[World Model]]
- [[Conditional Flow Matching]]
