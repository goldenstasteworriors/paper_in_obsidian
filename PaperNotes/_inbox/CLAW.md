---
title: "CLAW: Composable Language-Annotated Whole-body Motion Generation"
method_name: "CLAW"
authors: [Jianuo Cao]
year: 2026
venue: arXiv
tags: [humanoid, whole-body-motion, language-conditioned-control, data-generation, unitree-g1]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2604.11251v1
created: 2026-04-14
---

# 论文笔记：CLAW: Composable Language-Annotated Whole-body Motion Generation

## 元信息

| 项目 | 内容 |
|------|------|
| 作者 | Jianuo Cao 等 |
| 机构 | Nanjing University, University of California Berkeley |
| 日期 | April 2026 |
| 链接 | [arXiv](https://arxiv.org/abs/2604.11251v1) |
| 关键词 | humanoid, whole-body motion, language annotation, data engine |
| 对比基线 | mocap dataset, text-to-motion generation |

---

## 一句话总结

> `CLAW` 的价值不在于发明一个更大的生成模型，而在于给 Unitree G1 做出了一条可组合、可执行、带语言标注的 whole-body motion 数据生产线。

---

## 核心贡献

1. **可组合动作原语数据引擎**：把 whole-body motion mode 设计成可拼接的 building block。
2. **双界面采集**：既支持实时键盘控制，也支持序列编辑器做长时任务编排。
3. **低层控制闭环保证可执行性**：不是纯 kinematic 轨迹，而是由 low-level whole-body controller 跟踪。
4. **自动语言标注**：把长轨迹切分成多阶段描述，生成更适合语言条件控制的数据。
5. **面向 humanoid 数据扩展**：直接回应“高质量 whole-body + language 对数据稀缺”这个现实问题。

---

## 问题背景

### 这篇在解决什么

想训练语言条件下的 humanoid whole-body controller，最缺的不是模型结构，而是数据：

- mocap 数据贵，而且不一定对应机器人可执行轨迹；
- text-to-motion 模型生成的动作往往只在运动学上顺，不保证动力学可行；
- 真人遥操作收集 whole-body + language 数据，成本更高。

作者的思路很务实：

- 别先追求“会想”的 humanoid；
- 先把“可执行且可描述”的动作数据规模做起来。

### 现有路线的问题

1. **mocap 路线**
   动作自然，但和机器人本体约束不完全一致。
2. **生成模型路线**
   文字看起来懂，动作未必落地。
3. **纯人工遥操作**
   可执行但扩展性太差。

`CLAW` 试图把三者折中：

- 用 planner 保证结构化与可组合；
- 用 controller 保证可执行；
- 用 annotation pipeline 保证语言监督。

---

## 方法详解

### 总体结构

`CLAW` pipeline 大致分成四步：

1. 用户通过界面指定 motion intent；
2. kinematic planner 生成短时 reference motion；
3. low-level controller 在机器人上跟踪；
4. 系统把长轨迹自动切分并生成 language annotation。

### Figure 1: 系统入口与整体想法

![Figure 1](https://arxiv.org/html/2604.11251v1/x1.png)

**图解**：Figure 1 展示键盘模式和编辑器模式两种采集入口。它说明论文重点不是离线训练 trick，而是可交互的数据生产系统。

### 动作原语设计

论文把动作拆成若干 composable motion mode，  
每个 mode 都带结构化参数：

- movement direction
- heading
- speed
- pelvis height
- duration

这种设计很适合 humanoid whole-body，因为它在可组合性和可控性之间取了中间点。

### 低层控制

高层 planner 只负责短时 reference motion。  
真正让 G1 跑起来的是低层 [[Whole-Body Controller]]。

这点很重要，因为很多动作数据论文只是给出 kinematic sequence，  
而 `CLAW` 至少关心动作是否能被真实机器人跟踪出来。

### 自动语言标注

论文后半段很关键的一点，是把长轨迹自动分成多阶段并生成自然语言描述。  
这样最终得到的不是“动作片段数据库”，而是可直接用于 language-conditioned control 的监督对。

---

## 关键公式

### 公式1: [[Motion Primitive|动作组合]]

$$
\tau
=
\bigoplus_{i=1}^{N}
m_i(\mathbf{p}_i, d_i)
$$

**含义**：长轨迹 $\tau$ 由一串动作原语 $m_i$ 及其参数 $\mathbf{p}_i$、持续时间 $d_i$ 组合得到。

**符号说明**：
- $m_i$：第 $i$ 个 motion mode
- $\mathbf{p}_i$：速度、方向、高度等参数
- $\oplus$：时序拼接

### 公式2: [[Whole-Body Controller|轨迹跟踪]]

$$
\mathbf{u}_t = \pi_{\text{wbc}}(\mathbf{x}_t, \mathbf{r}_t)
$$

**含义**：低层控制器根据当前机器人状态 $\mathbf{x}_t$ 与参考动作 $\mathbf{r}_t$ 输出关节级控制。

### 公式3: 语言切分与标注

$$
\mathcal{S}
=
\left\{
s_k = (\tau_{t_k:t_{k+1}}, l_k)
\right\}_{k=1}^{K}
$$

**含义**：整段轨迹会被切成多个阶段片段，每段配一个语言描述 $l_k$。

### 公式4: 数据集目标

$$
\mathcal{D}
=
\left\{
(\tau_i, l_i)
\right\}_{i=1}^{M}
$$

**含义**：最终产出的训练集是大量可执行轨迹与语言描述的配对样本。

---

## 关键图表

### Figure 1: 采集界面

![Figure 1](https://arxiv.org/html/2604.11251v1/x1.png)

**说明**：键盘模式适合快速探索，编辑器模式适合长任务脚本式采集。

### Figure 2: CLAW pipeline 概览

![Figure 2](https://arxiv.org/html/2604.11251v1/x2.png)

**说明**：这张图应该对应 planner、controller、annotation 的整体串联，是全文最核心的一张结构图。

### Figure 7: 多阶段轨迹与自动标注

![Figure 7](https://arxiv.org/html/2604.11251v1/x5.png)

**说明**：Figure 7 展示长时任务如何被拆成多阶段并自动配上语言标签，这对后续训练 language-conditioned policy 很关键。

### Table 1: Motion mode 设计

| 设计点 | 作用 |
|--------|------|
| mode 离散化 | 保持可控性和可组合性 |
| speed / heading / height 参数 | 提高动作覆盖面 |
| duration 控制 | 便于长时任务拼接 |
| controller tracking | 保证机器人可执行性 |

**说明**：论文用表格列出不同 mode 支持哪些参数，本质是在定义一个面向 humanoid whole-body 的“动作 DSL”。

---

## 实验结果

### 论文重点不只是成功率

这篇真正要证明的不是“某个 benchmark 高了几点”，而是下面几件事：

1. 生成的 motion segment 能平滑衔接；
2. 机器人能稳定跟踪 reference；
3. 自动语言标注与动作阶段有一致性；
4. 长轨迹不是一堆拼接垃圾。

### 从 captions 可以看出的验证点

- `(a) Successful transition / (b) Failure transition`
  说明作者专门检查拼接处是否稳定。
- `Figure 7: Multi-stage trajectory`
  说明长时动作不是单段 sample，而是多阶段任务链。
- `TABLE I: Available motion modes`
  说明系统设计重点在动作覆盖面与参数化空间。

### 对你的价值

- 如果你想做 language-conditioned humanoid policy，这篇首先解决“数据从哪来”。
- 如果你想做 teleop 到 language 的桥接，这种结构化动作编排很适合作中间层。
- 如果你想要可控 whole-body 数据，而不是完全黑箱生成，这篇很值得借。

---

## 批判性思考

### 优点

1. 解决的是最脏但最真实的数据问题。
2. 可组合原语让 whole-body motion 采集具备规模化潜力。
3. 低层 controller 在环，减少“看起来像动作、实际跑不起来”的风险。

### 局限性

1. 数据多样性仍受 motion mode 词表限制，不是真正开放式行为分布。
2. 语言标注可能更像模板化描述，语义丰富度未必高。
3. 如果 low-level controller 本身有偏差，数据质量会被系统性带歪。

### 对你的启发

1. humanoid whole-body 数据不一定非得靠 mocap 或大模型合成。
2. 先定义可组合动作语法，再生成语言监督，可能是更稳的数据路线。
3. 对 whole-body teleop，结构化中间表示可能比直接 end-to-end 更可控。

---

## 关联笔记

### 方法相关

- [[Whole-Body Controller]]：CLAW 可执行性的核心保障。
- [[Motion Primitive]]：动作可组合设计的核心。

### 数据相关

- [[MoCap]]：传统 whole-body motion 数据来源。
- [[AMASS]]：human motion 数据集对比参照。
- [[Humanoid Robotics]]：方法面向的机器人平台与任务域。

---

## 速查卡片

> [!summary] CLAW
> - **核心**: 为 Unitree G1 构建可组合、可执行、带语言标注的 whole-body motion 数据引擎。
> - **方法**: 动作原语 + 交互式界面 + 低层控制跟踪 + 自动语言标注。
> - **结果**: 重点在平滑拼接、长轨迹编排和可训练数据生成。
> - **适用**: humanoid whole-body control, language-conditioned motion, teleop data generation。

*笔记创建时间: 2026-04-14*
