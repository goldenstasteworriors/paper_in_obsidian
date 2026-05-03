---
title: "DexGrasp-Zero: A Morphology-Aligned Policy for Zero-Shot Cross-Embodiment Dexterous Grasping"
method_name: "DexGrasp-Zero"
authors: ["Yuliang Wu", "Yanhan Lin", "WengKit Lao", "Yuhao Lin", "Yi-Lin Wei", "Wei-Shi Zheng", "Ancong Wu"]
year: 2026
venue: arXiv
tags: [cross-embodiment, dexterous-grasping, graph-neural-network, sim-to-real, robot-learning]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2603.16806v2
created: 2026-03-19
---

# DexGrasp-Zero

## 一句话判断

这篇最值钱的地方，不是又喊了一遍 zero-shot，而是它终于把 cross-embodiment dexterous grasping 的核心问题放回“表示和动作空间怎么对齐”本身，而不是继续拿中间 pose + retargeting 这套旧补丁硬撑。

## 论文信息

- 论文: [arXiv](https://arxiv.org/abs/2603.16806v2) | [PDF](https://arxiv.org/pdf/2603.16806v2)
- HTML: [arXiv HTML](https://arxiv.org/html/2603.16806v2)
- 项目主页: [DexGrasp-Zero](https://yliangwu.github.io/DexGrasp-Zero)
- 作者: Yuliang Wu, Yanhan Lin, WengKit Lao, Yuhao Lin, Yi-Lin Wei, Wei-Shi Zheng, Ancong Wu
- 机构: Sun Yat-sen University
- 训练手型: Allegro, Shadow, Ability, Schunk
- 零样本测试手型: LEAP, Inspire
- 真机平台: Kinova + LEAP, Kinova + Inspire, Piper + Revo2
- 数据集: [[YCB]] 45-object benchmark, PartNet / ShapeNet split
- 训练范式: [[PPO]] + sim-to-real [[Privileged Distillation]]

## 一句话总结

> DexGrasp-Zero 用 [[URDF]] 驱动的 morphology-aligned hand graph 和 [[Motion Primitive|手型无关动作原语]] 空间，把不同灵巧手的状态与动作统一到同一语义坐标里，再用 [[MAGCN]] 直接输出可执行物理命令，从而绕开中间 target retargeting 带来的运动学失真。

## 核心贡献

1. **统一状态表示**: 把各手型映射成 anatomy-aligned graph，不再用稀疏 keypoint 或 lossy unified state 硬拼。
2. **统一动作表示**: 用 flexion / abduction / axial rotation 三轴动作原语替代手型相关 joint target。
3. **物理属性注入**: 从 [[URDF]] 提取 joint limit、link length、axis direction、velocity bound 等 priors，逐层注入 GCN。
4. **端到端动作映射**: 直接输出可执行物理命令，不再需要 trainable retargeting module。
5. **真实世界验证**: 在 3 个真实平台、10 个未见物体上做零样本评测，平均成功率 82%。

## 问题背景

### 要解决的问题

作者抓住的是 cross-embodiment dexterous grasping 里最烦的一层:

- 不同灵巧手的关节数、连杆长度、关节极限和驱动约束完全不同。
- 观察空间和动作空间都跟 morphology 强绑定。
- 过去常见做法是先生成中间 motion target，再给每只手单独 retarget。

这套老办法的问题很直接:

- 中间 target 可能在源手型上合理，落到目标手型上就违反 joint limit。
- retargeting 模块本身又是新的误差源。
- 一旦换新手型，通常还得重新调或重新训。

### 现有方法为什么不够

论文把相关路线分成两类:

1. 静态 grasp pose generation:
   这类方法能给出手型相关的抓取姿态，但缺少闭环反馈，抗扰动差。
2. RL-based closed-loop transfer with retargeting:
   这类方法更动态，但动作语义仍然不统一，最后还是要落回 hand-specific retargeting。

作者的判断很清楚: 问题不是“再找一个更好的 retargeting”，而是“别再把动作语义建在 retargeting 上”。

## 方法详解

### 整体架构

DexGrasp-Zero 的输入和输出分成三层:

- **输入状态**: 手-物交互图状态 `X_node^h`、手型图邻接 `A^h`、全局特征 `x_g^h`
- **中间动作**: 手型无关的原语动作 `\alpha_{\text{prim}}^h`
- **最终执行**: 通过 hand-specific 固定映射 `\mathcal{M}_h` 变成真实关节增量 `\Delta q^h`

这条设计线的本质是:

- 状态统一在 morphology-aligned graph
- 动作统一在 motion primitive space
- 执行差异只留给固定物理映射

### 1. Morphology-Aligned State Graph

作者不是按“每个物理关节一个节点”去建图，而是按 anatomy unit 去建:

- tip node
- distal node
- middle node
- proximal node
- metacarpal node
- wrist node

边则沿着真实 kinematic chain 连接。这样做有两个直接好处:

1. 不同手型在语义层上能对齐。
2. 某些手型 DoF 不同，也不会把同一 anatomical unit 强行拆碎。

单节点特征 `x_i^h` 包含:

- 节点到物体表面的距离向量 `d_i^h`
- 节点局部关节角 `\theta_i^h`
- 关节角速度 `\dot{\theta}_i^h`
- contact flag `c_i^h`
- contact force magnitude `f_i^h`
- primitive activation vector `m_i^h`
- node semantic type `n_i^h`

全局特征 `x_g^h` 包含:

- wrist 到目标点的偏移
- wrist 线速度和角速度
- object 线速度和角速度

### 2. Hand-Agnostic Motion Primitive Space

论文把动作统一成三个原语轴:

- **Flexion**
- **Abduction**
- **Axial Rotation**

每个节点预测一组三维 primitive action:

- `\Delta_{\text{flex}}`
- `\Delta_{\text{abd}}`
- `\Delta_{\text{rot}}`

再加 wrist 的 6-DoF 位姿增量，拼成完整动作:

- wrist position delta
- wrist orientation delta
- per-node primitive action

这一步非常关键，因为它把“不同手型的不同 joint command”先提升到同一个 biomechanical 语义空间，再由固定映射 `\mathcal{M}_h` 下沉到具体关节命令。

### 3. [[MAGCN]] 与 Physical Property Injection

模型主干是一个带物理先验逐层注入的图网络。

具体分三块:

1. **Morphology-Aligned Graph Encoder**
   输入 graph state，输出 node embedding 和 global embedding。
2. **Physical Property Encoder**
   从 [[URDF]] 解析 hand-specific physical graph，编码:
   - link length
   - axis direction
   - velocity bound
   - torque / damping related priors
   - joint limit
3. **Layer-wise Physical Injection**
   不是开头一次 early fusion，而是在每层 GCN message passing 时都融合 `E_p^h`。

作者特地做了 ablation，证明一次性 early fusion 很不稳定，seen-hand 平均成功率从 92.0% 直接掉到 50.5%，说明这些物理先验不是“多喂一点信息”就行，而是得在特征传播过程中持续约束。

### 4. Activation Mask 与可执行性约束

并不是每个节点都支持三个 primitive 轴。于是作者构建了 node-level activation mask:

- 哪些节点允许 flexion
- 哪些节点允许 abduction
- 哪些节点允许 rotation

decoder 在输出每个节点动作时，会把 node embedding 和对应 mask 行拼接起来，再预测 primitive action。

奖励里还有一个 feasibility penalty:

- 对 inactive primitive axis 上的输出做平方惩罚

这一步的意义很现实:

- 防止模型在语义上“想象”出某个轴的动作
- 但该手型物理上根本做不出来

### 5. Reward 设计

抓取奖励由两部分组成:

- `r_grasp`: 距离、接触、力、动作正则
- `r_pen`: 不可执行 primitive 轴惩罚

展开后:

- `r_dis`: 惩罚 hand nodes 到 object surface 的距离
- `r_contact`: 奖励接触形成
- `r_force`: 惩罚超阈值接触力
- `r_reg`: 正则 joint increment
- `r_pen`: 惩罚 mask 不允许的 primitive 输出

这套设计不花哨，但很对症:

- 不只追“抓到了”
- 还约束“是不是物理上像回事”

### 6. Sim-to-Real [[Privileged Distillation]]

真机没有 simulation 里的 per-finger contact state 和 contact force，所以作者用了 teacher-student 方案:

- **Teacher**: 在仿真里看 privileged tactile / contact / force
- **Student**: 没有这些量，只看历史视觉和 proprioception
- **Student backbone**: 仍然是 [[MAGCN]]
- **Temporal estimator**: 单层 LSTM, hidden size 256, history length 5

训练流程:

1. 先用 teacher 权重初始化 student
2. 用 MSE 让 student 模仿 teacher action output
3. 再过渡到 RL fine-tuning

这一步解决的是部署时最现实的问题:

- 训练时最有用的接触信息，真机上往往拿不到
- 但你又不想完全放弃 contact-aware 行为

## 关键公式

### 公式 1: [[MAGCN|策略输出与物理执行映射]]

$$
\boldsymbol{\alpha}_{t}^{h}\sim\pi_{\theta}\big(\cdot\mid\mathbf{s}_{t}^{h}\big),\qquad
\boldsymbol{\alpha}_{\text{physical},t}^{h}=\mathcal{M}_{h}\big(\boldsymbol{\alpha}_{t}^{h}\big)
$$

**含义**: 给定手型 `h` 的状态 `\mathbf{s}_t^h`，策略先输出 hand-agnostic action，再通过 hand-specific 映射 `\mathcal{M}_h` 变成物理可执行命令。

**符号说明**:
- `\pi_\theta`: 共享策略网络
- `\mathbf{s}_t^h`: 第 `h` 种手型在时刻 `t` 的 graph state
- `\boldsymbol{\alpha}_{t}^{h}`: 中间动作表示
- `\boldsymbol{\alpha}_{\text{physical},t}^{h}`: 真正执行的物理动作
- `\mathcal{M}_h`: 手型相关但固定的动作映射

### 公式 2: [[Reinforcement Learning|跨手型强化学习目标]]

$$
\max_{\theta}\;
\mathbb{E}_{h\sim\mathcal{H}_{\text{train}}}
\left[
\sum_{t=0}^{T}\gamma^{t}\,
r\!\left(\mathbf{s}_{t}^{h},\,\boldsymbol{\alpha}_{\text{physical},t}^{h}\right)
\right]
$$

**含义**: 在训练手型集合 `\mathcal{H}_{\text{train}}` 上最大化折扣累计回报，目标是学到一个跨手型共享策略。

**符号说明**:
- `\mathcal{H}_{\text{train}}`: 训练用手型集合
- `\gamma`: 折扣因子，文中设为 `0.996`
- `r(\cdot)`: 抓取与可执行性联合奖励

### 公式 3: [[Motion Primitive|统一动作原语空间]]

$$
\boldsymbol{\alpha}_{\text{prim}}^{h}
=
\big[
\Delta{\mathbf{p}_{w}^{h}}^{\top},
\Delta{\boldsymbol{\theta}_{w}^{h}}^{\top},
{\boldsymbol{\alpha}_{1}^{h}}^{\top},
\dots,
{\boldsymbol{\alpha}_{N_h}^{h}}^{\top}
\big]^{\top}
\in
\mathbb{R}^{6+3N_h}
$$

**含义**: 完整动作由 wrist 的 6-DoF 增量和每个 graph node 的 3 维 primitive action 拼接而成。

**符号说明**:
- `\Delta\mathbf{p}_{w}^{h}`: wrist 位置增量
- `\Delta\boldsymbol{\theta}_{w}^{h}`: wrist 姿态增量
- `\boldsymbol{\alpha}_{i}^{h}`: 第 `i` 个节点的三轴 primitive action
- `N_h`: 手型 `h` 的 graph node 数量

### 公式 4: [[URDF|原语到关节的手型映射]]

$$
\Delta \mathbf{q}^{h}=\mathcal{M}_{h}\big(\boldsymbol{\alpha}_{\text{prim}}^{h}\big),\qquad
\Delta q_{j}^{h}=s_{j}^{h}\cdot\alpha_{n_j,(p_j)}^{h}
$$

**含义**: hand-agnostic primitive action 通过固定的 hand-specific mapping 变成各关节的物理增量命令。

**符号说明**:
- `\Delta\mathbf{q}^{h}`: 手型 `h` 的 joint increment
- `s_j^h`: 第 `j` 个关节的方向 / 符号因子
- `\alpha_{n_j,(p_j)}^h`: 与关节 `j` 对应的 primitive 分量

### 公式 5: [[Motion Primitive|动作可执行轴掩码]]

$$
\mathbf{M}_{\text{activation}}^{h}
=
\big[
\mathbf{m}_{1}^{h},
\dots,
\mathbf{m}_{N_h}^{h}
\big]^{\top}
\in
\{0,1\}^{N_h\times 3}
$$

**含义**: 对每个节点标记哪些 primitive axis 可执行，用于 decoder conditioning 和 reward penalty。

**符号说明**:
- `\mathbf{m}_i^h`: 第 `i` 个节点的三维可执行性指示向量
- `N_h`: 手型 `h` 的节点数

### 公式 6: [[Motion Primitive|抓取奖励与可执行性惩罚]]

$$
r = r_{\text{grasp}} + r_{\text{pen}}
$$

其中

$$
r_{\text{grasp}}
=
w_{\text{dis}}r_{\text{dis}}
+
w_{\text{contact}}r_{\text{contact}}
+
w_{\text{force}}r_{\text{force}}
+
w_{\text{reg}}r_{\text{reg}}
$$

以及

$$
r_{\text{pen}}
=
-w_{\text{pen}}
\sum_{i=1}^{N_h}
\left\|
\big(1-\mathbf{m}_{i}^{h}\big)\odot\boldsymbol{\alpha}_{i}^{h}
\right\|_2^2
$$

**含义**: 在鼓励接触和抓取稳定性的同时，显式惩罚落在不可执行 primitive axis 上的动作输出。

**符号说明**:
- `r_{\text{dis}}`: 距离项
- `r_{\text{contact}}`: 接触项
- `r_{\text{force}}`: 接触力惩罚
- `r_{\text{reg}}`: 动作正则
- `r_{\text{pen}}`: 不可执行动作惩罚

## 关键图表

### Figure 2: Universal Hand Representation / 统一手型表示

![Figure 2](https://arxiv.org/html/2603.16806v2/x1.png)

**说明**: 这张图最重要的是把不同灵巧手统一成 anatomy-aligned graph，同时定义了 flexion / abduction / axial rotation 三类 primitive。它解释了这篇论文为什么能跨手型共享策略，而不是每只手再单独补 retargeting。

### Figure 3: Architecture of DexGrasp-Zero / 模型总览

![Figure 3](https://arxiv.org/html/2603.16806v2/x2.png)

**说明**: 整体结构分成三部分:

- graph encoder 编码 hand-object state
- physical property encoder 编码 [[URDF]] priors
- decoder 输出 wrist command 和 node-level primitive action

其中真正关键的是 layer-wise physical injection，不是简单 early fusion。

### Figure 4: Hardware Setup / 真机硬件平台

![Figure 4](https://arxiv.org/html/2603.16806v2/x3.png)

**说明**: 作者在 3 套平台上验证了 zero-shot transfer:

- Kinova + LEAP
- Kinova + Inspire
- Piper + Revo2

这说明它不是只在“换一个仿真 URDF 文件”上做 transfer，而是真的跨到不同硬件组合。

### Figure 5: Simulated Grasps on Training Hands / 训练手型抓取可视化

![Figure 5](https://arxiv.org/html/2603.16806v2/x4.png)

**说明**: 这张图对应作者的核心 claim: 单一策略可以在多种 seen hands 上形成稳定抓取，而不是某只手专用策略。

### Figure 9: Real-World Evaluation Props / 真机评测物体

![Figure 9](https://arxiv.org/html/2603.16806v2/figs/obj_selected.png)

**说明**: 真机评测物体一共 10 个，包括酒杯、饮料瓶、喷壶、酱料瓶、玩具狗、咖啡杯、塑料锤、网球、魔方、橙子。这个集合覆盖了不同尺寸、刚性和形状，不只是几个最容易抓的规则体。

### Figure 10: Training Curves / 仿真训练曲线

![Figure 10](https://arxiv.org/html/2603.16806v2/figs/training_curve.png)

**说明**: 作者用这张图说明训练在不同随机种子下比较稳定。对 RL-based cross-embodiment policy 来说，这点很重要，不然所谓 transfer 很可能只是碰巧。

### Figure 11: Failure Cases / 失败案例

![Figure 11](https://arxiv.org/html/2603.16806v2/x8.png)

**说明**: 失败主要集中在:

- 小物体上的空抓
- Revo2 这种低 DoF 手型的拇指对掌能力不足
- 更大物体超过手部包覆范围

作者没有把失败都推给 perception，而是明确指出 lack of tactile feedback 和 embodiment-specific dexterity 是主要瓶颈。

### Figure 12: Barrett Hand Generalization / 非拟人手泛化

![Figure 12](https://arxiv.org/html/2603.16806v2/x9.png)

**说明**: 把训练在四种 anthropomorphic hands 上的 full model 直接 zero-shot 到 Barrett Hand，成功率还有 0.70。这不能说明问题彻底解决了，但至少说明这套 graph + primitive interface 不只适用于类人手。

## 实验结果

### Table 1: Cross-Embodiment Training and Zero-Shot Transfer

| Method | Variant | Allegro | Shadow | Ability | Schunk | LEAP | Inspire | Seen Avg | Unseen Avg |
|--------|---------|---------|--------|---------|--------|------|---------|----------|------------|
| CrossDex | per-object | 0.81 | 0.85 | 0.90 | 0.90 | 0.34 | 0.44 | 0.865 | 0.39 |
| CrossDex | multi-object | 0.39 | 0.69 | 0.42 | 0.60 | 0.19 | 0.34 | 0.525 | 0.265 |
| DexGrasp-Zero | w/o motion primitives | 0.52 | 0.51 | 0.64 | 0.59 | 0.39 | 0.29 | 0.565 | 0.34 |
| DexGrasp-Zero | early fusion | 0.42 | 0.47 | 0.59 | 0.54 | 0.46 | 0.34 | 0.505 | 0.40 |
| DexGrasp-Zero | w/o Gphysical priors | 0.91 | 0.89 | 0.90 | 0.84 | 0.82 | 0.79 | 0.885 | 0.805 |
| DexGrasp-Zero | w/o Mactivation & rpen | 0.92 | 0.91 | 0.90 | 0.81 | 0.50 | 0.76 | 0.885 | 0.63 |
| DexGrasp-Zero | full model | 0.92 | 0.95 | 0.90 | 0.91 | 0.93 | 0.82 | 0.92 | 0.85 |

**表格说明**: 这张表已经把故事说完了。full model 在 unseen hands 上 0.85，显著高于 CrossDex 的 0.39。去掉 motion primitive 直接崩到 0.34，说明统一动作语义不是装饰。

### Table 2: Single-Hand Training Transfer on PartNet

| Train Hand | Allegro | Shadow | Ability | Schunk | LEAP | Inspire |
|-----------|---------|--------|---------|--------|------|---------|
| GraspXL | 0.94 | 0.93 | 0.91 | 0.90 | 0.95 | 0.91 |
| Allegro | 0.93† | 0.83 | 0.80 | 0.69 | 0.48 | 0.77 |
| Shadow | 0.55 | 0.98† | 0.80 | 0.82 | 0.77 | 0.94 |
| Ability | 0.60 | 0.60 | 0.86† | 0.86 | 0.88 | 0.90 |
| Schunk | 0.61 | 0.52 | 0.83 | 0.92† | 0.90 | 0.94 |
| LEAP | 0.50 | 0.68 | 0.65 | 0.69 | 0.90† | 0.69 |
| Inspire | 0.61 | 0.83 | 0.87 | 0.88 | 0.88 | 0.96† |

**表格说明**: 就算只在单一手型上训练，DexGrasp-Zero 依然有不差的 cross-hand transfer。尤其 Shadow / Schunk 训练后到 Inspire 还能到 0.94，说明这套表征确实学到了跨手型共享结构。

### Table 3: Real-World Zero-Shot Grasping on Unseen Hands

| Method | LEAP | Inspire | Revo2 | Average |
|--------|------|---------|-------|---------|
| Intra-hand (Oracle) | 0.90 | 0.90 | 0.78 | 0.86 |
| Cross-hand w/o Gphysical | 0.84 | 0.80 | 0.62 | 0.75 |
| Cross-hand (Ours) | 0.88 | 0.86 | 0.72 | 0.82 |

**表格说明**: 这张表说明作者不是只在仿真里自嗨。cross-hand policy 与 oracle 的差距不算离谱，但在 Revo2 这种更难的手型上仍明显掉点，说明 morphology gap 没有被“彻底解决”。

### Table 4: Training and Architecture Hyperparameters

| Parameter | Value |
|-----------|-------|
| RL algorithm | PPO |
| Discount factor `\gamma` | 0.996 |
| GAE `\lambda` | 0.95 |
| PPO clip `\epsilon` | 0.2 |
| Optimizer | Adam |
| Learning rate | `5 × 10^{-4}` (adaptive KL schedule) |
| Max gradient norm | 0.5 |
| PPO epochs / update | 4 |
| Simulator frequency | 400 Hz physics / 20 Hz control |
| Episode length | 120 + 30 lift steps |
| Reward weights | `w_dis=0.3, w_contact=1.0, w_force=0.5, w_reg=1.5, w_pen=0.3` |

**表格说明**: 训练配置本身不奇怪，真正重要的不是 PPO 调了多神，而是动作空间和物理约束设计得对。

### Table 5: Per-Object Real-World Results

| Object | LEAP | Inspire | Revo2 |
|--------|------|---------|-------|
| wine-glass | 5/5 | 5/5 | 4/5 |
| beverage bottle | 4/5 | 3/5 | 4/5 |
| spray bottle | 4/5 | 4/5 | 4/5 |
| squeeze sauce bottle | 4/5 | 5/5 | 4/5 |
| toy dog | 5/5 | 5/5 | 2/5 |
| coffee mug | 5/5 | 5/5 | 4/5 |
| plastic toy hammer | 4/5 | 5/5 | 2/5 |
| tennis ball | 4/5 | 3/5 | 5/5 |
| Rubik's cube | 5/5 | 4/5 | 3/5 |
| orange | 4/5 | 4/5 | 4/5 |
| Average | 0.88 | 0.86 | 0.72 |

**表格说明**: Revo2 明显更吃亏，问题不只是 policy 本身，而是小尺寸手和较弱拇指对掌能力造成的 enclosure 上限。

### Table 6: URDF Prior Sensitivity

| Link-Length Scale | Success Rate |
|------------------|--------------|
| 1 | 0.92 |
| 2 | 0.85 |
| 1/4 | 0.87 |

**表格说明**: 只改 [[URDF]] 派生特征、不改真实仿真几何和策略参数，性能就会掉，说明 physical prior 不是摆设，模型真的在用这些编码。

### Table 7: Backbone Comparison

| Backbone | Train-hand SR (%) | Unseen-hand SR (%) |
|----------|-------------------|--------------------|
| GCN (ours) | 91.3 / 92.1 / 92.5 (91.9 ± 0.6) | 86.1 / 84.9 / 85.5 (85.5 ± 0.6) |
| Graph-Transformer | 86.4 / 87.2 / 86.9 (86.8 ± 0.4) | 81.5 / 80.4 / 79.8 (80.6 ± 0.9) |

**表格说明**: 图 transformer 没赢。对这个任务来说，local message passing 的 kinematic inductive bias 反而更稳。

### 额外结果与部署细节

- 仿真控制频率: 20 Hz policy, 400 Hz physics
- 真机推理: 单张 RTX 3090, 20 Hz
- grasp 执行: 130 steps 后 scripted lift
- student distillation: 单层 LSTM, hidden size 256, history length 5
- 非拟人 Barrett Hand zero-shot 成功率: 0.70

## 批判性思考

### 优点

1. **问题抓得准**: 它正面解决的是 state / action alignment，而不是继续在 retargeting 外面贴胶带。
2. **结构设计自洽**: graph state、motion primitive、URDF prior、activation mask 是一整套连贯设计，不是东拼西凑。
3. **ablation 很有说服力**: motion primitive、physical prior、layer-wise injection、activation mask 全都能用数据证明价值。
4. **真机结果够硬**: 三个平台、十个对象，不是随便录个 demo 就算完。

### 局限性

1. **任务还是 grasp，不是 manipulation**: 抓住和能完成长程操作不是一回事。
2. **tactile 缺失仍是瓶颈**: 失败案例已经说明小物体和不稳定包覆时，缺触觉就容易空抓。
3. **输出动作仍偏 hand-centric**: 还没触到 arm-hand-body 一体化控制。
4. **新手型泛化仍受 morphology 相似性影响**: single-hand transfer 的稳定性明显依赖 source / target hand 的形态接近程度。

### 潜在改进方向

1. 把 graph 对齐从 hand 扩到 arm-hand-body，多做 whole-body contact task。
2. 引入显式 tactile / force sensing，而不是只靠 temporal estimation 猜接触。
3. 从 grasp 扩到 grasp-to-manipulate，验证动作原语空间能否承载更长时序技能。
4. 研究更一般的 non-anthropomorphic end-effector transfer，而不只 Barrett 一种。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [x] 训练细节较完整
- [x] benchmark 和评测协议较明确

## 关联笔记

### 基于

- [[CrossDex]]: 两者都做 cross-embodiment dexterous grasping，但 DexGrasp-Zero 去掉了中间 retargeting target。
- [[GraspXL]]: 单手训练 benchmark 主要拿它作参照，用来证明 zero-shot transfer 不是自说自话。

### 方法相关

- [[MAGCN]]: 本文的核心 backbone。
- [[Motion Primitive]]: 统一动作语义空间的关键。
- [[URDF]]: 提供 hand-specific physical prior。
- [[Privileged Distillation]]: 解决 sim-to-real 时 privileged contact 信号不可用的问题。

### 数据相关

- [[YCB]]: cross-embodiment 主 benchmark。

## 速查卡片

> [!summary] DexGrasp-Zero
> - **核心**: 用 morphology-aligned graph + motion primitive 统一不同灵巧手的状态和动作语义
> - **方法**: [[MAGCN]] + layer-wise [[URDF]] prior injection + activation mask + [[Privileged Distillation]]
> - **结果**: unseen hands 仿真 85%，三套真机平台平均 82%
> - **意义**: 这是把 cross-embodiment 问题从“怎么 retarget”往“怎么统一表示”真正推进了一步

## 我的结论

如果你关心的是 cross-embodiment dexterous manipulation，这篇是必须跟的，因为它不是在旧管线旁边做 cosmetic improvement，而是在改动作语义接口本身。它还远不是终点，但它至少把问题放对了地方。
