---
title: "FAST: Efficient Action Tokenization for Vision-Language-Action Models"
method_name: "FAST"
authors: [Karl Pertsch, Kyle Stachowicz, Brian Ichter, Danny Driess, Suraj Nair, Quan Vuong, Oier Mees, Chelsea Finn, Sergey Levine]
year: 2025
venue: arXiv
tags: [action-tokenization, vision-language-action, robot-policy, autoregressive-model, action-compression]
zotero_collection: 多模态
image_source: online
arxiv_html: https://ar5iv.labs.arxiv.org/html/2501.09747v1
created: 2026-04-29
---

# 论文笔记：FAST: Efficient Action Tokenization for Vision-Language-Action Models

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Physical Intelligence; UC Berkeley; Stanford |
| 日期 | January 2025 |
| 项目主页 | https://pi.website/research/fast |
| 对比基线 | [[OpenVLA]]; [[Diffusion Policy]]; π0 diffusion VLA; FSQ tokenizer |
| 链接 | [arXiv](https://arxiv.org/abs/2501.09747) / [arXiv HTML](https://ar5iv.labs.arxiv.org/html/2501.09747v1) |

---

## 一句话总结

> FAST 用 DCT+BPE 压缩动作块，让自回归 VLA 能高效学习高频灵巧控制。

---

## 核心贡献

1. **指出高频动作 tokenization 的核心瓶颈**: 常见 per-dimension、per-timestep binning 在高频控制下会产生强时间相关 token，使 next-token objective 的边际信息量很低，模型容易学到“复制上一个动作”的局部解。
2. **提出 FAST 动作 tokenizer**: 先用 [[Discrete Cosine Transform]] 把动作块变到频域，再量化稀疏系数，并用 [[Byte Pair Encoding]] 做无损序列压缩，得到更短、更高信息量的离散动作 token。
3. **发布 FAST+ 通用 tokenizer**: 在 1M 条真实机器人动作轨迹上训练 [[FAST+]]，覆盖多种 embodiment、动作空间和控制频率，可以作为黑盒 tokenizer 接入 [[Vision-Language-Action Model]]。
4. **扩展自回归 VLA 的可用范围**: 与 π0 结合得到 π0-FAST，在 10k 小时机器人数据上训练，性能接近 diffusion VLA，但训练时间最多减少 5x。

---

## 问题背景

### 要解决的问题

[[Vision-Language-Action Model]] 通常把连续机器人动作离散成 token，再像语言模型一样自回归预测动作序列。问题是机器人控制常需要输出 [[Action Chunking|动作块]] $a_{1:H}$，高频动作块里的相邻动作高度相关。朴素 binning 会把每个时间步、每个维度都独立离散化，得到很长的 token 序列。

### 现有方法的局限

朴素 [[Action Tokenization]] 在低频数据上可用，但在高频灵巧任务中会失效：

- token 数随控制频率和动作维度线性增长，训练和推理都变慢。
- 相邻 token 的差异很小，next-token loss 很容易通过复制前一 token 降低。
- 对 DROID 这类较高频、真实场景、多任务数据，OpenVLA 风格 tokenizer 难以有效拟合。

### 本文的动机

作者把动作序列视作连续时间信号：高频动作虽然 token 多，但多数信息集中在低频结构里。因此应先做时间序列压缩，再离散成 token。这个思路类似 NLP 里的 [[Byte Pair Encoding]]：不是让模型逐个预测冗余字符，而是把高频模式合并成更高信息密度的 token。

---

## 方法详解

### 模型架构

FAST 本身不是新的 VLA backbone，而是可插拔的 [[Action Tokenization]] 模块：

- **输入**: 观测 $o$、语言指令 $l$、状态 $s$，以及训练时的动作块 $a_{1:H}$。
- **Backbone**: 论文实验接入 [[OpenVLA]] 风格模型和 π0 VLA。
- **核心模块**: [[Discrete Cosine Transform]] 用于时间序列压缩，[[Byte Pair Encoding]] 用于离散 token 序列压缩。
- **输出**: 用于自回归预测的动作 token $[T_1,\ldots,T_n]$，解码后恢复连续动作块 $a_{1:H}$。
- **FAST+**: 在 1M 真实机器人 action trajectories 上训练 BPE 字典，作为跨 embodiment 的通用动作 tokenizer。

### FAST Tokenizer

#### 模块1: 分位数归一化

**设计动机**: 不同机器人、动作空间和控制频率的动作尺度差异很大，直接做频域变换会让大尺度维度主导 token 分布。

**具体实现**:
- 对每个动作维度，用训练集第 1 和第 99 分位数映射到 $[-1,1]$。
- 使用分位数而不是 min/max，降低异常动作对量化范围的影响。

#### 模块2: DCT 频域压缩

**设计动机**: 机器人动作轨迹通常平滑，低频成分能解释大部分形状，高频成分多是细节或突变。

**具体实现**:
- 对每个动作维度独立应用 [[Discrete Cosine Transform]]。
- 对 DCT 系数执行 scale-and-round 量化，得到稀疏整数矩阵。
- scale 控制重建误差和压缩率之间的 trade-off。

#### 模块3: 频率优先 flatten + BPE

**设计动机**: DCT 后矩阵很稀疏，需要把稀疏系数压缩成短 token 序列。

**具体实现**:
- 将 $|A|\times H$ 的 DCT 系数矩阵展平成整数序列。
- 采用低频优先顺序，让不同动作维度的低频成分更靠近，便于 BPE 合并常见模式。
- 用 [[Byte Pair Encoding]] 训练固定词表，把整数序列压缩成动作 token。

#### 模块4: FAST+

**设计动机**: 单数据集训练 tokenizer 会限制泛化，VLA 需要跨机器人、跨动作空间的 tokenizer。

**具体实现**:
- 使用约 1M 真实机器人动作轨迹训练 BPE 字典。
- 训练混合包含单臂、双臂、移动平台、关节空间、末端空间、相机坐标系动作，频率覆盖 5-50 Hz 等。
- 输入动作统一 pad 到 32 维，以适配不同动作维度。

---

## 关键公式

### 公式1: [[Action Tokenization|动作 tokenization 目标]]

$$
T_a: a_{1:H}\rightarrow [T_1,\ldots,T_n],\quad T_i\in |V|
$$

**含义**: 把长度为 $H$、维度为 $|A|$ 的连续动作块映射到长度可变的离散 token 序列。

**符号说明**:
- $a_{1:H}$: 未来 $H$ 步连续动作。
- $T_a$: 动作 tokenizer。
- $T_i$: 第 $i$ 个离散动作 token。
- $|V|$: 动作 token 词表大小。
- $n$: tokenized action sequence 长度，可随动作序列变化。

### 公式2: [[Discrete Cosine Transform|FAST 频域变换]]

$$
C_j^i=\operatorname{DCT}(a_{1:H}^i)_j
$$

**含义**: 对第 $i$ 个动作维度的时间序列做 DCT，得到第 $j$ 个频率系数。

**符号说明**:
- $a_{1:H}^i$: 第 $i$ 个动作维度在动作块内的时间序列。
- $C_j^i$: 第 $i$ 维动作在第 $j$ 个频率上的 DCT 系数。
- $j$: 频率索引，低 $j$ 对应低频成分。

### 公式3: [[Action Tokenization|DCT 系数量化]]

$$
\bar{C}_j^i=\operatorname{round}(\gamma C_j^i)
$$

**含义**: 用缩放系数 $\gamma$ 控制 DCT 系数量化精度。较大的 $\gamma$ 通常重建误差更小但 token 更多，较小的 $\gamma$ 压缩更强但损失更大。

**符号说明**:
- $\bar{C}_j^i$: 量化后的整数频域系数。
- $\gamma$: scale-and-round 的缩放系数。

### 公式4: [[Byte Pair Encoding|BPE 压缩]]

$$
[T_1,\ldots,T_n]=\Phi(\operatorname{flatten}(\bar{C}))
$$

**含义**: 将量化后的稀疏 DCT 系数矩阵展平，并用 BPE 字典 $\Phi$ 编码成短 token 序列。

**符号说明**:
- $\bar{C}$: 量化后的 DCT 系数矩阵。
- $\operatorname{flatten}$: 频率优先的矩阵展平操作。
- $\Phi$: BPE tokenizer / dictionary。

### 公式5: [[Discrete Cosine Transform|动作反解码]]

$$
\hat{a}_{1:H}^i=\operatorname{IDCT}\left(\frac{\operatorname{reshape}(\Phi^{-1}([T_1,\ldots,T_n]))^i}{\gamma}\right)
$$

**含义**: 推理时先用 BPE 反解码 token，再反量化、reshape 为频域矩阵，最后 IDCT 恢复连续动作块。

**符号说明**:
- $\Phi^{-1}$: BPE 反解码。
- $\operatorname{reshape}$: 将展平序列恢复为每个维度的频域系数。
- $\operatorname{IDCT}$: inverse DCT。
- $\hat{a}_{1:H}^i$: 重建得到的第 $i$ 个动作维度轨迹。

---

## 关键图表

### Figure 1: FAST 总览

![Figure 1](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/figures/convergence_2.jpg)

**说明**: FAST 用时间序列压缩 tokenization 训练自回归 VLA，得到 π0-FAST。它在灵巧和长时程 manipulation 任务上接近 diffusion π0，但训练约 5x 更快。

### Figure 2: FAST vs OpenVLA-style binning

![Figure 2](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x1.png)

**说明**: 左侧展示 FAST 接入自回归 Transformer 的训练方式；右侧显示控制频率越高，FAST 相比朴素 binning 的优势越明显。

### Figure 3: 采样率 toy study

![Figure 3](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/figures/case_study.png)

**说明**: 在插值任务中，朴素 tokenization 随采样率提升而 MSE 急剧上升，甚至退化为复制初始动作；FAST 在不同采样率下保持较好预测。

### Figure 4: FAST tokenization pipeline

![Figure 4](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x2.png)

**说明**: 动作块先归一化，再 DCT 到频域，量化为稀疏矩阵，按低频优先展平，最后 BPE 压缩为动作 token。

### Algorithm 1: FAST Tokenizer

| 步骤 | 操作 | 作用 |
|------|------|------|
| 1 | $C_j^i\leftarrow\operatorname{DCT}(a_{1:H}^i)$ | 逐动作维度计算频域系数 |
| 2 | $\bar{C}_j^i\leftarrow\operatorname{round}(\gamma C_j^i)$ | 量化 DCT 系数 |
| 3 | $z\leftarrow\operatorname{flatten}(\bar{C})$ | 低频优先展平稀疏矩阵 |
| 4 | $[T_1,\ldots,T_n]\leftarrow\Phi(z)$ | BPE 压缩为动作 token |

**说明**: 这是 FAST 的核心算法。它的唯一学习部分是 BPE 字典，DCT 与量化都是解析操作。

### Figure 5: 评估环境

![Figure 5](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/figures/environments.jpg)

**说明**: 论文测试 7 个评估环境，包括 6 个真实机器人任务和 1 个仿真任务，覆盖桌面整理、T-shirt folding、grocery bagging、toast out of toaster、laundry folding 和 DROID 等。

### Table I: 平均 token 数和压缩率

| Dataset | Action Dim | Control Frequency | Avg. Token Naive | Avg. Token FAST | Compression |
|---------|------------|-------------------|------------------|-----------------|-------------|
| BridgeV2 | 7 | 5 Hz | 35 | 20 | 1.75 |
| DROID | 7 | 15 Hz | 105 | 29 | 3.6 |
| Bussing | 7 | 20 Hz | 140 | 28 | 5.0 |
| Shirt Fold | 14 | 50 Hz | 700 | 53 | 13.2 |

**说明**: 高频和高维动作下，FAST 的压缩收益更明显。Shirt Fold 中朴素方法每秒动作块约 700 token，FAST 约 53 token。

### Figure 6: 不同 tokenizer 的策略性能

![Figure 6](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x3.png)

**说明**: FAST 和 FSQ 等压缩型 tokenizer 明显优于朴素 binning；但 FSQ 在需要高精度重建的任务上不如 FAST 稳定。

### Figure 7: DROID zero-shot 环境泛化

![Figure 7](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x4.png)

**说明**: 同一个 DROID policy checkpoint 能在三个大学校园的新场景中 zero-shot 执行简单桌面任务，说明 FAST 使自回归 VLA 能真正拟合 DROID 这类 in-the-wild 数据。

### Figure 8: FAST+ 通用 tokenizer

![Figure 8](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x5.png)

**说明**: FAST+ 在训练时未见过的多种机器人数据集上也能获得高压缩率，覆盖单臂、灵巧手、UMI、humanoid 和 navigation 数据。

### Figure 9: π0 diffusion vs π0-FAST 单任务训练

![Figure 9](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x8.png)

**说明**: 小数据集上 diffusion π0 和 π0-FAST 接近；大数据集如 Table Bussing 上，π0-FAST 收敛更快；DROID 上自回归 FAST 能达到可用泛化，而朴素 tokenizer 不行。

### Figure 10: Laundry Folding rollout

![Figure 10](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x9.png)

**说明**: 展示 π0-FAST 在 laundry folding 上的长时程 rollouts，任务需要从篮子中取出衣物、展开、折叠和堆叠。

### Figure 11: π0-FAST vs diffusion π0 generalist policy

![Figure 11](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x10.png)

**说明**: π0-FAST 在多个 generalist manipulation 任务上匹配 diffusion π0，同时训练所需 compute 更低。

### Table II: DROID evaluation tasks

| Task | Trials |
|------|--------|
| Put the spoon in the dish rack | 4 |
| Put carrot in bowl | 4 |
| Put plate in dish rack | 2 |
| Wipe the table | 2 |
| Put the plate on the table | 2 |
| Clean up the table | 2 |
| Close the drawer | 4 |
| Put the stapler on the notebook | 2 |
| Put stapler in the drawer | 4 |
| Clean the whiteboard | 2 |
| Put the marker in the cup | 4 |
| Put the black sponge in the blue bowl | 2 |
| Put the red bottle in the black bowl | 2 |
| Put the watermelon in the purple bowl | 2 |
| Move the watermelon from the purple bowl to the blue bowl | 2 |
| Put the tape in the purple bowl | 2 |
| Put the water bottle on the left side of the table | 2 |
| **Total** | **44** |

**说明**: DROID 定量评估覆盖 16 个任务、44 次 trials，用任务进度 rubric 打分。

### Figure 12: 压缩-重建 trade-off

![Figure 12](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x11.png)

**说明**: FAST 在多个数据集上有稳定的压缩-重建表现。VQ/FSQ 类方法低保真时压缩强，但高保真重建扩展性差；FAST 更适合精细控制。

### Figure 13: 真实任务初始配置

![Figure 13a](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/figures/task_bus.jpeg)
![Figure 13b](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/figures/task_shirt.jpeg)
![Figure 13c](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/figures/task_grocery.jpeg)
![Figure 13d](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/figures/task_toast.jpeg)
![Figure 13e](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/figures/task_laundry.jpeg)

**说明**: 展示 Table Bussing、T-Shirt Folding、Grocery Bagging、Toast out of Toaster、Laundry Folding 的样例初始场景。

### Figure 14: DROID 定量评估场景

![Figure 14](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x12.png)

**说明**: 展示 DROID 定量评估的真实桌面场景和物体配置。

### Table III: FAST+ 泛化评估数据集

| Morphology | Dataset | Platform | Action Space | Action Dim | Control Frequency | Task |
|------------|---------|----------|--------------|------------|-------------------|------|
| Single Arm | SOAR | WidowX | EEF | 7 | 5 | Pick/place |
| Single Arm | DROID-Eval EEF | Franka | EEF | 7 | 15 | Pick/place |
| Single Arm | DROID-Eval Joint | Franka | Joint | 8 | 15 | Pick/place |
| Single Arm | SERL | Franka | EEF | 7 | 10 | Insertion |
| Single Arm | π Table Bussing | UR5 | Joint | 8 | 20 | Pick/place |
| Dexterous | NYU DexHand | ALLEGRO | Joint+EEF | 30 | 16 | Dexterous manipulation |
| Dexterous | Berkeley DexHand | ALLEGRO | Joint | 16 | 20 | In-hand manipulation |
| Dexterous | Berkeley DexArm | xArm+ALLEGRO | Joint | 23 | 20 | Dexterous pick/place |
| Dexterous | HATO | UR5+Psyonic Hand | EEF+Joint | 24 | 10 | Dexterous pick/place |
| UMI | UMI | UMI | EEF | 7 | 20 | Pick/place |
| UMI on Legs | UMI | EEF | 7 | 20 | Whole-body manipulation |
| Humanoid | HumanPlus | Unitree H1 | Joint | 40 | 50 | Whole-body manipulation |
| Humanoid | UCSD TeleVision | Unitree H1 w/Neck | Joint | 28 | 60 | Manipulation+active perception |
| Navigation | Waymo | Waymo Car | 2D delta | 2 | 10 | Autonomous Driving |

**说明**: 该表强调 FAST+ 不只是面向单一机械臂，而是面向不同机器人形态、动作空间和频率的通用动作 tokenizer。

### Figure 15: compute-matched generalist policy

![Figure 15](https://ar5iv.labs.arxiv.org/html/2501.09747/assets/x13.png)

**说明**: 在相同训练 compute 下，π0-FAST 明显优于 diffusion π0，原因是自回归 FAST 的训练收敛更快。

---

## 实验

### 数据集

| 数据集 / 任务 | 规模或设置 | 特点 | 用途 |
|---------------|------------|------|------|
| Synthetic interpolation | 25-800 timesteps | 控制采样率，验证高频 token 相关性问题 | 机制分析 |
| BridgeV2 | 5 Hz, 7D action | 低频桌面 manipulation | tokenizer 压缩比较 |
| DROID | 75k successful episodes, 21M samples | in-the-wild、多视角、多语言标注 | 大规模真实机器人训练和 zero-shot 评估 |
| LIBERO | 270k samples | simulation benchmark | VLA 任务性能 |
| Table Bussing | UR5e, 20 Hz | 单臂拾取/分类、遮挡和反光物体 | 单任务训练 |
| T-Shirt Folding | bimanual ARX, 50 Hz | 双臂高频 cloth manipulation | 灵巧控制 |
| Grocery Bagging | UR5e | out-of-the-box generalist evaluation | 泛化评估 |
| Toast out of Toaster | bimanual Trossen ViperX | ALOHA-style 双臂任务 | 泛化评估 |
| Laundry Folding | bimanual ARX | 长时程 cloth manipulation | 泛化评估 |

### 实现细节

- **Backbone**: π0 VLA 和 OpenVLA-style autoregressive VLA。
- **输入图像**: 通常 2-3 个相机视角，分辨率 224x224；每个 image 由预训练 vision encoder 编码后拼接。
- **额外输入**: language instruction 和 proprioceptive state；状态用 256-bin tokenization 后作为文本 token 输入。
- **动作输出**: FAST tokenized action chunks。
- **优化器**: AdamW，学习率 $5\times 10^{-5}$，1k steps linear warmup，之后 constant LR。
- **优化细节**: $b_1=0.9$，$b_2=0.95$，无 weight decay，gradient clipping 为 1，EMA 权重 0.999。
- **推理**: 默认 greedy autoregressive decoding；部分双臂任务使用温度 $\beta=0.7$，帮助策略离开初始静止状态。
- **DROID 训练**: 单第三人称视角 + wrist camera；随机采样 DROID 的两个外部相机之一和三条语言标注之一；不使用相机标定；训练 3 epochs，约 240k iterations，batch size 256，8xH100 上约 4 天。

### 关键实验结论

1. **高频控制下 tokenizer 不是工程细节，而是学习瓶颈**: toy study 说明朴素 binning 的问题来自训练目标的信息结构，不是模型容量或数据难度。
2. **压缩动作目标能显著提升自回归 VLA 训练效率**: FAST 和 FSQ 都优于 naive binning，但 FAST 在高保真重建上更适合精细控制。
3. **FAST 让 DROID 上的自回归 VLA 变得可训练**: 论文强调这是首次能在 DROID 上高效训练并 zero-shot 部署到未见环境的 language-conditioned generalist manipulation policy。
4. **π0-FAST 的 compute efficiency 强**: 性能接近 diffusion π0，但训练更快；compute-matched 时明显优于 diffusion π0。

---

## 批判性思考

### 优点

1. **问题定位清楚**: 论文不是简单换 tokenizer，而是从 next-token objective 的边际信息量解释为什么高频动作会让自回归训练退化。
2. **方法简单且可插拔**: DCT、rounding、BPE 都是成熟组件，不需要改 VLA backbone，也不需要引入 diffusion head。
3. **工程价值高**: FAST+ 作为黑盒 tokenizer 对实际训练 VLA 很有吸引力，尤其适合已有 LLM/VLM 自回归基础设施。
4. **实验覆盖广**: 从 toy study、压缩重建、单任务训练、大规模 DROID 到 π0 generalist policy，证据链比较完整。

### 局限性

1. **DCT 假设偏向平滑轨迹**: 对强非平滑、接触切换非常频繁或离散模式明显的动作，低频优先压缩可能不总是最优。
2. **scale 超参数仍需权衡**: $\gamma$ 控制重建误差和 token 数，虽然比 VQ 训练简单，但不同任务可能仍需调节。
3. **BPE 字典的分布依赖没有完全消失**: FAST+ 的泛化很强，但极端新 embodiment 或动作语义可能仍受 tokenizer 训练混合影响。
4. **执行策略仍是 open-loop chunk**: action chunking 提高 temporal consistency，但长 chunk 也可能降低闭环反馈频率。

### 潜在改进方向

1. **自适应频率保留**: 根据任务阶段或接触事件动态调整 DCT 系数量化尺度。
2. **混合 tokenizer**: 对平滑自由空间运动用 FAST，对接触突变阶段使用 learned residual 或 event token。
3. **闭环 chunk 解码**: 在 FAST tokenization 基础上研究更短延迟的 receding-horizon 解码和在线 re-tokenization。
4. **tokenizer uncertainty**: 估计重建误差或 token 分布置信度，作为策略执行时的安全信号。

### 可复现性评估

- [ ] 代码开源：论文页给出项目主页，但笔记生成时未确认完整训练代码状态。
- [x] 预训练 tokenizer / FAST+：论文声明 release FAST+ universal tokenizer。
- [x] 训练细节完整：优化器、学习率、EMA、DROID setup、数据过滤等说明较充分。
- [x] 数据集可获取：LIBERO、DROID、BridgeV2、Open X-Embodiment 等大部分为公开数据集。
- [ ] 大规模 π0 训练完全复现成本高：10k 小时数据和 8xH100 级训练设置对普通实验室不友好。

---

## 关联笔记

### 基于

- [[Vision-Language-Action Model]]: FAST 服务于自回归 VLA 的动作输出 tokenization。
- [[Action Chunking]]: 论文把未来动作块作为模型输出对象。
- [[Discrete Cosine Transform]]: FAST 的连续动作压缩核心。
- [[Byte Pair Encoding]]: FAST 用于压缩量化后的频域整数序列。

### 对比

- [[OpenVLA]]: 代表 OpenVLA-style per-dimension binning tokenizer。
- [[Diffusion Policy]]: 代表不通过离散动作 token、而用 diffusion 解码动作的 VLA/robot policy 思路。
- [[Finite Scalar Quantization]]: 论文比较的 learned / vector-quantized tokenizer 类方法。

### 方法相关

- [[Action Tokenization]]: 本文核心问题。
- [[FAST+]]: 通用动作 tokenizer。
- [[DROID]]: 关键大规模真实机器人训练和评估数据集。

---

## 速查卡片

> [!summary] FAST: Efficient Action Tokenization for Vision-Language-Action Models
> - **核心**: 高频动作序列要先压缩再做自回归 token prediction。
> - **方法**: 分位数归一化 + DCT + scale-and-round + 低频优先 flatten + BPE。
> - **结果**: π0-FAST 匹配 diffusion π0，训练最多 5x 更快；compute-matched 时更强。
> - **适用场景**: 高频、灵巧、多机器人 embodiment 的 VLA 动作输出。

---

*笔记创建时间: 2026-04-29*
