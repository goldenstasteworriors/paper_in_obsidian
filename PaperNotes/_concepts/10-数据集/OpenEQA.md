---
type: concept
aliases: [OpenEQA, Embodied Question Answering]
---

# OpenEQA

## 定义
OpenEQA 是 embodied question answering benchmark，用真实场景中的问题评估模型对环境、对象、属性、空间关系和常识的理解。

## 数学形式
OpenEQA 常使用 LLM-based score 比较模型答案和参考答案：

$$
score = \operatorname{Judge}(a_{pred}, a_{gt}, q)
$$

## 核心要点
1. 问题来自真实环境，覆盖对象状态、空间理解、属性识别和世界知识。
2. 对机器人模型的环境理解能力有参考价值。
3. RoboBrain 在部分子项领先，但空间/对象识别并非全面最优。

## 代表工作
- [[RoboBrain]]: 使用 OpenEQA 作为机器人 VQA benchmark。

## 相关概念
- [[RoboVQA]]
- [[Vision-Language Model]]
