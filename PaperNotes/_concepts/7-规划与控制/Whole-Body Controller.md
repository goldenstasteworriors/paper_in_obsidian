---
tags: [concept, control]
created: 2026-03-16
---

# Whole-Body Controller

`Whole-Body Controller` 常写作 `WBC`，指一类把全身动力学、接触约束和任务目标统一进控制求解器的执行器。

## 为什么重要

- 它是 humanoid 和 whole-body robot 把高层策略落到真实执行的关键中间层。
- 很多生成动作模型最终是否可落地，取决于 WBC 会不会把动作改形改得太离谱。
- 在 [[PhysMoDPO]] 和 [[ZeroWBC]] 这类工作里，WBC 都是连接 motion prior 与物理执行的重要环节。
