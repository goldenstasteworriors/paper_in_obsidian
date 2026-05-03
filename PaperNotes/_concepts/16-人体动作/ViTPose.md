---
type: concept
aliases: [ViTPose]
---

# ViTPose

## 定义
`ViTPose` 是基于 Vision Transformer 的 2D 姿态估计框架，常用于人体关键点检测，也可经过领域适配迁移到机器人原生关节检测。

## 数学形式

$$
P_{2D} = f_{\text{ViT}}(I)
$$

## 核心要点

1. 用 Transformer backbone 预测图像中的 2D 关键点。
2. 默认多在 COCO 等人体数据上预训练，直接迁到机器人时容易出现 morphology gap。
3. Dream2Act 用它做 backbone，再通过机器人领域数据微调 native pose estimator。

## 代表工作

- [[Dream2Act]]: 冻结 ViT-Base 前九层，只微调后几层和 heatmap head 做 G1 原生关节检测。

## 相关概念

- [[SMPL]]
- [[MoCap]]

