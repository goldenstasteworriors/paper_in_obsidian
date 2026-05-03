---
title: "$π_0$: A Vision-Language-Action Flow Model for General Robot Control"
method_name: "Pi0"
authors: [Kevin Black, Noah Brown, Danny Driess, Adnan Esmail, Michael Equi, Chelsea Finn, Niccolo Fusai, Lachy Groom, Karol Hausman, Brian Ichter, Szymon Jakubczak, Tim Jones, Liyiming Ke, Sergey Levine, Adrian Li-Bell, Mohith Mothukuri, Suraj Nair, Karl Pertsch, Lucy Xiaoyang Shi, James Tanner, Quan Vuong, Anna Walling, Haohuan Wang, Ury Zhilinsky]
year: 2024
venue: arXiv
tags: [vision-language-action, robot-foundation-model, flow-matching, cross-embodiment, dexterous-manipulation, imitation-learning]
zotero_collection: 具身智能, 多模态
image_source: local
arxiv_html: https://ar5iv.labs.arxiv.org/html/2410.24164v4
created: 2026-04-28
---

# 论文笔记：$π_0$: A Vision-Language-Action Flow Model for General Robot Control

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Physical Intelligence |
| 日期 | 2024-11-13（Zotero PDF / arXiv v3）；arXiv 最新版本 v4 为 2026-01-08 |
| 项目主页 | https://physicalintelligence.company/blog/pi0 |
| 对比基线 | [[OpenVLA]], [[Octo]], [[ACT]], [[Diffusion Policy]], π0-small |
| 链接 | [arXiv](https://arxiv.org/abs/2410.24164) / [DOI](https://doi.org/10.48550/arXiv.2410.24164) |

---

## 一句话总结

> Pi0 把预训练 VLM、跨形态机器人数据和 Flow Matching 动作专家结合起来，做高频连续动作的通用机器人策略。

---

## 核心贡献

1. **Flow Matching VLA 架构**: 在 [[Vision-Language-Action Model]] 中加入 [[Flow Matching]] 动作专家，直接生成连续 [[Action Chunking|动作块]]，避免把机器人动作粗暴离散成 token。
2. **跨形态大规模预训练**: 使用自有 π dataset、[[Open X-Embodiment]]、DROID、Bridge v2 等数据，在 7 种机器人配置、68 个任务、约 10,000 小时示教上训练 [[Generalist Robot Policy]]。
3. **预训练/后训练 recipe**: 先用多样但噪声更大的数据学习广泛物理能力，再用高质量任务数据 fine-tune，使策略兼具恢复能力和流畅执行能力。
4. **真实机器人复杂任务验证**: 覆盖叠衣服、清桌、装箱、鸡蛋装盒、移动机器人取衣和折衣等长时序灵巧任务，展示比 OpenVLA、Octo、ACT、Diffusion Policy 更强的真实世界表现。

---

## 问题背景

### 要解决的问题

现有 [[Vision-Language-Action Model]] 往往能把语言和视觉语义接到机器人动作上，但在真实灵巧操作里仍有三个硬问题：数据规模不足、跨任务/跨机器人泛化弱、连续高频动作建模不够细。Pi0 的目标是训练一个能直接接受图像、语言指令和本体状态，并输出机器人连续控制动作的 [[Robot Policy]]。

### 现有方法的局限

- [[OpenVLA]] 这类自回归 VLA 倾向于把动作离散化成 token，适合低频或粗粒度动作，但对 20-50Hz 的灵巧控制不够自然。
- [[Octo]] 和 [[Diffusion Policy]] 能建模动作块或扩散动作分布，但缺少大规模预训练 [[Vision-Language Model]] 的语义能力。
- ACT 等窄任务 imitation learning 方法在单任务上强，但跨任务、跨形态和语言泛化有限。

### 本文的动机

作者认为机器人基础模型应该像 LLM/VLM 一样：用大规模、多任务、多形态数据预训练，再用高质量数据后训练。架构上，语义理解交给预训练 [[PaliGemma]] VLM，机器人连续动作分布交给 [[Flow Matching]] action expert。

---

## 方法详解

### 模型架构

Pi0 是一个基于 [[Transformer]] 的 [[Vision-Language-Action Model]]：

- **输入**: 多路 RGB 图像 $I_t^{1:n}$、语言命令 $\ell_t$、本体状态 $q_t$、带噪动作块 $A_t^\tau$。
- **Backbone**: [[PaliGemma]]，由视觉编码器和 Gemma 语言模型组成，提供互联网尺度视觉-语言语义表示。
- **核心模块**: 一个约 300M 参数的 action expert，专门处理机器人状态 token 和动作 token。
- **输出**: 长度 $H=50$ 的连续 [[Action Chunking|动作块]] $A_t=[a_t,\dots,a_{t+H-1}]$。
- **总参数**: 约 3.3B，其中 VLM backbone 约 3B，action expert 约 300M。

### Action Expert

**设计动机**: 图像和语言 token 已被 [[PaliGemma]] 预训练过，但机器人状态和动作 token 分布完全不同。Pi0 使用类似 [[Mixture of Experts]] 的双权重设计：VLM expert 处理图像/语言，action expert 处理 $q_t$ 与 $A_t^\tau$。

**具体实现**:

- 状态 $q_t$ 通过线性层投影到 transformer embedding 空间。
- 每个动作 $a_{t'}^\tau$ 作为一个 action token 输入 action expert。
- action tokens 使用双向注意力，使一个动作块内部的所有动作可以相互 attend。
- 图像/语言 block、状态 block、动作 block 之间使用 blockwise causal attention，以减少对 VLM 预训练分布的破坏，并便于推理时缓存 observation prefix。

### 训练流程

Pi0 的训练分为两段：

- **Pre-training**: 使用自有机器人数据和开源 [[Open X-Embodiment]] 数据，学习跨任务、跨形态的基础能力；语言标签包括任务名和约 2 秒粒度的 segment annotation。
- **Post-training**: 对具体下游任务使用更高质量、更一致的轨迹 fine-tune，使策略执行更流畅、更接近目标风格。

这个 recipe 的关键假设是：低质量但多样的预训练数据提供恢复和泛化能力，高质量后训练数据提供任务效率和策略一致性。

---

## 关键公式

### 公式1: [[Action Chunking|动作块分布]]

$$
p(A_t \mid o_t), \quad A_t = [a_t, a_{t+1}, \dots, a_{t+H-1}], \quad H=50
$$

**含义**: Pi0 不是预测单步动作，而是条件于当前观测 $o_t$ 预测未来 $H$ 步动作块。

**符号说明**:

- $A_t$: 从时刻 $t$ 开始的动作块。
- $a_t$: 单步机器人动作。
- $H$: 动作块长度，本文实验中为 50。
- $o_t=[I_t^1,\dots,I_t^n,\ell_t,q_t]$: 当前观测，包括图像、语言和本体状态。

### 公式2: [[Flow Matching|条件 Flow Matching 损失]]

$$
L_\tau(\theta)=
\mathbb{E}_{p(A_t\mid o_t), q(A_t^\tau\mid A_t)}
\left\|v_\theta(A_t^\tau,o_t)-u(A_t^\tau\mid A_t)\right\|^2
$$

**含义**: 训练网络预测从噪声动作到真实动作的向量场，而不是用交叉熵预测离散动作 token。

**符号说明**:

- $\tau \in [0,1]$: flow matching 时间步。
- $A_t^\tau$: 第 $\tau$ 个 flow 时间步的带噪动作块。
- $v_\theta(A_t^\tau,o_t)$: 模型预测的向量场。
- $u(A_t^\tau\mid A_t)$: 目标 denoising vector field。

### 公式3: [[Flow Matching|线性高斯路径]]

$$
q(A_t^\tau\mid A_t)=\mathcal{N}(\tau A_t,(1-\tau)I)
$$

$$
\epsilon \sim \mathcal{N}(0,I), \quad
A_t^\tau=\tau A_t+(1-\tau)\epsilon, \quad
u(A_t^\tau\mid A_t)=\epsilon-A_t
$$

**含义**: 训练时从高斯噪声和真实动作之间插值得到带噪动作，并监督模型输出把噪声推向真实动作的向量场。

**符号说明**:

- $\epsilon$: 标准高斯噪声。
- $I$: 单位协方差。
- $\tau=0$: 纯噪声侧。
- $\tau=1$: 真实动作侧。

### 公式4: [[Flow Matching|Euler 推理积分]]

$$
A_t^{\tau+\delta}=A_t^\tau+\delta v_\theta(A_t^\tau,o_t)
$$

**含义**: 推理时从 $A_t^0\sim\mathcal{N}(0,I)$ 出发，用 10 步 Euler 积分得到动作块。

**符号说明**:

- $\delta$: 积分步长，本文为 0.1。
- $A_t^0$: 初始噪声动作。
- $A_t^1$: 最终采样出的动作块。

### 公式5: [[Flow Matching|时间步采样分布]]

$$
p(\tau)=\mathrm{Beta}\left(\frac{s-\tau}{s};1.5,1\right), \quad s=0.999
$$

**含义**: 训练时更强调低 $\tau$ 的高噪声区域，因为动作预测中即使在强观测条件下，学习平均动作仍很困难。

**符号说明**:

- $s$: 截断阈值，本文使用 0.999。
- $\mathrm{Beta}(\cdot;1.5,1)$: 偏向低 timestep 的采样分布。

---

## 关键图表

### Figure 1: Teaser / 系统概览

![[assets/Pi0_fig1_teaser_page.png]]

**说明**: Zotero PDF v3 的首页 teaser，展示 Pi0 如何把预训练 VLM、跨形态数据和 flow action expert 组合成通用机器人策略。

### Figure 2: Mobile Laundry / 移动机器人叠衣服

![[assets/Pi0_fig2_mobile_laundry.jpeg]]

**说明**: 移动双臂机器人从烘干机取衣、移动到桌面并折叠衣物，体现长时序、移动操作和柔性物体操作能力。

### Figure 3: Framework / 架构流程

![[assets/Pi0_fig3_framework.png]]

**说明**: 输入图像、语言和机器人状态后，VLM backbone 处理视觉语言，action expert 用 [[Flow Matching]] 输出动作块。

### Figure 4: Dataset Mixture / 数据混合

![[assets/Pi0_fig4_dataset.png]]

**说明**: 预训练 mixture 包含自有 π dataset 和 OXE Magic Soup；自有双臂数据在 timestep 数量上占比很大，但训练权重做了重采样。

### Figure 5: Robot Embodiments / 机器人平台

![[assets/Pi0_fig5_robots.png]]

**说明**: 覆盖 UR5e、Franka、ALOHA/Trossen、ARX/AgileX、移动双臂平台等多种 [[Cross-Embodiment]] 形态。

### Figure 6: Zero-shot Tasks / 基座模型评测任务

![[assets/Pi0_fig6_zeroshot_tasks.png]]

**说明**: 包括 shirt folding、bussing easy/hard、grocery bagging 和 toast out of toaster，用于评估预训练后无需后训练的能力。

### Figure 7: Zero-shot Results / 基座模型结果

![[assets/Pi0_fig7_zeroshot_results.png]]

**说明**: Pi0 在全部 zero-shot 任务上显著优于 OpenVLA、Octo 和 π0-small；OpenVLA 的动作离散化和缺少动作块是主要短板。

### Figure 8: Language Tasks / 语言任务

![[assets/Pi0_fig8_language_tasks.png]]

**说明**: 评估清桌、摆桌和购物袋打包等需要中间语言指令的任务。

### Figure 9: Language Results / 语言遵循结果

![[assets/Pi0_fig9_language_results.png]]

**说明**: Pi0 的语言跟随率明显高于 π0-small；human intermediate command 和 high-level VLM command 都能提高复杂任务表现。

### Figure 10: Fine-tuning Tasks / 新技能任务

![[assets/Pi0_fig10_finetune_tasks.png]]

**说明**: 包括叠碗、叠毛巾、把饭盒放入微波炉、换纸巾卷、Franka 抽屉收纳等不同难度的新任务。

### Figure 11: Fine-tuning Results / 数据量消融

![[assets/Pi0_fig11_finetune_results.png]]

**说明**: Pi0 在多数任务上优于从头训练和 prior baselines；预训练对接近预训练分布的任务帮助尤其大。

### Figure 12: Complex Tasks / 复杂长时序任务

![[assets/Pi0_fig12_complex_tasks.png]]

**说明**: 展示叠衣服、移动叠衣、真实午餐桌清理、组装纸箱、鸡蛋装盒、食物打包等长时序任务。

### Figure 13: Complex Results / 后训练复杂任务结果

![[assets/Pi0_fig13_complex_results.png]]

**说明**: Fine-tuned Pi0 在多数复杂任务上超过 scratch 和 zero-shot ablation，说明预训练与后训练都很关键。

### Figure 14: Flow Timestep Sampling / 时间步采样

![[assets/Pi0_fig14_timestep_sampling.png]]

**说明**: 采样分布偏向高噪声低 timestep 区域，并截断接近 1 的 timestep。

### Table 1: 推理耗时

| 模块 | 耗时 |
|------|------|
| image encoders | 14 ms |
| observation forward pass | 32 ms |
| x10 action forward pass (flow) | 27 ms |
| network latency (off-board) | 13 ms |
| total on-board inference | 73 ms |
| total off-board inference | 86 ms |

**说明**: 在 RTX 4090 上，3 相机输入时总推理耗时约 73ms；移动机器人 off-board 推理加 Wi-Fi 延迟约 86ms。由于一次输出动作块，UR5e/Franka 每 0.8s 推理一次，50Hz 机器人每 0.5s 推理一次。

---

## 实验

### 数据集

| 数据集 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| π dataset | 903M timesteps；7 种机器人配置；68 个任务 | 大量自有真实机器人灵巧操作数据，双臂数据占比较大 | 预训练主数据 |
| OXE Magic Soup | OXE 子集 | 来自多机器人、多场景的开源数据 | 预训练补充 |
| Bridge v2 / DROID | 开源真实机器人数据 | 物体和环境多样，控制频率多为 2-10Hz | 预训练补充 |
| Task-specific post-training data | 简单任务约 5 小时，复杂任务 100+ 小时 | 更高质量、更一致的轨迹 | 后训练 |

### 实现细节

- **Backbone**: [[PaliGemma]]，约 3B 参数。
- **Action expert**: Gemma-style transformer expert，width 1024，MLP dim 4096，约 300M 参数。
- **Action horizon**: $H=50$。
- **Flow integration**: 10 steps，$\delta=0.1$。
- **最大动作/状态维度**: 18 维；低维机器人 zero padding。
- **摄像头输入**: 每个机器人 2 或 3 路 RGB 图像，缺失图像 slot mask。
- **训练步数**: 主模型 700k steps；compute parity ablation 160k steps。

### 主要结果

- **Zero-shot**: Pi0 在 shirt folding 和 bussing easy 上接近满分，在其他任务上也明显领先。
- **语言遵循**: VLM 初始化带来明显语言理解优势，π0-small 即使拿到 human intermediate commands 也不能稳定受益。
- **新技能 fine-tuning**: Pi0 在多数任务上比 OpenVLA、Octo、ACT、Diffusion Policy 更强；在和预训练任务相似的新任务上，预训练收益最大。
- **复杂任务**: 对 folding laundry、table bussing、mobile laundry 等长任务，fine-tuned Pi0 明显优于 scratch 和 zero-shot 版本。

---

## 批判性思考

### 优点

1. **架构选择合理**: 用 [[Flow Matching]] 建模连续动作，比离散 action token 更适合高频灵巧操作。
2. **数据 recipe 有说服力**: 多样预训练数据负责泛化和恢复，高质量后训练数据负责流畅执行，解释了为什么只用高质量数据或只用杂数据都不够。
3. **真实机器人实验强**: 不是只在 LIBERO 这类模拟 benchmark 上验证，而是在多平台、多长时序真实任务上评估。
4. **跨形态处理简单直接**: 统一到最大动作维度、zero padding 和 mask，工程上可扩展。

### 局限性

1. **数据和训练成本极高**: 10,000 小时真实机器人数据和 3.3B 模型不是一般实验室可以复现的规模。
2. **开放性不足**: 论文展示了大量真实实验，但数据、完整训练 recipe、模型权重的可获取性有限。
3. **高层语义规划仍外接**: Table bussing 等任务仍需要 high-level VLM policy 或人类中间指令，Pi0 本身更像强动作执行器加语言条件策略。
4. **跨形态只是共享模型，不等于零成本迁移**: 对很多复杂任务仍需要 task-specific post-training。

### 潜在改进方向

1. 用更高效的 action representation 或蒸馏降低 3.3B VLA 的部署成本。
2. 将 high-level planning 与 low-level control 更紧密联合训练，减少外部 VLM policy 依赖。
3. 增加 online correction / RL fine-tuning，使后训练不只依赖离线示教。
4. 研究更细粒度的 embodiment adapter，避免简单 zero padding 在大规模跨形态中浪费容量。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [ ] 训练细节完整
- [ ] 数据集可获取

整体判断：思想和实验强，但复现门槛非常高；更适合作为 VLA scaling recipe 和架构设计参考，而不是可直接复刻的开源 baseline。

---

## 关联笔记

- [[Vision-Language-Action Model]]
- [[Flow Matching]]
- [[Action Chunking]]
- [[Cross-Embodiment]]
- [[Generalist Robot Policy]]
- [[PaliGemma]]
- [[OpenVLA]]
- [[Octo]]
- [[Diffusion Policy]]
- [[ACT]]
- [[Open X-Embodiment]]
