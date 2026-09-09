---
title: "ω-0: A Latent Predictive World Action Model for Concurrent Humanoid Loco-Manipulation"
method_name: Omega0
authors: [Zhe Li, Zhenzhe Zhang, Yangyang Wei, Wenjie Zhang, Xichen Yuan, Peiyuan Zhi, Gen Li, Xinying Guo, Fengjie Gao, Jianfei Yang, Shanghang Zhang]
year: 2026
venue: arXiv
tags: [world-action-model, humanoid, loco-manipulation, latent-prediction, human-to-robot]
zotero_collection: 世界模型/WM+humanoid
image_source: mixed
arxiv_html: https://arxiv.org/html/2608.06375v2
created: 2026-09-09
---

# 论文笔记：ω-0

## 元信息

| 项目 | 内容 |
|---|---|
| 机构 | NTU MARS Lab、北京大学、BAAI、HKUST(GZ) |
| 版本 | arXiv v2，2026-08-09；全文含附录 39 页 |
| Zotero | item 2034，世界模型/WM+humanoid |
| 项目主页 | https://gentlefress.github.io/OMEGA-0_page/ |
| 对比基线 | ACT、Diffusion Policy、π0.5、InternVLA-M1、EgoVLA、GR00T-N1.7、ψ0、Fast-WAM、DiT4DiT |
| 原文 | https://arxiv.org/html/2608.06375v2 |
| 数据 | https://huggingface.co/datasets/keycharon/omega-HOME |

## 一句话总结

> 用未来视觉 latent 监督全身动作生成，让人形机器人在移动中持续操作。

## 核心贡献

1. 将 [[World Action Model|世界动作模型]] 用于同时移动与操作，以紧凑未来视觉特征监督动作生成。
2. 通过人体运动格式统一、SONIC 仿真回放及可跟踪性筛选，把人类示范转成机器人可执行的 [[Latent Action|动作 latent]]。
3. 提供 ω-HOME 数据集与单模型、多任务实机结果。注意发布状态与论文声称的六模态完整性是两个问题，见研究判断。

## 问题背景

### 要解决的问题

擦大桌子、拖地、从低处取衣物需要腿部移动、躯干姿态、双臂接触与平衡连续协同。作者关注 concurrent loco-manipulation，而不是只把“走到目标”和“站定操作”串起来。

### 现有方法的局限

作者指出，机械臂导向的 VLA 缺少统一全身动作接口；视频为中心的 WAM 又可能把视频时序误差带入控制，并增加推理负担。这是作者对相关工作的归纳，不能理解为所有既有模型都不能同步移动与操作。

### 本文的动机

未来场景反映接触、目标接近与任务进展，但控制未必需要生成高保真的完整视频。可以让未来预测塑造动作表示，再用已有全身控制器实现可执行性。

## 方法详解

### 模型架构

- 输入：当前视角图像、语言指令、47 维机器人状态；用视角 token 区分 ego/exo。
- 语义特征：Qwen3-VL-2B-Instruct 经全身动作预训练后的隐藏表示。
- 当前视觉：冻结的 [[V-JEPA]] 2.1 编码器；语言额外经 T5 编码。
- 联合预测器：prefix、motion queries、video queries；运动查询读取视觉查询，形成含未来信息的动作条件。
- 动作头：[[Diffusion Transformer]] 采用 x0 预测，生成 25 步动作块。
- 输出：每步 66 维，即 SONIC 全身 latent 64 维与左右手各 1 维开合命令。手部值范围为 0–1，不能因此称为直接预测全部灵巧手关节。
- 执行：SONIC 低层控制器驱动 G1；使用 [[Action Chunking]] 和 [[Real-Time Chunking]]。
- 参数量：明确给出 VLM 为 2B；完整系统总参数未明确报告。

### 核心模块

#### Stage 1：全身动作语义预训练

把公开数据中的 SMPL-X/SMPL-H 转为 [[SMPL]]，以 [[FAST Action Tokenizer]] 将连续全身运动转为离散标签，再训练 VLM 根据图像与语言预测动作 token。后续阶段使用隐藏特征作为条件；部署动作并非直接由这些离散 token 逐个解码得到。

数据来自 ARCTIC、Xperience-10M、Motion-X。原文将 tokenizer 描述为以 L1 重建误差优化的 FAST tokenizer；具体实现细节仍需代码确认。

#### Stage 2：人类运动到机器人 latent

先统一 z-up 坐标、首帧 yaw，再用 SONIC 回放运动，记录机器人状态与控制器 latent，丢弃无法可靠跟踪的运动。可跟踪人体运动不等价于在目标物体上能维持正确接触，论文没有完整证明这一迁移环节保留所有交互语义。

prefix 汇合 VLM、T5、视角与当前视觉特征。两组 queries 分别读取 prefix，之后 motion queries 读取 video queries。未来监督来自冻结的 **Wan encoder**，不是 V-JEPA 的未来特征；V-JEPA 用于当前观测。

动作头以未来感知运动特征、语言与状态为条件，去噪预测干净动作 latent。动作 MSE 与未来视觉 MSE 联合训练。VLM、V-JEPA、Wan 冻结。

#### Stage 3：真实数据微调与连续执行

用 11 个下游任务约 2220 条真实轨迹联合微调同一个策略。训练时随机选择 0–8 步干净动作前缀，仅在剩余部分计算动作损失，以学习在已有动作上下文后继续执行。

部署每次预测 H=25 步，执行 K=8 步，缓存上次未执行片段作为下次前缀，并对重叠部分线性混合。64 维 latent 用均值标准差归一化，状态和两维手部命令用 min-max。

#### 两个需要澄清的部署细节

1. 正文 motion queries 显式读取 video queries；附录又说未来视觉分支不是实时控制必需。可以确定无需像素视频解码，但是否连内部 video queries 一起裁掉并不清楚，不能自行补成完整部署实现。
2. 附录称前向约 0.14 秒、可超过 7 Hz；这描述前向吞吐能力。数据记录为 30 Hz，而每轮执行 8 步，若动作也按 30 Hz 串行执行，更新时间还包含执行调度，不能直接等同于闭环稳定运行 7 Hz。异步实现、部署硬件与精确时序尚待确认。

## 关键公式

完整收录正文与附录的 27 个展示公式，以及行内评测公式，位于本文末尾“公式完整摘录”。每个公式附用途与符号解释。

