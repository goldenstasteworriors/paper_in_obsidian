---
title: "BAT: Balancing Agility and Stability via Online Policy Switching for Long-Horizon Whole-Body Humanoid Control"
method_name: "BAT"
authors: ["Donghoon Baek", "and collaborators"]
year: 2026
venue: arXiv
tags: [humanoid, whole-body-control, hierarchical-rl, policy-switching, motion-tracking, loco-manipulation]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2604.01064v1
created: 2026-04-03
---

# BAT

## 一句话判断

这篇工作的价值不在于又训出一个更大的 humanoid policy，而在于它承认单一控制器在长时程 whole-body skill 里就是会顾此失彼，于是把“什么时候切策略”本身做成了主问题。

## 论文信息

- 论文: [arXiv](http://arxiv.org/abs/2604.01064v1) | [PDF](https://arxiv.org/pdf/2604.01064v1)
- 作者: Donghoon Baek 及合作者
- 机构: Georgia Tech / Samsung Research
- 机器人平台: Humanoid platform with simulation + Unitree G1 real hardware
- 任务类型: long-horizon whole-body control, loco-manipulation, policy switching
- 真实部署: 有。论文明确展示了 G1 上的 sequential task execution 和动态/静态动作切换

## 一句话总结

> [[BAT]] 保留 decoupled 与 coupled 两类 whole-body policy 的互补性，再用 [[Hierarchical Reinforcement Learning]] 和 option-aware [[VQ-VAE]] 学一个高层切换器，在长时程动作序列里在线挑更合适的控制器。

## 核心贡献

1. **把策略切换当成主问题**: 不是硬拗一个万能控制器，而是系统性建模 agility 和 stability 的 trade-off。
2. **离线构造高质量切换监督**: 用 sliding-horizon option evaluation 先生成 switching demonstrations，再拿来引导高层策略训练。
3. **提出 option-aware token 表征**: 在 [[VQ-VAE]] token 中显式编码 controller-aware 信息，提高 option prediction 和实际切换质量。

## 问题背景

### 要解决的问题

长时程 humanoid whole-body control 经常同时包含稳定步行、静态操作、快速动态过渡和受扰恢复。单一控制器通常只能在其中一部分场景里做得好，另一部分就开始崩。

### 现有方法的局限

- decoupled whole-body policy 往往更稳，但在敏捷动作上容易不够激进。
- coupled policy 往往更灵，但在复杂长时程序列里容易把稳定性和鲁棒性赔进去。
- heuristic switching 虽然能用，但扩展性差，一换任务模板就开始露馅。

### 本文的动机

作者的判断很直接：与其继续赌一个 policy 同时学会所有 motion phase，不如先承认控制器间存在结构性互补，再把切换时机学出来。

## 方法详解

### 整体架构

[[BAT]] 由三层组成：

- **底层 policy bank**: 两个互补控制器，分别记作 decoupled policy $\pi_D$ 和 coupled policy $\pi_C$
- **表示层**: option-aware [[VQ-VAE]]，把运动阶段压成更适合切换判定的离散 token
- **高层切换器**: 基于 [[Hierarchical Reinforcement Learning]] 的 switching policy，输出当前应该执行哪个低层 policy

论文里最关键的设计不是网络有多复杂，而是承认切换 supervision 本身稀缺。因此作者先通过 sliding-horizon pre-evaluation 离线构造 $\mathcal{D}_{Op}$，再用 BC-guided exploration 去稳定高层 RL。

### 模块 1: Option-Aware VQ-VAE

**设计动机**: 普通动作 token 只管压缩运动，不保证对“该切到哪套 policy”有判别力。

**具体实现**:
- 输入多帧 motion context 和参考状态
- 同时优化重建、next token prediction、option prediction
- 输出离散 latent token，直接提供给高层切换器

论文 Table I 的结果非常直接：Op-VQ-VAE 在 train / test 上的切换预测准确率分别是 `94.02%` 和 `93.73%`，明显高于 vanilla VQ-VAE 的 `62%` 左右。这不是小修小补，是表征目标根本换了。

### 模块 2: Sliding-Horizon Option Evaluation

**设计动机**: 真正有价值的切换点在长时程序列里很稀，直接靠 RL 硬撞会很慢。

**具体实现**:
- 在状态 $s_t$ 同时评估两种 option 在未来 $K$ 步内的回报
- 用差值 $\Delta Q(s_t)$ 近似谁在当前阶段更值
- 把得到的高质量标签用于构造 switching demonstrations

这一步很关键，因为它把“未来一段时间的行为后果”压回到当前切换决策，而不是只盯即时 reward。

### 模块 3: Decision Fusion Module

**设计动机**: 单独靠 option predictor 还是会抖，所以需要融合多路不确定性信息。

**具体实现**:
- 综合 high-level switch、option prediction 和 low-level policy traits
- 对不同时刻的 motion phase 做更稳的 controller selection
- 尽量避免频繁误切导致的 tracking failure

## 关键公式

### 公式 1: [[Hierarchical Reinforcement Learning|切换价值函数]]

$$
Q^{\pi_{sw}}(s_{t},c)=\mathbb{E}\!\left[\sum_{i=0}^{K-1}\gamma^{i}r_{t+i}+\gamma^{K}V(s_{t+K})\right]
$$

**含义**: 给定当前状态 $s_t$ 和待选控制器 $c$，这个式子衡量未来一个滑动窗口内选它到底值不值。

**符号说明**:
- $s_t$: 当前状态
- $c$: 当前候选 option / controller
- $K$: sliding horizon 长度
- $r_{t+i}$: 第 $t+i$ 步回报
- $V(s_{t+K})$: 窗口末端的 bootstrap value

### 公式 2: [[Hierarchical Reinforcement Learning|控制器差值评估]]

$$
\Delta Q(s_{t})
=Q(s_{t},D)-Q(s_{t},C)
\approx\sum_{i=d}^{K-1}\gamma^{i}\,\Delta r_{t+i}+\gamma^{K}\Delta V(s_{t+K})
$$

**含义**: 这个量直接衡量 decoupled policy 和 coupled policy 在当前阶段谁更占优，是 BAT 构造 switching supervision 的核心依据。

**符号说明**:
- $D, C$: 两个低层控制器
- $\Delta r_{t+i}$: 两个控制器在第 $t+i$ 步回报差
- $\Delta V(s_{t+K})$: 未来终端值差

### 公式 3: [[Hierarchical Reinforcement Learning|稀有切换状态样本复杂度]]

$$
N_{\mathrm{rare}}=\Omega\!\left(\frac{1}{p\,\varepsilon^{2}}\right)
$$

**含义**: 论文用它说明 rare-but-critical switching states 只靠在线采样会非常贵，因此必须用离线监督来补。

**符号说明**:
- $p$: 关键切换状态出现概率
- $\varepsilon$: 估计误差容忍度

## 关键图表

### Figure 1: 问题定义与动机

![Figure 1](https://arxiv.org/html/2604.01064v1/x1.png)

**说明**: 这张图最重要的信息不是“架构有几层”，而是作者明确承认了两类控制器在成功分布上的互补性。对 humanoid 来说，这种诚实比又一个统一模型更值钱。

### Figure 3: BAT 总体框架

![Figure 3](https://arxiv.org/html/2604.01064v1/x3.png)

**说明**: 图里把四个部分讲清楚了：option-aware VQ-VAE、offline data construction、option-guided HRL 和 decision fusion。整个系统的重点是“先拿到靠谱切换标签，再去学切换”，而不是端到端盲学。

### Figure 5: 多种切换策略对比

![Figure 5](https://arxiv.org/html/2604.01064v1/x5.png)

**说明**: 论文在 sequential multi-motion task 上比较了 heuristic、BC、fixed policy 和 BAT。这里最有价值的是 BAT 不只提高 reward，也提高 success rate，说明它不是单纯追 tracking 分数。

### Figure 7: 真机结果

![Figure 7](https://arxiv.org/html/2604.01064v1/x7.png)

**说明**: 真机图证明 BAT 不是只在 simulation 里挑 controller。论文明确展示了 G1 上连续任务执行和动态 / 静态动作切换。

## 实验结果

### Table 1: 切换预测准确率

| Feature | Train Acc | Test Acc |
|--------|-----------|----------|
| Raw Motion | 78.81 | 78.69 |
| VQ-VAE | 62.19 | 61.57 |
| **Op-VQ-VAE** | **94.02** | **93.73** |

**说明**: 这张表很关键。vanilla VQ-VAE 居然比 raw motion 还差，说明单纯离散化不等于切换友好；加了 option-aware 目标后才真正把 token 变成 controller selection 的好特征。

### Table 2: 不同 feature representation 的 switching control 表现

论文 Table II 报告 tracking reward 和 success rate，结论是：

- fixed $\pi_D$ 稳但不够灵
- fixed $\pi_C$ 灵但不够稳
- 只做 option prediction 不如融合策略
- **BAT 最接近 oracle option selection**

这正好说明它不是只学了一个 classifier，而是真把切换策略和控制表现耦起来了。

### Table 3: Diverse static / dynamic motions 上的 tracking performance

论文对比了 GMT、FALCON、TWIST、SONIC 和 BAT，关键结论是：

- **BAT 拿到最高 success rate**
- decoupled family 在 robustness 上更强
- coupled family 在某些敏捷动作上更猛
- BAT 通过切换把两边优点都薅了一点回来

### 真实部署

论文明确写到：

- 在 G1 上完成了 sequential task execution
- 面对 walking、running、jumping 和 dynamic transitions，BAT 会在 $\pi_D$ 与 $\pi_C$ 之间切换
- 说明其 online switching 不是只在离线 replay 上成立

## 实现细节

- **观测设计**: 由 5 个历史片段拼成 $o_t \in \mathbb{R}^{575}$
- **低层控制器**: decoupled whole-body policy + coupled whole-body policy
- **高层训练**: BC-guided exploration + RL fine-tuning
- **token 表征**: option-aware [[VQ-VAE]]
- **任务设置**: single-motion 与 sequential multi-motion 两类

## 批判性思考

### 优点

1. 终于正面承认 agility / stability trade-off，而不是神神叨叨吹统一策略。
2. 离线构造 switching supervision 很务实，能显著缓解稀有关键状态采样难题。
3. 真机验证让这篇不只是 simulation policy routing 自嗨。

### 局限性

1. 上限仍然受到底层两个 policy 本身的能力约束，本质还是“聪明调度”而不是“统一建模”。
2. 任务集虽然覆盖 static / dynamic motions，但距离开放世界 whole-body interaction 还有明显差距。
3. 如果动作库或低层 policy bank 更大，切换复杂度和 supervision 质量会不会迅速恶化，论文没展开。

### 潜在改进方向

1. 把 option bank 扩展到多于两个 controller，研究更细粒度的 skill routing。
2. 把 switching signal 和 environment contact phase 更紧地耦合，而不是主要依赖 motion context。
3. 研究是否能把 shared autonomy 或 teleoperation priors 也纳入高层切换逻辑。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [x] 训练细节基本完整
- [x] 任务设定与评测清晰

## 关联笔记

- [[Whole-Body Controller]]: BAT 关心的不是替代 whole-body controller，而是协调多种 controller。
- [[VQ-VAE]]: 论文把离散 token 从“压缩器”变成了“切换判别器”。
- [[Hierarchical Reinforcement Learning]]: 高层切换 policy 的核心训练范式。

## 总结

BAT 最值得学的不是某个公式，而是它对 humanoid 控制现实的判断：单一策略不够，就别继续骗自己。先把互补控制器管好，再谈统一，这条路反而更像能落地。
