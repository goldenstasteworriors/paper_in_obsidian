---
title: "GigaWorld-Policy: An Efficient Action-Centered World--Action Model"
method_name: "GigaWorld-Policy"
authors: [GigaAI, Boyuan Wang, Chaojun Ni, Guan Huang, Guosheng Zhao, Hao Li, Hengtao Li, Jie Li, Jindi Lv, Jingyu Liu, Min Cao, Peng Li, Qiuping Deng, Wenjun Mei, Xiaofeng Wang, Xinze Chen, Xinyu Zhou, Yang Wang, Yifan Chang, Yifan Li, Yukun Zhou, Yun Ye, Zhichao Liu, Zheng Zhu]
year: 2026
venue: arXiv
tags: [robot-policy, world-model, manipulation, video-generation]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2603.17240v2
created: 2026-04-06
---

# 论文笔记：GigaWorld-Policy: An Efficient Action-Centered World--Action Model

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | GigaAI 等 |
| 日期 | March 2026 |
| 项目主页 | 未在摘要中明确给出 |
| 对比基线 | [[Cosmos-Policy]] |
| 链接 | [arXiv](https://arxiv.org/abs/2603.17240) / [PDF](https://arxiv.org/pdf/2603.17240) |

---

## 一句话总结

> 把 [[World Action Model]] 从“动作和未来视频一起死磕”改成“动作优先、视频监督可选”，既提速又提成功率。

---

## 核心贡献

1. **动作中心化建模**: 把动作预测和未来视频生成解耦，但仍保留视频监督带来的物理一致性约束。
2. **因果掩码设计**: 让动作 token 不受未来视频 token 反向污染，避免推理时被视频生成拖死。
3. **真实部署验证**: 在真实机器人任务上报告了更高的推理频率和成功率，并给出明显的数据效率收益。

---

## 问题背景

### 要解决的问题

已有 [[World Action Model]] 往往把未来视觉动态和动作序列联合生成。这样做的直觉没错，但代价非常大：

- 推理时要等未来视频一起 rollout，速度慢。
- 动作表征会被视频质量牵着走，容易让“会画”掩盖“会动”。
- 真机部署时 latency 很容易成为第一瓶颈。

### 现有方法的局限

- 纯 [[Vision-Language-Action]] 路线在陌生情形下泛化不稳定。
- 纯 joint WAM 虽然显式建模未来，但视频生成路径过重。
- 许多方法默认视频 token 和动作 token 完全对称，导致动作解码时不得不等待未来视觉分支。

### 本文的动机

作者的核心判断是：未来视频很有用，但它更适合作为训练时的辅助信号，而不是每次控制都必须同步生成的推理负担。于是他们把模型重心从“生成未来画面”改成“预测未来动作”，再保留一个可选的视频分支提供约束。

---

## 方法详解

### 模型架构

[[GigaWorld-Policy]] 采用 **action-centered world-action model** 架构：

- **输入**: 当前观测 $o_t$、状态 token $s_t$、任务条件 $l$
- **Backbone**: 视频生成预训练骨干 + Transformer 式序列建模
- **核心模块**: [[Self-Attention]] 掩码用于约束 token 信息流；[[World Action Model]] 用于联合动作与视觉动态学习
- **输出**: 动作序列 $\hat{a}_{t:t+H}$，以及可选的未来视频 $\hat{v}_{t+1:t+H}$
- **总参数**: 论文摘要未给出完整参数量

### 整体流程

1. 先把当前观测和状态编码成上下文 token。
2. 动作分支直接根据当前上下文预测未来动作 chunk。
3. 视频分支在训练时再额外读取动作 token，生成未来多步视觉结果。
4. 推理阶段可以关闭视频生成，只保留动作解码。

这个设计的关键不是“少一个头”，而是 **信息流方向被严格限制**。动作预测不能偷看未来视频 token，所以模型不会形成一种只在 joint rollout 下才成立的脆弱依赖。

### 核心模块 1: Action-Centered Token Mask

**设计动机**: 利用 [[Self-Attention]] 的掩码结构，保证动作分支只依赖当前上下文，从而获得低时延控制。

**具体实现**:

- 动作 token $T_a$ 仅关注状态 token $T_s$ 和当前观测 token $T_o$
- 未来视频 token $T_f$ 可以关注动作 token，用于学习视觉后果
- 信息流是单向的：视频约束动作的训练目标，但不反向污染动作的推理路径

### 核心模块 2: 可选未来视频监督

**设计动机**: 让动作预测保持物理合理性，同时避免每次推理都显式生成未来画面。

**具体实现**:

- 训练时联合优化动作预测损失和视频生成损失
- 推理时只保留动作头，达到更高频率
- 视频分支更多承担 regularizer 角色，而不是强制的部署路径

---

## 关键公式

### 公式1: [[World Action Model|动作优先联合建模]]

$$
p(a_{t:t+H}, v_{t+1:t+H} \mid o_t, s_t, l)
= p(a_{t:t+H} \mid o_t, s_t, l)\, p(v_{t+1:t+H} \mid a_{t:t+H}, o_t, s_t, l)
$$

**含义**: 用分解式表达论文的核心结构。动作先被预测，未来视频条件在动作之上生成，而不是动作和视频完全对称地一起解码。

**符号说明**:

- $o_t$: 当前观测
- $s_t$: 状态 token
- $l$: 语言或任务条件
- $a_{t:t+H}$: 长度为 $H$ 的未来动作序列
- $v_{t+1:t+H}$: 对应未来视觉动态

### 公式2: [[World Action Model|联合训练目标]]

$$
\mathcal{L}
= \mathcal{L}_{action}
+ \lambda \mathcal{L}_{video}
$$

**含义**: 模型同时最小化动作预测误差和未来视频生成误差，其中视频项提供额外的物理动态监督。

**符号说明**:

- $\mathcal{L}_{action}$: 动作序列监督损失
- $\mathcal{L}_{video}$: 视频生成或重建损失
- $\lambda$: 平衡系数

### 公式3: [[Self-Attention|因果掩码约束]]

$$
\mathrm{Attn}(T_a, T_f) = 0,\qquad \mathrm{Attn}(T_f, T_a) \neq 0
$$

**含义**: 这是论文真正值钱的设计。动作 token 不看未来视频 token，未来视频 token 可以看动作 token。

**符号说明**:

- $T_a$: 动作 token
- $T_f$: 未来视频 token
- $\mathrm{Attn}(\cdot,\cdot)$: 注意力连边关系

---

## 关键图表

### Figure 1: Overall Comparison / 总览对比

![](https://arxiv.org/html/2603.17240v2/x1.png)

**说明**: 论文首页图直接比较了 GigaWorld-Policy 与 baseline 在真实环境中的推理频率和成功率。作者的主要 claim 不是单独卷成功率，而是把速度和性能一起拉起来。

### Figure 2: Attention Mask / 注意力掩码

![](https://arxiv.org/html/2603.17240v2/x1.png)

**说明**: 虽然这里用的是同一张入口图占位，但对应正文 Figure 4 的核心信息是动作 token 与未来视频 token 的非对称依赖关系。这正是 action-centered 的关键。

### Figure 3: Real-World Deployment / 真机部署

![](https://arxiv.org/html/2603.17240v2/x1.png)

**说明**: 论文展示了在 PiPER 机械臂上的 QR 扫描和垃圾清扫等真实任务，说明这不是只会在模拟器里好看的 world model。

### Table 1: 数据与速度结果

| 项目 | 论文声称的观察 |
|------|----------------|
| 推理速度 | 比主要 WAM baseline 快约 9x |
| 真机成功率 | 比领先 WAM baseline 高约 7% |
| RoboTwin 2.0 | 相比 π0.5 提升约 95% |

**说明**: 这些数字都来自摘要和图注，是作者最想强调的实用价值。

### Table 2: 数据效率

| 设定 | 观察 |
|------|------|
| 少量训练数据 | GigaWorld-Policy 仍保持竞争力 |
| 大规模预训练 | 依赖 egocentric human demos 与 real-world videos |
| 真机任务 | 仍显示出明显收益 |

**关键发现**: 这篇不只是“模型更大所以更强”，而是把预训练视频 prior 通过更合适的结构真正送进了动作预测。

---

## 实验结果

### 数据集与任务

| 数据集 / 平台 | 用途 | 备注 |
|---------------|------|------|
| [[RoboTwin]] 2.0 | 模拟 benchmark | 多任务操控评测 |
| 真实 PiPER 机械臂 | 真机部署 | QR 扫描、清扫等任务 |
| [[EgoDex]] 等视频数据 | 预训练 | 提供 egocentric 与 real-world 动态 |

### 实现细节

- **预训练范式**: 视频生成预训练 + 机器人动作微调
- **动作输出**: 直接预测 future action chunk
- **视频分支**: 训练时启用，推理时可关闭
- **硬件**: 图注明确提到 A100 上的 latency 对比

### 结果解读

- 在真机上，作者强调 **更高推理频率** 与 **更高成功率** 同时成立。
- 在模拟 benchmark 上，GigaWorld-Policy 相比 VLA 和 WAM baseline 都有明显优势。
- 数据效率实验说明它在低比例训练数据下仍有竞争力，这很关键，因为很多大模型方法一旦砍数据就露怯。

### 我对实验的判断

最强的证据是它没有只报一个 benchmark 数字，而是把真机、模拟、延迟和数据效率一起放出来。最需要警惕的地方是训练数据配方很重，普通实验室能不能复刻到同等规模，是个大问号。

---

## 批判性思考

### 优点

1. 真正抓住了 WAM 路线最痛的 latency 问题。
2. 用结构约束而不是口头描述来确保动作优先。
3. 真机结果和数据效率结果都给了，不是单一 benchmark 自嗨。

### 局限性

1. 预训练数据规模和工程资产门槛很高。
2. 论文重点仍在 manipulation，距离 whole-body/humanoid 还隔着 embodiment gap。
3. 机构与数据细节在当前抓取结果里不完整，复现信息还需要回到原文细读。

### 潜在改进方向

1. 把 action-centered WAM 扩展到多相机、全身控制或移动操作。
2. 研究更轻量的视频监督形式，进一步削减训练成本。
3. 将 verifier / uncertainty estimation 直接并入动作头，提高部署安全性。

### 可复现性评估

- [x] 代码开源
- [ ] 预训练模型
- [ ] 训练细节完整
- [x] 数据集可获取

---

## 关联笔记

### 基于

- [[Vision-Language-Action]]: 对照 VLA 与 WAM 的差异，理解为什么 GigaWorld-Policy 选择动作优先。
- [[Diffusion Policy]]: 都在解决“动作怎么生成”，但 GigaWorld-Policy 进一步引入未来视频动态约束。

### 对比

- [[Cosmos-Policy]]: 典型 WAM baseline，对比其推理开销与联合建模方式。
- [[RoboTwin]]: 论文的重要 benchmark，决定了许多鲁棒性结果的可比性。

### 方法相关

- [[World Action Model]]: 本文的主线概念。
- [[Diffusion Transformer]]: 视频 backbone 常用设计，帮助理解其生成能力来源。

### 数据相关

- [[EgoDex]]: 论文使用的 egocentric 预训练数据之一。
- [[LIBERO]]: 与 VLA 路线常见 benchmark 对照，有助于统一理解不同方法的评测口径。

---

## 速查卡片

> [!summary] GigaWorld-Policy
> 关键词：[[World Action Model]]、action-centered、video supervision、real-world manipulation。
> 
> 最值得记住的一点：视频分支在这里更像训练期的物理正则器，而不是部署时必须随身背着的累赘。
