---
type: concept
aliases: [RoboVQA Benchmark]
---

# RoboVQA

## 定义
RoboVQA 是面向机器人长程操作的视频-文本问答 benchmark，覆盖 planning、future prediction、success 判断和 affordance 类问题。

## 数学形式
常用 BLEU 指标评价生成答案和参考答案的 n-gram 一致性：

$$
BLEU = BP \cdot \exp\left(\sum_n w_n \log p_n\right)
$$

## 核心要点
1. 包含真实机器人长程 episode 的 video-text pairs。
2. 适合评估机器人任务规划文本能力。
3. RoboBrain 在 BLEU1-4 上显著高于多个 baseline。

## 代表工作
- [[RoboBrain]]: 使用 RoboVQA 评估机器人 planning 能力。

## 相关概念
- [[ShareRobot]]
- [[Trajectory Prediction]]
- [[Affordance]]
