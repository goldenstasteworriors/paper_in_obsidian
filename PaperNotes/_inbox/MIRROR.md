---
title: "MIRROR: Visual Motion Imitation via Real-time Retargeting and Teleoperation with Parallel Differential Inverse Kinematics"
method_name: "MIRROR"
authors: ["Junheng Li", "Lizhi Yang", "Aaron D. Ames"]
year: 2026
venue: arXiv
tags: [humanoid, teleoperation, inverse-kinematics, motion-retargeting, whole-body-control, robot-safety]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2603.23995v1
created: 2026-03-26
---

# MIRROR

## 一句话判断

这篇最值钱的地方，不是“又做了一个视觉 teleop demo”，而是终于把 humanoid real-time retargeting 里最恶心的三个坑放到同一个系统里处理了: 局部最优卡死、自碰撞约束、以及还得跑得够快。

## 论文信息

- 论文: [arXiv](https://arxiv.org/abs/2603.23995v1) | [PDF](https://arxiv.org/pdf/2603.23995v1)
- 项目主页: [MIRROR Project](https://caltech-amber.github.io/mirror/)
- 代码: 论文和项目页里暂未看到公开仓库
- 作者: Junheng Li, Lizhi Yang, Aaron D. Ames
- 机构: California Institute of Technology
- 机器人平台: Westwood Robotics THEMIS V2 Pro humanoid
- 任务类型: humanoid teleoperation, motion retargeting, real-time inverse kinematics, upper-body manipulation
- 感知前端: Stereolabs ZED 2i stereo camera + Body38 visual skeleton
- 安全机制: 任务空间 continuation + [[Control Barrier Function]] 约束 + Lyapunov progress certificate
- 硬件结果: tethered desktop 模式下 perception 到机器人接收命令约 54.9 ms，人动作到机器人动作真实端到端约 170 ms（PD）/ 250 ms（WBC）

## 一句话总结

> MIRROR 用并行 [[Differential Inverse Kinematics]]、离散时间 [[Control Barrier Function]] 约束和 progress certificate，把“快但容易卡死”的 differential IK，改造成了一个能在真机 humanoid 上稳定做视觉 teleoperation 的系统。

## 核心贡献

1. **完整可落地的视觉 teleoperation 管线**: 从 stereo skeleton 到 humanoid joint command，全链路都围绕真实部署的延迟和安全约束设计。
2. **并行 continuation differential IK**: 不是解单个 IK-QP，而是并行解一组 continuation 参数不同的 QP，主动提高逃离局部 basin 的概率。
3. **显式自碰撞安全约束**: 用离散时间 [[Control Barrier Function]] 在 IK 层面直接限制手肘和手部相对躯干/头部的安全裕量。
4. **Lyapunov 证书驱动候选选择**: 不是谁先解出来就用谁，而是只接受那些能让最终任务误差真正下降的候选解。
5. **真机端到端验证**: 在 THEMIS 上做了 upper-body motion mirroring、物体传递、部分遮挡、双臂协作和 tennis 动作等任务。

## 问题背景

### 要解决的问题

humanoid teleoperation 的根问题不是“有没有人体骨架”，而是把 noisy visual skeleton 变成安全、稳定、足够快的关节更新。只要控制链路里还有局部最优、关节极限或自碰撞边界，传统 differential IK 就很容易在关键时刻卡住。

### 现有方法的局限

- 传统 global IK 虽然更接近全局最优，但计算太重，不适合高频 whole-body teleoperation。
- 单实例 [[Differential Inverse Kinematics]] 很快，但它是局部线性化方法，容易被 joint limit、singularity 和 active collision constraint 困在局部 basin。
- 很多 camera-based teleoperation 工作把 pose estimation 讲得很热闹，却默认下游 IK 会自己把安全和实时性搞定。
- 单纯在低层 [[Whole-Body Controller]] 里补救，并不能从根本上解决 reference 生成本身已经跑偏的问题。

### 本文的动机

作者的判断很直接:

1. 对 humanoid 来说，“能实时解出来”比“离全局最优更近”更重要。
2. 既然单个 differential IK 解容易卡，那就并行看多个 continuation 目标。
3. 既然安全约束在局部优化里会改变 active set，那就必须把碰撞约束放进优化本体，而不是做后处理。
4. 既然 continuation 候选不止一个，就需要一个面向最终任务误差的选择准则，而不是看中间目标是否对齐得最漂亮。

## 方法详解

### 整体框架

MIRROR 整体分三层:

1. **Perception and Pose Processing**: 从 ZED 2i 提取 Body38 视觉骨架，并做滤波、跳变抑制和多人体拒绝。
2. **Task-space Command Continuation**: 把人体关键点映射到 robot torso frame，并生成一系列 continuation target。
3. **GPU-accelerated Whole-body Kinematic Retargeting**: 并行求解一族带碰撞约束的 IK-QP，再通过 progress certificate 选出真正往最终目标走的那一个。

### 感知与姿态处理

感知前端不是花哨的大模型，而是一个很务实的实时骨架流:

- 用 ZED 2i 的 Body38 输出全身 3D 关键点。
- 只保留对 teleoperation 真有用的 task-space target，例如 torso、双手、双肘、指尖。
- 先减去 body anchor，转到局部 body frame，避免全局坐标变化把下游控制搞乱。
- 对每个关键点做三层稳态处理:
  - confidence-based gating
  - jump rejection
  - multi-body rejection

这部分的意义不是“让骨架更平滑”这么简单，而是保证下游 IK 面对的是一个没有明显离群点、没有身份切换、没有大幅跳变的目标流。

### Command continuation

作者不是直接让机器人去追最终 task-space target，而是先做两件事:

1. **Command scaling**: 解决人和机器人身体尺度不同的问题，把人体 body-frame 关键点缩放到机器人 torso frame。
2. **Continuation target generation**: 把当前 task value 和最终 target 之间按不同的 $\alpha$ 做插值。

这一步非常关键。传统 differential IK 一旦直接追远距离目标，就容易在约束激活时停在坏 basin 里。MIRROR 则故意在不同 $\alpha$ 上并行求解，让求解器有机会从不同 active-set regime 里找到更好的下降方向。

### 并行 differential IK

每个 continuation 参数 $\alpha_j$ 都会产生一个独立的 QP:

- 目标项让 $J(q)\Delta q$ 逼近 $\alpha_j e(q)$。
- 正则项惩罚过大的关节增量。
- 约束项包括自碰撞 D-CBF、关节增量上界和关节位置界。

他们的 upper-body 实现把问题分成左右手臂两个子 QP，再通过固定 embedding 合成全局更新。作者的核心论点是，分布式小 QP 不只是更快，还能在固定时间预算下给你更多 continuation candidate，从而提高“碰到能逃出坏 basin 的更新方向”的概率。

### 自碰撞安全

MIRROR 没有把自碰撞安全留给低层，而是在 IK 里直接把它写成离散时间 [[Control Barrier Function]] 约束:

- 用 3 个 bounding sphere 近似头和躯干。
- 用 4 个关键点代表双手和双肘。
- 约束这些关键点相对 sphere 的安全函数 $h_i(q)$ 保持非负。

这并不等价于“绝对不会撞”，因为真实硬件还有控制误差和执行延迟，但它至少保证优化器不会为了追任务误差主动往明显不安全的方向解。

### 候选选择与 progress certificate

MIRROR 的 selection 不是“选 tracking 最准的 continuation 参数”，而是“选能让最终 global IK objective 下降的 continuation 参数”。

具体来说:

- 先定义最终任务误差对应的 Lyapunov-like objective $V(q)$。
- 对每个候选 $\Delta q(\alpha_j)$，预测下一步误差 $e^+(q)$ 和 $V^+(\Delta q)$。
- 只有满足足够下降量的候选才会被接受。
- 在所有可接受候选里，选 continuation 参数最大的那个，也就是“尽量激进、但依然被证明在往前走”的更新。

这一步是整篇论文最值得借鉴的地方。它不是让 continuation 变成 heuristics，而是给了一个明确的 certificate。

### 硬件执行

最后的 joint position / velocity command 会下发给 THEMIS 的低层控制器执行。论文里明确说 MIRROR 本身不依赖某个特定的低层控制实现，因此可以和不同的 [[Whole-Body Controller]] 或 joint-space PD 控制配合。

这个设计是对的，因为它把“参考动作生成”和“低层平衡/接触控制”拆开了。坏处也明显: 最终硬件 tracking 质量仍然部分受低层控制器能力限制。

## 关键公式

### 公式 1: 关键点稳态滤波

$$
\bar{p}_t=
\begin{cases}
\bar{p}_{t-1}, & \text{if invalid}, \\
\lambda_{jr} p_t + (1-\lambda_{jr}) \bar{p}_{t-1}, & \|p_t-\bar{p}_{t-1}\| > \tau_{jr}, \\
\alpha_{jr} p_t + (1-\alpha_{jr}) \bar{p}_{t-1}, & \text{otherwise}.
\end{cases}
$$

**含义**: 视觉关键点不是直接拿来用，而是先按置信度、跳变幅度决定保守更新还是正常更新。

**符号说明**:
- $p_t$: 当前帧观测到的 3D 关键点
- $\bar{p}_{t-1}$: 上一帧滤波结果
- $\tau_{jr}$: jump rejection 阈值
- $\lambda_{jr}$: 跳变时的保守混合系数
- $\alpha_{jr}$: 正常情况下的滤波系数

### 公式 2: continuation 目标

$$
x_d(\alpha) = (1-\alpha)x + \alpha x_d
$$

$$
d_x(\alpha) = x_d(\alpha) - x(q) = \alpha e(q)
$$

**含义**: MIRROR 不直接追最终目标 $x_d$，而是追一组由 $\alpha$ 控制的中间目标，以提高逃离局部 basin 的概率。

**符号说明**:
- $x$: 当前 task-space 值
- $x_d$: 最终期望 task-space 目标
- $x(q)$: 当前关节位形对应的 forward kinematics
- $e(q)$: 最终目标误差
- $\alpha \in [0,1]$: continuation 参数

### 公式 3: 离散时间 [[Control Barrier Function]] 约束

$$
h_i(q) = \|x_i^{pos}(q) - c_o(q)\|^2 - \rho_i^2
$$

$$
\nabla h_i(q)^\top \Delta q \ge -\gamma h_i(q)
$$

**含义**: 只要这条不等式成立，离散时间下的关节更新就不会主动破坏关键点相对 torso/head 球体的安全裕量。

**符号说明**:
- $x_i^{pos}(q)$: 手或肘等关键点位置
- $c_o(q)$: 躯干/头部包围球中心
- $\rho_i$: 球半径、肢体厚度和 safety margin 的和
- $\gamma$: D-CBF 收敛系数

### 公式 4: 并行 IK-QP 目标

$$
\Delta q(\alpha_j) \in \arg\min_{\Delta q}
\frac{1}{2}\|J(q)\Delta q-\alpha_j e(q)\|^2_{W_x}
\frac{1}{2}\|\Delta q\|^2_{W_q}
$$

subject to

$$
\nabla h_i(q)^\top \Delta q \ge -\gamma h_i(q), \quad
\Delta q_{min} \le \Delta q \le \Delta q_{max}, \quad
q_{min} \le q+\Delta q \le q_{max}.
$$

**含义**: 每个 continuation 参数都对应一个独立 QP，同时平衡 task-space tracking、更新幅度和安全约束。

**符号说明**:
- $J(q)$: 任务雅可比
- $W_x, W_q$: 任务误差和关节更新的权重矩阵
- $\Delta q_{min}, \Delta q_{max}$: 关节增量上下界
- $q_{min}, q_{max}$: 关节位置上下界

### 公式 5: progress certificate

$$
V(q) = \frac{1}{2} e(q)^\top W e(q)
$$

$$
\hat{e}^{+}(\Delta q) = e(q) - J(q)\Delta q
$$

$$
\hat{V}^{+}(\Delta q) = \frac{1}{2}\hat{e}^{+}(\Delta q)^\top W \hat{e}^{+}(\Delta q)
$$

$$
\hat{V}^{+}(\Delta q(\alpha_j)) \le V(q) - \eta
$$

**含义**: 只有真正能让最终目标误差下降的候选才会被接受，而不是只看中间 continuation target 的局部对齐。

**符号说明**:
- $V(q)$: 最终 tracking 目标对应的 Lyapunov-like 目标函数
- $\hat{e}^{+}$: 一步线性化后的预测误差
- $\eta$: 最小下降阈值

### 公式 6: 并行候选带来的逃逸概率

$$
\mathbb{P}\big(\exists k \le K: \alpha_k \in A_{esc}^{pc}(q)\big)
= 1-(1-p^{pc}(q))^K
$$

**含义**: 如果 progress-certified escaping set 的测度大于 0，那么并行候选数 $K$ 越大，至少有一个候选能逃离坏 basin 的概率就越高。

## 关键图表

### Figure 1: Real-time human-humanoid motion mirroring teleoperation

![Figure 1](https://arxiv.org/html/2603.23995v1/x1.png)

**说明**: 论文的门面图，但不是空摆拍。它直接传达出 MIRROR 的目标不是离线 retargeting，而是“人动的时候 humanoid 也得在安全约束下实时跟”。

### Figure 2: MIRROR pipeline architecture

![Figure 2](https://arxiv.org/html/2603.23995v1/x2.png)

**说明**: 这张图是全篇最重要的系统图。左边是 perception 和 command smoothing，中间是 task continuation，右边是带 D-CBF 的并行 distributed differential IK，最后再下发到 THEMIS。读完这张图基本就抓住整篇方法了。

### Figure 3: Snapshots of real-time teleoperation

![Figure 3](https://arxiv.org/html/2603.23995v1/x3.png)

**说明**: 展示 pose mirroring 和 mimicking 的直观效果。这里最重要的不是“动作像不像”，而是看系统有没有在不同手臂姿态里频繁卡死或出现明显自碰撞。

### Figure 4: Useful real-world tasks through MIRROR teleoperation

![Figure 4](https://arxiv.org/html/2603.23995v1/x4.png)

**说明**: 包含物体传递、部分遮挡、双臂操作和 tennis 动作。它说明作者不是只拿单臂抬手做 demo，而是故意放进了更容易触发碰撞和局部最优问题的动作。

### Figure 5: Comparison of motion capture devices tracking hand location

![Figure 5](https://arxiv.org/html/2603.23995v1/x5.png)

**说明**: 把 raw vision、filtered vision、Meta Quest 3 VR 和 OptiTrack 放在一起比。结论很明确: 原始视觉关键点抖动明显，做完 filtering/robustification 之后，轨迹虽然不如 OptiTrack 这么干净，但已经足够支持 teleoperation。

### Figure 6: Latency breakdown with different hardware setups

![Figure 6](https://arxiv.org/html/2603.23995v1/x6.png)

**说明**: 这张图说明 MIRROR 不是只会在论文里说“real-time”。不同硬件设置下的 perception、IK 和总模块延迟都被拆开了，方便看瓶颈到底在相机、求解器还是通信。

### Figure 7: Left hand tracking performance on hardware

![Figure 7](https://arxiv.org/html/2603.23995v1/x7.png)

**说明**: 真机左手 task-space 跟踪曲线。这里能看出 MIRROR 生成的 joint-level command 在 WBC 执行后依然会有误差，但整体趋势跟随是稳定的。

### Table 1: Ablation study on differential IK solving methods over long-horizon hand tracking

| Method | Batch K | eta | Solve Time [ms] | hand error [mm] | final hand error [mm] | Self Collision | Singularity | Stagnation |
|--------|---------|-----|-----------------|-----------------|-----------------------|----------------|-------------|------------|
| Global IK (SQP) | 1 | - | 176.57 ± 4.20 | 12.44 ± 3.12 | 6.58 ± 2.23 | 42/250 | 0/250 | 0/250 |
| Monolithic QP | 1 | - | 0.58 ± 0.05 | 18.57 ± 9.82 | 16.23 ± 4.12 | 135/250 | 17/250 | 44/250 |
| Distributed QP | 1 | - | 0.94 ± 0.06 | 17.72 ± 10.68 | 10.44 ± 4.56 | 142/250 | 19/250 | 46/250 |
| Parallel Dist. QPs, no progress certificate | 4096 | - | 4.08 ± 0.06 | 16.61 ± 7.95 | 11.45 ± 3.34 | 68/250 | 9/250 | 45/250 |
| Parallel Dist. QPs, with certificate | 4096 | 0.0005 | 4.10 ± 0.04 | 16.67 ± 7.58 | 10.30 ± 4.45 | 18/250 | 7/250 | 17/250 |
| Parallel Dist. QPs, stronger certificate | 4096 | 0.001 | 4.14 ± 0.07 | 22.09 ± 7.16 | 15.65 ± 4.41 | 3/250 | 5/250 | 7/250 |

**说明**: 这张表把论文的核心 trade-off 讲透了。global IK 精度最好但慢得离谱；普通 QP 快，但碰撞和 stagnation 爆炸；MIRROR 的并行 distributed QP 在约 4 ms 内明显压低 collision 和 stagnation。更大的 $\eta$ 让系统更保守、更安全，但 tracking error 也会升高。

## 实验结果

### 实验设置

- **仿真后端**: MuJoCo
- **硬件平台**: THEMIS V2 Pro humanoid，40 actuated DOF
- **桌面计算平台**: Intel Ultra 9 285K + NVIDIA RTX 5090
- **CPU QP 求解器**: OSQP
- **GPU batch 求解器**: 自定义 ADMM-QP in PyTorch

### 主要结论

1. **global IK 不现实**: 176 ms 的求解时间虽然精度最好，但对 real-time teleoperation 基本没法用。
2. **单实例 differential IK 不稳**: 不管 monolithic 还是 distributed，只要没有 parallel continuation，就容易 self-collision、singularity 和 stagnation。
3. **并行 continuation 真有用**: batch size 增大后，论文观察到 CBF violation 和 stagnation 持续下降，这和理论部分的 escape probability 结论是一致的。
4. **progress certificate 不是装饰**: 加上证书后 collision 和 stagnation 进一步降低，说明候选筛选标准确实有效。
5. **更强的证书更保守**: $\eta$ 增大后，安全性更强，但 tracking accuracy 会掉，这就是非常典型的 robustness-accuracy trade-off。

### 延迟结果

- perception 到机器人接收 joint-space command 的平均总延迟约 **54.9 ms**
- 人动作到机器人动作的真实端到端视频测量延迟约 **170 ms**（tethered PD mode）
- 同样测量在 tethered WBC mode 下约 **250 ms**
- 论文声称该结果优于 H2O（约 373 ms）和 HumanPlus（约 340 ms），也接近 VR/MoCap 系统

### 真机任务

- upper-body motion mirroring
- object transfer
- partial occlusion
- dual-arm manipulation
- hand-to-hand transfer
- tennis motion

这些任务并不意味着 MIRROR 已经解决了 full-body loco-manipulation，但至少说明它不是单个关节跟踪的实验室玩具。

## 批判性思考

### 优点

1. **问题定义准**: 把 teleoperation 真正的系统瓶颈锁定在 IK basin trapping，而不是继续把锅都甩给感知噪声。
2. **方法和部署强绑定**: 每个设计点都对着 real-time 和 safety 来，不像很多控制论文只在离线优化上堆理论。
3. **定量 trade-off 讲清楚**: Table 1 和 latency breakdown 都让系统代价很透明。

### 局限性

1. **目前主要是 upper-body**: 论文结论里也承认 full-body 还需要更多 coupling/consensus 设计。
2. **安全模型比较粗**: 自碰撞靠几个 bounding sphere 近似，覆盖不了全部几何细节。
3. **最终执行依赖低层控制器**: 论文明确说 tracking performance 也取决于下游 [[Whole-Body Controller]]，说明参考动作生成不是全部。

### 潜在改进方向

1. 把 distributed formulation 扩到 full-body loco-manipulation，并显式处理肢体之间的 coordination constraint。
2. 用更细的几何模型或 contact-aware safety model 取代简单 sphere CBF。
3. 把 continuation candidate 的选择和低层控制器状态联合起来，而不是只看高层几何误差下降。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [x] 方法细节较完整
- [x] 硬件与实验设置写得比较清楚

## 关联笔记

### 基于

- [[Differential Inverse Kinematics]]: MIRROR 的主体就是把 differential IK 从单实例局部更新，改造成并行 continuation 求解。
- [[Control Barrier Function]]: 论文把自碰撞安全直接写进离散时间 IK 约束，而不是后处理。

### 对比

- [[CuRobo]]: 两者都利用并行化提高优化鲁棒性，但 CuRobo 更偏 collision-free motion generation，MIRROR 更聚焦 real-time teleoperation IK。
- [[Model Predictive Control]]: MIRROR 选择 continuation + batch QP，而不是把控制频率全部交给重型 MPC。

### 方法相关

- [[Whole-Body Controller]]: MIRROR 生成 joint-level reference，真正的平衡与执行仍靠 WBC。

## 速查卡片

> [!summary] MIRROR
> - **核心**: 用并行 continuation differential IK 解决 humanoid teleoperation 里的局部最优和安全约束问题
> - **方法**: visual skeleton + command continuation + D-CBF constrained batch QP + progress certificate
> - **结果**: 约 4 ms IK 求解时间，显著降低 collision/stagnation，并在 THEMIS 上完成真实 teleop 任务
> - **代码**: 未见公开仓库，项目页已提供视频和论文入口

*笔记创建时间: 2026-03-26*
