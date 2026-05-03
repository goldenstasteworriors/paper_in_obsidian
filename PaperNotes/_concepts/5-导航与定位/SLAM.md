---
type: concept
aliases: [Simultaneous Localization and Mapping]
---

# SLAM

## 定义

机器人在未知环境中同时完成自身定位与地图构建的一类方法总称。

## 数学形式

$$
p(x_{1:T}, m \mid z_{1:T}, u_{1:T})
$$

## 核心要点

1. 核心是状态估计与地图更新的联合推断。
2. 常和视觉、激光、IMU 等多传感器融合。
3. 在导航、主动感知和状态估计中都是基础模块。

## 代表工作

- [[AWARE]]: 关注窄视场 LiDAR-Inertial 场景下的主动感知与里程计稳定性。

## 相关概念

- [[Model Predictive Control]]

