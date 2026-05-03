---
title: "Sumo: Dynamic and Generalizable Whole-Body Loco-Manipulation"
method_name: "Sumo"
authors: [John Z. Zhang]
year: 2026
venue: arXiv
tags: [whole-body-control, loco-manipulation, model-predictive-control, legged-robotics, sim-to-real]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2604.08508v1
created: 2026-04-13
---

# 论文笔记：Sumo: Dynamic and Generalizable Whole-Body Loco-Manipulation

## 元信息

| 项目 | 内容 |
|------|------|
| 作者 | John Z. Zhang |
| 机构 | RAI Institute |
| 日期 | April 2026 |
| 链接 | [arXiv](https://arxiv.org/abs/2604.08508v1) / [Project](https://sumo.rai-inst.com/) |
| 关键词 | whole-body control, loco-manipulation, sample-based MPC, sim-to-real |
| 对比基线 | end-to-end RL, end-to-end MPC, hierarchical RL |

---

## 一句话总结

> `Sumo` 的核心不是重新训练一个无所不能的大策略，而是把预训练低层 whole-body policy 当成稳定执行器，再用高层 sample-based [[Model Predictive Control]] 在测试时在线 steering，靠结构分工把 loco-manipulation 任务适配和全身动力学稳定同时做出来。

---

## 核心贡献

1. **分层控制框架**：高层 planner 负责任务适配，低层 policy 负责稳定 whole-body dynamics，不再强行把两者压进一个端到端黑箱。
2. **network-policy-augmented rollouts**：在 [[MuJoCo]] 里滚动的不是裸动力学，而是“动力学 + 低层 locomotion policy”组合系统，这让高层规划得到的动作更可执行。
3. **test-time cost shaping**：任务变了可以直接改 cost，而不用重新训练策略。
4. **real-world Spot 验证**：在重物推拖、upright、大物体拖动等真实任务上给出稳定结果。
5. **humanoid sim extension**：虽然主结果在四足 Spot 上，但同一套思路也能迁移到 G1 humanoid 仿真任务。

---

## 问题背景

### 这篇在解决什么

legged loco-manipulation 的难点从来不是“让机器人会走”或者“让机械臂会动”这么简单，而是：

- 一边保持本体平衡；
- 一边和大物体发生强接触；
- 还要根据不同任务目标实时调整策略。

如果完全依赖端到端 [[Reinforcement Learning]]，任务一变通常就要重训。  
如果完全依赖经典 [[Model Predictive Control]]，又很难在高维 whole-body 接触动力学下保持实时。

### 现有路线的问题

1. **end-to-end RL**
   训练成本高，换目标函数和任务就容易重来。
2. **end-to-end MPC**
   在复杂接触和高维动作下实时性压力非常大。
3. **hierarchical RL**
   看起来分层，但上层如果仍然是 learned module，任务切换仍然不够灵活。

作者的判断很直接：  
低层 whole-body stabilization 这件事适合交给 learned policy，  
高层 task adaptation 这件事更适合让 online planner 来做。

---

## 方法详解

### 总体结构

系统分成两个层次：

1. **低层 whole-body control policy**
   输入当前机器人状态和高层命令，输出关节级控制。
2. **高层 sample-based MPC**
   在测试时搜索 torso、arm、leg command 序列，并用 rollout 评估哪组命令最能完成任务。

### 结构图

![Figure 2](https://arxiv.org/html/2604.08508v1/x1.png)

**图解**：Figure 2 展示了整套系统。绿色部分是高层 planner，紫色部分是预训练 whole-body control policy。高层不直接控制所有关节，而是输出较低维的 body command；低层再把这些命令翻译成稳定的关节动作。

### 为什么这样分层

作者的关键洞见是：

- 低层 policy 已经学会了复杂 whole-body locomotion 的稳定模式；
- 真正经常变化的是任务目标、物体位置、接触几何和 cost 偏好；
- 所以没必要每次任务变化都把低层重训一遍。

这使得 `Sumo` 的核心不是 learning more，  
而是 **planning over a learned stabilizer**。

### network-policy-augmented dynamics

普通 MPC 会直接在动力学模型上滚动 joint action。  
`Sumo` 则让高层规划的动作先进入低层 policy，再由低层 policy 产生真实控制输入。

![Figure 3](https://arxiv.org/html/2604.08508v1/x2.png)

**图解**：Figure 3 对比了两种 rollout。传统方式直接把动作送入多体动力学模型；`Sumo` 的方式是在 rollout 里保留低层 locomotion policy。这让高层搜索的动作天然受到低层稳定性先验约束，不容易找到一堆物理上会摔的伪优解。

### 高层动作空间

高层 planner 输出的是较抽象的 whole-body command，例如：

- torso 目标
- arm / end-effector 相关命令
- leg / locomotion command

这种动作空间比 joint torque 或 joint target 低维很多，  
因此 sample-based planning 可以承受。

### 低层策略的角色

低层策略是预训练 whole-body control policy。它负责：

- balance-preserving locomotion
- 接触中稳定推进
- 把高层命令转成关节级动作

换句话说，高层告诉机器人“往哪里推、怎么靠近、任务目标是什么”，  
低层负责“别摔，别乱抖，把这个动作做出来”。

---

## 关键公式

### 公式1: [[Model Predictive Control|高层优化目标]]

$$
\mathbf{a}^{\star}_{0:H-1}
=
\arg\min_{\mathbf{a}_{0:H-1}}
\sum_{t=0}^{H-1} c(\mathbf{s}_t, \mathbf{a}_t) + c_f(\mathbf{s}_H)
$$

**含义**：高层 planner 在长度为 $H$ 的预测窗口内，搜索一段最优高层命令序列，使累计阶段代价与终端代价最小。

**符号说明**：
- $\mathbf{s}_t$：时刻 $t$ 的系统状态
- $\mathbf{a}_t$：时刻 $t$ 的高层命令
- $c(\cdot)$：阶段代价
- $c_f(\cdot)$：终端代价

### 公式2: [[Whole-Body Controller|低层策略执行]]

$$
\mathbf{u}_t = \pi_{\theta}(\mathbf{s}_t, \mathbf{a}_t)
$$

**含义**：低层策略 $\pi_{\theta}$ 接收当前状态和高层命令，输出关节级控制输入 $\mathbf{u}_t$。

**符号说明**：
- $\pi_{\theta}$：预训练 low-level policy
- $\mathbf{u}_t$：关节动作 / 控制命令

### 公式3: [[MuJoCo|增强 rollout 动力学]]

$$
\mathbf{s}_{t+1} = f\bigl(\mathbf{s}_t, \pi_{\theta}(\mathbf{s}_t, \mathbf{a}_t)\bigr)
$$

**含义**：高层 planner 评估的不是裸系统动力学 $f(\mathbf{s}_t,\mathbf{u}_t)$，而是经过低层策略后的闭环动力学。这就是论文最关键的 network-policy-augmented rollout。

### 公式4: 任务自适应 cost shaping

$$
c(\mathbf{s}_t, \mathbf{a}_t)
=
w_p c_{\text{progress}}
+ w_c c_{\text{contact}}
+ w_s c_{\text{stability}}
+ w_u c_{\text{effort}}
$$

**含义**：不同任务只需要改权重或 cost 项，就能在不重训低层策略的前提下切换行为偏好。

**直觉**：
- 想更快推物体：加大 progress reward
- 想更稳：加大 stability penalty
- 想适应不同物体：改接触相关 cost

---

## 关键图表

### Figure 2: 系统总览

![Figure 2](https://arxiv.org/html/2604.08508v1/x1.png)

**说明**：整篇论文最重要的一张图。它清楚表明 Sumo 不是端到端策略，也不是纯规划，而是 planner over learned WBC。

### Figure 3: rollout 对比

![Figure 3](https://arxiv.org/html/2604.08508v1/x2.png)

**说明**：这张图解释了为什么高层 planning 不会轻易滚出一堆不稳定动作，因为 rollout 时低层 policy 始终在闭环里。

### Figure 7: Spot 真机任务序列

![Figure 7](https://arxiv.org/html/2604.08508v1/img/task_freeze_frames_graded/tire_upright_frame_1.png)

**说明**：Figure 7 展示 Spot 真机上多个典型任务，包括 upright tire、upright barrier、dragging barrier 等。这些任务比静态 grasping 更能体现 whole-body 接触和任务适配能力。

### Figure 8: G1 humanoid 仿真任务

![Figure 8](https://arxiv.org/html/2604.08508v1/img/task_freeze_frames/g1_box_push/frame_0001.jpg)

**说明**：Figure 8 给出 G1 humanoid 上的 box push、chair push、door open、table push。作者用这部分说明方法并不绑死在 Spot 上，但需要注意这里只是 simulation，不是真机 humanoid。

---

## 实验设置

### 机器人平台

- **Spot quadruped**：真实世界主平台
- **G1 humanoid**：仿真泛化平台

### 任务类型

Spot 真机任务包括：

- Tire Upright
- Barrier Upright
- Cone Upright
- Chair Upright
- Tire Stack
- Barrier Drag
- Box Push

G1 humanoid 仿真任务包括：

- Box Push
- Door Open
- Chair Push
- Table Push

### 仿真与规划效率

论文给出一项很关键的 timing 结果：

- 32 路 parallel rollout，1.5 秒仿真 horizon
- 含低层 policy 时约 `43.45 ms`
- 裸 MuJoCo rollout 约 `21.73 ms`

这意味着把 low-level policy 放进 rollout 当然更贵，  
但贵得还在可用范围内，不至于把 planning 直接拖死。

---

## 关键实验结果

### Table I: rollout timing

| Method | Rollout Time |
|--------|--------------|
| MuJoCo with low-level policy | 43.45 ± 1.88 ms |
| MuJoCo only | 21.73 ± 1.86 ms |

**解读**：闭环 rollout 成本大约翻倍，但换来的好处是高层搜索空间更可执行。这是非常划算的工程交换。

### Figure 4: 和 E2E RL / E2E MPC 比较

论文在五类 loco-manipulation 任务上对比：

- `Sumo`
- end-to-end RL
- end-to-end MPC

结论很清楚：`Sumo` 在不同对象和任务上的成功率最稳，  
说明“planner + learned stabilizer”这套组合确实优于把问题全丢给一端。

### Figure 5: 和 hierarchical RL 比较

在 push 与 upright 任务上，`Sumo` 相比 hierarchical RL 依旧更稳。  
这意味着“分层”本身不是答案，**可测试时修改目标的规划层** 才是核心优势。

### Figure 6: compute vs success

Figure 6 比较了 compute hours 和最大成功率。  
作者想传达的点是：`Sumo` 不仅成功率更高，而且超参搜索代价也更合理。

这个结果很重要，因为它说明方法不是靠天量调参勉强堆出来的。

### Table II: Spot 真机结果

论文报告 Spot 真机多任务 10 次试验的完成时间和成功率。  
其中多个任务达到接近满成功：

- Tire Upright：10 / 10
- Barrier Upright：9 / 10

这比只给仿真曲线更有说服力，因为这类大物体交互任务一旦控制不稳，很容易直接失败。

### Table III: G1 humanoid simulation

G1 humanoid 仿真里：

- Box Push：9 / 10
- Door Open：10 / 10
- Chair Push：10 / 10

作者借此说明方法结构可以延展到 humanoid。  
但要记住，这里只是 simulation，不能拿它直接当“humanoid real-world solved”。

---

## 方法优点

### 1. 结构分工清晰

这篇论文最讨喜的地方是逻辑干净：

- 低层 policy 解决稳定执行
- 高层 MPC 解决任务适配

没有把所有问题硬塞给单一模型。

### 2. test-time flexibility 很强

任务一变直接改 cost。  
这一点对机器人系统非常实际，比“再收一批数据重训”靠谱得多。

### 3. 真机结果有说服力

Spot 上的大物体推拖和 upright 任务，本来就很考验 whole-body coordination。  
这不是桌面抓取那种容易被 benchmark 美化的场景。

### 4. 方法具有可迁移性

虽然主平台是 quadruped，但结构并不绑死四足。  
作者至少给了 humanoid 仿真的 early evidence。

---

## 方法局限

### 1. humanoid 证据还不够硬

最吸引你的那部分其实是 whole-body / humanoid，但论文最扎实的真实结果仍然是 Spot。  
humanoid 目前只有仿真，离“真实人形通用 loco-manipulation”还差一截。

### 2. 低层策略仍然需要高质量预训练

`Sumo` 不是不要训练，而是把训练负担放到底层 WBC policy。  
如果低层策略本身不稳，高层 planner 也救不了。

### 3. 规划实时性仍有上限

43 ms 的 rollout 本身不错，但面对更高维 humanoid、更复杂接触和更长 horizon 时，计算压力会迅速上来。

### 4. 泛化的边界要说清楚

论文里的 generalizable 更接近：

- 跨任务
- 跨物体
- 同一结构范式下的迁移

而不是跨所有 embodiment 的 universal controller。

---

## 和相关工作的关系

### 对比 end-to-end RL

优点：

- 更灵活
- 改任务不用重训
- 真机部署更可控

代价：

- 需要 online planning
- 需要设计 cost

### 对比纯 MPC

优点：

- 不需要在高维 joint action 上直接做困难规划
- 借助 learned policy 获得动态稳定性先验

### 对比 [[Hierarchical Reinforcement Learning]]

作者的观点很隐含但很明确：  
hierarchical RL 仍然可能在任务切换时不够弹性，而显式 planning 能在测试时更自然地注入任务偏好。

---

## 对我的研究有什么用

如果你关心：

- whole-body control
- loco-manipulation
- humanoid / cross-embodiment
- online adaptation

那这篇非常值得记。

具体借鉴点有三条：

1. **结构上**：可以考虑 planner-over-policy，而不是 policy-over-everything。
2. **表示上**：高层动作空间要抽象得足够低维，否则 sample-based planning 很难跑起来。
3. **实验上**：真机大接触任务比一堆小型 benchmark 更能暴露 whole-body 方法的成色。

---

## 我最认同的点

这篇最强的不是某个花哨模块，而是工程判断非常老练：  
**把该学的学掉，把该规划的留给测试时规划。**

这比“再做一个更大的端到端机器人 foundation model”诚实得多。

---

## 我最质疑的点

作者用 Spot 的真机成功说明方法有效，这没问题。  
但如果把标题里的 “generalizable whole-body loco-manipulation” 解读得太满，就会有点夸张。

因为目前最强证据还是：

- quadruped 真机
- humanoid 仿真

离跨 embodiment 的真实统一控制器，还不能说只差临门一脚。

---

## 可复现信息

- arXiv HTML: https://arxiv.org/html/2604.08508v1
- PDF: https://arxiv.org/pdf/2604.08508v1
- Project: https://sumo.rai-inst.com/
- 主要仿真器: [[MuJoCo]]
- 核心范式: sample-based [[Model Predictive Control]] + pre-trained [[Whole-Body Controller]]

---

## 相关概念

- [[Model Predictive Control]]
- [[Whole-Body Controller]]
- [[Reinforcement Learning]]
- [[Hierarchical Reinforcement Learning]]
- [[MuJoCo]]
- [[Proprioception]]

---

## 结论

`Sumo` 是一篇很值得精读的系统论文。  
它没有假装自己解决了全部 embodied intelligence，而是把 loco-manipulation 里最关键的结构问题拆清楚了：  
**稳定执行交给 learned WBC，任务适配交给 online planning。**

如果后面你要做 humanoid whole-body manipulation、contact-rich locomotion、或者 planner-policy 混合架构，这篇应该放在近期待读列表前排。
