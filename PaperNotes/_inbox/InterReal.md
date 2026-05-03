---
title: "InterReal: A Unified Physics-Based Imitation Framework for Learning Human-Object Interaction Skills"
method_name: "InterReal"
authors: ["Dayang Liang", "et al."]
year: 2026
venue: arXiv
tags: [humanoid, hoi, physics-based-imitation, reinforcement-learning, sim-to-real]
image_source: online
created: 2026-03-10
---

# InterReal

## 一句话判断

这篇工作的重点不是“让 humanoid 动起来”，而是让 humanoid 在有物体扰动的情况下继续把 [[HOI]] 任务做完。核心价值在于把 motion augmentation 和 automatic reward learning 组合起来，缓解交互任务里最容易把策略打崩的两件事：分布偏移和 reward 权衡。

## 论文信息

- 论文: [arXiv](http://arxiv.org/abs/2603.07516v1) | [PDF](https://arxiv.org/pdf/2603.07516v1)
- 作者: Dayang Liang 等
- 机构: Xiamen University / Zhejiang University / ShanghaiTech University / TeleAI
- 任务: humanoid box-picking, box-pushing
- 真实部署: 有，论文报告了在 Unitree G1 上的 real-world deployment

## 关键图

![InterReal framework](https://arxiv.org/html/2603.07516v1/fig/iros_fw.png)

图里最重要的结构是双层训练：
- 内层用 [[PPO]] 学具体的 HOI policy。
- 外层用 [[SAC]] 风格的 meta-policy 动态分配 reward 权重。
- 中间再插一层 HOI motion augmentation，把同一个任务中的物体位置、交互几何和轨迹扰动提前注入训练。

## 问题定义

作者把 HOI 控制写成一个 MDP。状态包含 humanoid proprioception、物体状态、交互特征和任务 phase；动作对应机器人 23 维可学习自由度。

## 关键公式

### 1. HOI 任务目标

论文把任务记为 `\mathcal{T} = (S, A, P, f_t, \gamma)`，优化目标是最大化折扣累计回报：

$$
\mathbb{E}_{\pi}\left[\sum_{t=0}^{T}\gamma^t f_t\right]
$$

含义：
- `S` 是 human-object interaction system 的状态空间。
- `A` 是策略输出动作。
- `P` 是系统动力学。
- `f_t` 是当前时刻总 reward。
- `\gamma` 是折扣因子。

### 2. 动态加权奖励

InterReal 不把 reward 权重写死，而是让外层 meta-policy 动态调整：

$$
f_t(\Theta) = \sum_{k=1}^{K}\theta_t^{k} r_k(t)
$$

含义：
- `r_k(t)` 是第 `k` 个子奖励项，比如 tracking、interaction graph、torque penalty、CoM 相关项。
- `\theta_t^{k}` 是当前 phase 下该子奖励的权重。
- `\Theta` 不是固定超参数，而是外层策略根据训练进度在线调整的对象。

## 方法拆解

### 1. HOI motion augmentation

作者观察到，交互任务里最容易炸的是物体位置、接触几何和姿态扰动。于是他们不是只追一条 reference motion，而是围绕 anchor motion 生成一组同任务的变体轨迹，让策略在训练时就见过“物体不老实”的情况。

这一步的意义很直接：
- 提高 observation perturbation 下的稳定性。
- 减少 policy 被单一 reference trajectory 绑死。
- 让 sim-to-real 时物体初始位姿偏差不至于直接把策略打穿。

### 2. Inner-loop HOI policy learning

内层还是比较老实的 physics-based imitation 学法：
- 策略: [[PPO]]
- 输入: humanoid proprioception + object features + interaction features + task phase
- 输出: humanoid 控制动作

它的优势不是新，而是把 interaction feature 和 phase 明确塞进 observation，而不是假设“上肢自己会学会怎么和物体打交道”。

### 3. Outer-loop automatic reward learning

真正让这篇论文和普通 imitation + PPO 拉开距离的是外层 meta-policy。

作者的核心判断是：HOI 任务不同阶段的 reward emphasis 不一样。比如 lifting 初期更需要 balance，接触建立之后更需要 interaction tracking，硬用一组固定权重是很蠢的。

所以他们让外层策略把 PPO 子任务当成 environment，依据 tracking error 等高层指标动态选择 reward weight `\Theta`。这比手工 grid search 一堆 reward coefficient 更像一个能扩到复杂任务的方案。

## 实验结果

从论文富化结果和 PDF 文本能确认的点：
- 主任务是 box-picking 和 box-pushing。
- 作者报告了 tracking accuracy 和 task success rate 的提升。
- 有 automatic reward 的 ablation。
- 有 sim-to-real / real-world deployment。

对我来说，最关键的不是“数字大了多少”，而是以下两点都出现了：
- `V-D Deployment` 章节明确写了 deployment。
- 图 1 直接给了真实机器人完成交互任务的 live photos。

这意味着它不是停在 simulation 里自嗨。

## 我觉得最值钱的地方

### 1. 它抓对了 HOI 里的真难点

很多 humanoid work 还停在“不倒”和“会跟动作”，InterReal 已经开始正面处理 interaction disturbance 和 reward balancing，这才是把 whole-body control 真正推向任务化的方向。

### 2. reward learning 放在这里很合理

很多 paper 把 automatic reward learning 当花活，这篇不是。HOI 任务 phase 明显、子目标切换明显，动态 reward 权重确实有存在理由。

### 3. 对 sim-to-real 的姿态比较踏实

它没有幻想一个完美 reference 就能通吃现实，而是先承认交互几何和物体状态会漂，再用 augmentation 去顶。

## 局限

### 1. 任务集还比较规整

目前主打 box-picking / box-pushing，这对验证“interaction-aware”已经够了，但离开放世界多物体、多接触模式还有明显距离。

### 2. 框架复杂度不低

双层策略、动态 reward、motion augmentation 叠在一起，训练和调试成本都不低。它更像一个认真系统，而不是轻量 recipe。

### 3. 泛化边界还要继续追

从现有信息看，它证明了“这套东西能 work”，但还没完全证明“这套东西能广泛地 work”。

## 对当前工作流的启发

- 如果你做 humanoid HOI，这篇值得优先精读。
- 如果你做 reward design，可以重点看它如何把 tracking error 变成 meta-policy 的学习信号。
- 如果你做 sim-to-real，这篇的 motion augmentation 设计比单纯 domain randomization 更贴任务。

## 相关概念

- [[HOI]]
- [[PPO]]
- [[SAC]]
- [[Sim-to-Real]]
