---
title: "Ψ₀: An Open Foundation Model Towards Universal Humanoid Loco-Manipulation"
method_name: "Psi0"
authors: ["Songlin Wei", "Hongyi Jing", "Boqian Li", "Zhenyu Zhao", "Jiageng Mao", "Zhenhao Ni", "Sicheng He", "Jie Liu", "Xiawei Liu", "Kaidi Kang", "Sheng Zang", "Weiduo Yuan", "Marco Pavone", "Di Huang", "Yue Wang"]
year: 2026
venue: arXiv
tags: [humanoid, loco-manipulation, whole-body-control, egocentric-data, foundation-model, vision-language-action]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2603.12263v1
created: 2026-03-16
---

# Psi0

## 一句话判断

这篇最重要的贡献不是“再做一个 humanoid foundation model”，而是把数据配方讲明白了: human egocentric data 和 humanoid real-world data 不该一锅炖，而应该按目标分阶段训练。对你关心的 whole-body loco-manipulation 来说，这比再看一个更大的 VLA 名字有用得多。

## 论文信息

- 论文: [arXiv](http://arxiv.org/abs/2603.12263v1) | [PDF](https://arxiv.org/pdf/2603.12263v1)
- HTML: [arXiv HTML](https://arxiv.org/html/2603.12263v1)
- 作者: Songlin Wei, Hongyi Jing, Boqian Li, Zhenyu Zhao, Jiageng Mao, Zhenhao Ni, Sicheng He, Jie Liu, Xiawei Liu, Kaidi Kang, Sheng Zang, Weiduo Yuan, Marco Pavone, Di Huang, Yue Wang
- 机构: NVIDIA
- 平台: Unitree G1 humanoid + Dex3-1 dexterous hands
- 数据: [[EgoDex]] 预训练, Humanoid Everyday 任务无关 post-training, 每任务 80 条 teleop fine-tuning 轨迹
- 任务类型: long-horizon dexterous loco-manipulation, whole-body motion, locomotion, dual-arm coordination
- 真实部署: 有。论文在 8 个真实长程 humanoid 任务上做了 10 次 rollout/task 的系统评测

## 一句话总结

> Psi0 先用 [[Vision-Language Model]] 在 [[EgoDex]] 上学 task-space next-action token，再用 flow-based action expert 在 humanoid 真实数据上学 joint-space action chunk，最后用 real-time chunking 和低层 whole-body 控制把它稳定落到真机上。

## 核心贡献

1. **分阶段训练 recipe**: 先预训练视觉动作表征，再 post-train 机器人控制，而不是继续混训 human / humanoid / internet data。
2. **面向 whole-body 的 action expert**: 视觉语言骨干和 flow-based 动作头解耦，减少高层感知和低层关节控制互相拖累。
3. **真实 humanoid 长程 benchmark**: 不是单个 pick-and-place，而是 8 个 3 到 5 步子任务组成的真实 loco-manipulation 任务。
4. **部署级 real-time chunking**: 直接解决大模型 inference latency 带来的停顿和动作抖动，不是假装推理延迟不存在。

## 问题背景

### 要解决的问题

作者抓住的瓶颈很准确:

- human data 和 humanoid data 的运动学差异很大，盲目 co-training 既浪费数据也浪费模型容量。
- 纯 robot-only 数据太贵，尤其对 whole-body dexterous tasks 更难规模化。
- 大参数量 VLA 在真机执行时有推理延迟，naive chunk switching 很容易带来动作 jitter。

### 为什么现有路线不够

- 继续堆 noisy internet clip 或 heterogeneous cross-embodiment robot data，未必真的提升 humanoid control。
- 把感知、动作语义和 joint-level control 都塞进一个模型，往往导致训练目标互相冲突。
- deployment 阶段如果采用“停一下算下一段动作”的同步策略，长程任务会被 latency 和 discontinuity 直接拖垮。

### 本文的基本判断

这篇论文的态度很明确:

1. human data 应该主要用来学可泛化的视觉动作先验。
2. humanoid real-world data 应该主要用来学可执行的 joint-level control。
3. 训练阶段就要为 real-time chunk transition 做准备，而不是把部署问题留给后处理。

## 方法详解

### 整体架构

Psi0 由三块组成:

- **预训练阶段**: 用 [[Vision-Language Model]] 骨干在 [[EgoDex]] 上做 task-space next-action token 预测。
- **后训练阶段**: 用 flow-based action expert 在 humanoid robot data 上学习 joint-space action chunk。
- **部署阶段**: 用 real-time chunking 和 lower-body controller 解决长延迟下的 whole-body 连续执行。

作者并不试图让一个大模型同时学会“看懂世界”“规划动作语义”“输出稳定关节轨迹”三件事，而是把它们拆开。

### 阶段 1: egocentric human data 预训练

输入包括:

- 自然语言指令 $\ell$
- 当前视觉观测 $\mathbf{o}_t$
- 历史动作 token $\mathbf{a}_{<t}$

输出是下一步 task-space action token $\mathbf{a}_t$。这一阶段的目标不是精确 joint control，而是把第一视角观察、语言目标和动作语义对齐起来。

关键点有三个:

1. 只在这个阶段使用大规模 human egocentric data。
2. 动作处于 task-space，而不是 humanoid joint-space。
3. 训练目标是 next-action autoregression，不做昂贵的 action chunking。

### 阶段 2: humanoid robot post-training

这一阶段切到真实 humanoid data，目标从“理解动作语义”变成“生成可执行的关节动作块”。

- 视觉语言骨干冻结。
- 动作头改成 flow-based action expert。
- 动作表示换成 36-DoF joint-space vector，包含 hand, arm, torso, base height 和 locomotion commands。

作者用的不是继续扩大 human data，而是任务无关的 Humanoid Everyday 数据集。这个决定非常关键，因为它说明他们想把 human data 用在“泛化表征”，把 robot data 用在“执行落地”。

### MM-DiT Action Head

Figure 3 展示了作者把 naive DiT 改成 MM-DiT 的原因: 视觉语言隐藏状态和动作隐藏状态不该只是简单拼接，而要在 flow timestep $\tau$ 条件下做跨模态交互。作者的重点不在于“更复杂的 DiT”，而在于 action expert 真正服务于 VLA，而不是做个挂名 head。

### Real-Time Chunking

Psi0 明确把部署 latency 当成核心问题处理。论文指出:

- 同步“stop-think-execute”会导致明显停顿。
- naive 提前切 chunk 虽然能减少停顿，但会引入 chunk-to-chunk 抖动。
- 最终采用 training-time RTC，而不是 test-time inpainting。

训练中他们随机 mask 前 $d \in [1, d_{max}]$ 个 action token，并让模型在看到前缀 clean token 的情况下预测剩余 token，从而在部署时能平滑续接未执行完的 chunk。

### Whole-Body Teleoperation Pipeline

作者还给了完整的 teleop 采集方案，这点很重要，因为 post-training 数据质量直接决定 whole-body skill 上限。

- 头显 + wrist tracker: 解 multi-target IK，得到 arm joints 与 torso pose
- 低层 locomotion RL policy: 输出 lower-body joints
- MANUS gloves: 精确 finger tracking
- waist / foot trackers: 提供高层 locomotion commands

这套设计比直接端到端全身 retargeting 更稳，因为作者明确指出 whole-body direct retargeting 容易导致 foot drifting 和 lower-body instability。

## 关键公式

### 公式 1: [[Vision-Language Model|任务空间动作自回归建模]]

$$
p_{\theta}(\mathbf{a})=\prod_{t=1}^{N}p_{\theta}(\mathbf{a}_{t}\mid \mathbf{a}_{<t}, \ell, \mathbf{o}_{t})
$$

**含义**: 预训练阶段把 action prediction 直接写成自回归条件建模。视觉观测 $\mathbf{o}_t$、语言指令 $\ell$ 和历史动作 token 一起决定下一步动作 token。

**符号说明**:

- $\mathbf{a}$: 整段动作 token 序列
- $\mathbf{a}_t$: 第 $t$ 个动作 token
- $\mathbf{a}_{<t}$: 历史 token 前缀
- $\ell$: language instruction
- $\mathbf{o}_t$: 当前视觉观测
- $\theta$: 视觉语言骨干参数

### 公式 2: Flow Matching 动作头训练目标

$$
\mathcal{L}_{fm}
=
\mathbb{E}\left[
\left\lVert
v_{\rho}^{flow}(\mathbf{z}_{t}, \mathbf{a}_{t}^{\tau}, \tau)
-
(\bm{\epsilon}-\mathbf{a}_{t})
\right\rVert
\right]
$$

**含义**: post-training 阶段不再预测 task-space token，而是让 flow-based action expert 学 joint-space action chunk 的速度场。模型在带噪动作 $\mathbf{a}_{t}^{\tau}$ 上预测从噪声走回真实动作的方向。

**符号说明**:

- $\mathbf{z}_t$: 条件特征，来自冻结的视觉语言骨干
- $\mathbf{a}_{t}^{\tau}$: flow timestep $\tau$ 下的带噪动作
- $v_{\rho}^{flow}$: action expert 的 velocity field
- $\bm{\epsilon}$: 噪声样本
- $\rho$: 动作头参数

### 公式 3: Joint-Space 动作向量定义

$$
\mathbf{a}
=
\left\{
\mathbf{q}_{hand},
\mathbf{q}_{arm},
\mathbf{torso}_{rpy},
h_b,
v_x,
v_y,
v_{yaw},
p_{yaw}
\right\}
$$

**含义**: 作者在 post-training 中把动作显式拆成 hand, arm, torso 和 locomotion command 四部分。这样做的核心不是形式漂亮，而是承认 whole-body loco-manipulation 需要同时处理 dexterous upper body 和 lower-body base motion。

**符号说明**:

- $\mathbf{q}_{hand}$: 双手关节动作
- $\mathbf{q}_{arm}$: 双臂关节动作
- $\mathbf{torso}_{rpy}$: torso 旋转命令
- $h_b$: base height
- $v_x, v_y$: 平面速度
- $v_{yaw}, p_{yaw}$: yaw 速度与姿态控制量

## 关键图表

### Figure 2: 训练与部署总览

![Figure 2](https://arxiv.org/html/2603.12263v1/x2.png)

**说明**: 这是整篇论文最重要的一张图。它把「EgoDex 预训练 -> humanoid post-training -> RTC 部署」三段式流程画得非常清楚，也直接说明作者拒绝混训 human 和 robot 数据。

### Figure 3: MM-DiT Action Head

![Figure 3](https://arxiv.org/html/2603.12263v1/x3.png)

**说明**: 这张图强调 action head 不是把 DiT 生搬硬套到机器人上，而是让视觉语言 token 与动作 token 在 timestep 条件下交互。它回答的是“为什么不是 naive DiT 就够了”。

### Figure 4: Real-Time Chunking

![Figure 4](https://arxiv.org/html/2603.12263v1/x4.png)

**说明**: 黄色是当前执行 chunk，青色是 naive 下一段 chunk，红色是 RTC 约束后的连续 chunk。直观看，RTC 的目标就是抑制连续 chunk 间的发散，避免真机动作抖动。

### Figure 5: 真实遥操作采集系统

![Figure 5](https://arxiv.org/html/2603.12263v1/x5.png)

**说明**: 这里展示了 MANUS glove + headset + wrist/waist/foot tracker 的组合。重点不在设备名，而在 upper-body IK 与 lower-body locomotion command 被明确拆开了。

### Figure 6: 八个真实世界任务

![Figure 6](https://arxiv.org/html/2603.12263v1/figures/PSI-Tasks-v3.png)

**说明**: 任务涵盖倒水、擦碗、推车、交接物体、拉托盘、下蹲放袋子等。它们不是单步操纵，而是 manipulation、whole-body motion 和 locomotion 混在一起的长程任务。

### Figure 7: 真实机器人 benchmark

![Figure 7](https://arxiv.org/html/2603.12263v1/x6.png)

**说明**: 左图按任务列出 success rate，右图按技能类型聚合。最关键的信息不是“Psi0 赢了”，而是它在哪些子技能上赢得多: 精细手部、双臂协调和长程 locomotion 都能看到提升。

### Figure 8: Training-Time RTC

![Figure 8](https://arxiv.org/html/2603.12263v1/x7.png)

**说明**: 这张图把 training-time RTC 的 mask 机制画出来了。核心不是换一个损失，而是训练时就让模型学会接住前缀 clean action token。

### Figure 9: 实时系统设计

![Figure 9](https://arxiv.org/html/2603.12263v1/x8.png)

**说明**: server 端有 Control Loop 和 Inference Loop，两者异步工作。只要当前 chunk 执行到阈值 $t \ge s_{min}$，就提前触发下一段推理，从而避免 inference gap。

### Figure 10: 单人 whole-body teleop

![Figure 10](https://arxiv.org/html/2603.12263v1/x9.png)

**说明**: 这张图把 upper-body retargeting、IK 和 lower-body RL policy 的分工画得很清楚。作者的策略不是强迫一个 human full-body tracking 直接复制到 robot，而是只保留更可靠的控制分量。

## 实验结果

### 实现细节

- 机器人平台: Unitree G1，29 DoF whole-body，双臂带 7-DoF Dex3-1 dexterous hands
- 视觉: head-mounted Intel RealSense D435i
- 预训练数据: EgoDex，约 900M frames
- post-training 数据: Humanoid Everyday，约 3M frames real-world teleop
- 下游 fine-tuning: 每任务 80 条 teleoperated trajectories
- 预训练资源: 64x A100，10 天
- post-training 资源: 32x A100，约 30 小时

### 真实世界任务设置

8 个任务全部是多步长程任务，每个任务包含 3 到 5 个子任务。论文允许 evaluator 在早期失败后人工帮助策略进入后续步骤，因此不仅报告 overall success，还报告 sub-task progress。

任务类型包括:

1. 打开水龙头并装水
2. 喷水清洗并折叠碗
3. 拿瓶子转身倒水进杯
4. 抓罐头、转身倒入盘子并推车
5. 把玩具放进篮子后走去交给人
6. 推车、抓葡萄并放盘
7. 提着午餐袋下蹲放桌上
8. 拉托盘并把薯片罐扔进垃圾桶

### 真实机器人 benchmark

从 HTML 表格可读出的整体 success rate 显示，Psi0 在所有 8 个长程任务上都压过了比较强的 GR00T-N1.6、$\pi_{0.5}$、H-RDT 和 InternVLA-M1。

代表性结果如下:

| Task | Psi0 | GR00T-N1.6 | $\pi_{0.5}$ | 备注 |
|------|------|------------|-------------|------|
| Task 1: 去盖子+开水龙头+装水 | 6/10 | 2/10 | 2/10 | 含手指精细接触 |
| Task 2: 喷水+擦碗+叠放 | 7/10 | 4/10 | 3/10 | 双手和容器约束 |
| Task 3: 拿瓶子+转身+倒水 | 8/10 | 4/10 | 2/10 | 需要 locomotion + pour |
| Task 4: 抓罐头+倒入盘子+推车 | 7/10 | 3/10 | 1/10 | manipulation 与 base motion 混合 |
| Task 5: 拿玩具+行走+递交 | 9/10 | 0/10 | 5/10 | 人机交互味更重 |
| Task 6: 推车+抓葡萄+放盘 | 6/10 | 4/10 | 3/10 | 双阶段长程任务 |
| Task 7: 拿袋子+转身+下蹲+放置 | 9/10 | 5/10 | 2/10 | 需要 whole-body balance |
| Task 8: 拉托盘+转身+投掷 | 5/10 | 1/10 | 1/10 | 最难，精细抓取与 locomotion 都脏 |

这张表说明两件事:

1. Psi0 不只是某个单项 manipulation 技能强，而是跨多种 skill 组合都更稳。
2. 即便如此，最难任务也只有 5/10，说明这条路线还远没到“通用 humanoid agent”。

### Ablation: 预训练和 post-training 都有硬贡献

Table I 研究了 pre-training、post-training 和 RTC 的作用。虽然 HTML 截取有限，但可以直接读到趋势:

- 没有 pre-training / post-training 时，整体 success 基本接近 0/10。
- 加入 pre-training 后，长程 dual-arm carry 这类任务能明显起来。
- 再加 post-training 后，overall success rate 可以进一步抬到 8/10 量级。

这正好支持作者的中心论点: human egocentric pretraining 和 humanoid post-training 两者缺一不可。

### Ablation: EgoDex 规模很关键

Table V 对比了 full EgoDex 和 10% EgoDex 预训练:

| Setting | Pick Dumpling | Pick Hippo | Carry Box | Overall SR |
|---------|---------------|------------|-----------|------------|
| Baseline (Psi0) | 9/10 | 9/10 | 10/10 | 8/10 |
| 10% EgoDex | 6/10 | 1/10 | 5/10 | 1/10 |

另一个实验里:

| Setting | Grasp Bottle | Wipe Bowl | Stack Up | Overall SR |
|---------|--------------|-----------|----------|------------|
| Baseline (Psi0) | 10/10 | 9/10 | 7/10 | 7/10 |
| 10% EgoDex | 9/10 | 10/10 | 7/10 | 6/10 |

结论很清楚: EgoDex 规模不是装饰项，尤其对更难的组合任务影响很大。

### Ablation: 只用 Humanoid Everyday 不够

Table VI 比较 full recipe 和 “只在 HE 上预训练”的变体:

| Setting | Pick Dumpling | Pick Hippo | Carry Box | Overall SR |
|---------|---------------|------------|-----------|------------|
| Baseline (Psi0) | 9/10 | 9/10 | 10/10 | 8/10 |
| HE only | 9/10 | 4/10 | 10/10 | 4/10 |

另一个任务组:

| Setting | Grasp Bottle | Wipe Bowl | Stack Up | Overall SR |
|---------|--------------|-----------|----------|------------|
| Baseline (Psi0) | 10/10 | 9/10 | 7/10 | 7/10 |
| HE only | 10/10 | 9/10 | 4/10 | 4/10 |

这说明 human egocentric pretraining 不是可有可无的前菜，而是整套 recipe 的关键组成。

### RTC 的作用

作者在 X-A 节里还把 RTC 移植到 GR00T-N1.6 上。结果显示 RTC 对 GR00T 只带来“可比”表现，不是无脑增益。这说明 RTC 不是万能补丁，它必须和 action head、chunk training 配方一起设计才有效。

## 关键表格

### Table I: 组件消融

论文比较了 pre-training、post-training、RTC 以及 MM-DiT/naive DiT 的组合。最重要的结论不是某一行具体数字，而是:

- **不做 pre-training** 基本学不起来长程任务。
- **只做 pre-training 不做 post-training** 能提升泛化，但精确执行仍不够。
- **post-training + MM-DiT** 才把 humanoid joint control 真正立起来。

### Table II: FAST Tokenizer

| Setting | Reconstruction L1 Loss | Avg Token Length |
|---------|------------------------|------------------|
| Before | $5.83 \\times 10^{-4}$ | 2.08 |
| After | $\mathbf{1.95 \\times 10^{-4}}$ | 13.04 |

**解读**: FAST tokenizer 的训练不是细枝末节。token 更长但重建误差更低，说明 action chunk 在后续大模型训练里能更稳定地承载控制信息。

### Table III: 真实世界详细 benchmark

这张表列了每个子任务的 success，比如 grasp, pull, walk, squat, pour 等。它比单个 overall SR 更有价值，因为能看出 Psi0 的真正优势在:

- 较长动作链下的 continuity
- manipulation 与 locomotion 的交替切换
- 一些带 orientation change 的 whole-body 操作

### Table IV-VI: RTC 与数据 recipe 消融

这几张表共同说明:

1. RTC 不是白给增益，但能减少部署抖动。
2. 缩减 EgoDex 会让性能明显掉下去。
3. 只依赖 humanoid robot data 不能替代 human egocentric pretraining。

## 批判性思考

### 优点

1. **数据观很对**: 作者没有继续迷信 heterogeneous data 混训，而是根据 human / humanoid 的作用分配训练职责。
2. **工程闭环完整**: 从数据采集、action tokenizer、post-training 到 deployment RTC 都讲清楚了。
3. **benchmark 比较硬**: 8 个真实长程任务比一堆单步 manipulation demo 更能说明问题。
4. **部署问题不回避**: 直接把 latency 和 chunk continuity 当论文主要问题之一处理，这很少见。

### 局限性

1. **仍然依赖 per-task fine-tuning**: 虽然 foundation model 很响，但下游任务仍要 80 条 teleop 轨迹微调，离真正 zero-shot generalist 还远。
2. **精细 manipulation 仍是短板**: 最难任务整体只有 5/10，说明手部接触与长程规划还没有被彻底打通。
3. **评价仍然偏特定场景**: 任务都在 pantry / household setup，离更开放的环境和更强扰动还有距离。
4. **RTC 不是万能药**: 它能改善 continuity，但不自动解决错误恢复、碰撞回退和 long-horizon replanning。

### 潜在改进方向

1. 用更轻、更快的 action-conditioned backbone 进一步压 inference latency。
2. 把 tactile / force feedback 纳入 action expert，而不是只靠视觉与语言。
3. 把当前 per-task fine-tuning 进一步压缩成更少演示，或者更强的 in-context adaptation。
4. 引入显式 failure recovery / replanning，而不是只保证 chunk continuity。

### 可复现性评估

- [ ] 完整代码已验证可用
- [ ] 全部数据集可公开获取
- [x] 训练 recipe 足够明确
- [x] 真实硬件与传感器配置写得较清楚
- [x] 关键 ablation 足够支持中心论点

## 对当前工作流的启发

- 如果你做 humanoid whole-body imitation，这篇最值得借的是“human data 用来学表征，robot data 用来学执行”的 recipe。
- 如果你做 teleop 数据采集，这篇证明了 task-agnostic humanoid data 仍然非常值钱，不一定非得每个任务都从零采。
- 如果你做 deployment，RTC 那部分比很多大模型论文都更值得看，因为它真的在解决上线时会遇到的连续执行问题。

## 关联笔记

### 基于

- [[Vision-Language Model]]: 预训练阶段的视觉语言骨干
- [[EgoDex]]: human egocentric pretraining 的核心数据来源
- [[Whole-Body Controller]]: 部署侧 whole-body 执行的关键组件

### 对比

- [[WholeBodyVLA]]: 同样瞄准 humanoid control，但更依赖 robot-specific data
- [[InternVLA]]: 代表现有 humanoid / VLA 风格基线
- [[RDT]]: 机器人 foundation model 对比面之一
- [[ACT]]: 作为 action expert / behavior cloning 路线的重要参照
- [[ZeroWBC]]: 同样利用人类第一视角数据，但 ZeroWBC 更强调“生成人体动作再 tracking”，Psi0 更强调 staged humanoid foundation model

### 方法相关

- [[Reinforcement Learning]]: lower-body locomotion policy 与整体部署稳定性仍依赖 RL
- [[DeepMimic]]: 代表更传统的 motion imitation 参照系
- [[MaskedMimic]]: partial observation / motion tracking 相关比较对象
- [[OmniControl]]: text-conditioned motion 方向的相关方法

## 速查卡片

> [!summary] Psi0
> - **核心问题**: human/humanoid data 混训效率低，whole-body loco-manipulation 难以稳定落地
> - **方法**: VLM on EgoDex pretrain + flow-based action expert post-train + real-time chunking
> - **亮点**: 8 个真实长程 humanoid 任务，全面压过 GR00T-N1.6 / $\pi_{0.5}$ / H-RDT 等基线
> - **真正价值**: 给出了一个更可信的 humanoid foundation model 数据 recipe
> - **主要短板**: 仍需 per-task fine-tuning，精细 manipulation 和 failure recovery 还没打透

*笔记创建时间: 2026-03-16 15:05*
