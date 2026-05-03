---
title: "RT-1: Robotics Transformer for Real-World Control at Scale"
method_name: "RT-1"
authors: [Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen Chebotar, Joseph Dabis, Chelsea Finn, Keerthana Gopalakrishnan, Karol Hausman, Alex Herzog, Jasmine Hsu, Julian Ibarz, Brian Ichter, Alex Irpan, Tomas Jackson, Sally Jesmonth, Nikhil J Joshi, Ryan Julian, Dmitry Kalashnikov, Yuheng Kuang, Isabel Leal]
year: 2022
venue: arXiv
tags: [vision-language-action, robot-transformer, imitation-learning, real-world-robotics, multi-task-learning, scalable-robot-learning]
zotero_collection: 多模态
image_source: mixed
arxiv_html: https://arxiv.org/html/2212.06817
created: 2026-04-28
---

# 论文笔记：RT-1: Robotics Transformer for Real-World Control at Scale

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Robotics at Google; Everyday Robots; Google Research, Brain Team |
| 日期 | 2022-12; arXiv v2 2023-08 |
| 项目主页 | [robotics-transformer1.github.io](https://robotics-transformer1.github.io/) |
| 对比基线 | [[Gato]], [[BC-Z]], [[SayCan]] |
| 链接 | [arXiv](https://arxiv.org/abs/2212.06817) / [arXiv HTML](https://arxiv.org/html/2212.06817) |

---

## 一句话总结

> [[RT-1]] 用高效 [[Transformer]] 策略在 13 台真机、13 万演示、700+ 指令上学习可泛化的语言条件机器人控制。

---

## 核心贡献

1. **真机规模化 VLA 策略**: 提出 [[RT-1]]，把语言指令、图像历史和离散化动作统一建模为 [[Vision-Language-Action|视觉-语言-动作]] 序列控制问题。
2. **实时可部署架构**: 用 [[FiLM]] 条件化 [[EfficientNet]]、[[TokenLearner]] 压缩视觉 token、decoder-only [[Transformer]] 输出动作 token，使 35M 参数模型可以 3 Hz 闭环控制。
3. **大规模实证**: 在 130k 真机演示、744 个指令、3000+ 次真机评测上，证明规模、任务多样性和高容量架构共同带来泛化与鲁棒性。
4. **数据吸收能力**: 进一步混入仿真数据和不同机器人形态的 Kuka 数据，显示 RT-1 可以吸收异构数据而基本不损伤原任务性能。

---

## 问题背景

### 要解决的问题

论文关注一个直接但很难的问题：能否训练一个单一的语言条件机器人策略，让它从大量真实机器人数据中学习多任务控制，并在新指令、新物体、新背景和长程任务中保持可用性能。形式上，策略 $\pi$ 在每个时刻接收语言指令 $i$ 和视觉历史 $\{x_j\}_{j=0}^t$，输出动作分布 $\pi(\cdot \mid i, \{x_j\}_{j=0}^t)$，目标是在指令、初始状态和动力学分布上最大化成功率。

### 现有方法的局限

早期端到端机器人学习通常是单任务或少量多任务数据，难以像 NLP/CV 那样从大规模宽分布数据中获得泛化。已有 [[Gato]]、[[BC-Z]]、Perceiver-Actor 等工作要么真机任务覆盖窄，要么更偏训练任务内表现，要么推理速度不适合实时控制。

### 本文的动机

作者的核心判断是：机器人泛化不是单纯换一个模型就能解决，而需要开放式、任务无关的大规模数据加上足够高容量又足够高效的模型。[[Transformer]] 适合吸收多任务数据，但必须通过压缩图像 token、动作离散化和推理缓存，才能满足真机闭环控制频率。

---

## 方法详解

### 模型架构

[[RT-1]] 采用 [[Transformer]] 策略架构：

- **输入**: 自然语言指令 $i$ + 6 帧图像历史 $\{x_{t-5}, \ldots, x_t\}$。
- **语言编码**: 使用 [[Universal Sentence Encoder]] 得到指令 embedding。
- **视觉编码**: 6 张 $300 \times 300$ 图像输入 ImageNet 预训练 [[EfficientNet]]-B3，输出 $9 \times 9 \times 512$ 特征图，即每帧 81 个视觉 token。
- **早期语言融合**: 在 EfficientNet 内部插入 identity-initialized [[FiLM]] 层，让语言从图像特征抽取阶段就影响视觉表示。
- **Token 压缩**: [[TokenLearner]] 将每帧 81 个视觉-语言 token 压缩到 8 个 token，6 帧共 48 个 token。
- **策略 Backbone**: 8 层 decoder-only [[Transformer]]，约 19M 参数。
- **输出**: 每步输出离散化动作 token，包括 7 维手臂动作、3 维底盘动作和 1 维动作模式。
- **总参数**: 约 35M；视觉/语言 tokenizer 16M，Transformer 19M。

### 核心模块

#### 模块1: FiLM-conditioned EfficientNet

**设计动机**: 让图像编码器从早期开始知道当前语言目标，避免像后融合架构那样先抽取任务无关 patch 特征再让 Transformer 处理全部冗余视觉信息。

**具体实现**:

- 语言指令先经过 [[Universal Sentence Encoder]]。
- 语言 embedding 进入 [[FiLM]] 层生成仿射调制参数 $\gamma, \beta$。
- [[FiLM]] 插入 EfficientNet 的 MBConv blocks 中。
- $\gamma, \beta$ 生成层零初始化，使调制一开始近似恒等映射，减少破坏 ImageNet 预训练特征的风险。

#### 模块2: TokenLearner 压缩

**设计动机**: 真机控制需要稳定、低延迟推理，直接让 Transformer 处理所有图像 token 会过慢。

**具体实现**:

- [[TokenLearner]] 学习元素级注意力图，从 81 个视觉-语言 token 中软选择重要组合。
- 每帧只保留 8 个 token，6 帧形成 48 个 Transformer 输入 token。
- 作者报告 TokenLearner 带来约 $2.4\times$ 推理加速；复用重叠时间窗口的 token 带来约 $1.7\times$ 加速。

#### 模块3: 离散动作建模

**设计动机**: 把连续控制转为离散 token 预测，使机器人策略更接近序列建模问题，并可直接用分类交叉熵训练。

**具体实现**:

- 每个动作维度离散成 256 个 bins。
- 动作维度包括：手臂 $(x, y, z, roll, pitch, yaw, gripper)$，底盘 $(x, y, yaw)$，以及 arm/base/terminate 三态模式。
- 控制频率为 3 Hz，直到输出 terminate 或达到时间步上限。

---

## 关键公式

### 公式1: [[Robot Policy|语言条件视觉策略]]

$$
a_t \sim \pi(\cdot \mid i, \{x_j\}_{j=0}^{t})
$$

**含义**: 策略在语言指令和当前视觉历史条件下采样动作。

**符号说明**:

- $i$: 语言指令。
- $x_j$: 第 $j$ 个时刻的图像观测。
- $a_t$: 第 $t$ 个时刻执行的机器人动作。
- $\pi$: 学到的语言条件机器人策略。

### 公式2: [[Imitation Learning|演示数据集]]

$$
D = \{(i^{(n)}, \{(x_t^{(n)}, a_t^{(n)})\}_{t=0}^{T^{(n)}})\}_{n=0}^{N}
$$

**含义**: 训练数据由成功演示 episode 组成，每条 episode 包含语言指令、图像序列和动作序列。

**符号说明**:

- $D$: 演示数据集。
- $N$: episode 数量。
- $T^{(n)}$: 第 $n$ 条 episode 的长度。

### 公式3: [[Behavioral Cloning|行为克隆目标]]

$$
\mathcal{L}_{BC} = - \sum_{(i, x, a) \in D} \log \pi(a_t \mid i, \{x_j\}_{j=0}^{t})
$$

**含义**: RT-1 通过最大化专家动作似然进行 [[Behavioral Cloning]]；动作离散化后实现为分类交叉熵。

**符号说明**:

- $\mathcal{L}_{BC}$: 行为克隆损失。
- $a_t$: 专家演示动作。
- $\pi(a_t \mid \cdot)$: 策略对专家动作的预测概率。

### 公式4: [[FiLM|语言条件特征调制]]

$$
\mathrm{FiLM}(h; \gamma, \beta) = \gamma(i) \odot h + \beta(i)
$$

**含义**: 语言 embedding 生成缩放和平移参数，对视觉特征 $h$ 做条件化调制。

**符号说明**:

- $h$: EfficientNet 中间视觉特征。
- $\gamma(i), \beta(i)$: 由语言指令生成的调制参数。
- $\odot$: 逐元素乘法。

### 公式5: [[Action Tokenization|动作离散化]]

$$
y_{t,d} = \operatorname{bin}(a_{t,d}; 256)
$$

**含义**: 第 $d$ 个动作维度被映射到 256 个离散 token 之一。

**符号说明**:

- $a_{t,d}$: 第 $t$ 步第 $d$ 个连续动作分量。
- $y_{t,d}$: 离散动作 token。
- $\operatorname{bin}$: 均匀分桶函数。

---

## 关键图表

### Figure 1: 系统概览

![[assets/RT-1_fig1_architecture.png]]

![[assets/RT-1_fig1_tasks.png]]

**说明**: 上半部分展示 RT-1 输入语言和图像、输出离散手臂/底盘动作；下半部分强调 130k 演示与 3000 次真机评测的规模。

### Figure 2: 机器人、环境与物体集合

![[assets/RT-1_fig2_robot_setup.png]]

**说明**: 包含训练用 robot classroom、两个真实 office kitchen、Everyday Robots 移动机械臂，以及用于技能/物体多样性的对象集合。

### Figure 3: RT-1 模型结构

![[assets/RT-1_fig3_model.png]]

**说明**: 指令经 USE embedding 调制 EfficientNet，视觉-语言 token 经 TokenLearner 压缩，再进入 decoder-only Transformer 输出动作 token。

### Figure 4: 评测场景

![[assets/RT-1_fig4_eval_scenarios.png]]

**说明**: 覆盖干扰物、背景变化和真实厨房多级泛化场景，分别检验 object clutter、视觉分布偏移和组合任务泛化。

### Figure 5: 执行轨迹示例

![[assets/RT-1_fig5_trajectories.png]]

**说明**: 展示 RT-1 在取物、移动物体、放入抽屉、拉餐巾、扶正罐子、开抽屉等多类指令上的真机轨迹。

### Figure 6: 跨机器人数据吸收

![[assets/RT-1_fig6_kuka.png]]

**说明**: 用 Kuka bin-picking 数据和 Everyday Robots 数据混训，测试是否能从不同形态机器人经验中迁移。

### Figure 8: 数据采集环境示例

![[assets/RT-1_fig8_env_examples.png]]

**说明**: 附录展示更丰富的 robot classroom 数据采集环境。

### Figure 9: 数据与任务增长

![[assets/RT-1_fig9_growth.png]]

**说明**: 展示数据量、任务数量和 seen instruction 成功率随时间增长的关系。

### Figure 10: 背景泛化

![[assets/RT-1_fig10_backgrounds.png]]

**说明**: 背景评测覆盖桌布纹理、未见厨房、材质/光照/背景变化等强视觉偏移。

### Figure 11: 真实指令多级泛化

![Figure 11](https://arxiv.org/html/2212.06817/x8.png)

**说明**: L1 为新台面布局和光照，L2 额外加入未见干扰物，L3 进一步包含新物体或新位置。

### Figure 12: 干扰物鲁棒性

![[assets/RT-1_fig12_distractors.png]]

**说明**: 干扰物场景从 0-5 个干扰物到 9 个干扰物并遮挡目标物体。

### Figure 13: 注意力可视化

![[assets/RT-1_fig13_attention.png]]

**说明**: Transformer 不同层和 head 倾向关注可交互区域，例如可抓取物体和抽屉。

### Table 1: 技能与指令统计

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
| Sec. 6.3/6.4 tasks | 9 | open large glass jar of pistachios |
| **Total** | **744** | - |

**说明**: 任务分布明显不均匀，Move Object Near Object 和取放类任务占多数。

### Table 2: 主结果

![[assets/RT-1_table2_baselines.png]]

| Model | Seen Tasks | Unseen Tasks | Distractors | Backgrounds |
|------|-----------:|-------------:|------------:|------------:|
| Gato | 65 | 52 | 43 | 35 |
| BC-Z | 72 | 19 | 47 | 41 |
| BC-Z XL | 56 | 43 | 23 | 35 |
| **RT-1** | **97** | **76** | **83** | **59** |

**关键发现**: RT-1 在 seen、unseen、干扰物和背景四类评测都显著领先；尤其 unseen task 为 76%，说明它不是简单记忆训练指令。

### Table 3: 真实厨房多级泛化

![[assets/RT-1_table3_realistic.png]]

| Model | All | L1 | L2 | L3 |
|------|----:|---:|---:|---:|
| Gato | 30 | 63 | 25 | 0 |
| BC-Z | 45 | 38 | 50 | 50 |
| BC-Z XL | 55 | 63 | 75 | 38 |
| **RT-1** | **70** | **88** | **75** | **50** |

**关键发现**: RT-1 在真实厨房综合场景中整体最强；L3 仍只有 50%，说明强组合分布偏移仍很难。

### Table 4 / 9: 混入仿真数据

![[assets/RT-1_table4_sim.png]]

| Training Data | Real Objects Seen Skill | Sim Objects Seen Skill | Sim Objects Unseen Skill |
|--------------|-------------------------:|-----------------------:|-------------------------:|
| Real Only | 92 | 23 | 7 |
| Real + Sim | 90 | 87 | 33 |

**关键发现**: 混入仿真数据几乎不损伤真实已见任务，但显著提升只在仿真中出现物体的真实执行能力。

### Table 5 / 10: 混入 Kuka 数据

![[assets/RT-1_table5_kuka.png]]

| Training Data | Classroom Eval | Bin-picking Eval |
|--------------|---------------:|-----------------:|
| Kuka + EDR | 90 | 39 |
| EDR only | 92 | 22 |
| Kuka only | 0 | 0 |

**关键发现**: 单独 Kuka 数据无法直接迁移到 EDR，但与 EDR 数据混训后能从 Kuka 经验中获得 bin-picking 增益。

### Table 6 / 11: SayCan 长程任务

| Method | Kitchen1 Planning | Kitchen1 Execution | Kitchen2 Planning | Kitchen2 Execution |
|--------|------------------:|-------------------:|------------------:|-------------------:|
| Original SayCan | 73 | 47 | - | - |
| SayCan w/ Gato | 87 | 33 | 87 | 0 |
| SayCan w/ BC-Z | 87 | 47 | 87 | 13 |
| SayCan w/ RT-1 | 87 | 67 | 87 | 67 |

**关键发现**: 在长程任务中，低层策略成功率会指数式影响整体任务；RT-1 作为 SayCan skill policy 明显优于 Gato 和 BC-Z。

### Table 7: 数据规模与多样性消融

![Table 7](https://arxiv.org/html/2212.06817/extracted/2212.06817v2/figures/data_ablation_simple.png)

**关键发现**: 数据多样性比单纯数据量更关键；移除任务多样性比减少相近任务内演示更伤泛化和鲁棒性。

### Table 8 / 12: 未见指令与 SayCan 指令列表

**说明**: 附录列出用于 unseen task 和 SayCan 长程评测的具体指令，主要用于保证 held-out 指令确实没有出现在训练集中。

### Table 13: 模型消融

![[assets/RT-1_table13_model_ablation.png]]

**关键发现**: 预训练、历史帧、Transformer、离散动作和语言早融合都会影响性能；最终 RT-1 在质量和推理速度之间取得较好折中。

---

## 实验

### 数据集

| 数据集 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| RT-1 real robot demonstrations | 约 130k episodes | 13 台 Everyday Robots，17 个月，744 条语言指令 | 主训练 |
| Simulation data | 约 518k successful trajectories | real2sim + multi-task RL，包含现实中未见物体 | 异构数据吸收 |
| Kuka QT-Opt data | 约 209k episodes | Kuka IIWA bin-picking，形态和动作空间不同 | 跨机器人数据吸收 |
| Real-world evaluations | 3000+ rollouts | seen/unseen/distractor/background/long-horizon | 真机评测 |

### 实现细节

- **Backbone**: FiLM-conditioned EfficientNet-B3 + TokenLearner + 8 层 decoder-only Transformer。
- **图像输入**: 6 帧，分辨率 $300 \times 300$。
- **视觉 token**: 每帧 81 个 EfficientNet token，TokenLearner 压缩到每帧 8 个。
- **动作空间**: 7 维手臂 + 3 维底盘 + 1 维模式；每个连续动作维度 256 bins。
- **训练目标**: [[Behavioral Cloning]]，动作 token 使用 [[Categorical Cross-Entropy]]。
- **部署频率**: 3 Hz 闭环控制，模型推理预算小于 100 ms。

### 主要结果

RT-1 在 seen tasks 上达到 97% 成功率，在 unseen tasks 上达到 76%，干扰物和背景鲁棒性分别为 83% 和 59%。相对最强 baseline，它在新任务、干扰物、背景上分别高约 24/36/18 个百分点。长程 SayCan 场景中，Kitchen1/Kitchen2 execution success 均为 67%，而 Gato 在 Kitchen2 为 0%，BC-Z 为 13%。

### 消融结论

数据侧，任务多样性对泛化的影响大于相近任务内的演示数量。模型侧，RT-1 不是单点 trick：早期语言融合、ImageNet 预训练、历史帧、Transformer 容量、离散化动作和 TokenLearner 的实时压缩共同构成最终效果。

---

## 批判性思考

### 优点

1. **真正的真机规模实验**: 130k 演示和 3000+ 真机 rollout 在机器人学习论文中很有分量。
2. **工程约束清晰**: 没有只追求大模型容量，而是把 3 Hz、<100 ms 推理预算作为架构设计核心。
3. **评测覆盖多维泛化**: unseen instruction、干扰物、背景、真实厨房和长程任务都单独评估。
4. **为后续 VLA 奠基**: [[RT-1-X]]、[[RT-2-X]] 和 Open X-Embodiment 等后续工作都直接继承了这种大规模多任务机器人策略路线。

### 局限性

1. **数据和硬件门槛极高**: 13 台真机、17 个月采集、专用移动机械臂，使复现实验几乎不可行。
2. **泛化主要是组合式泛化**: unseen tasks 仍由已见技能和已见对象重组，完全新概念、新技能或开放世界任务没有解决。
3. **仍依赖封闭数据**: 数据集和训练细节没有完整开放，社区难以验证 scaling law 和消融结论。
4. **动作粒度偏低频**: 3 Hz 对桌面移动操作可用，但对高速动态操作、灵巧手或接触丰富任务未必够。
5. **语义理解有限**: 使用 USE embedding 而不是强 VLM/LLM，语言泛化能力受限，这也是 RT-2 系列继续改进的方向。

### 潜在改进方向

1. 用更强的 [[Vision-Language Model]] 或 [[Vision-Language-Action]] 预训练表示替代 USE + EfficientNet。
2. 引入跨形态 action representation，减少 Kuka/EDR 这类跨机器人数据混训的手工动作空间对齐。
3. 结合 [[Action Chunking]] 或高频低层控制器，让策略既能做语义决策，又能处理更细粒度接触控制。
4. 开放或构建可替代的公共大规模数据集，让结论可复现、可比较。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [ ] 训练细节完整
- [ ] 数据集可获取

可复现性偏低。论文提供了架构、数据规模和主要实验，但核心数据、真机平台和完整训练 pipeline 都不是普通实验室可直接复现的。

---

## 关联笔记

### 基于

- [[Transformer]]: 作为序列建模 backbone。
- [[Imitation Learning]]: 通过成功演示学习策略。
- [[FiLM]]: 实现语言条件视觉特征调制。
- [[TokenLearner]]: 降低视觉 token 数量以满足实时推理。

### 对比

- [[Gato]]: 同为 Transformer generalist agent，但原始工作真机任务少；本文用同数据重训并比较架构。
- [[BC-Z]]: SayCan 中使用的 ResNet 策略 baseline。
- [[SayCan]]: 长程任务框架，RT-1 可作为其低层 skill policy。

### 方法相关

- [[Vision-Language-Action]]: RT-1 是早期代表性真机 VLA 策略。
- [[Generalist Robot Policy]]: 单模型吸收多任务机器人经验。
- [[Action Tokenization]]: 将连续控制转化为离散 token 预测。
- [[Behavioral Cloning]]: 训练目标。

### 硬件/数据相关

- [[Mobile Manipulator]]: Everyday Robots 平台属于移动机械臂。
- [[Cross-Embodiment]]: Kuka + EDR 混训展示跨形态数据吸收的早期证据。
- [[QT-Opt]]: Kuka bin-picking 数据来源。

---

## 速查卡片

> [!summary] RT-1
> - **核心**: 大规模真机多任务演示 + 高效 Transformer 策略，实现语言条件机器人控制。
> - **方法**: USE + FiLM EfficientNet + TokenLearner + decoder-only Transformer + 离散动作 token。
> - **结果**: 744 指令、130k 演示、3000+ 真机 rollout；seen 97%，unseen 76%，distractor 83%，background 59%。
> - **链接**: [Project](https://robotics-transformer1.github.io/) / [arXiv](https://arxiv.org/abs/2212.06817)

---

*笔记创建时间: 2026-04-28 12:00*
