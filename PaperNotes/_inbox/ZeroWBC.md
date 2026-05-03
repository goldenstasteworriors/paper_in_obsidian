---
title: "ZeroWBC: Learning Natural Visuomotor Humanoid Control Directly from Human Egocentric Video"
method_name: "ZeroWBC"
authors: ["Haoran Yang", "Jiacheng Bao", "Yucheng Xin", "Haoming Song", "Yuyang Tian", "Bin Zhao", "Dong Wang", "Xuelong Li"]
year: 2026
venue: arXiv
tags: [humanoid, whole-body-control, egocentric-perception, visuomotor-control, motion-generation, motion-tracking]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2603.09170v1
created: 2026-03-11
---

# ZeroWBC

## 一句话判断

这篇工作的关键不是“让 humanoid 继续做动作跟踪”，而是把 [[Vision-Language Model]]、[[VQ-VAE]] 和通用 motion tracker 串成一条数据更便宜的 whole-body control 路线，用人类第一视角视频加 [[MoCap]] 替代大规模机器人 teleoperation。

## 论文信息

- 论文: [arXiv](http://arxiv.org/abs/2603.09170v1) | [PDF](https://arxiv.org/pdf/2603.09170v1)
- 项目主页: [ZeroWBC.github.io](https://zerowbc.github.io/)
- 作者: Haoran Yang, Jiacheng Bao, Yucheng Xin, Haoming Song, Yuyang Tian, Bin Zhao, Dong Wang, Xuelong Li
- 机构: University of Science and Technology of China / Shanghai AI Laboratory / Northwestern Polytechnical University / Tsinghua University / Shanghai Jiao Tong University / TeleAI
- 机器人平台: Unitree G1
- 任务类型: humanoid scene interaction, whole-body control, natural visuomotor behavior
- 真实部署: 有。论文报告了真实机器人上的 obstacle avoidance, ball kicking, sofa sitting, move boxes 和 zero-shot chair sitting

## 一句话总结

> ZeroWBC 用人类 egocentric image + text 先生成未来人体动作，再 retarget 到 G1 上用通用 tracker 执行，从而绕开昂贵 humanoid teleop 数据采集。

## 核心贡献

1. **把第一视角人类数据拉进 humanoid whole-body control**: 不再依赖每个任务都重新收 real robot teleop 数据。
2. **两阶段解耦**: 先做视觉文本到人体动作的生成，再做机器人级别的 tracking 执行，减少一个模型同时扛 perception 和 low-level control 的负担。
3. **证明 scene interaction 能上真机**: 不只是在仿真里走路，而是做坐、绕障、踢球、搬箱子这类与环境耦合更强的动作。

## 问题背景

### 要解决的问题

现有 humanoid visual control 主要卡在两件事上：
- 大规模机器人 teleop 数据非常贵，难以覆盖多任务、多场景。
- 单阶段视觉到动作策略容易学到不自然、任务绑定很死的 whole-body behavior。

### 现有方法的局限

- 类似 [[WholeBodyVLA]] 的路线依赖 task-specific robot demonstrations，扩展性差。
- 纯 simulation RL 方法能学会单项技能，但换场景、换指令、换视觉输入就容易掉性能。
- 单个 reference motion tracking 已经很成熟，但 scene-conditioned interaction 还远不够。

### 本文的动机

作者的判断很直接：人类第一视角视频和全身动作捕捉比 humanoid teleop 更便宜、更自然，也更接近日后规模化收数的现实路径。因此不如先从人类动作生成“自然 whole-body intent”，再把它翻译给机器人去执行。

## 方法详解

### 整体架构

ZeroWBC 采用明显的两阶段架构：
- **阶段 1: Multimodal Motion Generation**
  输入第一视角图像和文本指令，输出未来人体动作 token 序列，再解码成连续人体动作。
- **阶段 2: General Motion Tracking**
  把人体动作 retarget 到机器人关节空间，再由 tracking policy 输出底层控制。

这种拆法的好处是：
- 视觉语义和低层跟踪不必在一个网络里互相打架。
- 第一阶段可以吃大规模人类视频数据。
- 第二阶段可以专门为真实机器人稳定性做强化学习训练。

### 数据采集与对齐

作者没有走 robot teleoperation，而是自己搭了一套人类数据采集流程：
- 胸前固定 GoPro，模拟机器人胸前第一视角。
- 同步采集人体 [[MoCap]]。
- 强制把相机高度尽量对齐机器人相机高度，减少人和机器人视角差异。

这一步非常重要。它不是一个可有可无的工程细节，而是决定第一阶段生成出来的动作是否还能被第二阶段接住的关键。

### 阶段 1: 人体动作离散化与生成

作者先用 [[SMPL]] 人体参数表示动作，再用 [[VQ-VAE]] 把连续动作序列压成离散 motion tokens。

- **输入**: 初始第一视角图像 $v$，文本指令 $t$
- **中间表示**: 离散动作 token 序列 $z_{1:T}$
- **输出**: 连续人体动作序列
- **主干**: Qwen2.5-VL-3B

作者不是重新发明一个 motion generator，而是把 motion token 当成特殊词表 token，让现成的 VLM 做 next-token prediction。这个选择很现实：
- 直接复用预训练 VLM 的视觉文本对齐能力。
- 不需要再单独训练一个巨型 cross-modal generator。
- motion 序列天然适合自回归生成。

### 阶段 2: 通用动作跟踪

第二阶段的目标是把第一阶段生成的人体动作稳定落到 G1 身上。作者训练了一个 general motion tracker，核心做法包括：
- 使用多时间尺度 future motion target 作为命令输入。
- actor 只看部署时能拿到的紧凑观测。
- critic 看 privileged reference state 和 future targets。
- 采用 asymmetric [[PPO]] 和 [[Curriculum Learning]] 稳定训练。

从论文描述看，actor observation 一共 616 维，其中 motion command 就占 520 维，包含：
- 当前目标帧 1 个
- 短时未来帧 2 个
- 长时未来帧 5 个

这意味着 policy 并不是“盲追当前 pose”，而是在利用未来动作上下文提前准备速度变化、转向和接触事件。

## 关键公式

### 公式 1: [[VQ-VAE|动作离散化总损失]]

$$
\mathcal{L}_{\text{VQVAE}}
= \lambda_{r}\lVert\mathbf{m}-\hat{\mathbf{m}}\rVert_{1}
+ \lambda_{c}\lVert\mathrm{sg}[\mathbf{z}_{e}]-\mathbf{z}_{q}\rVert_{2}^{2}
+ \lambda_{v}\lVert\triangle\mathbf{m}-\triangle\hat{\mathbf{m}}\rVert_{1}
+ \lambda_{rr}\lVert\mathbf{m}_{0:3}-\hat{\mathbf{m}}_{0:3}\rVert_{1}
+ \lambda_{p}\lVert\mathbf{m}_{\mathrm{trans}}-\hat{\mathbf{m}}_{\mathrm{trans}}\rVert_{1}
$$

**含义**: 这个损失不是只管“重建得像不像”，还额外约束了速度平滑、根部旋转和全局平移，目的是让 motion token 不只是压缩动作，而是保留对机器人 tracking 真有用的动力学结构。

**符号说明**:
- $\mathbf{m}$: 原始人体动作序列
- $\hat{\mathbf{m}}$: 解码重建动作
- $\mathbf{z}_e$: 编码器输出的连续 latent
- $\mathbf{z}_q$: 量化后的 codebook 向量
- $\mathrm{sg}[\cdot]$: stop-gradient 操作
- $\triangle(\cdot)$: 时间有限差分，用于速度项

### 公式 2: [[Vision-Language Model|视觉文本到动作 token 的生成目标]]

$$
\mathcal{L}_{\text{gen}}
= - \sum_{i=1}^{T}\log P_{\theta}(z_i \mid \mathbf{v}, \mathbf{t}, z_{<i})
$$

**含义**: 作者把 motion generation 直接改写成 VLM 的自回归 token 预测问题。输入视觉上下文 $\mathbf{v}$ 和文本指令 $\mathbf{t}$，模型逐步生成离散动作 token，再交给 decoder 恢复连续动作。

**符号说明**:
- $\mathbf{v}$: egocentric visual context
- $\mathbf{t}$: language instruction
- $z_i$: 第 $i$ 个动作 token
- $z_{<i}$: 历史动作 token
- $\theta$: 生成模型参数

## 关键图表

### Figure 1: 视角对齐硬件配置

![Figure 1](https://arxiv.org/html/2603.09170v1/1.png)

**说明**: 这张图看似朴素，实际上说明了作者对 sim-to-real / human-to-robot gap 的理解是认真的。人类演示和机器人执行的相机高度被强制对齐，尽量避免第一视角语义对上了、空间几何却对不上的情况。

### Figure 2: ZeroWBC 两阶段架构

![Figure 2](https://arxiv.org/html/2603.09170v1/x1.png)

**说明**: 左半部分是“图像 + 指令 -> motion tokens -> 连续人体动作”，右半部分是“retarget -> RL tracker -> robot action”。这张图一眼就能看出作者在故意避免单阶段端到端系统的耦合灾难。

### Figure 3: G1 真机 scene interaction

![Figure 3](https://arxiv.org/html/2603.09170v1/x2.png)

**说明**: 论文展示了 few-shot 和 zero-shot 的真实任务，包括绕障、坐沙发、坐椅子和导航接近家具。最值得注意的是 zero-shot chair sitting，任务训练集里没有 chair 数据，说明预训练 VLM 的语义先验确实被利用到了。

### Figure 4: Fine-tuning 样本示例

![Figure 4](https://arxiv.org/html/2603.09170v1/x3.png)

**说明**: 这类图对理解第二阶段 domain-specific fine-tuning 很重要。作者不是盲信公开数据，而是承认 Nymeria 之类数据在空间精度和对齐质量上不够，于是补了一套自己的高质量数据。

### Figure 5: Failure case 分析

![Figure 5](https://arxiv.org/html/2603.09170v1/x4.png)

**说明**: 失败案例主要出现在 box moving、sofa sitting 和 ball kicking，说明系统在动态接触、精确位姿和复杂物体交互上仍有明显短板。

### Table 1: 多模态动作生成结果

论文在 [[Nymeria]] 和自采数据上比较不同训练配方。最强配置 `Nymeria + HumanML3D -> Self-collected` 的结果为：

| 评测集 | FID | Top-1 | Top-3 | MM-Dist | Diversity |
|--------|-----|-------|-------|---------|-----------|
| Nymeria | 0.298 | 0.668 | 0.847 | 2.286 | 19.534 |
| Self-Collected | 0.245 | 0.741 | 0.892 | 2.456 | 19.124 |

**说明**: 这说明公开数据预训练加少量高质量自采微调，比直接只用小规模自采数据更有效。作者并不是说“大数据万能”，而是在说“先做跨模态对齐，再做视角和空间精调”。

### Table 2: 与 MotionGPT 的文本生成质量对比

| Method | Bleu@1 | Bleu@4 | CIDEr | RougeL |
|--------|--------|--------|-------|--------|
| MotionGPT | 17.09 | 15.57 | 42.16 | 37.53 |
| **ZeroWBC** | **50.11** | **43.26** | **78.25** | **72.33** |

**说明**: 作者用文本描述和预测动作 token 的一致性指标证明视觉输入不是摆设。即便这个评测本身不能完全代表机器人执行效果，它至少说明第一视角图像确实帮助了动作语义对齐。

### Table 3: 通用动作跟踪结果

| Data | Method | MPJPE | MPJAE | MPJVE |
|------|--------|-------|-------|-------|
| HumanML3D | GMT | 0.5530 | 0.1046 | 0.4882 |
| HumanML3D | w/o Curr. | 0.8957 | 0.1225 | 0.6478 |
| HumanML3D | **Ours** | **0.5360** | **0.0910** | 0.4947 |
| MoCap | GMT | 0.4950 | 0.1014 | 0.4225 |
| MoCap | w/o Curr. | 0.5205 | 0.1139 | 0.5029 |
| MoCap | **Ours** | **0.4472** | **0.0991** | **0.3944** |
| Generation | GMT | 0.6013 | 0.1375 | 0.5112 |
| Generation | w/o Curr. | 0.8633 | 0.1517 | 0.6206 |
| Generation | **Ours** | **0.5671** | **0.1129** | **0.4680** |

**说明**: Curriculum learning 对 tracking 稳定性是有实打实贡献的，特别是 MPJVE 改善说明长时序动作没有那么容易累积抖动。

### Table 4: 真机成功率

| Task | Trials | Success Rate |
|------|--------|--------------|
| Obstacle Avoidance | 50 | 95.0% |
| Ball Kicking | 50 | 78.0% |
| Sofa Sitting | 50 | 84.0% |
| Move Boxes | 50 | 30.0% |

**说明**: 结果非常说明问题。导航和坐下这类宏观 whole-body task 已经能做得不错，但涉及持续物体交互的 move boxes 直接掉到 30%，说明这套系统还远没到精细 manipulation 阶段。

## 实验结果

### 数据集配置

- [[Nymeria]]: 约 300 小时多模态 egocentric 数据，用于第一阶段跨模态对齐
- [[HumanML3D]]: 14,616 条高质量 3D 动作，用于 text-motion 对齐和 tracker 预训练
- 自采数据: 约 5 小时，重点补空间精度、物体交互和视角一致性

### 训练细节

- 生成模型主干: Qwen2.5-VL-3B
- 生成模型训练资源: 32 张 NVIDIA A100
- tracking policy 训练资源: 2 张 NVIDIA RTX 4090，约两周
- tracking learning: asymmetric [[PPO]] + [[Curriculum Learning]]

### 最重要的实验结论

1. 公开大数据预训练 + 小规模高质量自采微调，明显优于只靠小数据从头训。
2. 加视觉模态后，动作 token 语义质量大幅超过 [[MotionGPT]] 这种纯 text-to-motion 基线。
3. 通用 tracker 在 HumanML3D、MoCap 和 generated motion 三种设置下都优于或接近 [[GMT]]，说明第二阶段不是摆设。
4. 真机上最稳的是导航和坐下，最难的是精细持续交互，这和当前 humanoid system 的真实瓶颈高度一致。

## 批判性思考

### 优点

1. **路线比多数 humanoid VLA 更现实**: 它认真处理了数据成本，而不是默认你能一直 teleop 收数据。
2. **两阶段设计清楚**: 视觉语义生成和机器人底层控制分开，工程上更容易调，也更容易定位错误。
3. **真机证据足够**: 有 zero-shot chair sitting 和多种 scene interaction，不是只在 simulation 里自嗨。

### 局限性

1. **推理延迟仍然偏大**: 论文自己承认 VLM latency 至少 500ms，这对动态环境交互是硬伤。
2. **精细 manipulation 还很弱**: move boxes 的 30% 成功率已经很诚实地说明问题。
3. **human-to-robot morphology gap 还没彻底解**: retargeting 能解决一部分，但人体动作并不天然适配机器人接触和力学约束。

### 潜在改进方向

1. 把第一阶段做成更低延迟的 action predictor，而不是重型 VLM 自回归。
2. 引入 tactile / force feedback，补精细交互和 manipulation 短板。
3. 把当前动作级两阶段结构继续扩展到更强的 task-level planning 和 closed-loop correction。

### 可复现性评估

- [ ] 代码完全开源
- [ ] 预训练模型完整可获取
- [x] 训练细节基本可读
- [ ] 数据集完全可获取

## 对当前工作流的启发

- 如果你在做 humanoid teleoperation，这篇最值得借的不是模型细节，而是“人类 egocentric 数据可替代大规模机器人 teleop”的数据观。
- 如果你在做 whole-body tracking，这篇第二阶段说明了未来动作上下文和 curriculum 依然很重要，别被“端到端 VLA 一把梭”洗脑。
- 如果你在做 scene interaction，这篇的强项是自然性和指令跟随，不是精密操作。不要误用它的成功案例去替代 manipulation 能力判断。

## 关联笔记

### 基于

- [[Vision-Language Model]]: 复用预训练视觉文本对齐能力，把动作建模成 token generation
- [[VQ-VAE]]: 把连续人体动作压成离散 codebook token
- [[SMPL]]: 统一人类动作表示

### 对比

- [[WholeBodyVLA]]: 都是视觉到 humanoid 行为，但 ZeroWBC 走的是 human data 路线
- [[GMT]]: 第二阶段通用 motion tracking 的直接比较对象
- [[MotionGPT]]: 纯 text-to-motion baseline，用来证明视觉模态的价值

### 数据相关

- [[Nymeria]]: 大规模 egocentric 多模态预训练数据
- [[HumanML3D]]: 通用 text-motion 数据补足动作语义
- [[MoCap]]: 自采阶段的高质量监督来源

## 速查卡片

> [!summary] ZeroWBC
> - **核心**: 用人类第一视角视频替代大规模 humanoid teleop 数据
> - **方法**: VQ-VAE 动作离散化 + Qwen2.5-VL 动作 token 生成 + RL 通用 tracker
> - **结果**: 真机上 95% 绕障、84% 沙发坐下、78% 踢球，但搬箱子只有 30%
> - **结论**: 很值得跟，但它解决的是 natural scene interaction，不是精细 manipulation

*笔记创建时间: 2026-03-11 22:40*
