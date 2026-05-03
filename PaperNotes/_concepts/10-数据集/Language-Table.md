---
type: concept
aliases: [Language Table, language-conditioned tabletop benchmark]
---

# Language-Table

## 定义

Language-Table 是面向语言条件 tabletop manipulation 的开源仿真 benchmark，常用于评估语言指令到低层动作的泛化。

## 数学形式

$$
\pi(a_t \mid I_t, l)
$$

## 核心要点

1. 输入通常为桌面图像和语言指令，输出为 2D 末端执行器动作。
2. 适合测试语言条件策略是否能组合物体、位置和动作。
3. 可作为真实机器人 VLA 方法的轻量补充评估。

## 代表工作

- [[RT-2]]: 使用 RT-2-PaLI-3B 在 Language-Table 上达到 90 ± 10。

## 相关概念

- [[Vision-Language-Action]]
- [[Behavioral Cloning]]
- [[Action Tokenization]]
