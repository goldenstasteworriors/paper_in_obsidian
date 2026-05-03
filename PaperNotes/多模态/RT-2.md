---
title: "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control"
method_name: "RT-2"
authors: [Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen Chebotar, Xi Chen, Brianna Zitkovich]
year: 2023
venue: CoRL / PMLR
tags: [vision-language-action, robot-policy, web-pretraining, semantic-generalization, behavior-cloning]
zotero_collection: 多模态
image_source: local
arxiv_html: https://arxiv.org/abs/2307.15818
created: 2026-04-28
---

# 论文笔记：RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Google DeepMind / Google Research |
| 日期 | July 2023 |
| 项目主页 | https://robotics-transformer2.github.io |
| 对比基线 | [[RT-1]], [[Vision-Language Model]], [[Action Tokenization]] |
| 链接 | [arXiv](https://arxiv.org/abs/2307.15818) / [PMLR](https://proceedings.mlr.press/v229/zitkovich23a.html) / [PDF](https://proceedings.mlr.press/v229/zitkovich23a/zitkovich23a.pdf) |

---

## 一句话总结

> RT-2 把机器人动作离散成文本 token，使预训练 VLM 能直接作为闭环机器人策略。

---

## 核心贡献

1. **提出 [[Vision-Language-Action|VLA]] 训练范式**: 将机器人观测、语言指令和动作统一到 VLM 的输入输出格式里，不重新设计机器人专用大模型。
2. **动作文本化**: 基于 [[Action Tokenization]] 将 6-DoF 位姿增量、夹爪开合和终止信号编码为 8 个离散 token，让 [[Vision-Language Model|VLM]] 以 next-token prediction 学习低层控制。
3. **[[Co-Fine-Tuning]] 配方**: 同时使用机器人轨迹数据和原始 web-scale vision-language 数据微调，缓解只用机器人数据微调导致的语义遗忘。
4. **实机规模验证**: 在约 6k 次真实机器人评估中，RT-2 在未见物体、背景、环境和 emergent semantic reasoning 上显著优于 RT-1、VC-1、R3M、MOO 等基线。

---

## 问题背景

### 要解决的问题

机器人策略通常只有有限的实机交互数据，难以覆盖开放世界中的物体、符号、语言表达和语义推理。RT-2 的问题是：能否把互联网规模 [[Vision-Language Model|视觉语言模型]] 中已有的语义知识直接迁移到闭环机器人控制里。

### 现有方法的局限

- [[RT-1]] 等大规模机器人策略能学习多任务操作，但泛化主要来自机器人数据规模和多样性，难以继承 web 语义知识。
- CLIPort、MOO、R3M、VC-1 等方法会引入预训练视觉或 VLM 表征，但通常把语义模型当作感知模块，动作头仍是机器人专用结构。
- 传统层级方法可用 LLM/VLM 做高层规划，但低层控制和高层语义往往分离，误差会在接口处积累。

### 本文的动机

如果把动作看作另一种“语言”，则 VLM 的 token 生成接口可以同时输出自然语言和机器人动作。这样模型参数、预训练知识和微调目标共享同一套 backbone，语义能力有机会直接进入控制策略。

---

## 方法详解

### 模型架构

RT-2 是基于预训练 [[Vision-Language Model|VLM]] 的 [[Vision-Language-Action|VLA]] 策略族：

- **输入**: 当前相机图像 + 语言指令，采用 VQA prompt，如 `Q: what action should the robot take to ...? A:`
- **Backbone**: [[PaLI-X]] 5B/55B、[[PaLM-E]] 12B，以及用于 Language-Table 的 PaLI 3B。
- **核心模块**: [[Action Tokenization]]、[[Co-Fine-Tuning]]、[[Output-Constrained Decoding]]。
- **输出**: 8 个动作 token，对应终止、末端位姿增量和夹爪开合。
- **执行方式**: 55B 模型部署在多 TPU 云服务上，实机通过网络查询，约 1-3 Hz；5B 模型约 5 Hz。

### 模块1: 动作 token 化

**设计动机**: 让 VLM 的文本输出空间能表达机器人动作，从而复用 next-token prediction 训练机制。

**具体实现**:
- 动作空间包含 6-DoF 末端位姿增量、夹爪 extension 和 episode termination。
- 除 termination 外，每个连续维度均匀离散为 256 bins。
- [[PaLI-X]] 直接使用整数 token；[[PaLM-E]] 用 256 个最低频 token 覆盖为动作词表。
- 解码后的 token 会 de-tokenize 回低层机器人控制命令，形成闭环控制。

### 模块2: Co-Fine-Tuning

**设计动机**: 只用机器人数据微调大 VLM 会破坏或遗忘原有视觉语言知识；混合 web 数据可以保持语义能力。

**具体实现**:
- [[PaLI-X]] 版本微调时机器人数据约占 batch mixture 的 50%。
- [[PaLM-E]] 版本微调时机器人数据约占 66%。
- 机器人轨迹被包装成 VQA 样式输入，动作 token 作为 answer。
- 原始 captioning / VQA / WebLI 等任务继续参与训练。

### 模块3: 输出约束解码

**设计动机**: 实机控制时必须输出合法动作 token，不能采样任意自然语言 token。

**具体实现**:
- 当 prompt 是 robot-action task 时，只允许从合法 action-token vocabulary 中采样。
- 当 prompt 是普通视觉语言任务时，仍允许输出完整自然语言词表。

### 模块4: Chain-of-Thought 动作生成

RT-2 还测试了 [[Chain-of-Thought Prompting|CoT]] 变体：在输出动作前先生成自然语言 `Plan`，再生成 `Action` token。该变体只做少量 gradient steps，用来探索 VLM 的语义推理是否能和低层动作生成共存。

---

## 关键公式

### 公式1: [[Action Tokenization|动作 token 序列]]

$$
y_t =
\text{``terminate } \Delta x\ \Delta y\ \Delta z\ \Delta r_x\ \Delta r_y\ \Delta r_z\ \text{gripper''}
$$

**含义**: 将机器人单步动作表示为 8 个 token 的序列，使动作可被 VLM 当作文本目标预测。

**符号说明**:
- $y_t$: 第 $t$ 步模型输出的动作 token 字符串。
- $\Delta x,\Delta y,\Delta z$: 末端位置增量，离散为 256 bins。
- $\Delta r_x,\Delta r_y,\Delta r_z$: 末端旋转增量，离散为 256 bins。
- `terminate`: episode 成功结束信号。
- `gripper`: 夹爪 extension token。

### 公式2: [[Behavioral Cloning|next-token 行为克隆损失]]

$$
\mathcal{L}_{\mathrm{RT2}}
= - \sum_{t=1}^{T} \log p_\theta(y_t \mid I_t, q_t, y_{<t})
$$

**含义**: 论文没有引入新的显式控制损失，而是把机器人动作预测纳入 VLM 的 next-token prediction；在机器人数据上等价于行为克隆。

**符号说明**:
- $I_t$: 当前图像观测。
- $q_t$: 由语言任务构造的 VQA prompt。
- $y_t$: 目标动作 token。
- $\theta$: RT-2 模型参数。

### 公式3: [[Co-Fine-Tuning|混合数据微调目标]]

$$
\mathcal{L}_{\mathrm{mix}}
= \lambda_{\mathrm{robot}} \mathcal{L}_{\mathrm{robot}}
+ \lambda_{\mathrm{web}} \mathcal{L}_{\mathrm{web}}
$$

**含义**: 这是对论文训练策略的等价抽象：robot trajectory 和 web vision-language tasks 混合采样共同优化，权重由 batch mixture 控制。

**符号说明**:
- $\mathcal{L}_{\mathrm{robot}}$: 动作 token 预测损失。
- $\mathcal{L}_{\mathrm{web}}$: captioning / VQA 等视觉语言任务损失。
- $\lambda_{\mathrm{robot}}, \lambda_{\mathrm{web}}$: 数据混合比例；RT-2-PaLI-X 约 50% robot，RT-2-PaLM-E 约 66% robot。

---

## 关键图表

### Figure 1: RT-2 Overview / 系统概览

![[RT2_page2-02.png]]

**说明**: 展示 RT-2 如何把机器人动作当作语言 token，与互联网规模视觉语言数据共同训练，并在推理时把输出 token 反解码为机器人动作。

### Figure 2: Emergent Behaviors / 涌现行为示例

![[RT2_page4-04.png]]

**说明**: 展示 RT-2 在未见语义任务中的执行示例，包括符号理解、物体属性推理、人类识别和语义指令泛化。

### Figure 3: Generalization Scenarios / 泛化场景

![[RT2_page5-05.png]]

**说明**: 展示未见物体、未见背景、未见环境三类泛化测试场景。

### Figure 4: Overall Performance / 总体成功率

![[RT2_page6-06.png]]

**说明**: RT-2 在 seen tasks 上与 RT-1 接近，但在 unseen object/background/environment 上显著更强。

### Figure 5: Language-Table OOD Behaviors / 仿真到真实 OOD 行为

![[RT2_page7-07.png]]

**说明**: 用较小 PaLI-3B 版本在 Language-Table 上展示 OOD 行为；同页包含 Table 1。

### Figure 6: Emergent Skills and Ablations / 涌现技能与消融

![[RT2_page7-07.png]]

**说明**: 左侧比较 emergent skills，右侧展示模型规模和训练方式对泛化的影响。

### Figure 7: Chain-of-Thought Rollouts / CoT 推理轨迹

![[RT2_page8-08.png]]

**说明**: RT-2-PaLM-E 先生成自然语言 plan，再输出 action token，展示多阶段语义推理到动作的桥接。

### Figure 8: Emergent Evaluation Scenarios / 涌现能力评估场景

![[RT2_page15-15.png]]

**说明**: 展示 symbol understanding、reasoning、person recognition 等定量评估使用的场景。

### Figure 9: Failure Cases / Language-Table 失败案例

![[RT2_page17-17.png]]

**说明**: RT-2 对未见物体动力学仍会失败，例如笔滚落或香蕉接触点导致的推动失败。

### Figure 10: Additional CoT Examples / 更多 CoT 示例

![[RT2_page19-19.png]]

**说明**: 更多 plan + action 形式的推理控制示例。

### Table 1: Language-Table 仿真任务

| Model | Language-Table |
|--------|----------------|
| BC-Zero | 72 ± 3 |
| RT-1 | 74 ± 13 |
| LAVA | 77 ± 4 |
| **RT-2-PaLI-3B** | **90 ± 10** |

**关键发现**: 即使在不同机器人和仿真环境上，小型 RT-2-PaLI-3B 也显著优于开源基线。

### Table 2: Seen robot skills

| Skill | Count | Example |
|------|------:|---------|
| Pick Object | 130 | pick iced tea can |
| Move Object Near Object | 337 | move pepsi can near rxbar blueberry |
| Place Object Upright | 8 | place water bottle upright |
| Knock Object Over | 8 | knock redbull can over |
| Open Drawer | 3 | open the top drawer |
| Close Drawer | 3 | close the middle drawer |
| Place Object into Receptacle | 84 | place brown chip bag into white bowl |
| Pick Object from Receptacle and Place on Counter | 162 | pick green jalapeno chip bag from paper bowl and place on counter |
| **Total** | **735** | - |

**关键发现**: 训练技能集中在拾取、移动、抽屉和容器操作，RT-2 的新能力主要来自语义组合，而不是新运动技能。

### Table 3: Unseen evaluation instructions

| 组别 | 内容 |
|------|------|
| Unseen Objects | banana、oreo、pear、cold brew can、toy、watch、cloth 等 |
| Unseen Backgrounds | 在新背景上执行 pick / move 等任务 |
| Unseen Environments | sink、office desk 等新环境中的 pick / move / put / push / point |

**关键发现**: 泛化评估覆盖物体、背景、环境三个轴，hard split 引入更大视觉和动力学分布偏移。

### Table 4: Emergent evaluation instructions

| 组别 | 示例任务 |
|------|----------|
| Symbol Understanding | move coke can near X / 3 / Y; push coke can on top of heart |
| Reasoning: Math | move banana near the sum of two plus one |
| Reasoning: Logos | move cup to google / android / youtube |
| Reasoning: Nutrition | pick a healthy drink / salty snack |
| Color and Multilingual | move apple to vaso verde; 德语/法语/西语指令 |
| Person Recognition | move coke can to Taylor Swift / person with glasses |

**关键发现**: 这些任务大多不需要新动作，而需要把 web 语义知识映射到已有动作技能。

### Table 5: Overall performance

| Model | Seen | Unseen Obj Easy | Unseen Obj Hard | Bg Easy | Bg Hard | Env Easy | Env Hard | Unseen Avg |
|------|-----:|----------------:|----------------:|--------:|--------:|---------:|---------:|-----------:|
| R3M | 45 | 32 | 14 | 13 | 9 | 0 | 2 | 12 |
| VC-1 | 63 | 34 | 10 | 13 | 3 | 0 | 0 | 10 |
| RT-1 | 92 | 31 | 43 | 71 | 9 | 26 | 14 | 32 |
| MOO | 75 | 58 | 48 | 38 | 41 | 19 | 3 | 35 |
| **RT-2-PaLI-X-55B** | **91** | **70** | **62** | **96** | **48** | **63** | **35** | **62** |
| **RT-2-PaLM-E-12B** | **93** | **84** | **76** | **75** | **71** | **36** | **33** | **62** |

**关键发现**: RT-2 的 unseen average 达到 62，约为 RT-1 的 2 倍。

### Table 6: Emergent evaluation

| Model | Symbol Avg | Reasoning Avg | Person Avg | Overall Avg |
|------|-----------:|--------------:|-----------:|------------:|
| VC-1 | 11 | 10 | 13 | 11 |
| RT-1 | 16 | 16 | 20 | 17 |
| **RT-2-PaLI-X-55B** | **82** | **46** | **53** | **60** |
| **RT-2-PaLM-E-12B** | **36** | **43** | **43** | **40** |

**关键发现**: RT-2-PaLI-X-55B 对符号理解提升最明显；RT-2-PaLM-E-12B 在数学相关推理上更强。

### Table 7: Size and training ablations

| Model | Size | Training | Avg |
|------|------|----------|----:|
| RT-2-PaLI-X | 5B | from scratch | 9 |
| RT-2-PaLI-X | 5B | fine-tuning | 42 |
| RT-2-PaLI-X | 5B | co-fine-tuning | 44 |
| RT-2-PaLI-X | 55B | fine-tuning | 52 |
| **RT-2-PaLI-X** | **55B** | **co-fine-tuning** | **63** |

**关键发现**: 预训练、模型规模和 co-fine-tuning 都有用；从零训练 5B 模型几乎不能泛化。

---

## 实验

### 数据集

| 数据集 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| WebLI / VLM mixture | WebLI 原始约 10B image-text pairs，过滤后约 1B examples | 多语言 image-text、captioning、VQA | 保留 web-scale 语义知识 |
| RT-1 robot dataset | 移动机械臂演示，735 个 seen skill labels | pick、move、drawer、receptacle 等 | 机器人动作学习 |
| Language-Table | 开源仿真 tabletop benchmark | 2D 推动和语言条件控制 | 额外仿真对比 |
| Real-world eval suite | 约 6k 实机 trials | seen / unseen / emergent / CoT | 主评估 |

### 实现细节

- **RT-2-PaLI-X-55B**: learning rate $1e^{-3}$，batch size 2048，80K gradient steps。
- **RT-2-PaLI-X-5B**: learning rate $1e^{-3}$，batch size 2048，270K gradient steps。
- **RT-2-PaLM-E-12B**: learning rate $4e^{-4}$，batch size 512，1M gradient steps。
- **RT-2-PaLI-3B for Language-Table**: learning rate $1e^{-3}$，batch size 128，300K gradient steps。
- **训练目标**: next-token prediction，在机器人数据上对应 [[Behavioral Cloning]]。
- **推理部署**: 大模型云端 TPU serving，实机网络查询。

### 可视化结果

定性结果说明 RT-2 的主要增益不是学会全新运动 primitive，而是把已有动作技能绑定到更丰富的视觉语义上。例如识别符号卡片、选择健康零食、处理多语言指令、根据人物属性移动物体。

---

## 批判性思考

### 优点

1. **接口极简**: 动作 token 化让 VLM 原生训练管线直接变成机器人策略训练管线。
2. **结果扎实**: 约 6k 实机评估覆盖 seen、unseen 和 emergent，避免只展示 demo。
3. **证明 web 知识可迁移到低层控制**: 不是只做高层 planner，而是把语义能力放进闭环 action prediction。

### 局限性

1. **不产生新运动技能**: RT-2 只能重组机器人数据中已有动作技能，不能因为 web 预训练就学会未见动力学或操作 primitive。
2. **推理成本高**: 55B 模型需要多 TPU 云服务，1-3 Hz 对高频控制任务可能不足。
3. **闭源依赖强**: PaLI-X / PaLM-E 和机器人数据都不易复现，方法思想强于可复现实验。
4. **动作离散化较粗**: 256-bin 离散动作适合低频 tabletop manipulation，但对灵巧操作、高精度接触和连续控制不一定足够。

### 潜在改进方向

1. 用开源 VLM/VLA backbone 复现该 recipe，并评估 [[OpenVLA]]、[[InternVLA]] 等后续模型。
2. 引入动作 chunk、diffusion / flow action head 或 continuous action decoder，提高控制频率和精度。
3. 扩大机器人数据的技能维度，而不只是物体和场景维度。
4. 用蒸馏、量化、边缘部署减少云端 TPU 依赖。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [ ] 训练细节完整
- [ ] 数据集可获取

论文提供了大量训练超参数和评估细节，但核心模型、机器人数据和 serving 系统均不可直接复现。

---

## 关联笔记

### 基于

- [[RT-1]]: RT-2 沿用其机器人数据、动作空间和离散动作表示。
- [[Vision-Language Model]]: 直接复用 PaLI-X / PaLM-E 的视觉语言预训练能力。
- [[Behavioral Cloning]]: 机器人轨迹上的 next-token action prediction 本质是模仿学习。

### 对比

- [[VC-1]]: 视觉表征预训练基线，缺少语言原生建模。
- [[R3M]]: 从人类活动视频学习表征的机器人预训练基线。
- [[MOO]]: 物体中心 VLM 辅助策略基线。

### 方法相关

- [[Action Tokenization]]: RT-2 的核心接口设计。
- [[Co-Fine-Tuning]]: 保持 web 语义知识的关键训练策略。
- [[Output-Constrained Decoding]]: 实机控制合法动作输出约束。
- [[Chain-of-Thought Prompting]]: 探索自然语言 plan 与动作 token 共存。
- [[PaLI-X]]: RT-2-PaLI-X backbone。
- [[PaLM-E]]: RT-2-PaLM-E backbone。

### 硬件/数据相关

- [[WebLI]]: PaLI 系列背后的 web-scale image-text 数据。
- [[Language-Table]]: RT-2-PaLI-3B 额外验证使用的仿真 benchmark。

---

## 速查卡片

> [!summary] RT-2
> - **核心想法**: 把机器人动作变成文本 token，让 VLM 直接输出动作。
> - **最重要结论**: web-scale VLM 预训练可以显著提升机器人策略的语义泛化。
> - **关键数字**: unseen average 62 vs RT-1 32；emergent average 60 vs RT-1 17。
> - **主要限制**: 不学新运动技能、推理成本高、核心模型和数据不可复现。
