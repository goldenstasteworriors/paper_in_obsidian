---
type: concept
aliases: [Morphology-Aligned Graph Convolutional Network, MAGCN]
---

# MAGCN

## 定义
用于跨手型抓取策略学习的图神经网络主干，把 morphology-aligned hand graph 和 hand-specific physical priors 结合起来编码状态。

## 数学形式

$$
\mathbf{E}_{\text{node}}^{h}=\phi_{\text{node}}\big(\mathbf{X}_{\text{node}}^{h},\,\mathbf{A}^{h},\,\mathbf{E}_{\text{p}}^{h}\big)
$$

## 核心要点

1. 输入是 anatomy-aligned hand-object graph，而不是 lossy keypoint list。
2. physical prior 不是一次性拼接，而是逐层注入 GCN。
3. 输出同时服务 node-level primitive decoding 和 wrist command decoding。

## 代表工作

- [[DexGrasp-Zero]]: 提出 MAGCN 作为跨 embodiment 抓取策略 backbone。

## 相关概念

- [[URDF]]
- [[Motion Primitive]]
- [[Privileged Distillation]]

