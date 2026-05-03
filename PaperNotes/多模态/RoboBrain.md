---
title: "RoboBrain: A Unified Brain Model for Robotic Manipulation from Abstract to Concrete"
method_name: "RoboBrain"
authors: [Yuheng Ji, Huajie Tan, Jiayu Shi, Xiaoshuai Hao, Yuan Zhang, Hengyuan Zhang, Pengwei Wang, Mengdi Zhao, Yao Mu, Pengju An, Xinda Xue, Qinghang Su, Huaihai Lyu, Xiaolong Zheng, Jiaming Liu, Zhongyuan Wang, Shanghang Zhang]
year: 2025
venue: CVPR 2025 / arXiv
tags: [robotic-manipulation, multimodal-large-language-model, affordance-perception, trajectory-prediction, task-planning, robotics-dataset]
zotero_collection: 多模态
image_source: local
arxiv_html: https://ar5iv.labs.arxiv.org/html/2502.21257v2
created: 2026-05-03
---

# 论文笔记：RoboBrain: A Unified Brain Model for Robotic Manipulation from Abstract to Concrete

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Peking University, BAAI, CAS, HKU 等 |
| 日期 | 2025-03-25 |
| 项目主页 | [RoboBrain](https://superrobobrain.github.io) |
| Zotero | `9MT9AP7E` |
| 链接 | [arXiv](https://arxiv.org/abs/2502.21257) / [HTML](https://ar5iv.labs.arxiv.org/html/2502.21257v2) |

---

## 一句话总结

> RoboBrain 用 [[ShareRobot]] 和多阶段训练，把 [[Multimodal Large Language Model]] 扩展成能做任务规划、[[Affordance]] 感知和 2D 轨迹预测的机器人“大脑”。

---

## 核心贡献

1. **统一机器人脑模型**: 提出 [[RoboBrain]]，把抽象语言指令、视觉观测、子任务规划、可交互区域和轨迹点预测放进同一个 [[Multimodal Large Language Model]] 框架。
2. **ShareRobot 数据集**: 从 [[Open X-Embodiment]] 中筛选高质量操作数据，标注 task planning、object affordance、end-effector trajectory，形成大规模异构训练/评测数据。
3. **多阶段训练策略**: 先做通用 [[LLaVA]] OneVision 训练，再混入机器人数据，最后用 [[LoRA]] 分别训练 A-LoRA 与 T-LoRA 来强化 [[Affordance]] 与 [[Trajectory Prediction]]。
4. **机器人 benchmark 提升明显**: 在 [[RoboVQA]]、[[OpenEQA]]、ShareRobot Eval、affordance AP 和 trajectory metrics 上整体优于对比模型。

---

## 问题背景

### 要解决的问题

现有 [[Multimodal Large Language Model]] 在通用图文理解上很强，但直接用于长程机器人操作时缺少三类能力：

- **Planning Capability**: 把高层任务拆成可执行的低层子任务。
- **Affordance Perception**: 根据当前视觉状态和任务意图定位对象的可交互区域。
- **Trajectory Prediction**: 从当前末端执行器位置预测一段可执行的 2D 运动轨迹。

### 现有方法的局限

[[LLaVA]]、Qwen2-VL、GPT-4V 等模型可以做视觉问答和描述，但通常没有用细粒度机器人执行数据训练；RT-H、RoboMamba 等机器人模型可以输出动作或规划文本，但对“能抓哪里”和“怎么移动过去”的显式建模仍不足。

### 本文的动机

作者认为机器人操作需要从“抽象语义”落到“具体动作表达”。因此论文先构造 [[ShareRobot]]，再训练 [[RoboBrain]]，让模型同时学习：

- 何时执行下一个 atomic task；
- 哪个区域是当前任务的 affordance；
- 末端执行器应该走过哪些 2D waypoint。

---

## 方法详解

### 模型架构

[[RoboBrain]] 基于 [[LLaVA]] 风格的 [[Vision-Language Model]]：

- **输入**: 图像、多个图像或视频 $X_v$，以及语言指令 $X_t$。
- **Vision Encoder**: [[SigLIP]]，把视觉输入编码为视觉特征 $Z_v$。
- **Projector**: 2-layer MLP，把 $Z_v$ 映射到 LLM 语义空间，得到视觉 token $H_v$。
- **LLM**: [[Qwen2.5]]-7B-Instruct，自回归生成规划文本、affordance 坐标或 trajectory 坐标。
- **Planning 主模型**: full model fine-tuning。
- **Affordance 分支**: A-LoRA，用于输出 bounding box。
- **Trajectory 分支**: T-LoRA，用于输出 2D waypoints。

### ShareRobot 数据集

[[ShareRobot]] 的构造流程：

1. 从 [[Open X-Embodiment]] 中按图像分辨率、描述准确性、成功状态、视频长度、无遮挡目标、轨迹清晰度筛选 demonstrations。
2. 每个操作视频抽取 30 帧，用 Gemini 将 high-level description 分解成 low-level atomic tasks。
3. 三位标注者审查和修正任务分解。
4. 将 planning 数据转成 [[RoboVQA]] 风格的 10 类 QA 模板。
5. 对 affordance 标注接触区域 bounding box，对 trajectory 标注/计算末端执行器 2D 轨迹点。

主要规模：

| 数据项 | 数量 |
|--------|------|
| 筛选后 instances | 51,403 |
| planning QA pairs | 约 1,028,060 |
| planning train/test | 1,000,000 / 2,050 |
| affordance train/test | 8,000 / 511 |
| trajectory train/test | 8,000 / 511 |
| 来源数据集 | 23 |
| 场景 | 102 |
| embodiment | 12 |
| atomic action 类型 | 132，论文图中统计 top 20 |

### 训练流程

RoboBrain 使用两阶段、五个主要 stage：

| Stage | 目标 | 数据 | 可训练参数 |
|-------|------|------|------------|
| Stage 1 | 视觉-语言对齐 | LCS-558K | Projector, 17M |
| Stage 1.5 | 通用图文知识 | 4M image-text | Full model, 8B |
| Stage 2 Single-Image | 视觉指令跟随 | 3.2M image data | Full model, 8B |
| Stage 2 OneVision | 高分辨率/视频理解 | 1.6M image & video | Full model, 8B |
| Stage 3 | 机器人知识学习 | 3M robotic data | Full model, 8B |
| Stage 4 A-LoRA | affordance skill | 10K affordance data | A-LoRA, 28M |
| Stage 4 T-LoRA | trajectory skill | 400K trajectory data | T-LoRA, 28M |

训练策略的关键点：

- Stage 3 中混合约 1.3M robotic data 和约 1.7M 通用 image-text 数据，缓解 catastrophic forgetting。
- robotic data 来源包括 [[RoboVQA]]-800K、ScanView、MMScan、3RScan、ScanQA、SQA3D 和 ShareRobot-200K。
- Stage 4 不全量训练模型，而是使用 [[LoRA]] 低秩适配器学习具体 affordance/trajectory 输出格式。
- 实验使用 Zero3 分布式训练，每台服务器 8xA800。

---

## 关键公式

### 公式1: [[Vision-Language Model|视觉特征编码]]

$$
Z_v = g(X_v)
$$

**含义**: 视觉编码器 $g(\cdot)$ 将图像或视频输入 $X_v$ 编码为视觉特征。

**符号说明**:
- $X_v$: 视觉输入，可以是单图、多图或视频。
- $g(\cdot)$: ViT/SigLIP 视觉编码器。
- $Z_v$: 视觉特征。

### 公式2: [[Vision-Language Model|视觉 token 映射]]

$$
H_v = h(Z_v)
$$

**含义**: projector $h(\cdot)$ 把视觉特征映射到 LLM 的 token 空间。

**符号说明**:
- $h(\cdot)$: 2-layer MLP projector。
- $H_v$: 输入给 LLM 的视觉 token 序列。

### 公式3: [[Affordance|Affordance 表示]]

$$
O_i = \{A_i^0, A_i^1, \ldots, A_i^N\}
$$

$$
A_i^j = \{l(x), l(y), r(x), r(y)\}
$$

**含义**: 图像中的第 $i$ 个物体可以有多个 affordance，每个 affordance 用 bounding box 表示。

**符号说明**:
- $O_i$: 第 $i$ 个物体及其 affordance 集合。
- $A_i^j$: 第 $i$ 个物体的第 $j$ 个 affordance。
- $\{l(x), l(y)\}$: bounding box 左上角坐标。
- $\{r(x), r(y)\}$: bounding box 右下角坐标。

### 公式4: [[Trajectory Prediction|轨迹 waypoint 表示]]

$$
P_{t:N} = \{(x_i, y_i) \mid i = t, t+1, \ldots, N\}
$$

**含义**: 从当前时刻 $t$ 到 episode 结束 $N$ 的末端执行器 2D 轨迹。

**符号说明**:
- $P_{t:N}$: 预测轨迹 waypoint 序列。
- $(x_i, y_i)$: 第 $i$ 个 2D waypoint。
- $N$: episode 总时间步。

---

## 关键图表

### Figure 1: Overview / 系统概览

![[assets/RoboBrain_fig1_overview.png]]

**说明**: RoboBrain 的三种核心能力是 planning、affordance perception 和 trajectory prediction；图下半部分展示训练数据组成和 ShareRobot VQA 示例。

### Figure 2: ShareRobot generation / 数据生成流程

![[assets/RoboBrain_fig2_sharerobot_generation.png]]

**说明**: 展示数据筛选、planning 标注、affordance 标注、trajectory 标注，以及 10 类 RoboVQA 风格问题模板。

### Figure 3: ShareRobot diversity / 数据多样性

![[assets/RoboBrain_fig3_sharerobot_diversity.png]]

**说明**: ShareRobot 涉及 23 个原始数据集、12 种 embodiment 和大量 atomic actions；高频动作包括 pick、move、reach、lift、place。

### Figure 4: RoboBrain pipeline / 模型流程

![[assets/RoboBrain_fig4_pipeline.png]]

**说明**: 图像/多图/视频输入先训练基础机器人脑，再用 A-LoRA 和 T-LoRA 分别发展 affordance 与 trajectory 技能；实际执行时先生成详细计划，再拆成子任务。

### Figure 5: Benchmark performance / 规划 benchmark

![[assets/RoboBrain_fig5_benchmarks.png]]

**说明**: RoboBrain 在 OpenEQA、ShareRobot、RoboVQA 上超过 GPT-4V、Claude3、LLaVA、Qwen2-VL、RoboMamba 等 baseline。

### Figure 6: Multi-round planning and concrete outputs

![[assets/RoboBrain_fig6_visualization.png]]

**说明**: 示例展示 RoboBrain 能基于实时图像反馈进行多轮规划，并为每一步输出 affordance 和 trajectory。

### Figure 7: Training data distribution

![[assets/RoboBrain_fig7_training_data_distribution.png]]

**说明**: 补充材料展示 Stage 3/robotic training 数据来源比例；机器人数据与通用数据混合是保持通用能力和增强机器人能力的关键。

### Figure 8: Additional planning cases

![[assets/RoboBrain_fig8_planning_cases.png]]

**说明**: 额外 planning 可视化包含成功样例和失败样例。失败点包括物体识别错误、关键步骤遗漏、动作决策偏差。

### Figure 9: Additional affordance cases

![[assets/RoboBrain_fig9_affordance_cases.png]]

**说明**: 展示多种任务指令下的 affordance bounding box。失败主要来自噪声环境下的物体误识别、干扰物遮挡或目标未识别。

### Figure 10: Additional trajectory cases

![[assets/RoboBrain_fig10_trajectory_cases.png]]

**说明**: 展示预测轨迹与 ground truth 轨迹。成功样例中预测更平滑，失败样例反映空间意识、物理约束和可变形物体理解不足。

### Figure 11: Gemini labeling prompt

![[assets/RoboBrain_fig11_gemini_prompt.png]]

**说明**: ShareRobot 用 Gemini 对视频帧做任务识别、步骤抽取和 frame window 标注，再由人工审查。

### Figure 12: Question templates

![[assets/RoboBrain_fig12_question_templates.png]]

**说明**: 展示 planning、planning with context、remaining steps、future prediction、success、discriminative/generative affordance、past description 等 10 类问题模板。

### Table 1/4: Training stage configuration

| Stage | Resolution | Tokens | Samples | Trainable | Batch | LR ViT | LR other | Epoch |
|-------|------------|--------|---------|-----------|-------|--------|----------|-------|
| Stage 1 | 384 | 729 | 558K | Projector 17.0M | 8 | - | 1e-3 | 1 |
| Stage 1.5 | Max 384x2x2 | Max 729x5 | 4M | Full 8.0B | 2 | 2e-6 | 1e-5 | 1 |
| Stage 2 Single-Image | Max 384x6x6 | Max 729x37 | 3.2M | Full 8.0B | 1 | 2e-6 | 1e-5 | 1 |
| Stage 2 OneVision | Max 384x6x6 | Max 729x37 | 1.6M | Full 8.0B | 1 | 2e-6 | 1e-5 | 1 |
| Stage 3 | Max 384x6x6 | Max 729x37 | 3M | Full 8.0B | 1 | 2e-6 | 1e-5 | 1 |
| Stage 4 A-LoRA | Max 384x6x6 | Max 729x37 | 10K | A-LoRA 28.0M | 4 | 2e-6 | 1e-5 | 1 |
| Stage 4 T-LoRA | Max 384x6x6 | Max 729x37 | 400K | T-LoRA 28.0M | 4 | 2e-6 | 1e-5 | 1 |

### Table 2/3: Affordance 与 trajectory 结果

| Model | AP |
|-------|----|
| LLaVA-NeXT-7B | 9.8% |
| Qwen2-VL-7B | 12.5% |
| RoboBrain | 27.1% |

| Method | DFD ↓ | HD ↓ | RMSE ↓ |
|--------|-------|------|--------|
| RoboBrain Base | 0.191 | 0.171 | 0.133 |
| + Start Points | 0.176 | 0.157 | 0.117 |
| + Max Points | 0.185 | 0.163 | 0.125 |
| + Spec Token | 0.109 | 0.010 | 0.091 |

### Table 5: General benchmark 摘要

| Dataset | RoboBrain | GPT-4V | LLaVA-OV-7B | InternVL2-8B | Qwen2-VL-7B | GPT-4o |
|---------|-----------|--------|-------------|--------------|-------------|--------|
| AI2D | 82.03 | 78.2 | 81.4 | 83.8 | - | 94.2 |
| ChartQA | 80.48 | 78.5 | 80 | 83.3 | 83 | 85.7 |
| DocVQA | 88 | 88.4 | 87.5 | 91.6 | 94.5 | 92.8 |
| TextVQA | 75.85 | - | 71.07 | 77.4 | 84.3 | - |
| MMMU | 49 | 56.8 | 48.8 | 51.8 | 54.1 | 69.1 |
| MME | 2084 | 1926 | 1998 | 2210 | 2327 | - |

**关键发现**: RoboBrain 的通用能力没有完全塌掉，但不是最强通用 MLLM；它的价值主要在机器人任务上。

### Table 6: Robotic benchmark 摘要

| Dataset / Metric | RoboBrain | GPT-4V | LLaVA-OV-7B | RoboMamba | Qwen2-VL-7B |
|------------------|-----------|--------|-------------|-----------|-------------|
| RoboVQA BLEU1 | 72.05 | 32.23 | 38.12 | 54.9 | 33.22 |
| RoboVQA BLEU2 | 65.35 | 26.51 | 33.56 | 44.2 | 26.11 |
| RoboVQA BLEU3 | 59.39 | 24.65 | 31.76 | 39.5 | 20.98 |
| RoboVQA BLEU4 | 55.05 | 23.94 | 30.97 | 36.3 | 17.37 |
| OpenEQA object-state | 70.4 | 63.2 | 72.02 | - | 72.06 |
| OpenEQA spatial | 46.46 | 33.6 | 48.98 | - | 50.39 |
| ShareRobot discriminative | 99.02 | - | 57.9 | - | 76.47 |
| ShareRobot future-prediction | 72.92 | - | 13.1 | - | 8.04 |
| ShareRobot planning-with | 91.95 | - | 44.25 | - | 45.12 |

**关键发现**: RoboVQA BLEU4 比第二名 RoboMamba 高 18.75，说明模型在长程规划文本上提升明显；但 OpenEQA 中 object recognition、spatial understanding 等子项并非全面第一。

### Table 7: ShareRobot 与数据比例消融

| Exp | OneVision | ShareRobot | Other robot | RoboVQA | OpenEQA | ShareRobot | Avg |
|-----|-----------|------------|-------------|---------|---------|------------|-----|
| A | 60% | 20% | 20% | 48.29 | 58.74 | 63.11 | 62.48 |
| B, no ShareRobot | 60% | 0% | 40% | 49.20 | 57.96 | 27.03 | 55.66 |
| C | 70% | 15% | 15% | 45.96 | 56.59 | 61.73 | 61.22 |
| D | 60% | 20% | 20% | 48.29 | 58.74 | 63.11 | 62.48 |
| E | 50% | 25% | 25% | 49.34 | 58.76 | 63.35 | 61.92 |
| F | 40% | 30% | 30% | 49.22 | 56.24 | 64.57 | 62.07 |
| G | 30% | 35% | 35% | 47.74 | 55.72 | 65.22 | 62.14 |

**关键发现**: 去掉 ShareRobot 后 ShareRobot Eval 从 63.11 掉到 27.03；4:6 左右的 robot/general 比例整体较均衡。

### Table 8/9: 架构泛化与阶段消融

| Model | SFT G:R | RoboVQA | ShareRobot | MME | MMMU |
|-------|---------|---------|------------|-----|------|
| LLaVA-OV-7B | 6:0 | 36.29 | 27.04 | 2001 | 49.65 |
| LLaVA-OV-7B | 6:4 | 43.63 | 54.66 | 1945 | 48.83 |
| Qwen2VL-7B | 6:0 | 24.05 | 28.17 | 2313 | 52.10 |
| Qwen2VL-7B | 6:4 | 58.94 | 58.86 | 2295 | 52.33 |
| OpenVLA-7B | 6:0 | 4.11 | 21.44 | 1681 | 35.07 |
| OpenVLA-7B | 6:4 | 54.79 | 60.56 | 1722 | 37.25 |

| Stage | RoboVQA | ShareRobot | MME | MMMU | Affordance ↑ | Trajectory ↓ |
|-------|---------|------------|-----|------|--------------|--------------|
| S1.5 | 2.60 | 9.81 | 1406 | 46.00 | 0.00 | 1.00 |
| S2-si | 28.90 | 13.31 | 2110 | 50.76 | 3.11 | 1.00 |
| S2-ov | 31.81 | 34.84 | 2083 | 49.95 | 8.50 | 1.00 |
| S3 | 62.96 | 65.05 | 2084 | 49.00 | 7.14 | 1.00 |
| S4-A | 62.96 | 65.05 | 2084 | 49.00 | 27.1 | - |
| S4-T | 62.96 | 65.05 | 2084 | 49.00 | - | 0.09 |

**关键发现**: ShareRobot 数据对多种 backbone 都有效；Stage 3 主要提升 planning，Stage 4 分别提升 affordance 和 trajectory。

---

## 实验

### 数据集

| 数据集 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| ShareRobot | 51,403 instances / 1,028,060 QA | 细粒度 planning + affordance + trajectory | 训练与评测 |
| RoboVQA | 18,248 video-text pairs | 真实机器人长程 VQA/planning | 评测 |
| OpenEQA | 1,600+ human questions / 180+ scenes | embodied QA | 评测 |
| AGD20K | affordance benchmark | 物体可交互区域 | affordance AP |
| LLaVA-OneVision-Data | 3.2M image + 1.6M image/video | 通用视觉指令训练 | 通用能力 |

### 实现细节

- **Backbone**: SigLIP + 2-layer MLP projector + Qwen2.5-7B-Instruct。
- **训练策略**: Stage 1/1.5/2 通用 OV，Stage 3 robot full fine-tuning，Stage 4 A-LoRA/T-LoRA。
- **分布式训练**: Zero3，每台服务器 8xA800。
- **指标**:
  - Planning: BLEU1-4 或 GPT-4o score。
  - Affordance: AP over IoU thresholds。
  - Trajectory: DFD、HD、RMSE。

---

## 批判性思考

### 优点

1. **任务定义清楚**: 论文没有把“机器人脑”停留在高层语义，而是明确拆成 planning、affordance、trajectory 三个可评测能力。
2. **数据贡献比模型结构更关键**: [[ShareRobot]] 的标注维度和规模是主要增量，消融表明去掉 ShareRobot 后性能大幅下降。
3. **训练路线务实**: 先继承通用 [[Vision-Language Model]] 能力，再通过机器人数据和 [[LoRA]] 适配具体输出，比从零训练更现实。
4. **覆盖长视频和高分辨率图像**: 这对 manipulation planning 中的历史状态和局部交互区域很重要。

### 局限性

1. **不是闭环控制策略**: 输出 planning、bounding box 和 2D trajectory，但没有直接证明能稳定驱动真实机器人完成闭环控制。
2. **轨迹是 2D visual trace**: 对真实机器人控制来说缺少 3D 位姿、接触力、关节约束和动力学约束。
3. **affordance 仍是 bounding box**: 对复杂可变形物体、铰接物体或多接触 manipulation 的表达能力有限。
4. **评测依赖 GPT-4o 打分**: OpenEQA/ShareRobot 的一部分评价使用 LLM score，存在评价器偏差风险。
5. **失败样例暴露世界模型不足**: 清理桌面、开冰箱、折布等失败说明模型还缺少细粒度空间理解、物理常识和对象状态建模。

### 潜在改进方向

1. 将 2D trajectory 扩展到 3D keypoints、SE(3) pose 或可执行 action chunks。
2. 把 affordance 从 box 扩展为 mask、contact point distribution 或 grasp pose candidates。
3. 接入低层 visuomotor policy，验证规划和 affordance 是否真正提升 real-world success rate。
4. 用更严格的机器人仿真/实机 benchmark 替代部分 LLM-as-judge 评价。
5. 引入 object-centric memory 和 physical constraints，减少对铰接/可变形对象的失败。

### 可复现性评估

- [ ] 代码开源：论文页面未在 Zotero 元数据中直接给出代码链接。
- [ ] 预训练模型：项目主页可能提供，需单独确认。
- [x] 训练细节完整：stage、数据量、学习率、batch size、可训练参数较完整。
- [x] 数据构造流程完整：筛选条件、标注流程、模板和统计较完整。
- [ ] 数据集可获取：论文称 open-source，但具体下载入口需项目主页确认。

---

## 关联笔记

- [[ShareRobot]]
- [[Multimodal Large Language Model]]
- [[Vision-Language Model]]
- [[LLaVA]]
- [[SigLIP]]
- [[Qwen2.5]]
- [[Affordance]]
- [[Trajectory Prediction]]
- [[LoRA]]
- [[RoboVQA]]
- [[OpenEQA]]
- [[Open X-Embodiment]]
