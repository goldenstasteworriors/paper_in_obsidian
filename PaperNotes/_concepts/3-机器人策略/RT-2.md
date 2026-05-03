---
type: concept
aliases: [Robotics Transformer 2, Vision-Language-Action Model]
---

# RT-2

## 定义
RT-2 是把机器人动作表示为语言 token，并用视觉语言模型主干进行机器人控制微调的 [[Vision-Language-Action Model]]。

## 数学形式

$$
p_\theta(a_t^{text} \mid I_t, l)
$$

## 核心要点
1. 将离散化动作 token 拼入文本序列，使 VLM 的生成接口可直接输出动作。
2. 通过 Web 视觉语言预训练继承语义和视觉泛化能力。
3. 与 RT-1 相比容量更大，更适合吸收异构机器人数据，但训练和部署成本更高。

## 代表工作
- [[RT-X]]: 将 RT-2 扩展为 RT-2-X，用跨本体数据训练。

## 相关概念
- [[Vision-Language-Action Model]]
- [[Vision-Language Model]]
- [[Action Tokenization]]
