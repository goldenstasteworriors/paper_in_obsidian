---
title: "EgoSteer: A Full-Stack System Towards Steerable Dexterous Manipulation from Egocentric Videos"
method_name: "EgoSteer"
authors: [Yifan Zhong, Zhang Chen, Tianrui Guan, Fanlian Zeng, Yuyao Ye, Tianjia He, Ka Nam Lui, Jiayi Li, Tingrui Zhang, Ruilin Yan, Xinhao Ji, Guangyu Zhao, Wenjie Lou, Jiayuan Zhang, Yuanpei Chen, Yaodong Yang]
year: 2026
venue: arXiv
tags: [vision-language-action, dexterous-manipulation, egocentric-video, world-model, imitation-learning]
zotero_collection: ego/ego 手
image_source: local
arxiv_html: https://arxiv.org/html/2607.09701
created: 2026-07-25
---

# 论文笔记：EgoSteer

## 元信息

| 项目 | 内容 |
|---|---|
| 机构 | Institute for AI, PKU；PKU-PsiBot Joint Lab；UPenn |
| 日期 | June 2026 |
| 项目主页 | https://egosteer.github.io/ |
| 对比基线 | [[Pi05]]、[[Being-H0.5]]、[[Diffusion Policy]]、IMLE |
| 链接 | [arXiv](https://arxiv.org/abs/2607.09701) / [Code](https://github.com/egosteer/egosteer) |

---

## 一句话总结

> 用 9.6K 小时第一视角人类视频预训练，再以统一动作空间、机器人后训练和 DAgger 纠错，将语言可控的双手灵巧操作扩展到 40+ 任务。

---

## 核心贡献

1. **EgoSmith 数据引擎**：将 12 个第一视角数据集加工为 9,606 小时、229 万段、约 10.4 亿帧的动作—语言对齐数据，4D 运动估计吞吐量约为 HaWoR 的 9 倍。
2. **统一机器人栈**：遥操作、策略推理和人在环纠错共享 FK/IK 与控制节点；相对运动映射使操作者可从任意失败状态平滑接管。
3. **EgoSteer VLA**：Qwen3-VL-2B 主干 + 约 300M 参数 DiT 动作专家 + 训练期约 70M 参数 DINOv3 潜空间世界模型专家。
4. **可控性与迁移实验**：40 个任务总体成功率 75%；10 任务对比为 74%，高于 Being-H0.5 的 39% 和 π0.5 的 22%；120/229 条示范即可适配折盒/拆蛋糕盒，成功率 75%/83%。
5. **完整开源栈**：策略、EgoSmith、机器人栈和 3B Base/RealMan 权重均已实际发布。

---

## 问题背景

### 要解决的问题

通用机器人不仅应“会做某个任务”，还应在同一场景中按自由语言选择目标物体、手、动作与顺序。双灵巧手拥有更强的操作能力，但高自由度使机器人数据昂贵，且现有 VLA 多依赖夹爪或任务专用微调。

### 现有方法的局限

- 原始[[First-Person Video|第一视角视频]]存在头动、遮挡、旁观者手、尺度漂移，并缺少语言与精确动作标注。
- 人手与机器人在外观、运动学和动力学上存在 embodiment gap，纯人类视频不能直接部署。
- 高自由度策略的失败状态难以通过离线遥操作数据覆盖。
- 推理延迟会在动作块之间制造停顿，接触丰富任务尤其敏感。

### 本文的动机

作者把瓶颈判断为“共依赖的全栈问题”：只有同时解决数据质量、跨具身动作表征、模型容量、实时执行和失败纠错，才可能出现真正的语言可控灵巧操作。

---

## 方法详解

### 1. EgoSmith

四阶段数据流水线：

1. **预过滤**：128 点网格平均光流去除行走片段；YOLO/手部几何规则去除遮挡、误检和旁观者干扰。
2. **4D 运动估计**：HaWoR 的 ViT 重建相机坐标系 MANO；DPVO 给出无尺度轨迹与深度，Any4D 给出度量深度，两者以背景像素深度中值比例恢复全局尺度。
3. **语言标注**：Qwen3.5-VL-Plus 再过滤 3.5% 无有效操作片段，并生成 L1 动词+物体、L2 gist、L3 物体中心、L4 手中心、L5 分步指令。
4. **后过滤**：episode 级相机位移/旋转、chunk 级腕与手指空间离群值、frame 级运动突跳三级质控。

### 2. 统一机器人栈与人在环纠错

双手使用 PsiBot SynGlove-Air，手腕使用 Vive Tracker；机械臂通过 mink 做 IK，6-DoF 灵巧手做关节映射。[[Human-in-the-loop|人在环]]接管时保存操作者与机器人当前状态，之后只映射操作者相对位移，因此不要求人先准确对齐机器人绝对姿态。作者报告交接成功率超过 85%，并只把介入片段加入后续 [[DAgger]] 训练。

### 3. 统一状态—动作空间

人类和机器人都表示为双手世界系状态：每手 3D 腕平移、6D 腕旋转和 15D 指尖关键点；训练时转到当前相机坐标系。模型观察 5 秒、6 帧（1 FPS）历史，预测 32 步、30 Hz [[Action Chunking|动作块]]。

### 4. EgoSteer 架构

- **Backbone**：Qwen3-VL-2B；图像历史作为视频，指令与相机内参作为文本，状态历史经两层 MLP 变成连续 token。训练时以 75% 概率 mask 每帧本体状态，防止 shortcut；双相机后训练时以 50% 概率丢弃胸前相机。
- **动作专家**：14 层 [[Diffusion Transformer|DiT]]，宽度 1024、8 头、约 300M 参数；通过投影后的 KV 与主干第 $2\ell$ 层联合注意，使用 [[Conditional Flow Matching]] 生成连续动作。
- **训练期 RTC**：给动作专家一段已知干净动作前缀，仅去噪后缀。部署取 32 步中的前 12 步；其中 4 步覆盖推理延迟，实际每轮执行 8 个新动作。
- **世界模型专家**：4 层、约 70M 参数；预测动作诱导的未来 [[DINOv3]] ViT-L/16 特征。它只在训练期塑造 backbone，推理时丢弃。
- **联合训练**：VLA 数据之外，共训练 10.4M VLM 样本以维持视觉语言、空间定位、具身 QA 和 affordance 能力。
- **工程**：HSDP、mixed precision、torch.compile、FlexAttention、WebDataset 流式读取与 16,384 样本 shuffle buffer。

---

## 关键公式

### 公式 1：[[Metric Scale Recovery|DPVO 度量尺度恢复]]

$$
s=\operatorname{median}_{t,(u,v)\in\mathcal{B}_t}
\frac{\mathbf D_t^{\mathrm{Any4D}}(u,v)}
{\hat{\mathbf D}_t^{\mathrm{DPVO}}(u,v)}
$$

**含义**：用去除手部区域后的背景像素，将 DPVO 的无尺度轨迹锚定到 Any4D 的物理尺度。

**符号说明**：

- $\mathcal B_t$：第 $t$ 帧有效背景区域。
- $s$：统一尺度因子；$\mathbf p_t=s\hat{\mathbf p}_t$。

### 公式 2：[[Conditional Flow Matching|条件流匹配]]

$$
\mathcal L_{\mathrm{CFM}}
=
\mathbb E_{\eta,\epsilon}
\left[
\left\|
v_\theta(\mathbf a^\eta_{\mathrm{suf}}\mid c,\mathbf a_{\mathrm{pre}},\eta)
-(\epsilon-\mathbf a_{\mathrm{suf}})
\right\|_2^2
\right],
\qquad
\mathbf a^\eta_{\mathrm{suf}}
=(1-\eta)\mathbf a_{\mathrm{suf}}+\eta\epsilon
$$

**含义**：在上下文和干净前缀条件下回归由真实后缀到高斯噪声的线性速度场；每个样本采 4 个时间点以提高有效 batch。

**符号说明**：

- $c$：图像、语言、相机与状态上下文。
- $\eta$：流时间；后缀使用偏置 Beta 分布采样。
- $\mathbf a_{\mathrm{pre}},\mathbf a_{\mathrm{suf}}$：RTC 的已知前缀与待预测后缀。

### 公式 3：[[Joint Attention|动作专家—主干联合注意力]]

$$
\begin{aligned}
\operatorname{Attn}_{\ell,m}
=&
\operatorname{Softmax}\left(
\frac{\mathbf Q_{\ell,m}^{\mathrm{AE}}
\operatorname{concat}
[\mathbf K_{f(\ell),m}^{\mathrm B}\mathbf W_\ell^{\mathrm K},
\mathbf K_{\ell,m}^{\mathrm{AE}}]^\top}
{\sqrt{d_{\mathrm{head}}}}
\right)\\
&\cdot
\operatorname{concat}
[\mathbf V_{f(\ell),m}^{\mathrm B}\mathbf W_\ell^{\mathrm V},
\mathbf V_{\ell,m}^{\mathrm{AE}}].
\end{aligned}
$$

**含义**：动作 token 同时访问自身序列和投影后的 VLM KV cache。

### 公式 4：[[World Model|未来潜特征回归]]

$$
\mathcal L_{\mathrm{WM}}
=
\frac{1}{H_vW_v}
\sum_{u=1}^{H_v}\sum_{v=1}^{W_v}
\left\|\mathbf Z_{u,v}-\hat{\mathbf Z}_{u,v}\right\|_2^2
$$

**含义**：以未来帧的 DINOv3 特征监督世界模型专家，避免像素预测对光照和背景噪声过敏。

### 公式 5：联合目标

$$
\mathcal L_{\mathrm{total}}
=
\mathcal L_{\mathrm{CFM}}
+\mathcal L_{\mathrm{WM}}
+0.05\mathcal L_{\mathrm{VLM}}
$$

**含义**：动作流匹配是主目标，潜空间未来预测塑造动作感知表征，VLM next-token loss 防止语义能力遗忘。

---

## 关键图表

### Figure 1：全栈系统与核心能力

![[assets/EgoSteer_fig1.png]]

EgoSmith → 人类视频预训练 → 机器人后训练/DAgger → 40+ 可控任务与长程少样本适配。

### Figure 2：EgoSmith 四阶段流水线

![[assets/EgoSteer_fig2.png]]

### Figure 3：统一机器人栈

![[assets/EgoSteer_fig3.png]]

### Figure 4：EgoSteer 架构

![[assets/EgoSteer_fig4.png]]

### Figure 5：40 任务可控操作结果

![[assets/EgoSteer_fig5.png]]

22 个任务成功率超过 80%，40 任务平均 75%；覆盖 7 类操作。

### Figure 6：预训练 scaling

![[assets/EgoSteer_fig6.png]]

3K→6K→9.6K 小时总体后训练成功率由 40%→43%→60%，但单任务并非单调。

### Figure 7：EgoSmith 数据统计

![[assets/EgoSteer_fig7.png]]

共 8,969 个不同物体名词、623 个动作动词，头部技能常见且有明显长尾。

### Figure 8：机器人遥操作数据统计

![[assets/EgoSteer_fig8.png]]

187 小时、193 个任务，其中 56 个常见任务、137 个长尾任务，涵盖 7 类操作。

### Figure 9：双视角轨迹与三级语言标注

![[assets/EgoSteer_fig9.png]]

### Figure 10：七类机器人任务示例

![[assets/EgoSteer_fig10.png]]

### Figure 11：VLM 共训练数据分布

![[assets/EgoSteer_fig11.png]]

10.4M 样本中 FineVision 34.1%、RefSpatial 24.1%、RoboInter-VQA 15.5%、RoboPoint 12.2%、Robo2VLM 7.5%、RoboAfford 6.5%、ShareRobot 0.1%。

### Table 1：主实验汇总

| 实验 | 方法/设置 | 平均或任务成功率 |
|---|---|---:|
| DAgger | EgoSteer-FT / EgoSteer-DG | 22.5% / **62.5%** |
| Baseline | π0.5 / Being-H0.5 / EgoSteer | 22% / 39% / **74%** |
| 训练消融 | 无 WM / 无 RTC / noisy / full | 31% / 39% / 33% / **44%** |
| 少样本长程 | DP / IMLE / scratch / EgoSteer | 0/0/0；**折盒 75%，拆蛋糕盒 83%** |

### Table 2：4D 运动估计

| Method | RPE↓ | ATE↓ | WA-MPJPE↓ | W-MPJPE↓ |
|---|---:|---:|---:|---:|
| HaWoR | 5.17 | 9.44 | 38.7 | 106.9 |
| **EgoSmith** | **2.42** | **7.60** | **25.9** | **86.0** |

### Table 3：12 个第一视角数据源

| Dataset | Hours | % | Episodes | Pipeline annotations |
|---|---:|---:|---:|---|
| Egocentric-100K | 8,049 | 83.8 | 1,795,731 | hand/depth/camera/language |
| EgoVerse | 690 | 7.2 | 35,175 | depth/language |
| EgoDex | 370 | 3.9 | 147,588 | depth/language |
| Egocentric-10K | 288 | 3.0 | 194,915 | hand/depth/camera/language |
| Ego4D | 138 | 1.4 | 74,505 | hand/depth/camera/language |
| EPIC-KITCHENS | 49 | 0.5 | 26,454 | hand/depth/camera/language |
| HoloAssist | 11.5 | 0.1 | 11,426 | depth/language |
| HOT3D | 4.5 | 0.05 | 1,105 | depth |
| TACO | 3.0 | 0.03 | 1,558 | language |
| OakInk-v2 | 1.7 | 0.02 | 891 | depth |
| H2O | 1.0 | 0.01 | 935 | native |
| FPHA | 0.5 | 0.01 | 578 | second-hand/depth/language |
| **Total** | **9,606** | **100** | **2,290,861** | — |

### Table 4：VLM 共训练数据

| Dataset | Samples | 覆盖能力 |
|---|---:|---|
| FineVision | 3.5M | caption、VQA、选择题、bbox |
| RefSpatial | 2.5M | VQA、选择题、pointing、spatial |
| RoboInter-VQA | 1.6M | VQA、选择题、pointing、bbox、trajectory、spatial、planning |
| RoboPoint | 1.3M | VQA、pointing、bbox、spatial |
| RoboAfford | 765K | VQA、pointing、bbox、affordance |
| Robo2VLM | 678K | VQA、选择题 |
| ShareRobot | 13K | VQA、bbox、affordance、trajectory、planning |

### Table 5：主训练配置

| Hyperparameter | Pre-training | Post-training |
|---|---:|---:|
| Camera / resolution | head / 384² | head+chest / 640×480 |
| GPUs | 128 A800 | 96 A800 |
| Global batch | 4608 | 384 |
| Steps | 175K | 60K |
| LR (VLM/AE/WM) | 1e-4/3e-4/3e-4 | 1e-5/3e-5/3e-5 |
| Freeze VLM / warmup | 5000 / 2000 | 0 / 2000 |
| Time | 164 h | 29 h |

### Table 6：DAgger 分任务结果

| Task | DG | FT |
|---|---:|---:|
| Stack tableware | 80% | 50% |
| Close laptop | 70% | 10% |
| Place phone on stand | 50% | 0% |
| Flip cup | 50% | 30% |
| **Average** | **62.5%** | 22.5% |

### Table 7：预训练规模

| Task | Scratch | 3K | 6K | 9.6K |
|---|---:|---:|---:|---:|
| Grasp object | 80 | 80 | 70 | 100 |
| Hand over object | 70 | 80 | 80 | 100 |
| Place items into container | 40 | 80 | 90 | 100 |
| Point at object | 20 | 40 | 60 | 70 |
| Place toy chick into slot | 30 | 0 | 20 | 40 |
| Pull out tissue | 60 | 20 | 50 | 80 |
| Push ball into box | 0 | 0 | 10 | 20 |
| Put garbage into trash bin | 0 | 60 | 30 | 30 |
| Stack paper cups | 0 | 20 | 10 | 40 |
| Stack tableware | 0 | 20 | 10 | 20 |
| **Average** | 30 | 40 | 43 | **60** |

### Table 8：强基线逐任务对比

| Task | EgoSteer | Being-H0.5 | π0.5 |
|---|---:|---:|---:|
| Grasp / hand over / into container | 100/100/100 | 80/60/50 | 80/20/0 |
| Pour / bread / tissue | 50/70/80 | 30/80/10 | 0/40/30 |
| Orientation / eraser / trash / tennis | 30/90/30/90 | 30/50/0/0 | 30/20/0/0 |
| **Average** | **74** | 39 | 22 |

### Table 9：训练组件消融

| Variant | Average |
|---|---:|
| No WM objective | 31% |
| No training RTC | 39% |
| Noisy data | 33% |
| **Full** | **44%** |

逐任务结果波动较大：例如无 WM 在“贴白板擦”达 80%，无 RTC 在“网球入桶”达 90%，均高于 full；因此该表支持的是整体平均趋势，而不是每个技能都一致受益。

### Table 10：消融训练配置

| 配置 | Pretrain steps | Post-train steps | GPU / batch |
|---|---:|---:|---|
| Full / no WM / no RTC / noisy | 30K / 80K / 30K / 20K | 均 60K | 均 64 A800 / 1152 |

### Table 11：长程少样本微调

| Hyperparameter | Box-Folding | Cake-Unboxing |
|---|---:|---:|
| Checkpoint | EgoSteer-9.6K@155K | 同左 |
| GPUs / batch | 8 A800 / 144 | 8 A800 / 144 |
| Steps | 44K | 12K |
| Demonstrations | 120 | 229 |
| Success | 75% | 83% |

---

## 实验判断

### 最可信的证据

- 所有 VLA 基线都在作者的同一机器人数据上后训练，EgoSteer 仍有 74% vs 39%/22% 的差距。
- DAgger 用少量失败状态纠错把四任务平均成功率从 22.5% 提至 62.5%，效果大且机制直接。
- 数据规模、数据清洗、世界模型和 RTC 均有消融。

### 需要谨慎的地方

- 每任务通常只有 10 次 randomized trials，置信区间很宽；大量 10% 粒度结果不适合过度排序。
- baseline 并非在完全对等架构、分辨率与部署优化下比较，论文自己也强调这些差异；因此 74% vs 39%/22% 是“全栈系统”优势，不能归因于世界模型单模块。
- 9.6K 小时数据中 Egocentric-100K 占 83.8%，广度主要来自单一来源；“数据规模”与“来源分布”纠缠。
- 训练规模极大（主预训练 128×A800、164 小时），公开权重使使用成为可能，但从头复现成本非常高。

---

## 批判性思考

### 优点

1. 正视 VLA 落地是数据—模型—控制—纠错的系统问题。
2. 人类与机器人统一为腕姿态和指尖关键点，跨具身接口干净、可解释。
3. 世界模型只在训练期使用，改善表征而不增加部署延迟。
4. DAgger 接管机制专门处理失败分布，比继续堆离线成功轨迹更有效。

### 局限性

1. 真实机器人评测次数少、平台仅两种，且主要结果集中于 RealMan。
2. 依赖昂贵 VLM 标注与 Any4D/DPVO/MANO 链路，自动标签误差可能形成系统性偏差。
3. 指尖关键点动作空间不能直接表达力、触觉和接触状态。
4. 论文未把“视觉未来预测是否真的改善因果动作想象”与一般辅助表征正则化严格区分。

### 可复现性评估

- [x] 官方代码仓库与 Apache-2.0 许可证
- [x] 训练、评测、部署代码与配置
- [x] Base 与 RealMan 权重
- [ ] 论文使用的完整 9.6K 小时加工后语料可直接获得
- [x] 环境、Docker、示例数据与运行命令
- [ ] 论文训练随机种子与全部真实机器人评测资产/协议

---

## 研究判断

### 作者思考路径重建

1. 通用 VLA 的 steerability 需要语言覆盖和任务多样性，但双灵巧手机器人数据最难规模化。
2. 第一视角人类视频规模大、视角与操作天然相关，却缺少可用于控制的世界系动作和语言。
3. 先前 HaWoR/EgoScale/Being-H 系列证明人类视频预训练有价值，但数据加工吞吐、尺度漂移和跨具身对齐仍限制扩大规模。
4. 即使预训练提供先验，机器人部署仍会遇到训练数据之外的失败状态；因此需要共享控制栈和低成本接管。
5. VLA 若只对当前观察到动作做映射，精细接触中的未来后果建模不足；用训练期潜空间世界模型可让 backbone 对动作诱导变化敏感。

### 核心 Intuition

人类视频负责提供“语言说什么、手大概怎样与物体交互”的广覆盖先验，少量机器人数据负责把这种先验落到具体动力学与硬件。失败后的人工接管专门填补策略自身诱导出的状态分布；未来潜特征预测则迫使视觉语言表征保留与动作后果有关的信息。

### 最脆弱假设

**假设**：腕姿态 + 15D 指尖关键点是足以连接人类操作和不同机器人具身的共同动作语言。

**为什么脆弱**：同一几何轨迹在不同手的关节限制、接触力、顺应性和摩擦下可能导致完全不同结果；接触丰富任务尤其不能只靠几何。

**论文证据**：两种具身上实现长程任务、RealMan 上覆盖七类操作，支持一定可迁移性；但仅两个平台、没有触觉/力控压力测试，也没有在显著不同手型与动力学上做统一接口对照。

### 最小复现实验

- **目标 claim**：人类视频预训练 + 统一关键点动作空间能提升新任务的样本效率。
- **数据/环境**：选 3 个 ManiSkill/IsaacLab 双手任务；生成 100–500 小时第一视角人手/类人轨迹与每任务 50 条机器人示范。
- **最小实现**：冻结同一视觉语言 backbone，只比较 scratch、普通动作预训练、统一腕+指尖预训练三组；不复现 EgoSmith 全流水线。
- **指标**：10/25/50 条机器人示范下 success、progress、恢复次数；固定 100 个随机种子 rollout。
- **支持/反驳标准**：统一空间组在三档数据上均显著提高成功率且优势在接触任务不消失则支持；若只提升视觉相似的 PnP、接触任务无收益或负迁移，则反驳强 claim。

### 最强反例设计

构造“几何轨迹相同、接触动力学不同”的跨具身任务：更换指尖材质/摩擦、关节顺应性和物体质量，而相机与指尖路径保持相近。比较 EgoSteer 的统一关键点策略与显式触觉/力条件策略。如果 EgoSteer 在几何观察不变时系统性失败，说明所谓跨具身先验主要学到运动学外观匹配，而非可迁移的操作知识。

### Follow-up Research Idea

**驱动局限/需求**：统一几何动作空间缺少接触等价性。

**新 framing**：把 human-to-robot transfer 定义为“接触事件与可实现效果的等价类对齐”，而不是轨迹对齐；动作表示为目标接触图、指尖 wrench 区间和物体状态变化，再由 embodiment-specific controller 实现。

**可借鉴工具**：接触图预测、tactile foundation model、object-centric world model、可微/学习型接触动力学。

**第一个实验**：在倒水、插入、擦拭三类任务上，只改变摩擦与顺应性，比较几何 action token 和 contact-effect token 的零样本/少样本迁移。

### 开源情况怎么样

- **代码**：官方已发布 [EgoSteer](https://github.com/egosteer/egosteer)、[EgoSmith](https://github.com/egosteer/egosmith) 和 [Robot Stack](https://github.com/egosteer/robot-stack)，EgoSteer 为 Apache-2.0；包含训练、评测、WebSocket 部署、Docker/conda 环境、配置和小型示例数据。
- **权重**：官方 Hugging Face 已发布 [EgoSteer-3B-Base](https://huggingface.co/EgoSteer/EgoSteer-3B-Base) 与 [EgoSteer-3B-RealMan](https://huggingface.co/EgoSteer/EgoSteer-3B-RealMan)。
- **数据集**：EgoSmith 代码已发布，但完整 9.6K 小时成品语料由 12 个来源组成，各源许可证/访问条件不同；官方代码库提供示例数据和转换流程，不能视为完整训练语料已一键公开。
- **可复现性结论**：**部分可复现**。模型训练/微调/离线评测链路和权重较完整，可在自有数据上使用；从头复现论文主模型需要 128 A800×164h、完整多源原始数据与加工流程，且真实机器人硬件、随机种子及全部评测资产不完整。
- **证据与核验日期**：[项目页](https://egosteer.github.io/)、[官方策略仓库](https://github.com/egosteer/egosteer)、[论文](https://arxiv.org/abs/2607.09701)，核验于 2026-07-25。

### 信息来源标注

- **论文原文明确声称**：9.6K 小时/12 数据集、187 小时/193 机器人任务、40 任务 75%、各消融和少样本结果。
- **相关文献中的已有结论**：EgoScale、Being-H 系列等已表明第一视角人类视频预训练可提供灵巧操作先验。
- **基于证据的合理推断**：性能提升是全栈协同结果，不能只归因于世界模型；DAgger 的主要价值来自覆盖策略诱导失败状态。
- **仍然不确定的猜测**：DINOv3 未来预测学到的是因果动作想象，还是一般性的时序表征正则；需要针对替代辅助目标的对照。

---

## 关联笔记

### 基于

- [[DAgger]]：针对策略访问状态收集纠错数据。
- [[Flow Matching]]：动作专家的连续生成目标。
- [[World Model]]：未来潜空间辅助监督。
- [[DINOv3]]：未来视觉特征教师。

### 对比

- [[Pi05]]：人类视频预训练 VLA 强基线。
- [[Being-H0.5]]：human-centric robot learning 基线。
- [[Diffusion Policy]]：少样本长程任务基线。

### 方法相关

- [[Dexterous Manipulation]]
- [[Action Chunking]]
- [[Human-in-the-loop]]
- [[Real-Time Chunking]]
- [[First-Person Video]]

---

## 速查卡片

> [!summary] EgoSteer
> - **核心**：人类第一视角数据规模化预训练 + 机器人 grounding + 失败状态 DAgger。
> - **方法**：Qwen3-VL + flow action expert + 训练期 DINOv3 world-model expert + RTC。
> - **结果**：40 任务 75%；10 任务 74% vs 39%/22%；长程少样本 75%/83%。
> - **代码**：https://github.com/egosteer/egosteer

---

*笔记创建时间：2026-07-25*
