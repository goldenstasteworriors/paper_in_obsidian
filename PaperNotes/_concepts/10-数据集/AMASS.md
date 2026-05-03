---
type: concept
aliases: [Archive of Motion Capture as Surface Shapes, AMASS]
---

# AMASS

## 定义
`AMASS` 是把多套动作捕捉数据统一到参数化人体模型上的大规模动作数据集，常用于人体动作建模、模仿学习和 retargeting。

## 数学形式

$$
\mathcal{D}_{\text{AMASS}} = \{\tau_1, \tau_2, \dots, \tau_N\}
$$

## 核心要点

1. 提供大规模、多动作类型的 [[MoCap]] 轨迹。
2. 常被用来训练 motion prior，或先做人类动作建模再映射到机器人。
3. Dream2Act 先把 AMASS 动作 retarget 到 G1，再在 Isaac Lab 中渲染机器人原生数据。

## 代表工作

- [[Dream2Act]]: 用 AMASS 生成 5.3M 帧初始 G1 轨迹，再下采样成 5338 个关键帧做高保真渲染。

## 相关概念

- [[SMPL]]
- [[ViTPose]]
- [[MoCap]]

