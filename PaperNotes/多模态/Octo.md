---
title: "Octo: An Open-Source Generalist Robot Policy"
method_name: "Octo"
authors: [Octo Model Team, Dibya Ghosh, Homer Walke, Karl Pertsch, Kevin Black, Oier Mees, Sudeep Dasari, Joey Hejna, Tobias Kreiman, Charles Xu, Jianlan Luo, You Liang Tan, Lawrence Yunliang Chen, Pannag Sanketi, Quan Vuong, Ted Xiao, Dorsa Sadigh, Chelsea Finn, Sergey Levine]
year: 2024
venue: RSS
tags: [generalist-robot-policy, robot-manipulation, imitation-learning, diffusion-policy, open-x-embodiment, transformer-policy]
zotero_collection: 多模态
image_source: mixed
arxiv_html: https://arxiv.org/html/2405.12213v2
created: 2026-04-28
---

# 论文笔记：Octo: An Open-Source Generalist Robot Policy

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | UC Berkeley, Stanford, Carnegie Mellon University, Google DeepMind |
| 日期 | May 2024 |
| 项目主页 | https://octo-models.github.io |
| 对比基线 | [[RT-1-X]], [[RT-2-X]], VC-1, ResNet+Transformer Scratch |
| 链接 | [arXiv](https://arxiv.org/abs/2405.12213) / [HTML](https://arxiv.org/html/2405.12213v2) / [Code](https://github.com/octo-models/octo) / [Weights](https://huggingface.co/rail-berkeley) |

---

## 一句话总结

> Octo 是一个开源、可微调的 [[Generalist Robot Policy|通用机器人策略]]，用 800k 条 [[Open X-Embodiment|跨本体机器人轨迹]] 预训练，并用 [[Diffusion Policy|扩散动作头]] 支持多机器人操控。

---

## 核心贡献

1. **开源通用机器人策略**: 发布 Octo-Small 27M 和 Octo-Base 93M，包括 checkpoint、JAX 训练/微调代码、Open X 数据加载器和示例。
2. **可组合输入输出接口**: 用 [[Transformer]] token 序列统一语言、目标图像、多视角观测和 readout token，使微调时可以新增传感器、任务输入或动作空间。
3. **跨本体大规模预训练实证**: 在 25 个 [[Open X-Embodiment]] 子数据集的 800k episode 上训练，在 9 个真实机器人设置上验证 zero-shot 与小样本微调。
4. **系统消融**: 证明大数据混合、[[Vision Transformer|ViT-style]] 主干、[[Diffusion Policy|diffusion]] 连续动作头、模型规模对通用机器人策略很关键。

---

## 问题背景

### 要解决的问题

传统机器人模仿学习通常要为每个机器人、每个任务重新收集数据并从头训练策略，泛化范围窄。Octo 试图把自然语言/目标图像条件下的多机器人操作策略做成一个可开源复用的初始化模型：用户只需少量目标域演示，就能适配新的观测、动作空间或机器人本体。

### 现有方法的局限

[[RT-1-X]]、[[RT-2-X]]、RoboCat 等已有 [[Generalist Robot Policy]] 证明了跨机器人训练有价值，但常见限制是输入观测和动作接口固定、对新观测/新动作空间微调支持不足，且大模型或训练流水线不完全开放。Octo 把重点放在“可改接口 + 可微调 + 可复现”。

### 本文的动机

机器人任务的异质性来自机器人本体、相机布置、proprioception、动作空间、语言标注缺失等多方面。作者认为如果把所有输入输出都 token 化，并用 readout token 与轻量 head 解耦，预训练主干就可以在微调时尽量保留，只替换或新增小模块。

---

## 方法详解

### 模型架构

Octo 是一个基于 [[Transformer]] 的条件策略 $\pi$：

- **输入**: 语言指令 $\ell$、目标图像 $g$、观测历史 $o_1,\ldots,o_H$，默认用 2 帧历史。
- **Task tokenizer**: 语言用 t5-base 产生 16 个语言 embedding token；目标图像走轻量 CNN patch tokenizer。
- **Observation tokenizer**: 第三人称图像 resize/crop 到 $256\times256$，wrist camera 到 $128\times128$；浅 CNN 后切成 $16\times16$ patch token。
- **Backbone**: block-wise masked [[Transformer]]，观测 token 因果地看当前/过去观测和 task token。
- **Readout token**: 学习到的 readout token 只读取上下文 embedding，不反向影响观测 token，用于输出动作。
- **输出**: [[Diffusion Policy|条件扩散动作头]]预测连续多模态动作分布，并通过 [[Action Chunking|动作块]]输出未来多步动作。
- **模型规模**: Octo-Small 12 层、hidden 384、6 heads、27M；Octo-Base 12 层、hidden 768、12 heads、93M。

### 核心模块

#### 模块1: 可组合 token 接口

**设计动机**: 让 [[Generalist Robot Policy]] 在不同机器人上共享主干，同时允许传感器和任务定义变化。

**具体实现**:
- 语言、目标图像、相机观测都转成统一 token 序列。
- 缺失模态用 mask 处理，例如无语言标注的数据仍可用目标图像训练。
- 微调新观测或新动作空间时，只需新增 positional embedding、轻量 encoder 或 action head，主干参数可保留。

#### 模块2: Block-wise masked Transformer

**设计动机**: 兼顾时序因果性、任务条件和可插拔 readout。

**具体实现**:
- 观测 token 只能 attend 到 task token 与当前/过去时刻观测。
- readout token 可 attend 到前面的任务/观测 token，但不被任务/观测 token attend。
- 该结构使 readout token 类似 BERT 的 `[CLS]`，作为当前策略状态的紧凑 embedding。

#### 模块3: 条件扩散动作头

**设计动机**: 机器人操作动作分布可能多模态，MSE 容易平均化，离散动作又损失连续控制精度。

**具体实现**:
- transformer 主干每次动作预测只前向一次。
- 多步 denoising 只在小型 3-layer MLP diffusion head 中完成，hidden dim 256，带 residual connection 和 layer normalization。
- 使用标准 DDPM 目标、cosine noise schedule、20 个 diffusion steps。

---

## 关键公式

### 公式1: [[Transformer|输入 token 到 readout embedding]]

$$
e_l, e_g, e_o = T(T_l, T_g, T_o)
$$

**含义**: 语言、目标图像和观测 token 进入 Octo Transformer 后，得到可供 readout/action head 使用的 embedding。

**符号说明**:
- $T_l$: 语言指令 token。
- $T_g$: 目标图像 token。
- $T_o$: 观测历史 token。
- $T$: Octo 的 transformer backbone。
- $e_l,e_g,e_o$: 对应模态的上下文 embedding。

### 公式2: [[Diffusion Policy|条件扩散反向采样]]

$$
x_{k-1} = \alpha\left(x_k - \gamma \epsilon_\theta(x_k, e, k) + \mathcal{N}(0, \sigma^2 I)\right)
$$

**含义**: 从高斯噪声 $x_K \sim \mathcal{N}(0,I)$ 开始，条件在 transformer readout embedding $e$ 上逐步去噪得到动作块。

**符号说明**:
- $x_k$: 第 $k$ 个扩散步的带噪动作变量。
- $\epsilon_\theta(x_k,e,k)$: 条件去噪网络，预测噪声。
- $e$: readout token 输出的策略上下文 embedding。
- $\alpha,\gamma,\sigma$: noise schedule 相关超参数，论文使用 cosine schedule。
- $I$: 单位矩阵。

### 公式3: [[Action Chunking|动作块策略输出]]

$$
\pi_\theta(a_{t:t+K-1}\mid o_{1:t}, \ell, g)
$$

**含义**: Octo 不是只预测单步动作，而是在当前观测历史、语言和目标图像条件下预测未来 $K$ 步动作块；微调时 Berkeley Bimanual 最佳设置为训练 chunk 64、测试时 receding horizon 执行 12 步后重规划。

**符号说明**:
- $a_{t:t+K-1}$: 从当前时刻开始的未来动作序列。
- $o_{1:t}$: 当前及历史观测。
- $\ell$: 语言指令。
- $g$: 目标图像。
- $K$: 动作块长度。

---

## 关键图表

### Figure 1: Overview / 系统概览

![Figure 1](https://octo-models.github.io/teaser.jpg)

**说明**: 展示 Octo 的总体定位：在 [[Open X-Embodiment]] 的 800k 多样化 episode 上预训练，支持灵活任务和观测定义，可快速微调到新观测和新动作空间。

### Figure 2: Model Architecture / 模型架构

![[Octo_fig2.png|600]]

**说明**: 左侧是语言/图像 tokenization；上方是 transformer backbone 和 readout/action head；下方展示微调时新增观测或动作头而不修改预训练主干。

### Figure 3: Training Dataset Composition / 训练数据构成

![Figure 3](https://arxiv.org/html/2405.12213v2/x2.png)

**说明**: Octo 从 [[Open X-Embodiment]] 中筛选 25 个数据集，按样本量和多样性调整采样权重；Bridge、Fractal、Kuka 各占 17%。

### Figure 4: Evaluation Tasks / 评测任务

![Figure 4](https://arxiv.org/html/2405.12213v2/x3.png)

**说明**: 9 个真实机器人设置，覆盖 zero-shot 的 WidowX/UR5/RT-1 Robot，以及微调的 Berkeley Insert、Stanford Coffee、CMU Baking、Berkeley Pick-Up、Berkeley Coke、Berkeley Bimanual。

### Figure 5: Zero-Shot Evaluation / 零样本评测

![Figure 5](https://arxiv.org/html/2405.12213v2/x4.png)

**说明**: 语言条件下 Octo 在三个机器人设置平均比 [[RT-1-X]] 高 29% 成功率，并在 WidowX 与 RT-1 Robot 上接近 [[RT-2-X]]。

### Figure 6: Model Scaling / 模型缩放

![Figure 6](https://arxiv.org/html/2405.12213v2/x5.png)

**说明**: Octo-Tiny、Octo-Small、Octo-Base 的 zero-shot 成功率随参数规模增加，在 UR5 和 WidowX 上均提升。

### Figure 7: Evaluation Tasks Appendix / 附录评测图

![Figure 7](https://arxiv.org/html/2405.12213v2/x6.png)

**说明**: 附录中复现 9 个评测任务的机器人图片，便于对照各任务设置。

### Table I: Finetuning Evaluation

| Method | Berkeley Insertion | Stanford Coffee | CMU Baking | Berkeley Pick-Up | Berkeley Coke | Berkeley Bimanual | Average |
|--------|-------------------:|----------------:|-----------:|-----------------:|---------------:|-------------------:|--------:|
| ResNet+Transformer Scratch | 10% | 45% | 25% | 0% | 20% | 20% | 20% |
| VC-1 | 5% | 0% | 30% | 0% | 10% | 50% | 15% |
| **Octo** | **70%** | **75%** | **50%** | **60%** | **100%** | **80%** | **72%** |

**说明**: 每个任务约 100 条目标域演示，20 次真实机器人 trial；Octo 平均比次优 baseline 高 52 个百分点。

### Table II: Model Ablations

| 配置 | Aggregate Performance |
|------|----------------------:|
| **Octo-Small** | **83%** |
| RT-X dataset mix | 60% |
| Single robot dataset (Bridge Data) | 43% |
| Discretized Action Prediction | 18% |
| Continuous Action Prediction (MSE) | 35% |
| ResNet-50 + Transformer | 70% |

**关键发现**: 最优组合是 ViT-style 架构、扩散动作头和更宽的数据混合；单机器人数据和不合适的动作目标都会显著掉点。

### Table III: Octo Pretraining Dataset Mixture

| 数据集 | 权重 | 数据集 | 权重 |
|--------|-----:|--------|-----:|
| Fractal | 17.0% | Kuka | 17.0% |
| Bridge | 17.0% | BC-Z | 9.1% |
| Stanford Hydra | 6.0% | Language Table | 5.9% |
| Taco Play | 3.6% | Furniture Bench | 3.3% |
| UTAustin Mutex | 3.0% | Austin Sailor | 2.9% |
| Roboturk | 2.8% | Toto | 2.4% |
| Austin Sirius | 2.3% | Berkeley Autolab UR5 | 1.5% |
| IAMLab CMU Pickup Insert | 1.2% | Viola | 1.2% |
| Berkeley Fanuc Manipulation | 1.0% | NYU Franka Play | 0.9% |
| UCSD Kitchen | <0.1% | Jaco Play | 0.6% |
| Berkeley Cable Routing | 0.3% | Austin Buds | 0.3% |
| CMU Stretch | 0.2% | NYU Door Opening | 0.1% |
| DLR EDAN Shared Control | 0.1% |  |  |

**说明**: 数据混合不是简单按原始规模采样，而是对“更多样”的数据集加权、对重复性强的数据集降权。

### Table IV: Training Hyperparameters

| Hyperparameter | Value |
|----------------|-------|
| Learning Rate | 3e-4 |
| Warmup Steps | 2000 |
| LR Scheduler | reciprocal square-root |
| Weight Decay | 0.1 |
| Gradient Clip Threshold | 1 |
| Batch Size | 2048 |

**说明**: Octo-Base 用 TPU v4-128 训练 300k steps，约 14 小时；单张 NVIDIA A5000 24GB 微调约 5 小时。

### Table V: Architecture Details

| Model | Layers | Hidden size | MLP size | Heads | Params |
|-------|-------:|------------:|---------:|------:|-------:|
| Octo-Small | 12 | 384 | 1536 | 6 | 27M |
| Octo-Base | 12 | 768 | 3072 | 12 | 93M |

**说明**: 两个模型都保持 12 层 transformer，主要差异是宽度和 attention heads。

### Table VI: Detailed Model Ablations

| 配置 | Put carrot | Put eggplant | Put bread | Put spoon | Average |
|------|-----------:|-------------:|----------:|----------:|--------:|
| **Octo-Small** | **80%** | **90%** | 70% | **90%** | **83%** |
| RT-X dataset mix | 80% | 80% | 40% | 40% | 60% |
| Single robot dataset | 20% | 70% | 60% | 20% | 43% |
| Discretized Action Prediction | 0% | 20% | 10% | 40% | 18% |
| Continuous Action Prediction (MSE) | 70% | 30% | 0% | 40% | 35% |
| ResNet-50 + Transformer | 80% | 60% | **100%** | 40% | 70% |

**说明**: 细分任务上，Octo-Small 的优势主要来自目标图像条件与语言条件两类任务都稳定。

### Table VII: Zero-shot Generalization Analysis

| Generalization Type | Task | Success Rate | Average |
|---------------------|------|-------------:|--------:|
| In-distribution | Put carrot on plate | 80% | 85% |
| In-distribution | Put eggplant in pot | 90% | 85% |
| Novel objects | Put bread on plate | 70% | 80% |
| Novel objects | Put spoon on glove | 90% | 80% |
| Novel environment | Put mushroom in pot | 20% | 40% |
| Novel environment | Put spoon on cloth | 60% | 40% |
| Novel skill | Flip cup on its side | 10% | 5% |
| Novel skill | Put block in slot | 0% | 5% |

**说明**: Octo 对新物体泛化较好，对新环境下降明显，对训练本体中未出现的新技能几乎失败。

---

## 实验

### 数据集

| 数据集 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| [[Open X-Embodiment]] subset | 25 datasets, 800k episodes | 多机器人、多任务、多相机/标注情况 | 预训练 |
| WidowX BridgeV2 | 每任务 10 trials | zero-shot，语言和目标图像条件 | 与 RT-1-X/RT-2-X 比较、消融 |
| UR5 Tabletop | 每任务 10 trials | zero-shot，环境重装导致相机和背景变化 | 跨时间/环境鲁棒性 |
| RT-1 Robot | 每任务 10 trials | proprietary robot，桌面与家具任务 | 与 RT-1-X/RT-2-X 比较 |
| 6 个微调设置 | 每个约 100 demos | 新观测、新动作空间、新机器人本体 | 数据效率评估 |

### 实现细节

- **Backbone**: ViT-style transformer-first 架构，浅 CNN patch encoder + 大 transformer backbone。
- **语言编码器**: t5-base 111M，输出 16 个 language embedding tokens。
- **优化器**: AdamW，learning rate 3e-4，warmup 2000，reciprocal square-root schedule，weight decay 0.1。
- **Batch Size**: 2048。
- **训练轮数**: 300k steps。
- **硬件**: Octo-Base 用 TPU v4-128 训练约 14 小时；微调可在单张 NVIDIA A5000 24GB 上约 5 小时完成。
- **数据增强**: 第三人称相机随机 crop 后 resize 到 $256\times256$，color jitter，像素归一化到 $[-1,1]$；wrist camera resize 到 $128\times128$。
- **动作头**: 3-layer MLP diffusion head，hidden 256，20 diffusion steps。

### 主要结果

1. **Zero-shot**: Octo 在 WidowX、UR5、RT-1 Robot 三个平台上语言条件控制效果超过 [[RT-1-X]]，并接近 [[RT-2-X]] 的测试结果。
2. **Goal image 更强**: 在 WidowX 上，目标图像条件比语言条件平均高 25% 成功率，说明目标图像提供了更具体的任务完成信息。
3. **微调优势明显**: 6 个微调任务平均 72%，scratch 为 20%，VC-1 为 15%。
4. **消融结论一致**: 更宽数据混合、ViT-style 架构、扩散动作头、模型规模都提升性能。

---

## 批判性思考

### 优点

1. **工程开放性强**: 不只发布模型，还发布训练、微调、数据加载和示例代码，对社区复现和二次开发价值大。
2. **接口设计实用**: readout token 与可新增 encoder/head 的设计，直接面对机器人真实部署中观测和动作空间经常变化的问题。
3. **实验覆盖面广**: 9 个真实机器人设置跨 4 个机构，包含新观测、关节位置动作空间和新机器人本体。
4. **消融信息有用**: 明确说明 MSE head、离散动作 head、ResNet encoder、相对夹爪表示、proprioception 等尝试的得失。

### 局限性

1. **zero-shot 仍偏 in-distribution**: 主要在预训练数据覆盖的机器人/任务分布附近有效，Table VII 显示 novel skill 平均只有 5%。
2. **语言和 wrist camera 数据不足**: 论文指出只有 56% 预训练数据含语言标注、27% 含 wrist camera，这解释了语言条件与多相机微调的弱点。
3. **训练数据是 optimal demonstrations**: 当前基本是离线 imitation，未处理次优数据、在线交互数据或 RL-style 改进。
4. **范围限于 manipulator**: 预训练和评测主要是单臂/双臂 manipulation，未覆盖导航、移动操作、腿式平台等更宽机器人形态。

### 潜在改进方向

1. 引入更多 wrist camera、语言标注和跨环境数据，减少当前 modality imbalance。
2. 结合离线 RL、偏好学习或在线 fine-tuning，让模型能从非最优轨迹和交互失败中学习。
3. 扩展到 mobile manipulation、navigation、humanoid/whole-body control，检验 token 接口是否仍可扩展。
4. 做更细的 data mixture 学习或数据选择，而不是手工调整采样权重。

### 可复现性评估

- [x] 代码开源
- [x] 预训练模型
- [x] 训练细节完整
- [x] 数据集可获取
- [x] 微调脚本公开
- [x] 项目页和 Colab 可用

---

## 关联笔记

### 基于

- [[Open X-Embodiment]]: 跨机器人预训练数据来源。
- [[Diffusion Policy]]: 连续多模态动作分布建模的动作头。
- [[Action Chunking]]: 一次预测未来动作序列，提升闭环控制稳定性。
- [[Vision Transformer]]: transformer-first 架构和训练 recipe 的主要灵感。

### 对比

- [[RT-1-X]]: 开放 checkpoint 的跨机器人 generalist policy baseline。
- [[RT-2-X]]: 55B vision-language-action 模型，作为更大规模闭源/半闭源基线。
- VC-1: 预训练视觉表征 baseline。

### 方法相关

- [[Generalist Robot Policy]]: Octo 的目标类别。
- [[Transformer]]: Octo backbone。
- [[Hindsight Goal Relabeling]]: 用未来状态作为目标图像，降低语言标注依赖。

### 硬件/数据相关

- [[Open X-Embodiment]]: 训练数据集合。

---

## 速查卡片

> [!summary] Octo: An Open-Source Generalist Robot Policy
> - **核心**: 开源、可微调的跨机器人操作策略。
> - **方法**: tokenized multimodal inputs + block-wise masked transformer + diffusion action head。
> - **结果**: zero-shot 超过 RT-1-X；约 100 demos 微调平均 72%，显著高于 scratch/VC-1。
> - **代码**: https://github.com/octo-models/octo

---

*笔记创建时间: 2026-04-28*
