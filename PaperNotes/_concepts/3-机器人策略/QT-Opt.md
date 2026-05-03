---
title: "QT-Opt"
type: concept
tags: [robot-learning, reinforcement-learning, grasping]
created: 2026-04-28
---

# QT-Opt

QT-Opt 是一种用于真实机器人抓取的离线/大规模强化学习方法，曾收集 Kuka IIWA 在 bin-picking 场景中的大量成功抓取数据。

## 在 RT-1 中

[[RT-1]] 使用 QT-Opt 的 Kuka bin-picking 数据测试跨机器人数据吸收能力。单独 Kuka 数据不能直接迁移到 Everyday Robots，但与 EDR 数据混训后能提升 bin-picking 泛化。

## 代表工作

- [[RT-1]]: Kuka QT-Opt data + EDR data 的跨形态混训实验。