最重要的关系是：视觉预测 MSE 约束 video queries，motion queries 经交叉注意力读取它们，动作 DiT 再输出可执行 latent。系统没有展示基于候选动作反事实 rollout 的规划搜索。

## 关键图表

文末完整收录 Figure 1–35、Table 1–16 与 Algorithm 1。Figure 2 是方法核心，Table 2 是总体结果，Table 4 是消融，Tables 6–16 是 Ego 逐试次标注；Figure 12–35 是数据任务图集。

### 主要结果解读

| 方法 | SR % | Score /41 | Progress % |
|---|---:|---:|---:|
| ψ0 | 44.5 | 23.6 | 59.6 |
| DiT4DiT | 43.6 | 23.1 | 61.0 |
| ω0 Ego | 79.1 | 35.8 | 88.7 |
| ω0 Omni | 81.8 | 36.7 | 90.3 |

Omni 在五个移动需求较强的任务上使用第三人称输入，其余用第一人称。因此 81.8% 不能当成纯机载第一人称结果，也不能仅解释成训练期多视角监督带来的收益。Ego 更适合评价纯第一人称部署。

Table 3 的额外 ω-HOME 预训练把 Ego 的 SR 从 79.1 提至 80.4，Omni 从 81.8 提至 82.4。不要与 Table 2 的基础结果混为同一设置。

### 消融解读

| 配置 | SR % | 相对 Full Ego 差值（百分点） |
|---|---:|---:|
| Full Ego | 79.1 | 0 |
| 去掉机器人状态 | 60.9 | -18.2 |
| 去掉 VLM prefix | 66.4 | -12.7 |
| 去掉 video queries | 64.5 | -14.6 |
| 去掉 RTC | 71.8 | -7.3 |
| 当前编码器换 Wan | 63.6 | -15.5 |

去掉 video queries 时同时移除视觉损失和 motion-to-video attention，因此证明的是整个分支有帮助，尚未隔离未来目标本身、额外参数与注意力结构各自的贡献。

作者还观察到 Wan 当前编码器可以提高离线未来 latent 预测准确性，却降低实机表现。这是“预测误差越小未必控制越好”的直接证据；不能仅用 latent MSE 判断世界模型价值。

## 实验

### 数据集

| 数据 | 规模/用途 | 注意事项 |
|---|---|---|
| ARCTIC、Xperience-10M、Motion-X | 人类视觉运动预训练 | 格式统一、人工筛选、SONIC 回放；过滤后规模与精确划分未完整给出 |
| ω-HOME | 40.3h、4827 episodes、24 任务、30 Hz | 论文描述 ego RGB、exo RGB-D、状态、SMPL、动作 latent 等同步信息 |
| 下游真实数据 | 11 任务约 2220 轨迹 | 一模型多任务微调，不是 11 个 zero-shot 新任务 |

### 实现细节

三阶段训练使用 8 张 H100；本文未提供足以重建训练的完整学习率、优化器、batch size、训练步数、随机种子、扩散步数、latent 预测 horizon、loss 权重和配置。部署参数见方法部分；不把 2B VLM 参数量说成全系统参数量。

### 评测口径与可视化结果

每任务每方法 10 次试验。Success Rate 要求全任务完成；Score 对完成的子任务累加、全套最大 41；Progress 按正文声称关注首次不可恢复失败前的有序进度。

附录列出 Ego 的逐试次二值阶段标注，能核对成功率，但主要基线和 Omni 未给等粒度原始表。泛化测试有跨物体 3 个任务、跨场景 2 个、人类迁移 1 个；人类迁移包含额外 fine-tuning，不应叫未训练的直接 zero-shot。

原文存在待澄清口径：正文失败在第 m 阶段写 Progress=m/n，若 m 从 1 编号则通常应为 (m-1)/n；附录 E 又将进度写作完成阶段比例。少数 SR（如表 5 跨场景 79.5%）也不能直接从“2任务各10次”的等权整数成功数推出，需要额外重复试验/平均方式说明。这里只标为复现疑点，不推断数据造假。

## 批判性思考

### 优点

1. 把语言视觉预训练、人类动作迁移、全身控制接口与未来监督整合为能运行的实机系统。
2. 直接预测统一全身 latent，减少高层显式拆分腿部和手部的限制。
3. 消融同时覆盖状态、语义、预测、RTC 与视觉编码器，附录提供动作维度和部分逐试次结果。

### 局限性

1. 强控制器与数据工程贡献很大，跨模型比较不能干净归因于世界建模；GR00T 等基线没有同等 RTC 设置，ψ0 使用另一低层接口。
2. 图像未来预测可能只是示范轨迹进度表示，尚无候选动作反事实预测实验来证明可用于一般规划。
3. 各任务只有 10 次评测，缺少多种子与不确定性；泛化场景数量有限。
4. SONIC 的运动可跟踪性筛选可能系统性排除困难动态运动与接触情形。
5. 代码与权重尚未确认发布，数据预处理与评测细节不够完整。

### 潜在改进方向

保持相同控制器、参数量、数据和 RTC，对比真实未来、当前帧复制、时序打乱、只保留 queries 四种条件；再引入相同外观而不同接触动力学的干预任务，区分语义进度建模与动作后果建模。

### 可复现性评估

- [ ] 官方策略代码与许可证可确认
- [ ] 训练/评测配置完整
- [ ] 策略预训练权重可获取
- [ ] 全部六模态数据、划分、预处理可确认
- [x] 公共数据仓库实际存在，可见视频、metadata 和 state_action.hdf5
- [x] 论文提供训练 GPU 数、动作/状态维度、RTC 主要参数
- [ ] 随机种子、全部评测标注与严格闭环时序完整

## 研究判断

### 作者思考路径重建

【基于证据的推断】已有全身追踪器提供稳定低层接口；大规模人类视频提供视觉运动先验；VLA 对复杂协调缺少未来约束，而视频生成昂贵且视觉保真不保证可执行。将动作语义预训练、控制器空间对齐和轻量未来监督结合，是从这些已有条件出发的合理路径，不能把本文当作发明 latent prediction 或动作分块。

### 核心 Intuition

机器人做下一段动作时，应同时形成对接下来场景变化的预期。让动作表示读取这个预期，有助于持续完成接触、位移和子任务衔接；已有全身控制器负责把高层动作 latent 变成平衡的运动。

### 最脆弱假设

【研究判断】预测的未来特征确实包含可用于当前动作决策的交互后果，而不仅是训练示范的视觉进度捷径。去掉分支后的下降支持“分支有价值”，但缺少动作干预、相同状态不同动作结果、时序打乱与等参数辅助任务实验，不能证明可干预的因果动力学。

