---
title: "OpenVLA: An Open-Source Vision-Language-Action Model"
method_name: "OpenVLA"
authors: [Moo Jin Kim, Karl Pertsch, Siddharth Karamcheti, Ted Xiao, Ashwin Balakrishna, Suraj Nair, Rafael Rafailov, Ethan Foster, Grace Lam, Pannag Sanketi, Quan Vuong, Thomas Kollar, Benjamin Burchfiel, Russ Tedrake, Dorsa Sadigh, Sergey Levine, Percy Liang, Chelsea Finn]
year: 2025
venue: CoRL / PMLR
tags: [vla, robot-learning, imitation-learning, open-source, multi-robot, efficient-finetuning, action-tokenization]
zotero_collection: 多模态
image_source: local
arxiv_html: https://arxiv.org/html/2406.09246
created: 2026-04-28
---

# 论文笔记：OpenVLA: An Open-Source Vision-Language-Action Model

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Stanford University, UC Berkeley, Toyota Research Institute, Google DeepMind, Physical Intelligence, MIT |
| 日期 | arXiv v3: 2024-09-05；CoRL 2024 / PMLR 2025 |
| 项目主页 | https://openvla.github.io |
| 对比基线 | [[RT-X]]、[[RT-2]]、[[RT-1]]、[[Octo]]、[[Diffusion Policy]] |
| 链接 | [PMLR](https://proceedings.mlr.press/v270/kim25c.html) / [arXiv](https://arxiv.org/abs/2406.09246) / [Code](https://github.com/openvla/openvla) / [Model](https://huggingface.co/openvla/openvla-7b) |

---

## 一句话总结

> [[OpenVLA]] 把开源 [[Vision-Language Model]] 微调成 7B [[Vision-Language-Action Model]]，在 970k 真实机器人轨迹上训练，并系统验证了多机器人泛化、微调和量化部署。

---

## 核心贡献

1. **开源通用 VLA**: 发布 7B 参数 [[Vision-Language-Action Model]]、权重、训练代码和微调流程，填补 RT-2/RT-2-X 这类闭源 VLA 的可复现实验空白。
2. **更强的真机泛化**: 在 WidowX 和 Google Robot 共 29 个任务上，OpenVLA 平均成功率相比闭源 55B [[RT-X|RT-2-X]] 高 16.5 个百分点，同时参数量约少 7 倍。
3. **微调与部署经验**: 系统比较 full fine-tuning、last-layer、frozen vision、sandwich、[[Low-Rank Adaptation|LoRA]]，并验证 4-bit [[Quantization|量化]] 能把推理显存降到约 7GB 且基本不降性能。

---

## 问题背景

### 要解决的问题

机器人策略很难泛化到训练数据外的物体、场景、语言指令和机器人本体。[[Vision-Language-Action Model]] 的思路是借用互联网级 [[Vision-Language Model]] 的视觉语言先验，再用机器人轨迹把输出空间改造成动作，从而让策略具备更强的对象识别、语言 grounding 和跨场景泛化能力。

### 现有方法的局限

之前强 VLA 代表如 [[RT-2]] / [[RT-X|RT-2-X]] 主要是闭源模型，研究者无法系统复现实验、改变数据配比或研究架构细节。另一方面，已有工作大多强调 out-of-the-box 评测，缺少“拿到一个新机器人/新任务后如何高效微调”的实践答案。

### 本文的动机

作者认为 VLA 要成为机器人领域的基础模型，必须像开源 LLM 一样提供权重、代码、训练 recipe 和微调入口。OpenVLA 的核心目标不是提出复杂新模块，而是给社区一个可复现、可扩展、能真机落地的强基线。

---

## 方法详解

### 模型架构

[[OpenVLA]] 采用 autoregressive [[Vision-Language-Action Model]] 架构，把动作预测转成语言模型的 next-token prediction：

- **输入**: 单帧 RGB 图像观测 $o_t$ + 语言指令 $l$。
- **视觉编码器**: 拼接 [[DINOv2]] 的空间细节特征和 [[SigLIP]] 的语义特征。
- **投影层**: 用 MLP projector 把视觉 patch token 映射到 [[Llama 2]] embedding 空间。
- **语言主干**: [[Llama 2]] 7B，来自 Prismatic VLM backbone。
- **动作输出**: 7D 末端执行器控制动作，包括 $\Delta x$、$\Delta \theta$ 和 gripper。
- **训练目标**: 只在动作 token 上计算 [[Cross-Entropy Loss]]。

### 动作 token 化

OpenVLA 沿用 [[RT-2]] 的“动作当语言 token”路线，但做了数据分位数裁剪：

- 每个连续动作维度独立离散成 256 个 bin。
- 离散范围取训练数据中该维度的 1% 到 99% 分位数，而不是 min-max，以免异常动作拉大 bin 宽。
- [[Llama 2]] tokenizer 原生 special tokens 不够 256 个，作者直接覆盖 Llama vocabulary 中最少使用的最后 256 个 token 作为动作 token。
- 推理时模型逐 token 生成动作 token，再由 action de-tokenizer 转回连续 7D 控制量。

### 训练数据

OpenVLA 使用 [[Open X-Embodiment]] 中的 970k 真实机器人 episode，目标是覆盖多机器人、多场景、多任务：

- 只保留至少有一个第三人称相机、且使用 single-arm end-effector control 的 manipulation 数据集。
- 数据配比大体沿用 [[Octo]] 的 mixture 权重，强调任务/场景/本体多样性。
- 作者尝试加入 [[DROID]]，但发现 action token accuracy 学得慢，最终训练最后三分之一阶段移除 DROID 并把权重重新分配。

### 关键训练选择

- **Backbone**: Prismatic 优于 LLaVA 和 IDEFICS-1，作者归因于 SigLIP-DINOv2 双视觉编码器带来的空间和语义兼顾。
- **图像分辨率**: 224x224 与 384x384 真机表现接近，但 384x384 训练耗时约 3 倍，因此最终用 224x224。
- **视觉编码器是否训练**: 与常规 VLM 训练不同，VLA 中 fine-tune vision encoder 很关键，因为机器人控制需要细粒度空间信息。
- **训练 epoch**: 最终训练跑 27 个 epoch，远多于常见 LLM/VLM 预训练的一两个 epoch。
- **训练资源**: 64 张 A100 训练 14 天，约 21,500 A100-hours，batch size 2048，固定学习率 $2\times10^{-5}$。

---

## 关键公式

论文主体没有编号公式，但方法中有三个核心数学定义。

### 公式1: [[Action Tokenization|分位数动作离散化]]

$$
\tilde{a}_t^i = \mathrm{clip}(a_t^i, q_{0.01}^i, q_{0.99}^i),\quad
z_t^i = \mathrm{bin}_{256}(\tilde{a}_t^i),\quad z_t^i \in \{0,\ldots,255\}
$$

**含义**: 第 $i$ 个连续动作维度先裁剪到训练数据 1%-99% 分位范围，再离散成 256 个 token。

**符号说明**:
- $a_t^i$: 时间 $t$ 的第 $i$ 个连续动作维度。
- $q_{0.01}^i, q_{0.99}^i$: 该动作维度在训练集中的 1% 和 99% 分位数。
- $z_t^i$: 离散化后的动作 token。

### 公式2: [[Vision-Language-Action Model|动作序列概率]]

$$
p_\theta(z_t^{1:N}\mid o_t,l)=\prod_{i=1}^{N}p_\theta(z_t^i\mid o_t,l,z_t^{<i})
$$

**含义**: OpenVLA 用自回归语言模型按顺序生成一个时间步的 $N$ 个动作 token。

**符号说明**:
- $\theta$: OpenVLA 模型参数。
- $o_t$: 当前图像观测。
- $l$: 语言任务指令。
- $N$: 动作维度数量，本文机器人控制主要为 7D。

### 公式3: [[Cross-Entropy Loss|动作 token 交叉熵]]

$$
\mathcal{L}_{action}=-\sum_{t}\sum_{i=1}^{N}\log p_\theta(z_t^i\mid o_t,l,z_t^{<i})
$$

**含义**: 训练时只在动作 token 位置上计算 next-token prediction 的交叉熵损失。

**符号说明**:
- $\mathcal{L}_{action}$: 动作建模损失。
- $z_t^{<i}$: 同一动作序列中第 $i$ 个 token 之前的已生成 token。
- $p_\theta$: 模型预测的 token 概率分布。

---

## 关键图表

> 下列图片是从本地 Zotero PDF 渲染的页面图，覆盖论文 Figure 1-11 与 Table 1-12。完整原始 PDF: `/home/ykj/Zotero/storage/GSY5W4W9/OpenVLA An Open-Source Vision-Language-Action Model.pdf`。

### Figure 1: OpenVLA 总览

![[OpenVLA_page1-01.png]]

**说明**: OpenVLA 从大规模真实机器人数据训练 VLA，输入图像和语言，输出闭环机器人控制动作；论文强调数据、权重和代码全部开源。

### Figure 2: 模型架构

![[OpenVLA_page4-04.png]]

**说明**: 图像经 DINOv2+SigLIP 编码，MLP 投影到 Llama 2 embedding 空间，语言指令经 Llama tokenizer，最终生成 7D action token 并 de-tokenize 为控制量。

### Figure 3 / Figure 4: 直接泛化评测

![[OpenVLA_page7-07.png]]

![[OpenVLA_page8-08.png]]

**说明**: Figure 3 展示 BridgeData V2 WidowX 的 visual/motion/physical/semantic/language grounding 任务；Figure 4 展示 Google Robot 的 seen 和 OOD 任务。OpenVLA 在 BridgeData V2 上显著超过 RT-2-X，在 Google Robot 上与 RT-2-X 接近。

### Figure 5: 新机器人任务微调

![[OpenVLA_page9-09.png]]

**说明**: Diffusion Policy 在窄的单指令任务上很强，但 OpenVLA/Octo 在多指令、多物体、语言 grounding 任务上更稳。OpenVLA 是唯一在所有真实微调任务上至少达到 50% 成功率的方法。

### Figure 6 / Table 1 / Table 2: 微调与推理效率

![[OpenVLA_page10-10.png]]

**说明**: Table 1 说明 LoRA rank 32/64 基本匹配 full fine-tuning，且只训练约 1.4% 参数；Table 2 说明 int4 推理成功率约 71.9%，接近 bfloat16 的 71.3%，显存从 16.8GB 降至 7.0GB。

### Table 3: OpenX 训练数据配比

![[OpenVLA_page21-21.png]]

**说明**: 训练 mixture 主要继承 Octo，并加入若干后续 OpenX 数据集；DROID 在训练末期被移除，原因是动作 token 学习进展慢。

### Figure 7 / Figure 8 / Table 4 / Table 5: BridgeData V2 细节

![[OpenVLA_page22-22.png]]

![[OpenVLA_page25-25.png]]

![[OpenVLA_page26-26.png]]

**说明**: Figure 7 列出 17 个 WidowX 评测任务；Figure 8 对比原始 BridgeData V2 sink environment。Table 4 中 OpenVLA 平均成功率为 70.6%，RT-2-X 为 50.6%，Octo 为 20.0%，RT-1-X 为 18.5%。Table 5 展示量化实验明细，int4 在多任务下与 bfloat16 接近。

### Figure 9 / Table 6: Google Robot 评测

![[OpenVLA_page27-27.png]]

**说明**: Google Robot 上 OpenVLA 与 RT-2-X 总体接近，二者显著优于 RT-1-X 和 Octo；RT-2-X 在语义泛化上更强，可能来自更大规模互联网预训练与 web+robot co-fine-tuning。

### Figure 10 / Figure 11 / Table 7 / Table 8: Franka 微调

![[OpenVLA_page29-29.png]]

![[OpenVLA_page30-30.png]]

![[OpenVLA_page31-31.png]]

**说明**: Franka-Tabletop 和 Franka-DROID 评测覆盖窄任务、多指令任务和视觉鲁棒性任务。Table 7 显示 OpenVLA 平均表现最高；Table 8 给出参数高效微调细节，LoRA 是性能与显存的最佳折中。

### Table 9 / Table 10 / Table 11 / Table 12: 消融与仿真补充

![[OpenVLA_page32-32.png]]

![[OpenVLA_page33-33.png]]

![[OpenVLA_page34-34.png]]

![[OpenVLA_page35-35.png]]

![[OpenVLA_page36-36.png]]

**说明**: Table 9 验证 OpenX 预训练、双视觉编码器、DINOv2 与 SigLIP 融合的重要性；Table 10 说明 fine-tune vision encoder 明显优于冻结；Table 11 用 blocking control 排除了不同量化速度的干扰；Table 12 显示 OpenVLA 在 LIBERO 仿真微调中平均成功率和平均排名也最高。

---

## 实验

### 数据集

| 数据集 / 设置 | 规模 | 特点 | 用途 |
|---|---:|---|---|
| [[Open X-Embodiment]] subset | 970k episodes | 多机器人、多任务、多场景真实操作数据 | OpenVLA 预训练 |
| BridgeData V2 WidowX | 17 tasks, 170 rollouts / method | visual/motion/physical/semantic/language grounding 泛化 | out-of-the-box 评测 |
| Google Robot | 12 tasks, 60 rollouts / method | RT-1/RT-2 系列常用移动操作平台 | out-of-the-box 评测 |
| Franka-Tabletop | 10-150 demos / task | 7DoF Franka，单指令与多指令任务 | 数据高效微调 |
| Franka-DROID | DROID 风格 Franka setup | wipe table 等视觉鲁棒性任务 | 数据高效微调 |
| LIBERO | 仿真 benchmark | 多 task suite | 补充微调评测 |

### 实现细节

- **Backbone**: Prismatic-7B VLM，视觉侧为 DINOv2 + SigLIP，语言侧为 Llama 2 7B。
- **输入分辨率**: 224x224。
- **动作表示**: 每维 256-bin [[Action Tokenization]]，范围为 1%-99% 分位数。
- **优化**: 固定学习率 $2\times10^{-5}$，batch size 2048。
- **预训练硬件**: 64 A100，14 天，约 21,500 A100-hours。
- **推理**: bfloat16 约需 15-16.8GB 显存；RTX 4090 约 6Hz；int4 可降至约 7GB。

### 主要结果

| 评测 | 关键数字 | 结论 |
|---|---:|---|
| BridgeData V2 | OpenVLA 70.6% vs RT-2-X 50.6% | OpenVLA 在多数泛化类型上最强 |
| Google Robot | OpenVLA 与 RT-2-X 均约 82.9% 总体成功率 | 闭源大模型在语义泛化仍有优势 |
| Franka 微调 | OpenVLA 平均最高，且所有任务 >=50% | 多指令/多物体任务中预训练收益明显 |
| LoRA | r=32/r=64 均 68.2%，Full FT 69.7% | LoRA 接近 full FT，只训练少量参数 |
| int4 量化 | 71.9% vs bfloat16 71.3% | 4-bit 推理显著降显存且基本不降成功率 |

---

## 批判性思考

### 优点

1. **基线价值很高**: 论文最大的意义是把强 VLA 从闭源黑箱变成可复现系统，后续很多 VLA 工作都可以真正修改架构、数据和训练策略。
2. **实验问题设计完整**: 不只做 out-of-the-box，还覆盖了新机器人微调、LoRA、量化、vision encoder 是否训练、OpenX mixture 等实际使用问题。
3. **工程结论直接可用**: 224 分辨率、fine-tune vision encoder、LoRA rank 32、int4 推理等结论对复现实验和部署都有指导意义。

### 局限性

1. **动作生成仍偏低频和单步**: OpenVLA 每次输出单步相对动作，没有 [[Action Chunking]] 和 temporal smoothing，因此在窄而精细的 dexterous 任务上不如 [[Diffusion Policy]] 平滑。
2. **训练成本仍然很高**: 虽然推理/微调可降成本，但从头预训练需要 64 A100 两周，普通实验室难以复现完整训练。
3. **语义泛化仍弱于闭源 RT-2-X**: RT-2-X 更大并保留 web co-training，OpenVLA 只用机器人数据 fine-tune 后可能损失部分互联网语义知识。
4. **动作空间假设较窄**: 主要面向单臂末端执行器 7D 控制，还没有解决多模态传感器、双臂、灵巧手、移动底盘等更异构动作空间。

### 潜在改进方向

1. 在 OpenVLA 上加入 [[Action Chunking]]、temporal ensemble 或 diffusion/action head，改善低频控制和轨迹平滑性。
2. 研究 web+robot co-training 或 continual pretraining，减少机器人微调对语义知识的遗忘。
3. 设计更好的 [[Action Tokenization]]，例如 vector-quantized tokenizer、flow/diffusion action decoder 或 embodiment-aware action representation。
4. 扩展到多相机、proprioception、力觉、双臂和灵巧手，检验 VLA 在更复杂本体上的可扩展性。

### 可复现性评估

- [x] 代码开源
- [x] 预训练模型开源
- [x] 训练/微调细节较完整
- [x] 数据来源可获取，基于 Open X-Embodiment
- [ ] 完整预训练成本较高，难以普通复现

---

## 关联笔记

- [[Vision-Language-Action Model]]
- [[Vision-Language Model]]
- [[Action Tokenization]]
- [[Open X-Embodiment]]
- [[RT-X]]
- [[RT-2]]
- [[Octo]]
- [[Diffusion Policy]]
- [[Low-Rank Adaptation]]
- [[Quantization]]
