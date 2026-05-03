---
title: "BiPreManip: Learning Affordance-Based Bimanual Preparatory Manipulation through Anticipatory Collaboration"
method_name: "BiPreManip"
authors: ["Yan Shen", "Feng Jiang", "Zichen He", "Xiaoqi Li", "Yuchen Liu", "Zhiyu Li", "Ruihai Wu", "Hao Dong"]
year: 2026
venue: arXiv
tags: [bimanual-manipulation, affordance-learning, robot-learning, point-cloud, real-world-evaluation]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2603.21679v1
created: 2026-03-24
---

# 论文笔记：BiPreManip: Learning Affordance-Based Bimanual Preparatory Manipulation through Anticipatory Collaboration

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Peking University, CFCS |
| 日期 | March 2026 |
| 项目主页 | https://sites.google.com/view/bipremanip |
| 对比基线 | [[ACT]] |
| 链接 | [arXiv](https://arxiv.org/abs/2603.21679) / [Project](https://sites.google.com/view/bipremanip) |

---

## 一句话总结

> BiPreManip 用 anticipatory affordance 把“先给另一只手创造条件，再执行目标动作”的双臂协作过程显式建模成了一个点云加语言驱动的四阶段框架。

---

## 核心贡献

1. **定义了 preparatory manipulation 问题**: 不再把双臂任务看成两只手同时去抓，而是明确建模“辅助臂先改变物体可操作性，主执行臂再完成目标动作”。
2. **提出四阶段协作框架**: 先预测主臂目标可供性，再预测辅臂 preparatory affordance，接着估计目标物体位姿并执行重定位，最后回到主臂做目标操作。
3. **给出仿真和真实世界验证**: 在 882 个仿真对象实例和 ARX-X7s 双臂平台上证明该框架对 edge-pushing、articulated manipulation 和 handover 都有提升。

---

## 问题背景

### 要解决的问题

很多物体不是“直接抓起来”就完了。比如平放在桌面的 iPad 需要先推到桌边，躺着的笔要先抬起或转向，带盖瓶子需要一只手先稳住或调整姿态，另一只手才能做真正的 goal-directed 操作。BiPreManip 关注的就是这种双臂协作中的 preparatory stage。

### 现有方法的局限

- 单步 grasp 或单臂 manipulation policy 往往默认目标区域一开始就可接近，这在真实任务里经常不成立。
- 传统双臂模仿学习通常只学最后的动作轨迹，没有把“为什么先这样摆物体”建成中间表示。
- 只靠视觉终态 supervision 的方法很难学会 anticipatory reasoning，也不容易泛化到 unseen object shape。

### 本文的动机

作者的核心判断很直接: 如果模型先知道主执行臂最终应该接触哪里、从什么方向下手，那么辅助臂的动作就不再是盲目的“先抓一下试试”，而会变成围绕目标 affordance 的 purposeful preparation。这正是 [[Affordance]] 表征在双臂任务里的价值。

---

## 方法详解

### 模型架构

BiPreManip 采用 **点云几何 + 语言条件 + 分阶段协作推理** 的架构：

- **输入**: 语言指令 $l$ 与物体点云 $O \in \mathbb{R}^{N \times 3}$
- **Backbone**: [[PointNet++]] 负责点云的 per-point / global feature，[[CLIP]] 负责文本编码
- **核心模块**: Goal Affordance Network、Pre-Affordance Network、Object Pose Predictor、Reorient Actor
- **输出**: 主臂目标动作 $a_{\text{goal}}$、辅臂 preparatory 动作 $a_{\text{pre}}$、以及中间目标物体位姿 $T^{\text{obj}} \in [[SE(3)]]$

整体流程可以概括为四步：

1. 预测主臂在任务完成阶段最应该接触的点和姿态。
2. 基于这个 anticipatory goal，为辅助臂预测 preparatory contact 和 orientation。
3. 估计物体应该被重定向到什么位姿，保证主臂有 collision-free access。
4. 在更新后的场景上重新执行主臂 affordance 预测并输出最终 goal action。

### 核心模块

#### 模块1: Goal Affordance Network

**设计动机**: 先显式回答“主执行臂最终应该怎么碰这个物体”，再让 preparatory stage 变得有目标。

**具体实现**:
- 用 [[PointNet++]] 对输入点云 $O$ 编码，得到每个点的几何特征 $f_p$。
- 用 [[CLIP]] 文本编码器把语言指令 $l$ 映射成文本特征 $f_l$。
- 通过 MLP 预测 per-point affordance score $s$，形成 dense affordance map。
- 在高分点 $p_{\text{goal}}$ 上，再用 [[cVAE]] 预测主臂 gripper orientation $d_{\text{goal}}$，得到 $a_{\text{goal}}=(p_{\text{goal}}, d_{\text{goal}})$。

#### 模块2: Pre-Affordance Network

**设计动机**: 辅助臂不是瞎动，而是围绕主臂未来 interaction 目标来做 preparatory action。

**具体实现**:
- 额外输入目标接触点和目标姿态特征 $(f_{p_{\text{goal}}}, f_{d_{\text{goal}}})$。
- 把几何、语言和 anticipatory goal feature 拼接后过 MLP，预测 preparatory affordance map。
- 在候选 preparatory 点上，再通过 [[cVAE]] 预测辅助臂 orientation $d_{\text{pre}}$。
- 最终得到 preparatory 动作 $a_{\text{pre}}=(p_{\text{pre}}, d_{\text{pre}})$。

#### 模块3: Anticipatory Object Pose Predictor + Reorient Actor

**设计动机**: 只知道“在哪抓”还不够，很多任务真正关键的是把物体变成更容易被主臂处理的姿态。

**具体实现**:
- Pose Predictor 输入主臂目标动作特征、辅助臂 preparatory 动作特征和全局物体特征 $f_O$。
- 它输出一个期望的物体刚体变换 $T^{\text{obj}}=(t^{\text{obj}}, r^{\text{obj}})$。
- 这个变换作用在点云上，得到新的物体配置 $O'$。
- Reorient Actor 进一步根据抓取后的场景和 $O'$ 预测辅助臂如何真正把物体转到目标配置。

#### 模块4: Re-invoking Goal Affordance

**设计动机**: preparatory action 成功后，主臂可接近区域已经改变，所以需要在新场景上重新做 goal affordance，而不是拿旧 prediction 硬上。

**具体实现**:
- 在更新后的点云或场景状态上重新调用 Goal Affordance Network。
- 生成更精确的最终 contact point 和 orientation。
- 让主臂在经过 preparatory stage 后执行真正的目标动作。

---

## 关键公式

### 公式1: [[SE(3)|物体重定位变换]]

$$
O^{\prime}=T^{\text{obj}}\cdot O
$$

**含义**: 把预测得到的目标物体位姿直接作用到原始点云上，形成 anticipatory stage 之后的理想配置。

**符号说明**:
- $O$: 原始物体点云
- $T^{\text{obj}}$: 预测的物体刚体变换
- $O'$: 重定位后的物体点云

### 公式2: [[Affordance|可供性分数损失]]

$$
\mathcal{L}_{\mathrm{aff}}=\|s_{\text{pred}}-s_{\text{gt}}\|_{1}
$$

**含义**: 监督模型学习每个点的 affordance score，让高分区域对准真实的接触有效区域。

**符号说明**:
- $s_{\text{pred}}$: 模型预测的 per-point affordance score
- $s_{\text{gt}}$: 来自示教或标注生成的 ground-truth affordance score
- $\|\cdot\|_1$: 逐点绝对误差

### 公式3: [[Geodesic Loss|姿态测地损失]]

$$
\mathcal{L}_{\mathrm{ori}}(d,d^{*})=
\arccos\!\left(\frac{\operatorname{Tr}\!\left(d^{\top}d^{*}\right)-1}{2}\right)
$$

**含义**: 用旋转流形上的 geodesic distance 来监督 gripper orientation，避免欧氏空间里直接回归旋转带来的伪距离。

**符号说明**:
- $d$: 预测的 gripper orientation
- $d^*$: 真值 orientation
- $\operatorname{Tr}(\cdot)$: 矩阵迹运算

### 公式4: [[KL Divergence|潜变量正则项]]

$$
\mathcal{L}_{\mathrm{KL}}=
D_{\mathrm{KL}}\!\left(q_{\phi}(z\mid d^{*},c)\,\|\,\mathcal{N}(0,1)\right)
$$

**含义**: 约束 [[cVAE]] 的潜变量分布，让 orientation sampling 在训练和推理时都保持可控。

**符号说明**:
- $q_{\phi}(z \mid d^*, c)$: 编码器给出的后验分布
- $c$: 条件上下文，来自几何和语言特征
- $\mathcal{N}(0,1)$: 标准高斯先验

### 公式5: [[SE(3)|anticipatory gripper orientation 变换]]

$$
R_{\text{grp,ant}}=
R_{\text{obj,init}}\cdot
R_{\text{obj,fin}}^{\top}\cdot
R_{\text{grp,fin}}
$$

**含义**: 利用物体初态和终态的旋转关系，把 final-stage gripper orientation 回推成 anticipatory stage 应该采用的姿态。

**符号说明**:
- $R_{\text{obj,init}}$: 物体初始旋转
- $R_{\text{obj,fin}}$: 物体目标终态旋转
- $R_{\text{grp,fin}}$: 最终目标动作对应的 gripper rotation
- $R_{\text{grp,ant}}$: anticipatory stage 的 gripper rotation

### 公式6: [[SE(3)|位姿预测器总损失]]

$$
\mathcal{L}_{\mathrm{M}}=
\mathcal{L}_{\mathrm{ori}}(r,r^{*})+
\mathcal{L}_{1}(t,t^{*})+
\mathcal{D}_{\mathrm{KL}}
$$

**含义**: 同时监督物体变换中的旋转、平移和潜变量分布，让 Pose Predictor 和 Reorient Actor 学到稳定的目标位姿分布。

**符号说明**:
- $r, r^*$: 预测与真值旋转
- $t, t^*$: 预测与真值平移
- $\mathcal{D}_{\mathrm{KL}}$: 潜变量正则

### 公式7: [[SE(3)|重定位后的抓手位姿]]

$$
T_{\text{grp}}^{\text{reorient}}=
T_{\text{obj}}^{\text{reorient}}
\left(T_{\text{obj}}^{\text{grasped}}\right)^{-1}
T_{\text{grp}}^{\text{grasped}}
$$

**含义**: 在保持抓取相对关系的前提下，把辅助臂当前抓手位姿映射到重定位后的目标抓手位姿。

**符号说明**:
- $T_{\text{obj}}^{\text{grasped}}$: 物体被抓住时的位姿
- $T_{\text{grp}}^{\text{grasped}}$: 抓手被抓住时的位姿
- $T_{\text{obj}}^{\text{reorient}}$: 期望的物体重定位目标位姿
- $T_{\text{grp}}^{\text{reorient}}$: 重定位时抓手应达到的位姿

---

## 关键图表

### Figure 2: Overview / 系统概览

![Figure 2](https://arxiv.org/html/2603.21679v1/x1.png)

**说明**: 这张图把 preparatory manipulation 的核心逻辑讲得很清楚。上面一行是主臂未来真正想完成的目标动作，下面一行是辅助臂先如何通过推、抬、转等动作创造可操作条件。论文的价值就在于把这个“先服务，再执行”的结构显式做成模型。

### Figure 3: BiPreManip Pipeline / 模型流水线

![Figure 3](https://arxiv.org/html/2603.21679v1/x2.png)

**说明**: 流水线依次经过 Goal Affordance、Pre-Affordance、Object Pose Predictor、Reorient Actor 和 re-invoked Goal Affordance。它说明作者不是直接从观测到双臂动作，而是把中间的 anticipatory object state 单独抽了出来。

### Figure 4: Simulation Experiments / 仿真实验可视化

![Figure 4](https://arxiv.org/html/2603.21679v1/x3.png)

**说明**: 第二列显示预测的 affordance maps。上半部分是主臂 anticipatory affordance，下半部分是辅助臂 preparatory affordance。这个可视化很重要，因为它证明模型不是黑箱地输出姿态，而是真的学到了不同阶段该碰哪里。

### Figure 5: Real-world Results / 真实世界结果

![Figure 5](https://arxiv.org/html/2603.21679v1/x4.png)

**说明**: 真实世界实验覆盖不同对象和任务类型。相比很多只给成功帧的论文，这里至少能看到 preparatory action 和 final action 的配合关系确实落在了实体硬件上。

---

## 实验

### 数据集

作者把任务拆成三类：

- **Edge-Pushing Tasks**: 如 bowl、cap、keyboard、window 等，要求先改变物体边缘可接近性。
- **Articulated Manipulation Tasks**: 如 bottle、dispenser、pen-cap、pliers、USB 等，要求先调整姿态再执行功能动作。
- **Plate-Lifting Tasks**: 用于考察单类但强 preparatory 依赖的任务。

数据规模来自 Table 4：

| 任务类型 | Train | Unseen | Total |
|------|------|------|------|
| Edge-Pushing | 457 | 147 | 604 |
| Articulated Manipulation | 194 | 61 | 255 |
| Plate-Lifting | 17 | 5 | 22 |
| Overall | 668 | 213 | 882 |

任务对象主要来自 [[PartNet]] 和 [[ShapeNet]] 风格的可操作对象实例，训练与 unseen 测试对象按 3:1 切分。

### 实现细节

- **视觉输入**: 物体 3D 点云，而不是 RGB-only observation
- **几何编码**: [[PointNet++]]
- **文本编码**: [[CLIP]]
- **动作建模**: 两个阶段的 orientation 都通过 [[cVAE]] 采样
- **真实硬件**: ARX-X7s dual-arm platform
- **深度相机**: Intel RealSense L515
- **评测设置**: 同时报告训练对象与 unseen 对象上的 success rate，并附加真实世界 10 次试验统计

### 评价设置

论文对比了五种 baseline：

- `W2A`
- `ACT`
- `3DA`
- `3DFA`
- `Heuristic`

这些 baseline 覆盖了从示教模仿到 3D affordance 估计再到启发式方法的多种路线，能比较清楚地看出 BiPreManip 是否真的从 anticipatory stage 获益。

---

## 实验结果

### Table 1a: Simulation Results on Edge-Pushing Tasks

| Method | Bowl | Cap | Keyboard | Laptop | Phone | Remote | Scissors | Switch | Window |
|------|------|------|------|------|------|------|------|------|------|
| W2A | 0 / 0 | 2 / 4 | 0 / 0 | 5 / 10 | 2 / 0 | 0 / 0 | 5 / 5 | 0 / 0 | 0 / 0 |
| ACT | 32 / 27 | 22 / 36 | 2 / 1 | 7 / 3 | 0 / 0 | 1 / 0 | 0 / 0 | 1 / 1 | 1 / 1 |
| 3DA | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 2 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 0 |
| 3DFA | 3 / 0 | 5 / 14 | 1 / 3 | 0 / 2 | 1 / 0 | 0 / 0 | 0 / 3 | 0 / 1 | 8 / 9 |
| Heuristic | 15 / 21 | 31 / 37 | 58 / 62 | 35 / 33 | 30 / 21 | 20 / 23 | 15 / 30 | 20 / 23 | 56 / 56 |
| **Ours** | **49 / 52** | **71 / 74** | **64 / 64** | **62 / 67** | **66 / 42** | **31 / 24** | **34 / 49** | **61 / 72** | **87 / 87** |

**表格说明**: Edge-pushing 这组结果说明 BiPreManip 不是只会 articulated task。对 bowl、cap、switch、window 这类需要先创造 graspable geometry 的任务，提升非常明显，尤其 unseen object 上没有明显崩掉。

### Table 1b: Simulation Results on Articulated / Plate Tasks

| Method | Bottle | Dispenser | Lighter | Pen-Button | Pen-Cap | Pliers | Stapler | USB | Plate |
|------|------|------|------|------|------|------|------|------|------|
| W2A | 1 / 2 | 0 / 1 | 2 / 0 | 0 / 0 | 1 / 0 | 9 / 8 | 16 / 16 | 5 / 3 | 4 / 4 |
| ACT | 2 / 0 | 54 / 43 | 34 / 30 | 15 / 9 | 0 / 0 | 24 / 8 | 38 / 23 | 1 / 1 | 30 / 26 |
| 3DA | 0 / 0 | 20 / 2 | 20 / 3 | 1 / 1 | 0 / 0 | 1 / 7 | 6 / 3 | 0 / 1 | 27 / 25 |
| 3DFA | 4 / 2 | 57 / 41 | 41 / 36 | 14 / 25 | 1 / 0 | 2 / 5 | 8 / 1 | 12 / 0 | 71 / 68 |
| Heuristic | 19 / 14 | 31 / 47 | 21 / 32 | 27 / 34 | 22 / 15 | 6 / 10 | 19 / 21 | 12 / 10 | 81 / 78 |
| **Ours** | **30 / 26** | **45 / 56** | **43 / 58** | **67 / 72** | **26 / 32** | **25 / 29** | **38 / 30** | **13 / 14** | **85 / 82** |

**表格说明**: 在 articulated tasks 上，最夸张的是 pen-button、lighter 和 dispenser。也就是说，一旦任务真的需要先调整对象姿态，再去碰功能区域，BiPreManip 的 anticipatory stage 就开始体现出价值。

### Table 2: Ablation on Articulated Manipulation

| Method | Bottle | Dispenser | Lighter | Pen-Button | Pen-Cap | Pliers | Stapler | USB |
|------|------|------|------|------|------|------|------|------|
| w/o Ant-Aff | 27 / 13 | 39 / 48 | 39 / 48 | 48 / 58 | 23 / 10 | 8 / 12 | 21 / 23 | 3 / 3 |
| w/o ObjPosePred | 24 / 15 | 38 / 45 | 31 / 52 | 51 / 50 | 21 / 8 | 20 / 31 | 14 / 14 | 10 / 6 |
| **Ours** | **30 / 26** | **45 / 56** | **43 / 58** | **67 / 72** | **26 / 32** | **25 / 29** | **38 / 30** | **13 / 14** |

**关键发现**:
- 去掉 anticipatory affordance 后，大多数任务都有明显掉点，尤其 pen-cap、USB 这类很依赖“先摆对再下手”的任务。
- 去掉 Object Pose Predictor 后，模型还能做一些简单 preparatory motion，但涉及姿态重定向的任务下降更明显。

### Table 3: Real-world Success Rate

| Method | Book | Hat | Bottle | Dispenser | Bowl | Handover Bottle |
|------|------|------|------|------|------|------|
| W2A | 0/10 | 1/10 | 0/10 | 1/10 | 0/10 | 0/10 |
| 3DFA | 1/10 | 0/10 | 0/10 | 2/10 | 0/10 | 2/10 |
| **Ours** | **7/10** | **8/10** | **6/10** | **8/10** | **5/10** | **6/10** |

**表格说明**: 真实世界不是全满分，但这恰好说明论文没装神。能在 book、hat、dispenser 这类任务做到 7 到 8 次成功，已经证明 preparatory reasoning 不只是仿真里会画 heatmap。

### Table 4: Dataset Statistics

| Task Type | Category Example | Train | Unseen | Total |
|------|------|------|------|------|
| Edge-Pushing | Bowl / Keyboard / Window | 457 | 147 | 604 |
| Articulated Manipulation | Bottle / Pen / USB | 194 | 61 | 255 |
| Plate-Lifting | Plate | 17 | 5 | 22 |
| **Overall** | All Tasks | **668** | **213** | **882** |

**表格说明**: 这个数据量不算 foundation model 级别，但作为双臂长时序 preparatory task 已经够说明问题，而且作者专门区分了 seen / unseen object split。

### 结果解读

1. **BiPreManip 的强项在“先把世界变对”**: 一旦任务需要先抬、转、推，显式 preparatory reasoning 就比直接学终态动作更靠谱。
2. **泛化没有完全塌**: 多数 unseen object 的 success rate 没有比 seen object 差一大截，说明 anticipatory affordance 不是纯记忆。
3. **真实世界成功率说明方法是可落地的**: 虽然没有到工业级稳定性，但已经过了“只会在仿真里赢 baseline”的门槛。

---

## 批判性思考

### 优点

1. 把双臂 preparatory stage 明确建模，这是这篇最重要的 conceptual contribution。
2. 中间表示足够可解释，affordance map、object pose 和 reorient actor 都能被逐步检查。
3. 同时给了仿真、消融和真实世界结果，论证链路比较完整。

### 局限性

1. 任务仍然是 object-centric 的双臂 manipulation，离 whole-body humanoid coordination 还有距离。
2. 点云和对象几何质量对框架很重要，真实场景中的遮挡、噪声和部分观测可能会放大误差。
3. 真实世界成功率虽可观，但远没到稳定 deployment 水平，尤其 bowl 和 handover bottle 这类任务还有明显失败空间。

### 潜在改进方向

1. 把 preparatory reasoning 从双臂扩展到 whole-body skill sequencing，例如 torso / base / arm 的协同。
2. 将 anticipatory affordance 和触觉、力觉反馈结合，避免只靠初始几何预测。
3. 引入层级规划或 world model，让 preparatory stage 不只是一跳重定位，而能支持更长链的多步准备动作。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [x] 训练细节完整
- [x] 数据集可获取

---

## 关联笔记

### 基于

- [[ACT]]: 都属于长时序 manipulation，但 ACT 更偏动作建模，BiPreManip 强调 preparatory reasoning。
- [[PointNet++]]: 提供点云几何表征，是 affordance map 和 object pose prediction 的基础。

### 对比

- [[Affordance]]: BiPreManip 不是只预测最终接触点，而是把目标 affordance 和 preparatory affordance 分成两层。
- [[cVAE]]: orientation sampling 依赖条件生成建模，而不是单点回归。

### 方法相关

- [[CLIP]]: 语言指令编码器，让 affordance 预测能区分打开、抬起、推移等不同目标。
- [[SE(3)]]: 主臂动作、辅臂动作和对象位姿重定位都在同一刚体变换空间里表示。

### 硬件/数据相关

- [[PartNet]]: 任务对象和 category 设计与可操作部件结构紧密相关。
- [[ShapeNet]]: 为 object shape variation 和 unseen split 提供了几何多样性来源。

---

## 速查卡片

> [!summary] BiPreManip
> - **核心**: 显式建模双臂 preparatory manipulation
> - **方法**: Goal Affordance + Pre-Affordance + Object Pose Predictor + Reorient Actor
> - **结果**: 仿真多类任务显著优于 baseline，真实世界达到 5/10 到 8/10
> - **代码**: https://sites.google.com/view/bipremanip

---

*笔记创建时间: 2026-03-24*