### 最小复现实验

【拟议实验，并非已运行】一周内以公开发布的两三个任务、冻结图像与文本特征以及 HDF5 动作标签训练小型条件扩散动作头。固定预算，比较真实未来目标、当前目标复制、同任务打乱未来、无视觉损失但保留全部 queries 四组；至少 3 个种子，按 episode/场景划分。

先测 held-out 动作误差、动作块边界跳变与未来特征误差；若已有 G1/SONIC 平台，再做每组每任务至少 30 次闭环试验，测成功、接触中断与恢复时间。没有机器人/仿真接触环境时，一周实验只能验证表示与离线动作预测，不能声称复现实机主结论。只有真实未来组在控制预算下稳定提升闭环表现，才支持其核心机制。

### 最强反例设计

【拟议实验】对外观相同的抽屉设置锁住/解锁、不同摩擦或隐藏负载，起始图像与姿态近似相同。让机器人执行小幅探测后需要分支决策；评价是否仍照着常见示范预测“门会打开”并持续失败。如果视觉预测很好但动作无法适应，会削弱其模型学到了可用于控制的交互后果这一解释。它不会否定原始分布内的实机成功结果。

### Follow-up Research Idea

【未验证研究设想】把目标从“预测示范未来图像 latent”改成“估计接下来哪种接触模式可达、其失败概率多大”。利用试探动作提供干预信息，联合学习接触状态、可执行性与不确定性；高层选择未来接触模式，SONIC 执行全身运动。

首个实验是同外观不同锁定/负载的门操作：比较无探测、固定探测、自适应探测三组，测成功率、耗时和外力峰值。价值在于任务从模仿惯常未来转向识别当前环境允许的未来，不是简单添加一个模块。

### 开源情况怎么样

核验日期：2026-09-09。

