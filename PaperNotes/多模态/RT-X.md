---
title: "Open X-Embodiment: Robotic Learning Datasets and RT-X Models"
method_name: "RT-X"
authors: [Open X-Embodiment Collaboration, Abby O'Neill, Abdul Rehman, Abhinav Gupta]
year: 2025
venue: arXiv
tags: [robot-learning, x-embodiment, vla, imitation-learning, dataset, multi-robot-transfer]
zotero_collection: 多模态
image_source: local
arxiv_html: https://arxiv.org/html/2310.08864
created: 2026-04-28
---

# 论文笔记：Open X-Embodiment: Robotic Learning Datasets and RT-X Models

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Open X-Embodiment Collaboration，21 个机构参与 |
| 日期 | 2025-05-14 arXiv v9；Zotero 初始日期为 2023-10-13 |
| 项目主页 | https://robotics-transformer-x.github.io |
| 对比基线 | [[RT-1]]、[[RT-2]]、Original Method |
| 链接 | [arXiv](https://arxiv.org/abs/2310.08864) / [HTML](https://arxiv.org/html/2310.08864) |

---

## 一句话总结

> 这篇论文把多机构多机器人数据统一成 [[Open X-Embodiment]]，并证明 [[RT-X]] 能从跨本体数据中获得正迁移。

---

## 核心贡献

1. **开放数据仓库**: 整合 60 个真实机器人数据集、22 种机器人本体、1M+ 轨迹、527 个技能和 160266 个任务，统一成 [[RLDS]] 格式。
2. **跨本体策略基线**: 基于 [[RT-1]] 和 [[RT-2]] 构建 [[RT-X]]，用同一套输入输出接口学习多机器人、多任务、多场景数据。
3. **实机正迁移证据**: 在 6 个机器人上做 3600 次真实评测，显示小数据域中 [[RT-1]]-X 平均成功率比原方法或单域 RT-1 高 50%，大模型 [[RT-2]]-X 在 emergent skills 上约 3 倍提升。

---

## 问题背景

### 要解决的问题

机器人学习长期是“一种机器人、一个环境、一个任务训练一个策略”。论文问的是：能否像 NLP/CV 里用大规模预训练模型一样，在机器人领域训练可复用的跨本体策略，即 [[X-Embodiment]] 策略。

### 现有方法的局限

现有机器人数据集通常窄：单机器人、单环境、少量物体或任务。跨本体迁移方法往往依赖显式对齐动作空间、加入 embodiment condition、学习可迁移表示或做域转换。本文反过来采用更直接的路线：先把大量异构数据合并，再看高容量策略是否能直接吃下这些差异。

### 本文的动机

单个机器人数据集覆盖不足，但多个实验室、多个机器人、多个环境的数据合起来更接近“大数据”条件。即使当前规模还远小于互联网文本/图像，统一数据格式和开放模型检查点也能让社区开始系统研究跨本体机器人学习。

---

## 方法详解

### 数据与动作空间统一

[[RT-X]] 面向语言条件机器人操作任务，输入为图像历史和自然语言指令，输出为离散化末端执行器动作。论文没有做严格的坐标系或控制语义对齐，而是采用粗粒度统一：

- **观测**: 每个数据集选一个 canonical RGB camera view，resize 到统一分辨率；不同相机位姿和属性仍然保留差异。
- **动作**: 转成 7 DoF 末端执行器动作，包含 $x,y,z,roll,pitch,yaw$ 和 gripper opening，可能表示位置、速度、增量或绝对值。
- **归一化与离散化**: 每个数据集先做 action normalization，再通过 [[Action Tokenization]] 把每个动作维度分成 256 个 bin；另加 1 个 episode termination 维度，因此共 8 个离散动作维度。
- **关键取舍**: 同一个 token 在不同机器人上可能对应不同物理运动，模型必须从图像、语言和数据分布中隐式处理本体差异。

### 模型架构

[[RT-X]] 不是新架构，而是把已有策略扩展到跨本体数据：

- **[[RT-1]]-X**: 35M 参数，图像历史经 ImageNet 预训练 [[EfficientNet]] 编码，语言经 USE embedding 编码，两者通过 [[FiLM]] 融合为 81 个 vision-language token，再由 decoder-only [[Transformer]] 输出离散动作。
- **[[RT-2]]-X**: 基于 [[Vision-Language-Action Model]]，把动作 token 当作文本 token，让 [[Vision-Language Model]] 主干通过 co-fine-tuning 同时学习 Web 视觉语言数据和机器人动作数据；本文主要用 RT-2-PaLI-X，视觉主干为 ViT，语言主干为 UL2。

### 训练与推理

- **目标函数**: 两类模型都使用标准 [[Cross-Entropy Loss]]，RT-1 在离散动作 bucket 上分类，RT-2 在语言/action token vocabulary 上分类。
- **数据混合**: 实验阶段的 robotics mixture 包含 9 种 manipulator 数据，来自 RT-1、QT-Opt、Bridge、Task Agnostic Robot Play、Jaco Play、Cable Routing、RoboTurk、NYU VINN、Austin VIOLA、Berkeley Autolab UR5、TOTO、Language Table 等。
- **RT-1-X**: 只在机器人数据混合上训练。
- **RT-2-X**: 按 RT-2 做 co-fine-tuning，Web VLM 数据和机器人数据约 1:1 混合。
- **推理频率**: 不同机器人按原系统需要运行在 3-10 Hz；RT-1 本地运行，RT-2 通过云服务查询。

---

## 关键公式

论文主体没有显式编号公式，但包含两个核心数学定义。

### 公式1: [[Action Tokenization|动作离散化]]

$$
a_t = (a_t^1,\ldots,a_t^8),\quad a_t^i \in \{0,\ldots,255\}
$$

**含义**: 每个时间步输出 8 个离散 token，其中 7 个对应末端执行器运动和 gripper，1 个对应 episode termination。

**符号说明**:
- $a_t$: 时间 $t$ 的动作 token 向量。
- $a_t^i$: 第 $i$ 个动作维度的离散 bin。
- $\{0,\ldots,255\}$: 每个动作维度均匀离散成 256 桶。

### 公式2: [[Cross-Entropy Loss|分类交叉熵目标]]

$$
\mathcal{L}_{CE} = -\sum_{t}\sum_{i=1}^{8}\log p_\theta(a_t^i \mid o_{\leq t}, l)
$$

**含义**: 模型根据图像观测历史 $o_{\leq t}$ 和语言指令 $l$，预测每个动作维度的离散 token。

**符号说明**:
- $\theta$: 策略模型参数。
- $o_{\leq t}$: 到当前时间的视觉观测历史。
- $l$: 语言任务指令。
- $p_\theta(a_t^i \mid o_{\leq t}, l)$: 模型对第 $i$ 个动作 token 的预测概率。

---

## 关键图表

### Figure 1: Open X-Embodiment 总览

![[RT-X_fig1_overview.png]]

**说明**: 数据集覆盖多机构、多机器人、多任务和多场景，是本文最重要的基础设施贡献。

### Figure 2: 数据集统计

![[RT-X_fig2_dataset_analysis.png]]

**说明**: Franka 数据集数量和场景多样性最高，xArm 和 Google Robot 贡献最多轨迹；技能以 pick/place 相关为主，但长尾包含 wiping、assembling 等；物体覆盖形状、容器、家具、食物、电器和餐具。

### Figure 3: RT-1-X 与 RT-2-X 架构

![[RT-X_fig3_architecture.png]]

**说明**: 两个模型都输入图像和语言指令、输出离散化末端执行器动作。[[RT-1]]-X 是机器人专用 Transformer 架构；[[RT-2]]-X 用 [[Vision-Language Model]] 把动作建模为语言 token。

### Figure 4: 小数据域实机结果

![[RT-X_fig4_small_data_results.png]]

**说明**: 在 Kitchen Manipulation、Cable Routing、NYU Door Opening、Autolab UR5、Task-Agnostic Play 上，[[RT-1]]-X 在 4/5 个数据集超过对应原方法，平均成功率 63%，高于 Original Method 的 41% 和单域 RT-1 的 44%。

### Figure 5: 跨本体 emergent skills

![[RT-X_fig5_emergent_skills.png]]

**说明**: 这些任务技能来自 Bridge/WidowX 数据而非 Google Robot 数据，但在 Google Robot 上评测；RT-2-X 能把别的机器人数据中的技能迁移到 Google Robot。

### Table I: 大数据域容量对比

![[RT-X_table1_capacity.png]]

| Evaluation Setting | Bridge IRIS | Bridge RAIL | RT-1 paper 6 skills |
|---|---:|---:|---:|
| Original Method | 13% | 13% | - |
| RT-1 | 40% | **30%** | **92%** |
| RT-1-X | 27% | 27% | 73% |
| RT-2-X (55B) | **50%** | **30%** | 91% |

**说明**: 在大数据域，35M 的 [[RT-1]]-X 容量不足，会低于单域 RT-1；55B 的 [[RT-2]]-X 才能吸收大规模异构数据并达到强表现。

### Table II: 消融实验

![[RT-X_table2_ablation.png]]

| Row | Model | Size | History | Dataset | Web Co-train | Init | Emergent Skills | RT-2 Generalization |
|---:|---|---:|---|---|---|---|---:|---:|
| 1 | RT-2 | 55B | none | Google Robot action | Yes | Web-pretrained | 27.3% | **62%** |
| 2 | RT-2-X | 55B | none | Robotics data | Yes | Web-pretrained | **75.8%** | 61% |
| 3 | RT-2-X | 55B | none | Robotics data except Bridge | Yes | Web-pretrained | 42.8% | 54% |
| 4 | RT-2-X | 5B | 2 | Robotics data | Yes | Web-pretrained | 44.4% | 52% |
| 5 | RT-2-X | 5B | none | Robotics data | Yes | Web-pretrained | 14.5% | 30% |
| 6 | RT-2-X | 5B | 2 | Robotics data | No | From scratch | 0% | 1% |
| 7 | RT-2-X | 5B | 2 | Robotics data | No | Web-pretrained | 48.7% | 47% |

**关键发现**: Web pretraining、模型容量、短历史图像都很关键；移除 Bridge 后 emergent skill 从 75.8% 降到 42.8%，说明跨本体技能迁移确实来自其他机器人数据。

---

## 实验

### 数据集

| 数据集/混合 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| [[Open X-Embodiment]] Dataset | 1M+ 轨迹，60 数据集，22 本体 | 真实机器人、多机构、多任务，统一 [[RLDS]] | 开放仓库与未来训练基础 |
| Robotics data mixture | 实验时 9 种 manipulator | RT-1、QT-Opt、Bridge 等多源数据 | 训练 RT-1-X / RT-2-X |
| 小数据域评测 | 5 个真实机器人数据域 | Kitchen、Cable、Door、UR5、Robot Play | 验证正迁移 |
| 大数据域评测 | Bridge、RT-1 | WidowX、Google Robot | 验证容量需求 |
| OOD / emergent skills | Google Robot 上新技能 | Bridge 中存在、Google Robot 原数据中不存在 | 验证跨本体技能迁移 |

### 实现细节

- **Backbone**: [[RT-1]]-X 使用 [[EfficientNet]] + [[Transformer]]；[[RT-2]]-X 使用 PaLI-X / ViT / UL2。
- **训练目标**: [[Cross-Entropy Loss]] over discrete action buckets 或 language/action token。
- **动作空间**: 7 DoF end-effector + termination，8 维 token，每维 256 bins。
- **评测规模**: 3600 次真实机器人 trials，跨 6 个机器人。
- **推理**: 3-10 Hz；RT-1 本地，RT-2 云端。

---

## 批判性思考

### 优点

1. **贡献重心正确**: 论文的价值不是新模型技巧，而是把社区异构数据真正打通，并提供可复用训练基线。
2. **实验问题清晰**: 分开验证小数据域正迁移、大数据域容量需求、OOD/generalization 和 emergent skills。
3. **结论有层次**: 不是简单说“数据越多越好”，而是明确指出小模型可能 underfit，跨本体数据需要足够模型容量和预训练。

### 局限性

1. **没有证明新机器人泛化**: 实验是在训练混合中已有机器人或已有数据域上评测，尚未系统研究完全新 embodiment 的 adaptation。
2. **动作对齐很粗糙**: 不对齐坐标系、控制频率和控制语义，虽然简单，但也让迁移机制更难解释。
3. **数据分布不均衡**: Franka、xArm、Google Robot 等占比明显更高，长尾本体和长尾技能是否真正受益仍不清楚。
4. **RT-2-X 复现门槛高**: 55B VLM + 云端推理不是普通实验室能完整复现的设置。

### 潜在改进方向

1. 加入显式 embodiment descriptor 或 robot morphology token，研究隐式迁移和显式条件化的差异。
2. 系统测试 unseen robot adaptation，包括零样本、少样本 finetune 和 adapter/LoRA。
3. 设计更稳定的跨机器人 action representation，例如 task-space skill primitive、relative action 或 object-centric action。
4. 在数据混合策略上做 scaling law：不同机器人/技能/场景的采样权重如何影响正迁移与负迁移。

### 可复现性评估

- [x] 数据集开放
- [x] 项目主页和使用代码开放
- [x] RT-1-X checkpoint 提供
- [ ] 55B RT-2-X 完整训练成本较高
- [ ] 训练超参和数据采样细节仍不足以低成本复现全部结果

---

## 关联笔记

### 基于
- [[RT-1]]: 机器人专用 Transformer 策略架构。
- [[RT-2]]: 将 Web 视觉语言预训练迁移到机器人动作 token 的 [[Vision-Language-Action Model]]。
- [[Open X-Embodiment]]: 本文提出并维护的开放机器人学习数据仓库。

### 方法相关
- [[X-Embodiment]]: 跨机器人本体学习。
- [[Vision-Language-Action Model]]: RT-2-X 的基础建模范式。
- [[RLDS]]: 数据统一格式。
- [[Action Tokenization]]: 离散化动作输出。
- [[Cross-Entropy Loss]]: 训练目标。

### 数据相关
- [[Open X-Embodiment]]: 60 数据集、22 机器人本体、1M+ 轨迹。

---

## 速查卡片

> [!summary] Open X-Embodiment / RT-X
> - **核心**: 通过开放多机器人数据仓库和 RT-X 基线验证跨本体正迁移。
> - **方法**: 统一图像/语言输入和 7 DoF 离散动作输出，在 [[RT-1]] / [[RT-2]] 上做多机器人联合训练。
> - **结果**: 小数据域 RT-1-X 平均成功率 63%，RT-2-X emergent skills 75.8%，约为 RT-2 的 3 倍。
> - **代码/数据**: https://robotics-transformer-x.github.io

---

*笔记创建时间: 2026-04-28*
