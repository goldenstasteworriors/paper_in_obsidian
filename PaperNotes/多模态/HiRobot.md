---
title: "Hi Robot: Open-Ended Instruction Following with Hierarchical Vision-Language-Action Models"
method_name: "HiRobot"
authors: [Lucy Xiaoyang Shi, Brian Ichter, Michael Equi, Liyiming Ke, Karl Pertsch, Quan Vuong, James Tanner, Anna Walling, Haohuan Wang, Niccolo Fusai, Adrian Li-Bell, Danny Driess, Lachy Groom, Sergey Levine, Chelsea Finn]
year: 2025
venue: ICML 2025
tags: [vision-language-action, hierarchical-policy, robot-instruction-following, human-robot-interaction, synthetic-data]
zotero_collection: 多模态
image_source: local
arxiv_html: https://arxiv.org/html/2502.19417v2
created: 2026-04-29
---

# 论文笔记：Hi Robot: Open-Ended Instruction Following with Hierarchical Vision-Language-Action Models

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Physical Intelligence, Stanford University, University of California Berkeley |
| 日期 | July 2025 |
| 项目主页 | https://www.pi.website/research/hirobot |
| 对比基线 | [[RT-1]], [[RT-2]], [[OpenVLA]], [[SayCan]] |
| 链接 | [arXiv](https://arxiv.org/abs/2502.19417) / [PDF](https://arxiv.org/pdf/2502.19417) |

---

## 一句话总结

> Hi Robot 用层级 VLM/VLA 把开放式人类指令和实时反馈转成可执行机器人技能。

---

## 核心贡献

1. **层级 VLA 系统**: 用高层 [[Vision-Language Model]] 做语义推理和反馈理解，用低层 [[Vision-Language-Action Model]] 执行动作，把复杂提示拆成原子技能。
2. **面向交互的合成数据生成**: 基于真实机器人轨迹和技能标注，用强 VLM 反推可能的人类指令、插话和机器人回应，训练高层策略。
3. **跨平台开放式评测**: 在单臂 UR5e、双臂 ARX、Mobile ARX 上评估 table bussing、sandwich making、grocery shopping，验证复杂指令、约束和中途反馈处理能力。

---

## 问题背景

### 要解决的问题

传统语言条件机器人策略通常适合原子指令，如“pick up the cup”。真实人机交互更像“帮我做一个不要番茄的素食三明治，如果有火腿再给朋友做一个”，还可能在执行中收到“that is not trash”“leave it alone”等 [[Situated Correction]]。Hi Robot 目标是在物理世界中把开放式自然语言、视觉上下文、用户约束和实时反馈都转成机器人可执行动作。

### 现有方法的局限

- 端到端 [[Vision-Language-Action Model]] 能执行低层动作，但复杂组合指令和动态反馈容易超出训练分布。
- 直接调用外部 [[Vision-Language Model]] 做高层规划可以理解语义，但缺少机器人能力边界和当前物理状态的训练 grounding。
- 先验技能库式系统依赖预定义 affordance 或 symbolic skill，物理灵巧性和实时语言交互能力不足。

### 本文的动机

作者把问题拆成 “System 2” 高层推理和 “System 1” 低层执行：高层模型只需要输出当前最合适的低层语言命令和可选 verbal response，低层 [[Pi0]] / [[Vision-Language-Action Model]] 专注把原子语言命令转成 [[Action Chunking|动作块]]。这保留了 VLA 的操作能力，也让系统能在新反馈到来时快速重新规划。

---

## 方法详解

### 模型架构

Hi Robot 采用 [[Hierarchical VLA]] 架构：
- **输入**: 多相机图像 $I_t^1,\ldots,I_t^n$、用户 prompt $\ell_t$、机器人状态 $q_t$。
- **高层策略**: 基于 [[PaliGemma]] 的 [[Vision-Language Model]]，输出低层命令 $\hat{\ell}_t$ 和可选机器人语音 $u_t$。
- **低层策略**: 基于 [[Pi0]] 的 [[Vision-Language-Action Model]]，用 [[Flow Matching]] 输出连续 [[Action Chunking|动作块]] $\mathbf{A}_t$。
- **调度方式**: 高层策略低频运行，每 1 秒或收到用户新反馈时触发；低层策略高频输出动作块。
- **总参数**: 高低层均从 PaliGemma-3B 初始化，低层额外带 action expert。

### 核心模块

#### 模块1: 高层 VLM 策略

**设计动机**: 用 [[Vision-Language Model]] 的语义和视觉 grounding 能力，把复杂人类语言映射到当前可执行技能。

**具体实现**:
- 输入当前多视角图像和用户语言 $\ell_t$。
- 输出 $\hat{\ell}_t$，即低层策略可理解的技能命令，如 “pick up one slice of bread”。
- 可在输出中包含机器人语音 $u_t$，用于确认、道歉或澄清；系统播放后再把语音部分从 $\hat{\ell}_t$ 中移除。
- 当用户中途插话时立即重新推理，因此能处理 [[Situated Correction]] 和任务切换。

#### 模块2: 低层 VLA 策略

**设计动机**: 复用 [[Pi0]] 的连续动作生成能力，让高层语言命令可以落到真实机器人控制。

**具体实现**:
- 输入图像、机器人关节/夹爪状态 $q_t$ 和低层命令 $\hat{\ell}_t$。
- 输出长度为 $H$ 的连续动作块 $\mathbf{A}_t=[a_t,\ldots,a_{t+H-1}]$。
- 使用 [[Flow Matching]] 训练连续动作分布，而不是离散动作 token。

#### 模块3: 合成交互数据

**设计动机**: 真实机器人示范通常只有粗粒度目标，不包含足够多开放式指令、负约束、用户纠错和机器人回复。

**具体实现**:
- 先收集 [[Teleoperation]] 轨迹 $\mathcal{D}_{demo}$。
- 人工或启发式切分成 1-3 秒的技能标签，形成 $\mathcal{D}_{labeled}$。
- 给数据生成 VLM 输入视觉上下文、历史技能和目标技能，让它生成可能的人类 prompt $\ell_t$ 与机器人回应 $u_t$，得到 [[Synthetic Interaction Data]] $\mathcal{D}_{syn}$。
- 高层策略在 $\mathcal{D}_{syn}\cup\mathcal{D}_{labeled}$ 上用 next-token cross entropy 训练。

---

## 关键公式

### 公式1: [[Action Chunking|动作块定义]]

$$
\mathbf{A}_t=[a_t,a_{t+1},\ldots,a_{t+H-1}]
$$

**含义**: 策略一次输出未来 $H$ 步动作，降低推理频率和执行抖动。

**符号说明**:
- $\mathbf{A}_t$: 时刻 $t$ 的动作块。
- $a_t$: 单步机器人动作。
- $H$: action chunk 长度。

### 公式2: [[Robot Policy|观测与策略分布]]

$$
\mathbf{o}_t=[I_t^1,\ldots,I_t^n,\ell_t,q_t],\qquad p(\mathbf{A}_t|\mathbf{o}_t)
$$

**含义**: 标准语言条件机器人策略用多相机图像、语言和本体状态预测动作块。

**符号说明**:
- $I_t^1,\ldots,I_t^n$: 多相机图像。
- $\ell_t$: 用户语言 prompt。
- $q_t$: 机器人关节和夹爪状态。
- $p(\mathbf{A}_t|\mathbf{o}_t)$: 条件动作分布。

### 公式3: [[Vision-Language Model|VLM 语言后缀分布]]

$$
p(\ell'|I,\ell)
$$

**含义**: VLM 根据图像 $I$ 和语言前缀 $\ell$ 预测语言后缀 $\ell'$。

**符号说明**:
- $I$: 输入图像。
- $\ell$: 语言前缀或用户问题。
- $\ell'$: 模型生成的回答、技能标签或机器人回应。

### 公式4: [[Decoder-only Transformer|自回归分解]]

$$
p(x_{t+1}|x_1,\ldots,x_t,I),\qquad
\ell=[x_1,\ldots,x_{t_p}],\quad
\ell'=[x_{t_p+1},\ldots,x_{t_p+t_s}]
$$

**含义**: 论文把常见 VLM 视为 decoder-only Transformer，自回归地产生后续 token。

**符号说明**:
- $x_t$: 第 $t$ 个 token。
- $t_p$: prefix token 长度。
- $t_s$: suffix token 长度。

### 公式5: [[Hierarchical VLA|层级策略分解]]

$$
p_{hi}(\hat{\ell}_t|I_t^1,\ldots,I_t^n,\ell_t)
$$

$$
p_{lo}(\mathbf{A}_t|I_t^1,\ldots,I_t^n,\hat{\ell}_t,q_t)
$$

**含义**: 高层策略输出低层语言命令，低层策略再根据命令和机器人状态输出动作。

**符号说明**:
- $p_{hi}$: 高层 VLM 策略。
- $p_{lo}$: 低层 VLA 策略。
- $\hat{\ell}_t$: 高层生成的原子技能命令。

### 公式6: [[Synthetic Interaction Data|合成数据生成]]

$$
p_{gen}(\ell_t,u_t|I_t^1,\ldots,I_t^n,\hat{\ell}_0,\ldots,\hat{\ell}_{t-1},\hat{\ell}_t,P)
$$

**含义**: 数据生成 VLM 在视觉上下文、历史技能、当前技能和任务 prompt $P$ 条件下，生成可能的人类交互和机器人回应。

**符号说明**:
- $p_{gen}$: 用于合成交互数据的 VLM。
- $u_t$: 机器人 verbal response。
- $P$: 描述任务、场景类别和回应类别的提示。

---

## 关键图表

### Figure 1: Open-ended instruction following

![[assets/HiRobot_fig1.png]]

**说明**: 展示 Hi Robot 能处理多阶段指令、未见长程任务、实时纠错、用户约束和开放式 prompt，并可生成道歉或确认回复。

### Figure 2: Overview of hierarchical VLA

![[assets/HiRobot_fig2.png]]

**说明**: 高层 [[Vision-Language Model]] 接收用户 prompt/interjection 和多视角图像，生成低层语言命令与可选语音；低层 [[Vision-Language-Action Model]] 接收命令、图像和关节状态输出动作。

### Figure 3: Data collection and generation

![[assets/HiRobot_fig3.png]]

**说明**: 从遥操作轨迹开始，人工标注短技能，再用数据生成 VLM 合成用户指令和机器人回应，最后训练高层策略。

### Figure 4: Task domains

![[assets/HiRobot_fig4.png]]

**说明**: 三个评测域分别覆盖 table bussing、sandwich making、grocery shopping；每个域都包含复杂指令、中途反馈和用户打断。

### Figure 5: Comparisons to prior methods

![[assets/HiRobot_fig5.png]]

**说明**: Hi Robot 在三类任务上的 [[Instruction Accuracy]] 和 [[Task Progress]] 均超过 GPT-4o high-level 与 flat VLA，平均 IA 比 GPT-4o 高 40% 以上，并接近 expert human high-level。

### Figure 6: Qualitative command comparisons

![[assets/HiRobot_fig6.png]]

**说明**: GPT-4o 容易误识别物体、跳过子任务或忽略用户意图；无合成数据版本能对齐图像但容易忽略用户约束；Hi Robot 的低层命令更贴合当前动作和请求。

### Figure 7: Ablation on synthetic data

![[assets/HiRobot_fig7.png]]

**说明**: 合成数据显著提升开放式指令处理能力；无合成数据版本在平均 IA 和 TP 上分别落后 46% 和 39%。

### Figure 8: Hierarchical policy vs. flat policy

![[assets/HiRobot_fig8.png]]

**说明**: 使用同样合成数据时，层级策略仍优于 flat VLA，平均 IA 和 TP 分别领先 19% 和 34%，说明单独的高层推理步骤对中途反馈和部分指令很关键。

### 附录表述: 低层策略单步推理延迟

| Component | Time |
|-----------|------|
| Image encoding | 14 ms |
| Observation processing | 32 ms |
| Action prediction x10 | 27 ms |
| Total on-board | 73 ms |
| Total off-board + WiFi | 86 ms |

**说明**: 低层策略可在约 10 Hz 策略频率运行；配合 [[Action Chunking]] 可控制 50 Hz 机器人执行。

### 附录表述: 高层策略单步解码延迟

| Hardware | Prefill | Decode |
|----------|---------|--------|
| RTX 4090 | 47 ms | 13.2 ms |
| H100 | 17.3 ms | 5.7 ms |

**说明**: 高层策略低频运行，主要在每秒一次或用户插话后触发，延迟不是控制回路瓶颈。

### 附录表述: 机器人平台

| Platform | Cameras | Configuration / Action Space | 用途 |
|----------|---------|------------------------------|------|
| UR5e | wrist + over-the-shoulder | 7D config/action | 单臂桌面清理 |
| Bimanual ARX | two wrist + base | 14D config/action | 双臂三明治制作 |
| Mobile ARX | two wrist + base | 14D config / 16D action | 移动双臂购物 |

**说明**: 方法不是单一硬件特化，而是在单臂、双臂和移动双臂平台上都评估。

### Listing 1: GPT-4o baseline prompt

**内容摘要**: GPT-4o baseline 被要求每 2 秒从预定义技能列表中选择一个表格清理指令，输入包含全局相机和腕部相机图像。这个 baseline 类似更强的 [[SayCan]] 变体，但仍缺少与机器人真实能力和训练数据的充分 grounding。

---

## 实验

### 数据集

| 数据集 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| $\mathcal{D}_{demo}$ | 未给具体条数 | 遥操作机器人完整任务轨迹，带粗粒度目标语言 | 低层策略训练基础 |
| $\mathcal{D}_{labeled}$ | 未给具体条数 | 从轨迹切分出的 1-3 秒短技能，含技能标签 | 高层/低层监督 |
| $\mathcal{D}_{syn}$ | 未给具体条数 | VLM 根据视觉、历史技能和当前技能合成的人类 prompt、interjection 和机器人回复 | 高层策略开放式交互训练 |

### 任务与指标

| 任务 | 机器人 | 核心挑战 |
|------|--------|----------|
| Table bussing | UR5e | 区分 trash/dishes、只清理某类物品、处理中途“not trash”纠错 |
| Sandwich making | Bimanual ARX | 操作柔软食材，理解过敏、禁用配料、补充/停止指令 |
| Grocery shopping | Mobile ARX | 移动双臂取货，理解“movie night”“something sweet”等隐式需求 |

| 指标 | 定义 |
|------|------|
| [[Instruction Accuracy]] | 高层预测的低层命令是否符合当前观察和用户意图 |
| [[Task Progress]] | 成功放置到正确位置或配置的对象比例 |

### Baselines

| 方法 | 说明 |
|------|------|
| Expert human high level | 人类专家替代高层模型输入低层命令，作为 oracle |
| GPT-4o high-level | GPT-4o API 做高层 VLM，低层策略与 Hi Robot 相同 |
| Flat VLA | 直接用同一个低层 [[Pi0]] 策略执行复杂 prompt，无高层 |
| Flat VLA with synthetic data | flat 策略加入合成数据训练，隔离层级结构收益 |
| Hi Robot without synthetic data | 去掉合成交互数据，评估合成数据贡献 |

### 实现细节

- **Backbone**: [[PaliGemma]] 3B。
- **低层策略**: [[Pi0]]，额外 action expert，通过 [[Flow Matching]] 产生连续动作。
- **优化器**: AdamW，$\beta_1=0.9,\beta_2=0.95$，weight decay 为 0。
- **梯度裁剪**: 最大范数 1。
- **EMA**: decay 0.999。
- **学习率**: warmup 1,000 steps 后保持 $1\times10^{-5}$。
- **Batch Size**: 512。
- **训练资源**: 高层策略约 2 小时，8 x H100。
- **语音交互**: Whisper large-v2 做 speech-to-text，Cartetia API 做 text-to-speech。

### 关键结果

1. Hi Robot 在三种任务上同时提升 [[Instruction Accuracy]] 和 [[Task Progress]]，尤其在复杂用户约束和中途反馈下优于 GPT-4o high-level 和 flat VLA。
2. GPT-4o 虽然模型更大，但常出现物体误识别、内部状态不一致或与机器人技能不匹配的问题。
3. flat VLA 难以处理中途反馈，因为没有解释性低层命令和高层重新规划。
4. 人类高层 oracle 接近完美，说明主要瓶颈在高层推理，而不是低层操作能力。
5. 合成数据和层级结构分别贡献明显：无合成数据平均 IA/TP 大幅下降；有合成数据但无层级结构也明显落后。

---

## 批判性思考

### 优点

1. **接口设计实用**: 高层输出自然语言技能，低层 VLA 执行动作，模块边界清晰，便于替换低层策略或高层 backbone。
2. **训练信号很聪明**: 用真实轨迹技能反推用户 prompt，比纯 LLM 生成任务更能贴近机器人实际 affordance。
3. **实验覆盖较强**: 单臂、双臂、移动双臂三类平台，任务覆盖清理、装配式食物制作和移动取物。

### 局限性

1. **高低层解耦**: 高层并不显式知道低层是否成功完成命令，只通过训练数据间接学习能力边界。
2. **长上下文记忆不足**: 论文承认高层在需要长时记忆的指令上容易失败。
3. **合成数据依赖 prompt engineering**: 交互类别和生成 prompt 设计会影响高层策略的行为覆盖。
4. **低层 OOD 恢复弱**: 掉落物体、错误累积等 failure recovery 仍是问题。
5. **复现门槛高**: 需要真实机器人数据、PaliGemma/π0 训练栈和高端 GPU；数据与代码未在论文中明确开源。

### 潜在改进方向

1. 让高层策略接收低层执行成功/失败信号，形成闭环能力建模。
2. 引入长上下文或外部记忆，追踪用户偏好、已经完成的子任务和被禁止的对象。
3. 把高低层合成单一模型，但在 inference 时动态切换抽象层级。
4. 加入失败恢复数据和 adversarial synthetic interaction，覆盖掉落、误抓、遮挡和歧义反馈。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [ ] 训练数据可获取
- [x] 训练细节完整
- [x] 硬件与延迟报告

---

## 关联笔记

### 基于

- [[Pi0]]: 低层 VLA 策略基础。
- [[PaliGemma]]: 高低层模型的 VLM 初始化。
- [[Action Chunking]]: 低层动作输出形式。
- [[Flow Matching]]: 低层连续动作生成目标。

### 对比

- [[RT-1]]: 早期大规模真实机器人 transformer 策略。
- [[RT-2]]: VLA 将网络知识迁移到机器人控制。
- [[OpenVLA]]: 开源 VLA 对照。
- [[SayCan]]: LLM 作为高层技能选择器的代表性系统。

### 方法相关

- [[Hierarchical VLA]]: 本文核心架构。
- [[Vision-Language-Action Model]]: 低层动作策略类型。
- [[Vision-Language Model]]: 高层推理策略类型。
- [[Synthetic Interaction Data]]: 高层策略训练关键数据。
- [[Situated Correction]]: 本文强调的实时反馈类型。

### 硬件/数据相关

- [[Teleoperation]]: 真实示范数据来源。
- [[Mobile Manipulator]]: Grocery shopping 使用移动双臂机器人。

---

## 速查卡片

> [!summary] Hi Robot
> 用高层 VLM 把开放式指令、视觉上下文和用户反馈转成低层技能命令，再由低层 VLA 执行动作。核心收益来自层级分解和基于真实技能的合成交互数据；主要短板是高低层解耦、长上下文弱和真实数据/硬件复现门槛高。
