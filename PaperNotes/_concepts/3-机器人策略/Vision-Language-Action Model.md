---
type: concept
aliases: [VLA, 视觉语言动作模型]
---

# Vision-Language-Action Model

## 定义
Vision-Language-Action Model 是将视觉输入、语言指令和机器人动作统一建模的策略模型，常把动作离散化为 token 进行预测。

## 数学形式

$$
p_\theta(a_{1:T} \mid I_{1:T}, l)
$$

## 核心要点
1. 视觉和语言提供任务语义与环境信息，动作 token 提供可执行控制输出。
2. 可以复用 [[Vision-Language Model]] 的预训练能力。
3. 在真实机器人上仍受动作表示、控制频率、数据覆盖和安全约束影响。

## 代表工作
- [[RT-2]]: 将动作作为文本 token 输出。
- [[RT-X]]: 将 RT-2 扩展到跨本体数据。

## 相关概念
- [[Vision-Language Model]]
- [[Action Tokenization]]
- [[RT-2]]
