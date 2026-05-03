---
type: concept
aliases: [WAM, 世界动作模型]
---

# World Action Model

## 定义
同时建模未来环境动态和对应动作序列的机器人策略范式。

## 数学形式
$$
p(a_{t:t+H}, v_{t+1:t+H}\mid o_t, s_t)
$$

## 核心要点
1. 把动作决策和未来视觉/状态演化放进同一框架。
2. 常借助视频预训练获得时空动态先验。
3. 关键挑战是推理成本高、动作与视觉表示容易耦合过深。

## 代表工作
- [[GigaWorld-Policy]]: 用 action-centered 设计降低推理开销。
- [[MV-VDP]]: 用多视角未来视频支撑动作解码。

## 相关概念
- [[Vision-Language-Action]]
- [[Diffusion Policy]]
