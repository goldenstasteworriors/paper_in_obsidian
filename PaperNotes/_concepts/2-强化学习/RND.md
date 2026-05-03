---
tags: [concept, rl]
created: 2026-03-12
---

# RND

`RND` 指 `Random Network Distillation`，是一种通过预测随机网络输出误差构造内在奖励的 exploration 方法。

## 为什么重要

- 它能在稀疏奖励场景里鼓励智能体访问新状态。
- 常被拿来和更结构化的 exploration 设计做对比。
- 在 dexterous manipulation 这类难探索任务里，RND 往往是最基础也最难绕开的参照物。