- **代码**：[项目主页](https://gentlefress.github.io/OMEGA-0_page/) 仍写 Code (WIP)，该链接回到本页占位；顶部 GitHub 跳到 GitHub 首页。未确认官方策略训练/评测仓库、代码许可证、运行命令和预训练策略权重。项目网站源码不能当成策略代码发布。
- **数据集**：项目页直接链接 [ω-HOME](https://huggingface.co/datasets/keycharon/omega-HOME/tree/main)，因此可视为官方指向的资源。仓库元数据标 MIT。已核对一个 mop_floor episode 包含 ego.mp4、exo.mp4、session_meta.json、state_action.hdf5，不能说“只公开视频”。但未逐项验证 HDF5 字段、全部 SMPL/深度模态、精确 split 与预处理；README 正文为空，数据平台自动生成的 video train split 不是论文官方评测划分。
- **整体结论：部分可复现**。数据与方法足以进行局部分析/重实现，当前尚不足以按官方配方端到端复现实机结果。缺策略代码、权重、训练配置和完整数据/评测协议。三套公共人类数据各自的许可与访问条件也需要单独核验，不把 ω-HOME 的 MIT 延伸到它们。

### 信息来源标注

- 论文明确声称：架构、三阶段流程、维度、任务数据、主表和消融数值。
- 已有工作：FAST、V-JEPA、Wan、SONIC、RTC 均来自前作；本文将其接入全身 WAM。
- 合理推断：当前证据更支持未来辅助的策略表示，而非可反事实规划的完整世界模型；不同控制器/RTC 妨碍纯机制归因。
- 不确定设想：接触可达性目标、干预数据与主动探测是否更有效，需要上述实验验证。

## 关联笔记

### 基于

- FAST、SONIC、V-JEPA、Wan、RTC：沿用已有组件，本文贡献在训练与全身控制整合。

### 对比

- ψ0：人类数据向 humanoid VLA 迁移，但动作接口与低层控制不同。
- Fast-WAM：同样重视世界建模对动作表示的帮助，不能把“不输出完整视频”单独作为本文独有创新。
- MotionWAM、DiT4DiT：用视频模型特征支持动作生成；本文强调 latent 辅助监督和统一全身输出。

### 方法相关

- [[Latent Predictive Whole-Body Policy]]：本文方法与控制有效性评估的专门概念笔记。

### 硬件/数据相关

G1、SONIC、ZED Mini、第三人称 ZED、Pico 4 Ultra、Inspire DexHands、ω-HOME。

## 速查卡片

> [!summary] Omega0
> - 核心：未来视觉 latent 辅助监督全身扩散策略。
> - 输入：图像、语言、47 维状态。
> - 输出：25×66 动作块，每轮执行前 8 步。
> - 结果：Ego SR 79.1%，Omni 81.8%；去掉未来查询 64.5%。
> - 警惕：Omni 输入不同；消融移除整分支；未来预测不等于反事实规划。
> - 开源：数据部分可用；代码 WIP，未确认策略权重。

*笔记创建时间：2026-09-09；来源为 Zotero 本地完整 PDF 与 arXiv v2，发布状态另作实时核验。*


## 公式完整摘录

以下保留原文 LaTeX；公式中的 K 在不同章节含义不同，应按对应说明阅读。

### 公式 1：[[Latent Predictive Whole-Body Policy|动作编码]]

$$
\mathbf{c}_{1:N}=\mathcal{E}_{\mathrm{act}}(\mathbf{a}_{t:t+H}),
$$

**含义与符号说明**：a 为连续动作轨迹，E_act 为编码器，c 为 N 个离散 token，H 为动作时间窗。

### 公式 2：[[Latent Predictive Whole-Body Policy|动作解码]]

$$
\hat{\mathbf{a}}_{t:t+H}=\mathcal{D}_{\mathrm{act}}(\mathbf{c}_{1:N}).
$$

**含义与符号说明**：D_act 为解码器，c 为动作 token，a-hat 为重建的连续轨迹。

### 公式 3：[[Latent Predictive Whole-Body Policy|Tokenizer 重建损失]]

$$
\mathcal{L}_{\mathrm{tok}}=\left\|\hat{\mathbf{a}}_{t:t+H}-\mathbf{a}_{t:t+H}\right\|_{1}.
$$

**含义与符号说明**：L_tok 为 L1 重建误差，a 为真实轨迹，a-hat 为解码轨迹。

### 公式 4：[[Latent Predictive Whole-Body Policy|VLM 输入拼接]]

$$
\mathbf{x}=[\mathbf{e}^{v},\mathbf{o}^{v}_{t},\ell].
$$

**含义与符号说明**：x 是 token 序列，e^v 是视角标识，o_t^v 是图像，ell 是指令。

### 公式 5：[[Latent Predictive Whole-Body Policy|动作 token 自回归分解]]

$$
p_{\theta}(\mathbf{c}_{1:N}\mid\mathbf{e}^{v},\mathbf{o}^{v}_{t},\ell)=\prod_{i=1}^{N}p_{\theta}(c_{i}\mid c_{<i},\mathbf{e}^{v},\mathbf{o}^{v}_{t},\ell).
$$

**含义与符号说明**：p_theta 是 VLM 概率，c_i 为第 i 个 token，c_<i 为先前 token；其余是输入条件。

### 公式 6：[[Latent Predictive Whole-Body Policy|VLM 交叉熵]]

$$
\mathcal{L}_{\mathrm{vlm}}=-\sum_{i=1}^{N}\log p_{\theta}(c_{i}\mid c_{<i},\ell,\mathbf{o}^{v}_{t},\mathbf{e}^{v}).
$$

**含义与符号说明**：对正确动作 token 的负对数似然求和；N 为 token 总数，theta 为模型参数。

### 公式 7：[[Latent Predictive Whole-Body Policy|机器人状态]]

$$
\mathbf{s}_{t}=[\mathbf{q}_{\mathrm{pos}},\mathbf{q}_{\mathrm{hand}},\mathbf{r}_{\mathrm{torso}}^{6D}].
$$

**含义与符号说明**：s_t 是状态，q_pos 为身体关节，q_hand 为手关节，r_torso^6D 为姿态六维表示。

### 公式 8：[[Latent Predictive Whole-Body Policy|当前视觉编码]]

$$
\mathbf{f}_{t}^{v}=\mathcal{E}_{\mathrm{VJEPA}}(\mathbf{o}_{t}^{v}).
$$

**含义与符号说明**：E_VJEPA 是冻结视觉编码器，o_t^v 是当前视角图像，f_t^v 是特征。

### 公式 9：[[Latent Predictive Whole-Body Policy|Prefix 条件]]

$$
\mathbf{p}=[\mathbf{f}_{\mathrm{vlm}},\mathbf{f}_{\ell},\mathbf{r}^{v},\mathbf{f}_{t}^{v}].
$$

**含义与符号说明**：p 汇集 VLM 特征 f_vlm、T5 特征 f_ell、视角 r^v、当前视觉 f_t^v。

### 公式 10：[[Latent Predictive Whole-Body Policy|位置编码注意力]]

$$
\mathrm{Attn}_{\mathcal{R}}(\mathbf{Q},\mathbf{K},\mathbf{V})=\mathrm{softmax}\left(\frac{\mathcal{R}(\mathbf{Q})\mathcal{R}(\mathbf{K})^{\top}}{\sqrt{d}}\right)\mathbf{V},
$$

**含义与符号说明**：Q/K/V 为查询键值，R 为 1D/2D/3D RoPE，d 为注意力维度。

### 公式 11：[[Latent Predictive Whole-Body Policy|双查询读取前缀]]

$$
\bar{\mathbf{q}}^{m}=\mathrm{CrossAttn}_{m}(\tilde{\mathbf{q}}^{m},\tilde{\mathbf{p}}),\quad\bar{\mathbf{q}}^{v}=\mathrm{CrossAttn}_{v}(\tilde{\mathbf{q}}^{v},\tilde{\mathbf{p}}).
$$

**含义与符号说明**：q^m/q^v 是运动/视觉查询，p 是 prefix；波浪线表示各自 self-attention 后，上划线为 cross-attention 后。

### 公式 12：[[Latent Predictive Whole-Body Policy|运动读取未来视觉]]

$$
\mathbf{h}^{m}=\mathrm{CrossAttn}_{mv}(\bar{\mathbf{q}}^{m},\bar{\mathbf{q}}^{v}),\quad\mathbf{h}^{v}=\bar{\mathbf{q}}^{v}.
$$

**含义与符号说明**：h^m 是最终运动特征，h^v 是视觉预测；CrossAttn_mv 让运动读取视觉查询。

### 公式 13：[[Latent Predictive Whole-Body Policy|未来视觉监督目标]]

$$
\mathbf{y}_{t+1:t+K}^{v}=\mathcal{E}_{\mathrm{Wan}}(\mathbf{o}_{t+1:t+K}^{v}),
$$

**含义与符号说明**：y 为未来特征，E_Wan 为冻结编码器，o_{t+1:t+K} 为未来观测；此 K 是未来视觉窗口，不等于附录执行步数 K。

### 公式 14：[[Latent Predictive Whole-Body Policy|未来视觉预测损失]]

$$
\mathcal{L}_{\mathrm{video}}=\left\|\mathbf{h}^{v}-\mathbf{y}_{t+1:t+K}^{v}\right\|_{2}^{2}.
$$

**含义与符号说明**：L_video 为视觉 MSE，h^v 为预测，y 为 Wan 提取的目标。

### 公式 15：[[Latent Predictive Whole-Body Policy|动作 DiT 条件融合]]

$$
\mathbf{c}_{\mathrm{dit}}=\Phi_{\mathrm{cond}}([\mathbf{h}^{m},\mathbf{f}_{\ell},\mathbf{f}_{s}]).
$$

**含义与符号说明**：Phi_cond 汇合运动 h^m、语言 f_ell、状态 f_s 为 c_dit。

### 公式 16：[[Latent Predictive Whole-Body Policy|扩散前向加噪]]

$$
\mathbf{z}_{\tau}=\sqrt{\bar{\alpha}_{\tau}}\mathbf{z}_{0}+\sqrt{1-\bar{\alpha}_{\tau}}\bm{\epsilon},\quad\bm{\epsilon}\sim\mathcal{N}(0,\mathbf{I}).
$$

**含义与符号说明**：z_0 为干净动作 latent，z_tau 为带噪 latent，alpha-bar 为累积噪声日程系数，epsilon 为标准高斯噪声。

### 公式 17：[[Latent Predictive Whole-Body Policy|干净动作预测]]

$$
\hat{\mathbf{z}}_{0}=\mathcal{D}_{\theta}(\mathbf{z}_{\tau},\tau\mid\mathbf{c}_{\mathrm{dit}}).
$$

**含义与符号说明**：D_theta 为动作 DiT，输入噪声 z_tau、扩散步 tau 与条件 c_dit，输出 z_0-hat。

### 公式 18：[[Latent Predictive Whole-Body Policy|动作去噪损失]]

$$
\mathcal{L}_{\mathrm{action}}=\left\|\hat{\mathbf{z}}_{0}-\mathbf{z}_{0}\right\|_{2}^{2}.
$$

**含义与符号说明**：L_action 比较预测与真实干净动作 latent 的平方 L2 误差。

### 公式 19：[[Latent Predictive Whole-Body Policy|Stage 2 联合目标]]

$$
\mathcal{L}_{\mathrm{stage2}}=\mathcal{L}_{\mathrm{action}}+\lambda_{\mathrm{video}}\mathcal{L}_{\mathrm{video}}.
$$

**含义与符号说明**：lambda_video 是未来监督权重，两个损失分别约束动作和视觉特征。

### 公式 20：[[Latent Predictive Whole-Body Policy|RTC 干净前缀]]

$$
\tilde{\mathbf{z}}_{\tau}^{1:M}=\mathbf{z}_{0}^{1:M},\quad\tilde{\mathbf{z}}_{\tau}^{M+1:H}=\mathbf{z}_{\tau}^{M+1:H}.
$$

**含义与符号说明**：M 为前缀长度，H 为动作窗口；前 M 步保留 z_0，剩余步骤加噪。

### 公式 21：[[Latent Predictive Whole-Body Policy|RTC 后缀损失]]

$$
\mathcal{L}_{\mathrm{RTC}}=\left\|\hat{\mathbf{z}}_{0}^{M+1:H}-\mathbf{z}_{0}^{M+1:H}\right\|_{2}^{2}.
$$

**含义与符号说明**：仅比较 M+1 到 H 的预测和真值，前缀不计入动作损失。

### 公式 22：[[Latent Predictive Whole-Body Policy|Stage 3 联合目标]]

$$
\mathcal{L}_{\mathrm{stage3}}=\mathcal{L}_{\mathrm{RTC}}+\lambda_{\mathrm{video}}\mathcal{L}_{\mathrm{video}}.
$$

**含义与符号说明**：RTC 后缀损失加未来视觉损失；lambda_video 是权重。

### 公式 23：[[Latent Predictive Whole-Body Policy|附录状态格式]]

$$
\mathbf{s}_{t}=[\mathbf{q}_{\mathrm{pos}},\mathbf{q}_{\mathrm{hand}},\mathbf{r}_{\mathrm{root}}^{6D}],
$$

**含义与符号说明**：q_pos、q_hand 与 root 姿态六维表示共同组成 47 维状态；原文 root/torso 名称需结合接口统一。

### 公式 24：[[Latent Predictive Whole-Body Policy|全身 latent 标准化]]

$$
\tilde{\mathbf{z}}=\frac{\mathbf{z}-\bm{\mu}_{z}}{\bm{\sigma}_{z}},
$$

**含义与符号说明**：z 为64维控制器latent，mu_z/sigma_z 为训练集均值/标准差，z-tilde 为归一化值。

### 公式 25：[[Latent Predictive Whole-Body Policy|状态与手命令 min-max]]

$$
\tilde{\mathbf{x}}=\frac{\mathbf{x}-\mathbf{x}_{\min}}{\mathbf{x}_{\max}-\mathbf{x}_{\min}}.
$$

**含义与符号说明**：x 为状态或手命令，x_min/x_max 为训练统计边界，x-tilde 为缩放结果。

### 公式 26：[[Latent Predictive Whole-Body Policy|初始 yaw 归一化]]

$$
\psi_{t}^{\mathrm{norm}}=\psi_{t}-\psi_{0},
$$

**含义与符号说明**：psi_t 是当前根部偏航，psi_0 是首帧偏航，psi_norm 保留相对转向。

### 公式 27：[[Latent Predictive Whole-Body Policy|重叠动作混合]]

$$
\mathbf{a}_{j}^{\mathrm{blend}}=(1-\alpha_{j})\mathbf{a}_{j}^{\mathrm{prev}}+\alpha_{j}\mathbf{a}_{j}^{\mathrm{next}},\qquad\alpha_{j}=\frac{j+1}{O+1},\quad j=0,\ldots,O-1.
$$

**含义与符号说明**：a_prev/a_next 是相邻动作块的对齐重叠段，O 为重叠长度，j 为索引，alpha_j 是线性混合系数。

### 行内评测公式与释义

$$
SR=N_{\mathrm{success}}/10
$$

成功数除以每任务试验数；N_success 为十次试验中完成全部目标的次数。

$$
\mathrm{Progress}=m/n
$$

原文如此表述：n 为有序子任务数，m 为首次失败阶段。若从 1 编号，有 off-by-one 歧义；不能私自修改成已核实协议。

$$
\mathrm{Score}_i=\sum_{j=1}^{n}\mathbf 1[\text{trial }i\text{ completes subtask }j]
$$

此式为对原文文字定义的数学重写（不是新增的原文展示式）；i 为试次，j 为子任务，不强制前缀连续完成。

## 图表完整摘录

来源为 arXiv v2 全文（含附录）。表格按原始行列展开；合并单元格的标签重复填写以避免丢失语义。

### Figure 1

![[assets/Omega0/page1.png]]

**图像来源**：Zotero PDF 第 1 页；保留完整页供对照。

**原文图注**：Figure 1: Overview of $\omega$ -0 and the $\omega$ -HOME dataset. $\omega$ -0 generates whole-body action latents from language, multi-view observations, and robot states, while $\omega$ -HOME provides 40h of multimodal household humanoid demonstrations for training and evaluation.


### Figure 2

![Omega0 Figure 2](https://arxiv.org/html/2608.06375v2/framework.png)

**原文图注**：Figure 2: Overview of $\omega$ -0. We first train a whole-body VLM for action-aware visual-language representation learning, and then use a joint video-action latent predictor to couple future visual latents with whole-body action generation. The predictor uses prefix-guided dual-query attention with token-specific positional encoding: 2D RoPE for visual prefix tokens, 3D RoPE for future video queries, and 1D RoPE for temporal action queries. The action DiT denoises SONIC-compatible whole-body action latents for real-world humanoid control, while the future visual branch provides lightweight latent supervision and optional visualization.


### Figure 3

![Omega0 Figure 3](https://arxiv.org/html/2608.06375v2/dataset.png)

**原文图注**：Figure 3: $\omega$ -HOME dataset statistics and representative multimodal demonstrations.


### Figure 4

![Omega0 Figure 4](https://arxiv.org/html/2608.06375v2/teleop.png)

**原文图注**：Figure 4: Real-robot teleoperation setup. We use a Pico 4 Ultra headset, handheld controllers, Pico trackers, and a ZED Mini camera to capture human head motion, hand commands, lower-body cues, and egocentric observations. The captured signals are retargeted to the humanoid with Inspire dexterous hands for whole-body loco-manipulation data collection.


### Table 1

| # | Task | Scene | Lower-body Involvement |
| --- | --- | --- | --- |
| 1 | Pick an apple and place into a basket | Tabletop | ✗ |
| 2 | Arrange an apple on a shelf | Shelf | ✓ |
| 3 | Pick clothes from bed and throw into basket | Bedroom | ✓ |
| 4 | Move towel from basket to washing machine | Laundry | ✓ |
| 5 | Wipe the table | Tabletop | ✓ |
| 6 | Mop the floor | Living room | ✓ |
| 7 | Pick trash from different heights into handheld bin | Household | ✓ |
| 8 | Pick apple from table, throw into drawer, and close drawer with knee | Tabletop | ✓ |
| 9 | Sweep trash from bed, turn around, and throw into bin | Bedroom | ✓ |
| 10 | Take clothes out of the washing machine | Laundry | ✓ |
| 11 | Retrieve a drink from the fridge | Fridge | ✓ |

**原文表注**：Table 1: Real-world household loco-manipulation task suite. The tasks are designed to evaluate coordinated upper- and lower-body control across tabletop, cleaning, laundry, and object-transfer scenarios.

### Table 2

| Method | Success Rate (%) $\uparrow$ | Score (Maximum 41) $\uparrow$ | Task Progress (%) $\uparrow$ |
| --- | --- | --- | --- |
| Classical imitation learning | Classical imitation learning | Classical imitation learning | Classical imitation learning |
| ACT | 8.2 | 10.6 | 32.4 |
| Diffusion Policy | 15.5 | 14.8 | 40.6 |
| Vision-language-action model | Vision-language-action model | Vision-language-action model | Vision-language-action model |
| $\pi$ -0.5 | 27.3 | 20.9 | 52.8 |
| InternVLA-M1 | 31.8 | 21.8 | 55.6 |
| EgoVLA | 25.5 | 18.6 | 49.1 |
| GR00T-N1.7 | 22.7 | 19.7 | 49.8 |
| Humanoid and world-action model | Humanoid and world-action model | Humanoid and world-action model | Humanoid and world-action model |
| $\psi$ -0 | 44.5 | 23.6 | 59.6 |
| Fast-WAM | 37.1 | 22.3 | 57.8 |
| DiT4DiT | 43.6 | 23.1 | 61.0 |
| $\omega\text{-}0_{\text{Ego}}$ | 79.1 | 35.8 | 88.7 |
| $\omega\text{-}0_{\text{Omni}}$ | 81.8 | 36.7 | 90.3 |

**原文表注**：Table 2: Overall real-world evaluation across 11 household loco-manipulation tasks. All methods are trained on the real-world dataset and evaluated under the same protocol. Success rate measures the fraction of successful trials. Score measures the average number of completed subtasks, with a maximum total score of 41 over the full task suite. Task progress measures the normalized progress before the first unrecoverable failure.

### Figure 5

![[assets/Omega0/page13.png]]

**图像来源**：Zotero PDF 第 13 页；保留完整页供对照。

**原文图注**：Figure 5: Real-world task setup. We evaluate $\omega$ -0 on diverse long-horizon household loco-manipulation tasks involving whole-body motion, locomotion, tool use, articulated-object interaction, and dexterous manipulation. The task instruction is overlaid on each rollout sequence, and key sub-task progress is denoted with orange markers for better visualization. All rollouts are autonomously executed by the learned policy on the real humanoid.


### Table 3

| Variant | w/ $\omega$ -HOME | SR (%) $\uparrow$ | Score $\uparrow$ | Progress (%) $\uparrow$ |
| --- | --- | --- | --- | --- |
| $\omega\text{-}0_{\text{Ego}}$ | ✗ | 79.1 | 35.8 | 88.7 |
| $\omega\text{-}0_{\text{Ego}}$ | ✓ | 80.4 | 36.9 | 89.7 |
| $\omega\text{-}0_{\text{Omni}}$ | ✗ | 81.8 | 36.7 | 90.3 |
| $\omega\text{-}0_{\text{Omni}}$ | ✓ | 82.4 | 37.5 | 91.2 |

**原文表注**：Table 3: Effect of using $\omega$ -HOME as additional real-world humanoid pre-training data.

### Table 4

| Variant | State | VLM Prefix | Video Query | RTC | Image Encoder | SR (%) $\uparrow$ | Score $\uparrow$ | Progress (%) $\uparrow$ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| w/o Robot state | ✗ | ✓ | ✓ | ✓ | V-JEPA | 60.9 | 29.8 | 75.6 |
| w/o VLM prefix | ✓ | ✗ | ✓ | ✓ | V-JEPA | 66.4 | 31.7 | 79.8 |
| w/o Video query | ✓ | ✓ | ✗ | ✓ | V-JEPA | 64.5 | 30.6 | 77.9 |
| w/o RTC | ✓ | ✓ | ✓ | ✗ | V-JEPA | 71.8 | 33.4 | 84.1 |
| Wan as encoder | ✓ | ✓ | ✓ | ✓ | Wan | 63.6 | 30.9 | 77.3 |
| Full $\omega\text{-}0_{\text{Ego}}$ | ✓ | ✓ | ✓ | ✓ | V-JEPA | 79.1 | 35.8 | 88.7 |
| Full $\omega\text{-}0_{\text{Omni}}$ | ✓ | ✓ | ✓ | ✓ | V-JEPA | 81.8 | 36.7 | 90.3 |

**原文表注**：Table 4: Ablation studies of $\omega$ -0 on real-world household loco-manipulation tasks. We evaluate the effect of robot state conditioning, the Whole-Body VLM prefix, future visual latent prediction through video queries, training-time RTC, and the current-image encoder. All variants are trained and evaluated under the same protocol.

### Figure 6

![Omega0 Figure 6](https://arxiv.org/html/2608.06375v2/real_world.png)

**原文图注**：Figure 6: Real-world task setup. We evaluate $\omega$ -0 on diverse long-horizon household loco-manipulation tasks involving whole-body motion, locomotion, tool use, articulated-object interaction, and dexterous manipulation. The task instruction is overlaid on each rollout sequence, and key sub-task progress is denoted with orange markers for better visualization. All rollouts are autonomously executed by the learned policy on the real humanoid.


### Figure 7

![Omega0 Figure 7](https://arxiv.org/html/2608.06375v2/generalization.png)

**原文图注**：Figure 7: Generalization and human-data transfer.We evaluate $\omega$ -0 on out-of-distribution objects and scenes, including novel object appearances, layouts, and household environments. We further fine-tune the model with human demonstration data and deploy it on the real humanoid, where it successfully completes the target tasks.


### Figure 8

![Omega0 Figure 8](https://arxiv.org/html/2608.06375v2/long_horizon.png)

**原文图注**：Figure 8: Real-world long-horizon tasks.


### Table 5

| Generalization Setting | Video Query | SR (%) $\uparrow$ | Score $\uparrow$ | Progress (%) $\uparrow$ |
| --- | --- | --- | --- | --- |
| Cross-object | ✗ | 66.7 | 7.6 | 63.3 |
| Cross-object | ✓ | 83.3 | 11.8 | 90.8 |
| Cross-scene | ✗ | 15.0 | 0.5 | 15.0 |
| Cross-scene | ✓ | 79.5 | 5.5 | 91.7 |
| Human Data Transfer | ✗ | 20.0 | 1.2 | 20.0 |
| Human Data Transfer | ✓ | 60.0 | 2.2 | 74.6 |

**原文表注**：Table 5: Effect of future video latent prediction on generalization. The maximum scores are 13 for cross-object generalization, 6 for cross-scene generalization, and 3 for human-data transfer.

### Algorithm 1：RTC 推理

Algorithm 1 RTC-style Receding-Horizon Inference 1: Initialize previous prefix $\mathbf{p}\leftarrow\emptyset$ 2: Tokenize language instruction once 3: for each policy update step $i$ do 4: Acquire current image $\mathbf{o}_{i}$ and robot state $\mathbf{s}_{i}$ 5: Initialize action chunk noise $\mathbf{z}_{i}\sim\mathcal{N}(0,I)$ 6: if $\mathbf{p}$ is not empty then 7: Replace the first prefix region of $\mathbf{z}_{i}$ with $\mathbf{p}$ 8: end if 9: Predict action chunk $\hat{\mathbf{a}}^{i}_{1:H}$ with $\omega$ -0 10: Execute the first $K$ actions on the robot 11: Store an unexecuted future segment of $\hat{\mathbf{a}}^{i}_{1:H}$ as the next prefix $\mathbf{p}$ 12: Blend overlapping actions between consecutive chunks 13: end for

### Table 6

| put_apple_and_close_drawer | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Correctly grasp the apple | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Transport the apple to the target drawer region | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 3: Place the apple completely inside the drawer | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 4: Fully close the drawer | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |

**原文表注**：Table 6: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on put_apple_and_close_drawer .

### Table 7

| wipe_table | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Correctly grasp the cloth | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Make effective wiping contact with the blue-marked region | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 3: Remove all specified blue marks | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

**原文表注**：Table 7: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on wipe_table .

### Table 8

| pick_garbage | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Stably hold the trash bin with the right hand | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Place the first target object into the bin | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 1 |
| Stage 3: Place the second target object into the bin | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 4: Place the third target object into the bin | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| Stage 5: Keep all target objects inside the bin with no distractor object | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 1 |

**原文表注**：Table 8: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on pick_garbage .

### Table 9

| clean_bed | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Correctly obtain the brush and dustpan | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Sweep all paper balls on the bed into the dustpan | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
| Stage 3: Turn toward the left basket while carrying the paper balls | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
| Stage 4: Dump all paper balls into the basket | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 0 |

**原文表注**：Table 9: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on clean_bed .

### Table 10

| mop_floor | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Correctly grasp the mop | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Make effective mopping contact with the target region | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 3: Remove all specified black water stains | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 1 |

**原文表注**：Table 10: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on mop_floor .

### Table 11

| pick_and_place | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Correctly grasp the apple | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Transport the apple to the fruit-basket opening | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 3: Release the apple and keep it inside the fruit basket | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

**原文表注**：Table 11: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on pick_and_place .

### Table 12

| put_clothes_into_bucket | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Correctly grasp the yellow cloth on the bed | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Transport the yellow cloth above the right white basket | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 3: Place the yellow cloth completely into the white basket | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |

**原文表注**：Table 12: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on put_clothes_into_bucket .

### Table 13

| washing_machine | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Correctly pick up the towel from the basket | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| Stage 2: Transport the towel to the washing-machine opening | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| Stage 3: Place the towel completely inside the washing machine | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |

**原文表注**：Table 13: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on washing_machine .

### Table 14

| arrange_fruit_in_the_closet | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Correctly grasp the apple | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Transport the apple near the target closet cell | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| Stage 3: Align the apple with the specified closet cell | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 1 |
| Stage 4: Stably place the apple into the specified cell | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 1 |

**原文表注**：Table 14: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on arrange_fruit_in_the_closet .

### Table 15

| pick_clothes_from_washing_machine | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Open the washing-machine door | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Completely take out the yellow cloth from the washing machine | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 3: Place the yellow cloth completely into the right box | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 1 |
| Stage 4: Fully close the washing-machine door | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 1 |

**原文表注**：Table 15: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on pick_clothes_from_washing_machine .

### Table 16

| retrieve_from_fridge | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Trial 5 | Trial 6 | Trial 7 | Trial 8 | Trial 9 | Trial 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stage 1: Open the refrigerator door | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Stage 2: Place the first fruit into the left fruit basket | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 |
| Stage 3: Place the second fruit into the left fruit basket | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 |
| Stage 4: Keep both fruits stably inside the fruit basket | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 |
| Stage 5: Fully close the refrigerator door | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 |

**原文表注**：Table 16: Per-trial progress annotations of $\omega\text{-}0_{\text{Ego}}$ on retrieve_from_fridge .

### Figure 9

![[assets/Omega0/page27.png]]

**图像来源**：Zotero PDF 第 27 页；保留完整页供对照。

**原文图注**：Figure 9: Per-task success rate comparison across seven models on 11 real-world household loco-manipulation tasks. Success rate is computed as the percentage of trials in which all progress stages of a task are completed.


### Figure 10

![[assets/Omega0/page27.png]]

**图像来源**：Zotero PDF 第 27 页；保留完整页供对照。

**原文图注**：Figure 10: Per-task task progress comparison across seven models. Task progress measures the normalized fraction of completed progress stages and provides a fine-grained view of partial task completion.


### Figure 11

![[assets/Omega0/page27.png]]

**图像来源**：Zotero PDF 第 27 页；保留完整页供对照。

**原文图注**：Figure 11: Per-task average score comparison across seven models. The score denotes the average number of completed progress stages for each task.


### Figure 12

![Omega0 Figure 12](https://arxiv.org/html/2608.06375v2/arrange_fruit_in_the_closet.png)

**原文图注**：Figure 12: Task card of arrange_fruit_in_the_closet , which evaluates spatial arrangement and precise fruit placement in a closet.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 13

![Omega0 Figure 13](https://arxiv.org/html/2608.06375v2/clean_bed.png)

**原文图注**：Figure 13: Task card of clean_bed , which evaluates tool use, bed cleaning, object sweeping, and whole-body turning.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 14

![Omega0 Figure 14](https://arxiv.org/html/2608.06375v2/mop_floor.png)

**原文图注**：Figure 14: Task card of mop_floor , which evaluates locomotion with tool use and contact-rich floor cleaning.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 15

![Omega0 Figure 15](https://arxiv.org/html/2608.06375v2/wipe_table.png)

**原文图注**：Figure 15: Task card of wipe_table , which evaluates sustained contact-rich tabletop cleaning.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 16

![Omega0 Figure 16](https://arxiv.org/html/2608.06375v2/pick_and_place_apple.png)

**原文图注**：Figure 16: Task card of pick_and_place_apple , which evaluates object grasping, transport, and placement.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 17

![Omega0 Figure 17](https://arxiv.org/html/2608.06375v2/pick_clothes_from_washing_machine.png)

**原文图注**：Figure 17: Task card of pick_clothes_from_washing_machine , which evaluates articulated-object interaction, laundry retrieval, and placement.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 18

![Omega0 Figure 18](https://arxiv.org/html/2608.06375v2/pick_garbage.png)

**原文图注**：Figure 18: Task card of pick_garbage , which evaluates long-horizon object collection and dual-hand coordination.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 19

![Omega0 Figure 19](https://arxiv.org/html/2608.06375v2/put_apple_and_close_drawer.png)

**原文图注**：Figure 19: Task card of put_apple_and_close_drawer , which evaluates tabletop manipulation and drawer operation.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 20

![Omega0 Figure 20](https://arxiv.org/html/2608.06375v2/put_clothes_into_bucket.png)

**原文图注**：Figure 20: Task card of put_clothes_into_bucket , which evaluates deformable-object handling and basket placement.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 21

![Omega0 Figure 21](https://arxiv.org/html/2608.06375v2/put_towel_into_washing_machine.png)

**原文图注**：Figure 21: Task card of put_towel_into_washing_machine , which evaluates towel handling and appliance loading.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 22

![Omega0 Figure 22](https://arxiv.org/html/2608.06375v2/retrieve_from_the_upper_fridge.png)

**原文图注**：Figure 22: Task card of retrieve_from_the_upper_fridge , which evaluates long-horizon object retrieval and refrigerator interaction.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 23

![Omega0 Figure 23](https://arxiv.org/html/2608.06375v2/brush_toilet.png)

**原文图注**：Figure 23: Task card of brush_toilet , which evaluates bathroom cleaning with tool use.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 24

![Omega0 Figure 24](https://arxiv.org/html/2608.06375v2/classify_gadgets.png)

**原文图注**：Figure 24: Task card of classify_gadgets , which evaluates semantic sorting and object classification.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 25

![Omega0 Figure 25](https://arxiv.org/html/2608.06375v2/collect_books.png)

**原文图注**：Figure 25: Task card of collect_books , which evaluates object collection and tabletop organization.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 26

![Omega0 Figure 26](https://arxiv.org/html/2608.06375v2/collect_fruits_from_the_closet.png)

**原文图注**：Figure 26: Task card of collect_fruits_from_the_closet , which evaluates fruit retrieval from structured storage.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 27

![Omega0 Figure 27](https://arxiv.org/html/2608.06375v2/collect_toys_from_the_bed.png)

**原文图注**：Figure 27: Task card of collect_toys_from_the_bed , which evaluates object collection from soft household surfaces.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 28

![Omega0 Figure 28](https://arxiv.org/html/2608.06375v2/fruit_bucket_arrangement.png)

**原文图注**：Figure 28: Task card of fruit_bucket_arrangement , which evaluates fruit arrangement and container organization.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 29

![Omega0 Figure 29](https://arxiv.org/html/2608.06375v2/grab_fruit_bucket.png)

**原文图注**：Figure 29: Task card of grab_fruit_bucket , which evaluates whole-body reaching and container grasping.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 30

![Omega0 Figure 30](https://arxiv.org/html/2608.06375v2/hang_clothes.png)

**原文图注**：Figure 30: Task card of hang_clothes , which evaluates clothes handling and hanging.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 31

![Omega0 Figure 31](https://arxiv.org/html/2608.06375v2/move_table_with_human.png)

**原文图注**：Figure 31: Task card of move_table_with_human , which evaluates human-robot collaborative furniture moving.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 32

![Omega0 Figure 32](https://arxiv.org/html/2608.06375v2/push_chair.png)

**原文图注**：Figure 32: Task card of push_chair , which evaluates furniture interaction and whole-body pushing.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 33

![Omega0 Figure 33](https://arxiv.org/html/2608.06375v2/put_the_beverage_in_the_lower_fridge.png)

**原文图注**：Figure 33: Task card of put_the_beverage_in_the_lower_fridge , which evaluates beverage placement and lower-fridge interaction.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 34

![Omega0 Figure 34](https://arxiv.org/html/2608.06375v2/put_the_bottle_in_the_upper_fridge.png)

**原文图注**：Figure 34: Task card of put_the_bottle_in_the_upper_fridge , which evaluates bottle placement into an upper refrigerator compartment.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。

### Figure 35

![Omega0 Figure 35](https://arxiv.org/html/2608.06375v2/wipe_basin.png)

**原文图注**：Figure 35: Task card of wipe_basin , which evaluates bathroom surface cleaning.

**阅读要点**：ω-HOME 单任务示范图集；展示采集的交互流程与视角，不等同于该任务已作为泛化测试成功。
