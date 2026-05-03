---
type: concept
aliases: [轨迹预测, 2D trajectory prediction, visual trace prediction]
---

# Trajectory Prediction

## 定义
Trajectory Prediction 在机器人操作中指根据当前观测和任务指令预测末端执行器或手部未来运动路径。

## 数学形式

$$
P_{t:N} = \{(x_i, y_i) \mid i=t,t+1,\ldots,N\}
$$

## 核心要点
1. RoboBrain 中的轨迹是 2D visual trace，而不是完整 3D 控制轨迹。
2. 常用 DFD、HD、RMSE 衡量预测轨迹和真实轨迹的相似度。
3. 对真实控制还需要结合 3D pose、动力学约束和低层控制器。

## 代表工作
- [[RoboBrain]]: 使用 T-LoRA 输出操作轨迹 waypoints。

## 相关概念
- [[Affordance]]
- [[Vision-Language-Action]]
- [[RoboBrain]]
