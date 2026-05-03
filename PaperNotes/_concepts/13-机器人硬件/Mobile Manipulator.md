---
title: "Mobile Manipulator"
type: concept
tags: [robot-hardware, manipulation, mobile-robot]
created: 2026-04-28
---

# Mobile Manipulator

Mobile Manipulator 指带移动底盘的机械臂系统，能够同时进行导航和操作。相比固定机械臂，它需要处理底盘位姿、视角变化和长程场景交互。

## 在 RT-1 中

[[RT-1]] 使用 Everyday Robots 移动机械臂，动作空间同时包含 7 维手臂控制和 3 维底盘控制，并通过 arm/base/terminate 模式选择当前控制对象。

## 代表工作

- [[RT-1]]: 面向真实厨房移动操作任务的大规模 VLA 策略。
