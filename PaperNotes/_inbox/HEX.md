---
title: "HEX: Humanoid-Aligned Experts for Cross-Embodiment Whole-Body Manipulation"
method_name: "HEX"
authors: [Shuanghao Bai, Meng Li, Xinyuan Lv, Jiawei Wang, Xinhua Wang, Fei Liao, Chengkai Hou, Langzhe Gu, Wanqi Zhou, Kun Wu, Ziluo Ding, Zhiyuan Xu, Lei Sun, Shanghang Zhang, Zhengping Che, Jian Tang, Badong Chen]
year: 2026
venue: arXiv
tags: [humanoid-robotics, whole-body-control, vision-language-action, cross-embodiment, imitation-learning]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2604.07993v1
created: 2026-04-10
---

# 论文笔记：HEX: Humanoid-Aligned Experts for Cross-Embodiment Whole-Body Manipulation

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Beijing Innovation Center of Humanoid Robotics, Xi'an Jiaotong University, Nankai University, Peking University |
| 日期 | April 2026 |
| 项目主页 | https://hex-humanoid.github.io/ |
| 对比基线 | ACT, SwitchVLA, GR00T N1.5, pi0.5 |
| 链接 | [arXiv](https://arxiv.org/abs/2604.07993v1) / [Project](https://hex-humanoid.github.io/) |

---

## 一句话总结

> HEX 用结构化 [[Proprioception]] 和 morphology-aware [[Mixture of Experts]] 显式建模 humanoid whole-body coordination，再用 [[Flow Matching]] 动作头把视觉语言和未来状态融合起来。

---

## 核心贡献

1. **whole-body VLA for humanoids**: 把高层 [[Vision-Language-Action]] 和低层 [[Whole-Body Controller]] 明确分层，而不是直接吐高维关节。
2. **cross-embodiment state space**: 通过 canonical body-part slots 构造共享 latent space，让不同 humanoid 的本体状态能在同一空间内学习。
3. **review-and-forecast**: 用 history cache 回看视觉语义上下文，再用未来 proprioceptive prediction 给动作生成提供前瞻。
4. **real-robot validation**: 在 Tienkung 2.0 / 3.0 上覆盖快反应、长时程、多阶段任务，并比 ACT、SwitchVLA、GR00T N1.5、pi0.5 更稳。

---

## 问题背景

### 要解决的问题

现有 humanoid manipulation 方法大多只在两条路里选一条：

1. 把 locomotion 和 manipulation 分成两个系统，各自工作，再靠人工接口拼起来。
2. 用 VLA 或 imitation 模型直接预测动作，但没有显式建模全身不同部位之间的协调关系。

这两条路的问题都很明显。前者系统脆，后者语义上看起来懂任务，动作上却经常不稳，尤其是在 fast-reaction 和 long-horizon whole-body manipulation 里更容易崩。

### 现有方法的局限

- 固定基座 manipulation 的范式默认腿是背景板，不适合双足人形。
- 直接预测高维关节或 latent command，往往没有把 body-part interaction 建模出来。
- 只看当前图像的 VLA 对 temporally evolving scene 不够敏感。
- 不同 humanoid 的状态定义、传感器和动作空间不一致，导致跨平台预训练很难做。

### 本文的动机

作者的核心判断很对：humanoid whole-body manipulation 不只是“再大一点的 VLM + action head”，而是同时需要：

- 有结构的全身本体状态表示。
- 对未来短时动力学的预测能力。
- 对过去视觉语义上下文的紧凑记忆。
- 以及把这两种信息真正融合到动作生成里。

---

## 方法详解

### 模型架构

[[HEX]] 采用分层 humanoid control 架构：

- **输入**: 语言指令 $L$ + 当前视觉观测 $V_t$ + 当前 humanoid state $P_t$
- **视觉语义分支**: 单步 VLM 编码当前观测，并维护一个 history query cache
- **状态预测分支**: [[Proprioception]] 经 canonical body-part slots 映射后送入 UPP
- **动作生成分支**: [[Flow Matching]] 动作头在双分支条件下迭代去噪
- **输出**: 高层动作 chunk，驱动手臂/手部并作为低层 [[Whole-Body Controller]] 的中间命令
- **低层控制**: task-specific [[Reinforcement Learning]] policy 保证 balance-preserving execution

### 结构总览

![Figure 1](https://arxiv.org/html/2604.07993v1/x1.png)

**说明**: Figure 1 展示了 HEX 的完整框架、预训练数据规模和真实机器人任务。最关键的信息有三个：它是 full-sized bipedal humanoid whole-body VLA；训练语料覆盖 7 种 humanoid embodiment、12M+ frames；评测任务包含 whole-body、long-horizon 和 fast-reaction 三类。

### 模块1: Visual Review with History Cache

作者没有把一段历史视频反复塞给 VLM，而是把过去几个时刻的 query token 缓存在 history cache 里。这样做的目的是保留时序语义，但避免历史图像重复编码带来的推理延迟。

- 当前步只编码一帧图像和当前指令。
- 历史信息通过 compact query feature 注入。
- 这套设计更像“review”，不是暴力堆长上下文。

### 模块2: UPP with Morphology-aware [[Mixture of Experts]]

UPP 是这篇真正值钱的部分。作者把不同 humanoid 的本体状态统一组织成固定的 body-part slots：

- left / right arms
- left / right hands
- left / right legs
- head
- waist
- others

缺失的部位用 learned missing-part token 补位。这样不同机器人虽然原始状态维度不同，但都能投影到共享 latent space。之后再通过 morphology-aware [[Mixture of Experts]] 在 token 级别做路由：

- 路由 expert 负责 embodiment-specific / part-specific variation
- shared expert 负责所有 embodiment 共通的 dynamics
- 中间 transformer backbone 负责 embodiment-agnostic temporal modeling

### 模块3: Action Expert

![Figure 3](https://arxiv.org/html/2604.07993v1/x3.png)

**说明**: Figure 3 左边是 UPP，右边是 Action Expert。Action Expert 不直接把视觉和状态特征拼接，而是让当前 action hidden states 作为 query，分别 cross-attend 到视觉语义特征和未来 proprioceptive 特征，再用门控融合。这比粗暴 concat 更合理，因为动作生成本身决定了需要从哪种信息里取多少。

### review-and-forecast 的含义

这篇论文最清楚的一点是把两类时间信息分开处理：

- **review**: history cache 提供过去视觉上下文。
- **forecast**: UPP 预测未来全身状态演化。

前者帮助理解任务和场景变化，后者帮助保证动作和全身动力学相容。这个分工比“让一个大模型自己悟出 everything”靠谱得多。

---

## 关键公式

### 公式1: [[Vision-Language-Action|当前步视觉语言编码]]

$$
[L'_t, V'_t, Q'_t] = f_{\mathrm{vlm}}([L, V_t, Q_t])
$$

**含义**: 当前语言 token、视觉 token 和 query token 一起送进 VLM，得到当前步的视觉语言上下文表示。

**符号说明**:
- $L$: 语言指令 token
- $V_t$: 当前时刻视觉观测
- $Q_t$: 当前 query token
- $L'_t, V'_t, Q'_t$: 编码后的视觉语言表示

### 公式2: [[Proprioception|未来状态预测]]

$$
P'_{t+1:t+\tau_p} = f_{\mathrm{upp}}(P_t, L'_t, V'_t, M^{vl}_t)
$$

**含义**: UPP 根据当前本体状态、视觉语言特征和历史 cache 预测未来一小段 whole-body proprioceptive latent。

**符号说明**:
- $P_t$: 当前 humanoid-aligned proprioceptive state
- $M^{vl}_t$: history cache
- $\tau_p$: 未来状态预测窗口

### 公式3: [[Mixture of Experts|双分支门控融合]]

$$
g_t = \sigma\left(W_g [H^{vl}_t ; H^p_t ; \hat{X}_t]\right)
$$

$$
F_t = H^{vl}_t + g_t \odot H^p_t
$$

$$
X'_t = X_t + F_t
$$

**含义**: Action Expert 先分别得到视觉语义条件和未来状态条件，再用门控决定 state branch 应该注入多少，最后做残差更新。

**符号说明**:
- $H^{vl}_t$: 视觉语言条件特征
- $H^p_t$: UPP 输出的未来状态特征
- $\hat{X}_t$: 归一化后的 action hidden states
- $g_t$: 门控权重

### 公式4: [[Flow Matching|动作生成目标]]

$$
\tilde{A}_{t:t+\tau_a} = (1-\lambda)N + \lambda A_{t:t+\tau_a}, \quad \lambda \sim \mathcal{U}(0,1)
$$

$$
\mathrm{Vel}_{t:t+\tau_a} = A_{t:t+\tau_a} - N
$$

$$
\mathcal{L} = \mathcal{L}_a + \alpha \mathcal{L}_s
$$

其中

$$
\mathcal{L}_a = \lVert D_a(Z^a_t) - \mathrm{Vel}_{t:t+\tau_a} \rVert_2^2
$$

$$
\mathcal{L}_s = \lVert D_s(P'_{t+1:t+\tau_p}) - s_{t+1:t+\tau_p} \rVert_2^2
$$

**含义**: 动作头学习 flow-matching velocity，UPP 额外承担未来状态预测，两个目标一起训练。

**符号说明**:
- $A_{t:t+\tau_a}$: 干净动作序列
- $N$: 高斯噪声
- $Z^a_t$: Action Expert 最终 hidden state
- $s_{t+1:t+\tau_p}$: 真实未来本体状态

---

## 关键图表

### Figure 1: 整体框架与任务范围

![Figure 1](https://arxiv.org/html/2604.07993v1/x1.png)

**说明**: 作者把高层 VLA 与低层 whole-body control 明确分层，同时展示了训练语料和任务覆盖范围。这个图直接回答“HEX 到底是做 fixed-base manipulation 还是 whole-body humanoid”这个问题。

### Figure 2: 高层策略结构

![Figure 2](https://arxiv.org/html/2604.07993v1/x2.png)

**说明**: Figure 2 清晰展示了 high-level policy 的三段结构：VLM review、UPP forecast、Action Expert dual conditioning。这是论文最重要的系统图。

### Figure 3: UPP 与 Action Expert 细节

![Figure 3](https://arxiv.org/html/2604.07993v1/x3.png)

**说明**: 左图说明 canonical body-part token + morphology-aware MoE + shared transformer backbone 的组合；右图说明 dual cross-attention 和 gated fusion 的动作生成方式。

### Figure 4: 数据采集

![Figure 4](https://arxiv.org/html/2604.07993v1/x4.png)

**说明**: 真实机器人 teleoperation pipeline。头部动作、双臂、灵巧手、腰腿控制是分设备采集的，这也解释了为什么低层 whole-body controller 仍然必须存在。

### Figure 10: 延迟与成功率

![Figure 10](https://arxiv.org/html/2604.07993v1/x10.png)

**说明**: RTX 4090 上，HEX 以 73.34 ms 延迟拿到 79.8% 平均成功率，成功率高于 ACT、SwitchVLA、GR00T N1.5 和 pi0.5，但 latency 不是最低。

### Table 1: Seen-task 成绩

| Method | Params | Avg Success (%) |
|--------|--------|-----------------|
| ACT | 80M | 57.1 |
| SwitchVLA | 0.3B | 40.5 |
| GR00T N1.5 | 3B | 70.2 |
| pi0.5 | 3.3B | 71.8 |
| **HEX** | **2.4B** | **79.8** |

**说明**: 在 seen real-robot tasks 上，HEX 的平均成功率最好。值得注意的是 ACT 非常小，但在部分 reactive task 上动作顺滑且延迟极低，说明小模型在 seen data 上并没有被彻底打死。

### Table 2: Long-horizon box convey

| Method | Grasp Box | Turn Around | Walk to Table | Place Box |
|--------|-----------|-------------|---------------|-----------|
| ACT | 80.0 | 80.0 | 46.7 | 26.7 |
| SwitchVLA | 73.3 | 60.0 | 33.3 | 13.3 |
| GR00T N1.5 | 73.3 | 66.7 | 40.0 | 20.0 |
| pi0.5 | 100.0 | 100.0 | 40.0 | 40.0 |
| **HEX** | **100.0** | **100.0** | **73.3** | **53.3** |

**说明**: 真正拉开差距的是后两阶段。前面抓起和转身大家都能做，到了 walk to table 和 place box 这种会累积误差的阶段，HEX 明显更稳。

---

## 实验结果

### 数据与训练

- 预训练语料超过 **12M+ frames**
- 覆盖 **7 个 humanoid embodiment**
- 包含 Tienkung 2.0、Tienkung 3.0、Tienyi、Unitree G1/H1、AgiBot 数据和 RoboCOIN 子集
- 高层 policy 用 24-layer transformer hidden size 768
- UPP 预测未来 **50-step** 状态
- 动作头预测 **100-step** action chunks
- MoE 使用 **16 routed experts + 2 shared experts**

### 真实机器人任务

论文评测了 7 个任务，包括：

1. Mirror the human's pose
2. Pour liquor while following order
3. Human assistant handover
4. Walking while avoiding obstacles
5. Kneel and manipulate objects
6. Tidy table
7. Bring box and pack all objects

这些任务覆盖了手臂、灵巧手、腰部和腿部协同，不是纯手部 manipulation。

### Generalization

作者对 4 个 seen task 做了 8 个 distribution shift 变体：

- fast switching
- human intervention
- visual distractors
- different positions
- unseen lights
- dynamic positions
- replace blocks with balls

HEX 在这些变体上的平均成功率达到 **61.8%**，高于 pi0.5 的 **44.3%**、GR00T N1.5 的 **41.0%** 和 SwitchVLA 的 **22.4%**。这个结果说明未来 proprioception 建模确实帮助了 whole-body robustness。

### 消融

作者做了两类消融：

1. **是否预训练**
2. **history cache / UPP / MoE 逐步加入**

结论很明确：

- 预训练主要提升优化效率和 early success，不明显改变单任务最终上限。
- history cache、UPP、MoE 每加一层都能带来更好表现。
- full HEX 在 Pouring 和 Box Conveying 上都最好。

---

## 批判性思考

### 优点

1. **问题定义准**: 它抓住的不是“humanoid 也能跑 VLA 了”，而是 whole-body coordination 没被显式建模。
2. **结构设计合理**: review-and-forecast 的拆分非常清楚，历史视觉和未来本体状态各司其职。
3. **真实任务有说服力**: 不是只做仿真，也不是只做单步抓取。
4. **cross-embodiment 处理自然**: canonical body-part slots 比直接硬对齐原始 state/action 空间更聪明。

### 局限性

1. **低层仍然不是统一模型**: 低层 [[Whole-Body Controller]] 依赖 task-specific RL policy，离真正统一的 humanoid foundation control 还差一截。
2. **跨平台泛化仍偏同家族**: 虽然有多 embodiment 预训练，但真实评测主要还是 Tienkung 系列。
3. **动作输出仍偏高层上肢控制**: 论文强调全身协调，但高层动作主要直接控制 arms/hands，腿和整体稳定性更多交给低层。
4. **工程链条复杂**: teleoperation 数据采集、body-part state mapping、MoE 路由、低层控制都需要大量系统工作。

### 潜在改进方向

1. 把低层 [[Whole-Body Controller]] 也纳入统一可迁移框架，而不是 task-specific RL。
2. 在更多异构 humanoid 平台上做真实跨平台 zero-shot / few-shot 评测。
3. 引入更丰富的 tactile / force proprioception，检验 UPP 是否仍能稳住结构化预测。
4. 研究 state forecast horizon 和 action chunk horizon 的耦合关系，而不是固定 50 / 100 步。

### 可复现性评估

- [x] 代码开源
- [ ] 预训练模型
- [x] 训练细节完整
- [ ] 数据集可获取

---

## 关联笔记

### 基于

- [[Vision-Language-Action]]: 高层策略沿用 VLA 范式，但加入 future-state conditioning。
- [[WholeBodyVLA]]: 同样做 humanoid whole-body VLA，但 HEX 更强调结构化 proprioceptive dynamics。

### 对比

- [[ACT]]: 小模型、低延迟、seen-task 拟合强，是非常重要的现实基线。
- [[OpenVLA]]: 虽然不是论文主基线，但可作为固定基座 VLA 与 humanoid VLA 的对照参照。

### 方法相关

- [[Cross-Embodiment]]: 共享状态空间是论文的核心前提。
- [[Mixture of Experts]]: 负责 token-wise specialization。
- [[Flow Matching]]: 负责高层动作 chunk 生成。
- [[Proprioception]]: 未来状态预测的建模对象。
- [[Action Chunking]]: 动作头本质上仍是 chunk-based generation。

### 硬件/数据相关

- [[Teleoperation]]: 真实机器人 whole-body 数据采集的核心来源。
- [[Humanoid Robotics]]: 论文整个问题设定都建立在真实双足人形平台上。

---

## 速查卡片

> [!summary] HEX
> - **一句话**: 用结构化未来本体状态预测给 humanoid VLA 补上 whole-body coordination。
> - **最强点**: long-horizon 和 fast-reaction 任务上比现有基线更稳。
> - **最该记住的模块**: history cache + UPP + gated action expert。
> - **最真实的局限**: 低层控制仍然依赖 task-specific RL，离真正统一全身控制还没到位。
