---
title: "Make Tracking Easy: Neural Motion Retargeting for Humanoid Whole-body Control"
method_name: "NMR"
authors: ["Qingrui Zhao", "Kaiyue Yang", "Xiyu Wang", "Shiqi Zhao", "Yi Lu", "Xinfang Zhang", "Wei Yin", "Qiu Shen", "Xiao-Xiao Long", "Xun Cao"]
year: 2026
venue: arXiv
tags: [humanoid, motion-retargeting, whole-body-control, imitation-learning, motion-tracking, robot-control]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2603.22201v1
created: 2026-03-25
---

# NMR

## 一句话判断

这篇最有价值的地方，不是又发了一个 retargeting 网络，而是正面承认传统几何优化 retargeting 本身就困在非凸局部最优里，然后用 `CEPR + neural mapping` 把这个老坑绕过去。

## 论文信息

- 论文: [arXiv](https://arxiv.org/abs/2603.22201v1) | [PDF](https://arxiv.org/pdf/2603.22201v1)
- 项目主页: [NMR Project](https://3dv-humanoidgroup.github.io/nmr.github.io/)
- 代码: [GitHub](https://github.com/3DV-HumanoidGroup/MakeTrackingEasy)
- 作者: Qingrui Zhao, Kaiyue Yang, Xiyu Wang, Shiqi Zhao, Yi Lu, Xinfang Zhang, Wei Yin, Qiu Shen, Xiao-Xiao Long, Xun Cao
- 机构: Nanjing University, Huawei Technologies, Horizon Robotics
- 机器人平台: Unitree G1
- 任务类型: humanoid motion retargeting, whole-body tracking reference generation, human-to-humanoid embodiment transfer
- 数据来源: human [[SMPL]] motion sequence，经 kinematic retargeting 和 physics refinement 生成人机配对数据
- 真实部署: 有。论文在 G1 上验证了 martial arts、dancing 等动态 whole-body motion 的 tracking 效果

## 一句话总结

> NMR 把 human-to-humanoid retargeting 从逐帧几何优化改成对物理可行动作分布的学习，并用 `CEPR` 生成约 30K 条 physics-preserved 人机配对数据作为监督。

## 核心贡献

1. **重写问题定义**: 把 retargeting 从 frame-wise optimization 改成 motion distribution mapping，直接绕开 IK / GMR 一类方法的局部最优陷阱。
2. **提出 CEPR 数据管线**: 先过滤人类动作，再做 kinematic retargeting，再用分簇 RL expert 在物理仿真里把参考动作修成机器人可执行轨迹。
3. **设计并训练 NMR 网络**: 用 1D ResNet encoder + Transformer + upsampling decoder 直接从 human motion sequence 预测 humanoid motion sequence。
4. **两阶段训练策略**: 先吃大规模 kinematic 数据学 coverage，再用 CEPR 精修物理可行性，避免只靠小规模 physics data 过拟合。
5. **证明下游收益**: cleaner reference 不只让 retargeting 指标好看，也能让下游 whole-body tracking policy 训练更快、更稳。

## 问题背景

### 要解决的问题

现有 humanoid learning pipeline 大量依赖人类动作数据，但人和机器人在关节拓扑、尺度、接触约束和动态可行性上完全不是一回事。motion retargeting 这一步如果做烂，后面的 tracking policy 只是在给脏 reference 擦屁股。

### 现有方法的局限

- 传统 IK / GMR / sequence-level optimization 本质还是在解非凸问题，初始化一差就容易卡死在局部最优。
- 纯几何 retargeting 不懂物理，SMPL 抖动、ground penetration、foot floating 这类源噪声会被原样传下去。
- 直接拿优化结果做监督会把错误写进数据集，神经网络只会把错误学得更快。
- 只靠 RL tracking policy 去消化脏 motion reference，会浪费大量训练预算在补偿 retargeting artifact 上。

### 本文的动机

作者的核心判断很直接:

1. retargeting 的难点不只是 mapping，而是 mapping 到物理可行的 humanoid manifold。
2. 既然优化方法容易掉坑，那就不要继续逼它当“老师”，而是让它只做初筛。
3. 先用 physics simulation 把数据修干净，再让网络学分布映射，才有可能同时兼顾 coverage 和 physical fidelity。

## 方法详解

### 整体框架

NMR 整个系统分两层：

1. `CEPR` 负责构造高质量监督数据。
2. `NMR` 负责学习 human motion 到 humanoid motion 的序列映射。

更具体地说，输入是 human [[SMPL]] sequence $\{s_t\}_{t=1}^T$，输出是 humanoid generalized coordinates $\{q_t\}_{t=1}^T$。和传统方法每帧独立解一个最优姿态不同，NMR 把整个序列当成一个时序建模问题处理。

### CEPR: Clustered-Expert Physics Refinement

CEPR 是这篇真正的灵魂，不是附属工程。

#### Step 1: Physics-aware human motion curation

- 先过滤不适合机器人执行的原始人类动作。
- 删除 excessive jerk、CoM 明显偏离支撑域、foot contact 不足、float / penetration 明显的序列。
- 这一步的作用不是“清洗得更好看”，而是避免一开始就把明显不合理的人类动作塞给机器人。

#### Step 2: Kinematic retargeting and hard filtering

- 使用 GMR 先做初始 human-to-humanoid kinematic retargeting。
- 然后对结果做硬阈值过滤：
- 关节速度过大则丢弃，避免 IK singularity 导致的 joint jump。
- 自碰撞比例超过 `cross_ratio = 0.05` 的序列丢弃。
- 平均足底离地高度超过 `float_threshold = 0.10m` 的序列丢弃。

这一步的意义在于：作者并没有否认优化法有用，而是把它降级成“粗糙生成器 + 过滤器”，而不再拿它当最终答案。

#### Step 3: Physics-based humanoid motion refinement

- 将保留下来的动作按语义和行为特征分簇。
- 使用 motion-text retrieval 模型 TMR 提取 latent feature，再用 K-Means 做 motion clustering。
- 每个 cluster 训练一个专门的 [[PPO]] tracking expert。
- 在 massively parallel physics simulator 中 rollout expert policy，把动作修正到 robot-feasible motion manifold。

这么做的核心原因是，单一 tracking policy 在全动作库上会出现 distributional conflict，而每条序列单独训 expert 又太贵。分簇是个很现实的中间解。

### NMR 网络结构

NMR 本身不复杂，但设计上很对症。

- **输入**: human motion sequence
- **Encoder**: 1D ResNet 提取局部时序特征
- **Backbone**: Transformer，结构参考 LLaMA，但把 causal attention 改成 full self-attention
- **Decoder**: upsampling + 1D Conv
- **输出**: 对齐长度的 humanoid motion sequence

关键点有两个：

1. human motion 和 humanoid motion 在时间上是一一对应的，所以没必要用 autoregressive generation，直接全局 self-attention 更合理。
2. 全局 temporal context 能帮模型在局部异常帧出现时做时序平滑，这也是它能过滤上游 SMPL 抖动的重要原因。

### 两阶段训练

作者把训练分成两个阶段，这比“直接拿最干净数据从头训”更聪明。

#### Stage 1: Kinematic alignment pre-training

- 用大规模 kinematic retargeting 数据预训练。
- 优点是覆盖面广，模型能学到足够多的 motion mode。
- 缺点是数据里还残留物理 artifact。

#### Stage 2: Physical grounding with CEPR data

- 在 CEPR 生成的高质量数据上微调。
- 学习率降低到 `1e-5`，batch size 保持一致。
- 目标是把 stage 1 学到的 broad coverage，进一步拉回到 physics-feasible manifold。

作者还特别做了 ablation:

- 只做 stage 1 的 `NMR w/o RL` 虽然运动学上看起来像样，但物理可行性明显不够。
- 只拿 CEPR 小数据从头训，又会因为 coverage 不够而过拟合。

这就说明两阶段不是装饰，而是必要条件。

## 关键公式

### 公式 1: 传统优化式 retargeting 目标

$$
\begin{aligned}
f(\mathbf{q}) &=
\sum_{(i,j)\in\mathcal{M}} w^{R}_{i,j}\|R^{h}_{i}\ominus R_{j}(\mathbf{q})\|^{2} \\
&\quad + \sum_{(i,j)\in\mathcal{M}_{ee}} w^{p}_{i,j}\|p^{\mathrm{target}}_{i}-p_{j}(\mathbf{q})\|^{2}
\end{aligned}
$$

**含义**: 这是优化法的代表性目标，前一项对齐旋转，后一项对齐末端位置。论文的论点不是这目标写错了，而是这种 frame-wise objective 在数学上就容易陷入坏局部最优。

**符号说明**:
- $\mathbf{q}$: 机器人广义坐标
- $\mathcal{M}$: human-robot 旋转对应集合
- $\mathcal{M}_{ee}$: end-effector 对应集合
- $R_i^h$: human 第 $i$ 个部位的旋转
- $R_j(\mathbf{q})$: robot 第 $j$ 个部位由 $\mathbf{q}$ 决定的旋转
- $p_i^{\mathrm{target}}$: human 目标末端位置
- $p_j(\mathbf{q})$: robot 末端位置

### 公式 2: Tracking reward 的 curriculum 收紧策略

$$
\sigma(i)=\sigma_{\text{start}}+(\sigma_{\text{end}}-\sigma_{\text{start}})\cdot\frac{i-i_0}{i_{\max}-i_0}
$$

**含义**: CEPR 里的 expert policy 训练不是一开始就逼最高精度，而是先用更宽松的 reward tolerance 学粗模式，再逐步收紧，降低大规模 motion library 带来的 sample inefficiency。

**符号说明**:
- $i$: 当前训练迭代
- $\sigma_{\text{start}}$: 初始宽松标准差
- $\sigma_{\text{end}}$: 末期严格标准差
- $i_0$: curriculum 起始迭代
- $i_{\max}$: 最大训练迭代

### 公式 3: NMR 的序列回归损失

$$
\mathcal{L}=\sum_{t=1}^{T}\|m_{\text{bot}}^{t}-\hat{m}_{\text{bot}}^{t}\|_{1}
$$

**含义**: 网络直接对整段 humanoid motion sequence 做逐时间步的 L1 回归。看起来朴素，但因为 supervision 已经被 CEPR 清洗过，这个简单目标反而能稳定学到物理更合理的序列映射。

**符号说明**:
- $T$: motion sequence 长度
- $m_{\text{bot}}^{t}$: 第 $t$ 帧目标 humanoid motion
- $\hat{m}_{\text{bot}}^{t}$: 第 $t$ 帧网络预测 motion

## 关键图表

### Figure 1: CEPR 数据构建管线

![Figure 1](https://arxiv.org/html/2603.22201v1/x1.png)

**说明**: 从 human motion dataset 到最终 physics preserved motion dataset，一共三层过滤。最重要的不是“数据变多”，而是每一步都在减少 source artifact 对下游监督的污染。

### Figure 2: NMR 网络结构

![Figure 2](https://arxiv.org/html/2603.22201v1/x2.png)

**说明**: 1D ResNet encoder 先提局部时序特征，Transformer 再用 full self-attention 聚合全局上下文，最后 decoder 回归 humanoid motion sequence。这张图很清楚地说明作者没有做 fancy diffusion 或 autoregressive，而是做了一套适合对齐序列映射的 backbone。

### Figure 3: CEPR 微调前后对比

![Figure 3](https://arxiv.org/html/2603.22201v1/x3.png)

**说明**: 这张图展示了 CEPR fine-tuning 的价值。没有 RL/physics refinement 时，网络会保留更多不稳定的关节行为；加了 CEPR 后，motion 明显更顺、更像机器人能真的执行出来的样子。

### Figure 4: 下游 tracking policy 训练曲线

![Figure 4](https://arxiv.org/html/2603.22201v1/x4.png)

**说明**: 这是很关键的一张图。NMR 不只是让 retargeting 指标变好，它还能让下游 policy 拿到更长 episode、更高 reward。也就是说 cleaner reference 在 RL training 里是直接省钱的。

### Figure 5: arm raise-lower 序列上的方法对比

![Figure 5a](https://arxiv.org/html/2603.22201v1/x5.png)

![Figure 5b](https://arxiv.org/html/2603.22201v1/x6.png)

**说明**: GMR 在错误初始化下会撞上 shoulder roll 下限，然后在一段时间内卡住，最后突然跳出局部最优，造成明显 joint jump。NMR 和 PHUMA 都更平滑，但 NMR 的轨迹更稳，而且没有那种突然 1.5 rad 跳变的灾难。

### Figure 6: 上游 SMPL 抖动修正

![Figure 6](https://arxiv.org/html/2603.22201v1/x7.png)

**说明**: 这张图很能说明 neural sequence model 的优势。面对上游 pose estimation jitter，优化法会机械传播错误，而 NMR 会利用前后时序上下文把异常帧抹平。

### Table 1: Policy Observation Space

| 观测组 | 组成 | 维度 |
|--------|------|------|
| Reference motion state | 参考关节位置 $\mathbf{q}^g$、关节速度 $\dot{\mathbf{q}}^g$、body position / velocity / orientation / angular velocity | 29 + 29 + 42 + 42 + 56 + 42 |
| Robot proprioception | 机器人 body position / velocity / orientation / angular velocity、关节位置 $\mathbf{q}^p$、关节速度 $\dot{\mathbf{q}}^p$ | 42 + 42 + 56 + 42 + 29 + 29 |
| Action history | 上一时刻动作 $\mathbf{a}_{t-1}$ | 29 |
| **总计** | - | **509** |

**说明**: expert policy 看的是 reference state 和 proprioception 的显式 tracking error，而不是盲目从 observation 里自己猜 target，这也是它能稳定修动作的原因。

### Table 2: Reward Terms for Expert Policy Training

| Reward term | Weight |
|-------------|--------|
| Anchor position | 1.0 |
| Anchor orientation | 1.0 |
| Anchor velocity | 1.0 |
| Body link position (rel.) | 1.0 |
| Body link orientation (rel.) | 1.0 |
| Body link linear velocity | 1.0 |
| Body link angular velocity | 1.0 |
| Action rate penalty | -0.1 |
| Undesired contacts penalty | -0.1 |

**说明**: 奖励设计明显偏 tracking，不追花哨 regularizer。作者把 reward 预算集中在“先把动作跟准”，而不是塞一堆泛正则项装复杂。

### Table 3: Retargeting Quality Comparison

| Method | Joint Jump ↓ | Self Collision ↓ | Joint Limit ↓ |
|--------|--------------|------------------|---------------|
| GMR | 56 (0.11%) | 947 (1.91%) | 21443 (43.21%) |
| PHUMA | 12 (0.02%) | 2456 (4.95%) | 10580 (21.32%) |
| NMR w/o RL | 2 (0.00%) | 779 (1.57%) | 19324 (38.94%) |
| **NMR** | **0 (0.00%)** | **431 (0.87%)** | **8339 (16.80%)** |

**说明**: 结果非常说明问题。`NMR w/o RL` 已经能把 joint jump 压下去，但 joint-limit violation 还是很严重；只有把 physics refinement 加回来，输出才真正变成硬件可执行 reference。

### Table 4: Tracking Accuracy

| Method | Short Success ↑ | Short MPJPE ↓ | Short W-MPJPE ↓ | Medium Success ↑ | Medium MPJPE ↓ | Medium W-MPJPE ↓ | Long Success ↑ | Long MPJPE ↓ | Long W-MPJPE ↓ |
|--------|------------------|---------------|------------------|------------------|----------------|------------------|----------------|--------------|----------------|
| PHUMA | 26/33 | 0.058 | 0.660 | **41/46** | 0.042 | 0.444 | 9/13 | 0.0429 | 0.460 |
| GMR | 25/33 | 0.048 | 0.244 | 40/46 | 0.046 | 0.450 | 9/13 | 0.043 | 0.319 |
| **NMR** | **31/33** | **0.040** | **0.237** | **41/46** | **0.035** | **0.308** | **10/13** | **0.040** | **0.291** |

**说明**: NMR 在三种长度段几乎都占优，尤其短序列 W-MPJPE 从 PHUMA 的 0.660m 拉到 0.237m，说明 sequence-level optimization 并不天然更稳，反而可能把短动作扭坏。

## 实验结果

### 数据集与设置

- 测试集来自 [[AMASS]]，共 82 条 motion sequence，约 119K frames，120Hz。
- 动作按复杂度分为：
- `ULOM`: upper-limb-only
- `WBPM`: whole-body primitive
- `WBCM`: whole-body complex
- 动作按长度分为：
- `Short < 250`
- `Medium 250–1000`
- `Long > 1000`
- 网络训练使用 AdamW，初始学习率 `2e-4`，cosine annealing，预训练 500 epochs。
- CEPR 微调阶段学习率降到 `1e-5`，再训练 50 epochs。
- expert policy 基于 [[PPO]] 训练，环境数 `num_envs = 16384`。

### 最重要的实验结论

1. **retargeting 质量显著提升**: NMR 达到 0 joint jump，self-collision 比 GMR 少 54%，joint-limit violation 比 PHUMA 少约一半。
2. **物理精修不可替代**: `NMR w/o RL` 虽然运动学上已经不错，但 joint-limit violation 高达 38.94%，说明 physics grounding 不是可选项。
3. **下游 tracking 更容易学**: cleaner motion reference 让 tracking policy 训练更快、reward 更高、episode 更长。
4. **对上游噪声更鲁棒**: NMR 不会像优化法那样逐帧照单全收，而是会利用时序上下文隐式修正异常 SMPL 帧。

## 批判性思考

### 优点

1. **问题定义够狠也够准**: 直接从非凸优化地狱里跳出来，而不是继续堆技巧救 GMR。
2. **CEPR 很有工程含金量**: 它把 simulation、clustered expert 和 data curation 串成了可扩展监督来源。
3. **对下游真正有帮助**: 不只是在 retargeting 指标上赢，而是实打实提升 [[Whole-Body Controller]] 的训练效率。
4. **时序建模抓到了核心**: full self-attention 对处理异常帧和平滑局部抖动确实有天然优势。

### 局限性

1. **morphology-specific**: 论文自己也承认，CEPR 是平台相关的。换机器人形态，数据管线基本要重跑。
2. **还没直接解决 contact planning**: NMR 生成的是更干净的 reference motion，不是 whole-body interaction policy 本身。
3. **依赖前置管线质量**: 虽然比纯优化法强，但 CEPR 还是要先有初始 retargeting、simulator 和 cluster expert 训练资源。
4. **关注点偏 tracking reference**: 如果任务核心是手部精细接触而不是全身轨迹平滑，收益未必同样显著。

### 潜在改进方向

1. 做 morphology-conditioned retargeting，让同一个模型支持多种 humanoid 平台。
2. 把 environment / contact condition 显式引入，而不是只做无条件 motion sequence mapping。
3. 将 NMR 和 scene-conditioned policy 结合，补上从“动作参考更好”到“interaction 更强”的最后一跳。
4. 尝试把触觉或接触事件 token 接进 retargeting / tracking pipeline，避免对纯 kinematics 过度依赖。

### 可复现性评估

- [x] 代码开源
- [x] 项目主页
- [x] 训练细节基本完整
- [x] 数据集来源可追溯
- [ ] 多平台复现实证

## 关联笔记

### 基于

- [[SMPL]]: NMR 的输入就是 human SMPL motion sequence。
- [[Reinforcement Learning]]: CEPR 核心步骤是用 physics-based RL expert 修正 kinematic reference。

### 对比

- [[ZeroWBC]]: ZeroWBC 更像“scene-conditioned humanoid control”，NMR 更像“给所有 humanoid control 先打干净 reference 地基”。
- [[Whole-Body Controller]]: NMR 不替代控制器，而是显著降低控制器吃脏数据的代价。

### 方法相关

- [[PPO]]: expert tracking policy 的训练算法。
- [[Curriculum Learning]]: 用于逐步收紧 tracking reward 的容忍范围。

### 硬件/数据相关

- [[AMASS]]: 论文主测试集来源。
- [[MoCap]]: 整条技术路线仍然高度依赖高质量人体动作数据。

## 速查卡片

> [!summary] Make Tracking Easy: Neural Motion Retargeting for Humanoid Whole-body Control
> - **核心**: 把 retargeting 从逐帧非凸优化改成对物理可行动作分布的学习。
> - **方法**: `CEPR` 生成 30K physics-preserved 配对数据，`NMR` 用 1D ResNet + Transformer 直接做序列映射。
> - **结果**: 0 joint jump，self-collision 比 GMR 少 54%，joint-limit violation 降到 16.80%，下游 tracking 训练更快。
> - **代码**: https://github.com/3DV-HumanoidGroup/MakeTrackingEasy

*笔记创建时间: 2026-03-25*
