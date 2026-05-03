---
title: "Morphology-Consistent Humanoid Interaction through Robot-Centric Video Synthesis"
method_name: "Dream2Act"
authors: ["Weisheng Xu", "Jian Li", "Yi Gu", "Bin Yang", "Haodong Chen", "Shuyi Lin", "Mingqian Zhou", "Jing Tan", "Qiwei Wu", "Xiangrui Jiang", "Taowen Wang", "Jiawen Wen", "Qiwei Liang", "Jiaxi Zhang", "Renjing Xu"]
year: 2026
venue: arXiv
tags: [humanoid-interaction, whole-body-control, robot-centric-generation, zero-shot, retargeting]
zotero_collection: _inbox
image_source: mixed
arxiv_html: https://arxiv.org/html/2603.19709v1
created: 2026-03-23
---

# 论文笔记：Morphology-Consistent Humanoid Interaction through Robot-Centric Video Synthesis

## 元信息

| 项目 | 内容 |
|------|------|
| 方法名 | Dream2Act |
| 机构 | HKUST(GZ), Harbin Institute of Technology Shenzhen, Shenzhen University, University of Cambridge |
| 日期 | March 2026 |
| 项目主页 | - |
| 对比基线 | human-centric retargeting pipeline |
| 链接 | [arXiv](https://arxiv.org/abs/2603.19709v1) / [HTML](https://arxiv.org/html/2603.19709v1) |

---

## 一句话总结

> Dream2Act 直接让视频生成模型在机器人自身形态上“做梦”，再把生成视频恢复成可执行的 whole-body 轨迹，从根上绕开 human-to-robot retargeting 的 morphology gap。

---

## 核心贡献

1. **机器人中心的交互生成**: 不再生成 human motion 再 retarget，而是直接生成 G1 自己与环境交互的视频先验。
2. **像素到物理的解耦恢复链**: 用 [[ViTPose]] 原生关节检测、2D-to-3D lifting 和 [[URDF]] 约束的 inverse kinematics，把视觉 hallucination 变成物理可执行轨迹。
3. **真实机器人零样本验证**: 在 Unitree G1 上做踢球、坐沙发、打沙袋、抱箱子四类 whole-body interaction，整体成功率 37.5%，而 retarget baseline 是 0%。

---

## 问题背景

### 要解决的问题

作者瞄准的是 humanoid interaction 里一个很老但一直没被正面处理的问题:

- 真实世界 whole-body interaction 很难收数据，task-specific policy training 的成本高得离谱。
- 现有 demonstration 路线通常先做人类动作估计，再把人类骨架映射到机器人。
- 但 humanoid 和 human 的骨骼比例、关节自由度、关节极限都不一样，retargeting 会把绝对空间关系直接搞歪。

对 ball kicking、sofa sitting 这种必须“人和物刚好对上位置”的任务来说，这不是一点小误差，而是根本碰不上目标。

### 现有方法的局限

传统路线大概是:

1. 用 [[SMPL]]、GVHMR 一类 human-centric 模型恢复人体动作。
2. 再把人类动作通过 GMR 或 IK 映射到机器人。
3. 最后由 [[Whole-Body Controller]] 去追这些轨迹。

这条线的问题非常直接:

- 中间表示是 human skeleton，不是 robot skeleton。
- retargeting 优化的是“像不像人”，不一定优化“机器人能不能碰到物体”。
- 一旦任务包含 locomotion，空间误差还会沿时间积累。

### 本文的动机

作者的核心判断很简单:

- 真正该被 hallucinate 的不是 human motion，而是 robot-native motion。
- 大规模视频生成模型已经能学到一些物理一致性和时空结构，可以直接拿来当 zero-shot interaction planner。
- 只要后端的 pose perception 和 kinematic recovery 足够稳，就能把视频先验落成可执行轨迹。

---

## 方法详解

### 整体架构

Dream2Act 的输入和输出非常清楚:

- **输入**: 第三人称视角下的机器人初始图像、目标物体、文本任务提示。
- **中间层**: 机器人中心的交互 hallucination 视频、原生 2D/3D 关节、根位姿和关节角。
- **输出**: 可直接送入 Sonic tracker 的 `(root_pos, root_rot, qpos)` 轨迹。

整条链路分成三段:

1. **Interaction Hallucination via Seedance 2.0**: 生成 G1 自己完成任务的视频。
2. **Native Pose Estimation and 2D-to-3D Lifting**: 从生成视频里抽 30 个机器人原生关节并恢复 3D。
3. **Morphology-Aware Kinematic Recovery and Physical Execution**: 用 [[URDF]] 约束 IK + root pose PnP 对齐，再由 Sonic 执行。

### 模块 1: Robot-Centric Interaction Hallucination

这部分的设计动机是，既然 retargeting 的根因是中间表示站错了坐标系，那就别再生成 human motion。

Dream2Act 直接把 Seedance 2.0 当作 generative world model 来用:

- 只需要一张真实环境里的 G1 初始图像。
- 再给一个语义任务 prompt。
- 生成结果保持固定第三人称视角和 G1 自身的物理外形。

作者把它看成一种 hallucination-to-execution pipeline:

- hallucination 负责给出 morphology-consistent visual prior。
- 后端恢复负责把这个 prior 约束到真实机器人动力学和运动学里。

这和 GenMimic / human-centric T2M 路线最根本的区别，是它从一开始就不经过 human embodiment。

### 模块 2: Hybrid Dataset 与原生 2D 检测

要把 hallucinated robot video 变成轨迹，前提是 2D 关键点检测必须对 G1 自己靠谱。

作者构造了一个 hybrid dataset:

- 从 [[AMASS]] 出发，把动作 retarget 到 G1 29-DoF 模型。
- 初始得到 5,337,514 帧轨迹，再下采样成 5,338 个关键帧。
- 在 Isaac Lab 里用 9 个相机构成半球形视角阵列，渲染精确 2D/3D 标注。
- 再采集真实 G1 视频，用 HITL 标注修正 sim-to-real 的视觉域偏差。

2D 检测 backbone 用的是 [[ViTPose]]:

- 冻结 ViT-Base 前 9 层。
- 只微调后 3 层和 Gaussian heatmap head。
- 目标是检测 30 个 G1 原生关节，而不是人体关键点。

作者最想证明的点不是“ViTPose 很强”，而是 human pose estimator 只在 human morphology 上强，拿到机器人上会崩。

### 模块 3: 2D-to-3D Lifting

从 2D 像素点到 3D 机器人关节，作者走的是 domain-specific lifting：

- 先把 2D 关键点做归一化，消除全局尺度影响。
- 再用专门针对 G1 关节分布训练的 lifting network 预测相机坐标系下的 3D joints。
- 实验里这一步在 simulation benchmark 上做到 29mm 的 MPJPE。

这一步的价值在于:

- 单目本来就有深度歧义。
- 但如果 3D 关节分布明确是 “G1-specific”，很多人类动作先验造成的自由度错误就不会传下来。

### 模块 4: Morphology-Aware Kinematic Recovery 与执行

作者把 recovery 拆成三小步:

1. **内部关节恢复**:
   用 [[URDF]] 约束的 IK，把预测 3D joints 对齐到 G1 的 forward kinematics 上。
2. **根位姿恢复**:
   用 PnP 式优化同时恢复 root translation 和 rotation，保证视觉投影和本体几何一致。
3. **统一格式执行**:
   把 `(root_pos, root_rot, qpos)` 封装成 GMR 格式，送给 Sonic tracker。

这样做的好处是:

- 内部关节和全局根位姿分开求，优化更稳。
- 末端位置对齐和整体平衡约束不互相污染。
- 后端直接复用通用 [[Whole-Body Controller]]，不需要额外 task-specific policy training。

---

## 关键公式

### 公式 1: [[ViTPose|2D 原生关节检测]]

$$
P_{2D}=f_{\text{ViT}}(I),\quad P_{2D}\in\mathbb{R}^{N\times 2}
$$

**含义**: 给定输入图像 $I$，微调后的 ViTPose 输出 G1 的 $N$ 个二维原生关节点。

**符号说明**:
- $I$: 第三人称相机图像
- $f_{\text{ViT}}(\cdot)$: 原生 2D pose estimator
- $P_{2D}$: 机器人 2D 关节坐标
- $N$: 关节数，文中为 30

### 公式 2: [[AMASS|2D 到 3D Lifting]]

$$
P_{3D}=\Phi_{\text{lift}}\big(\mathcal{N}(P_{2D})\big),\quad P_{3D}\in\mathbb{R}^{N\times 3}
$$

**含义**: 先对 2D 关节归一化，再用 lifting network 回归机器人原生 3D joints。

**符号说明**:
- $\mathcal{N}(\cdot)$: 2D 归一化函数
- $\Phi_{\text{lift}}(\cdot)$: 2D-to-3D lifting network
- $P_{3D}$: 相机坐标系下的 3D 关节位置

### 公式 3: [[URDF|约束逆运动学恢复]]

$$
q^{*}=\arg\min_{q}\sum_{i=1}^{N}\big\|\mathrm{FK}_{i}(q)-\hat{P}_{3D}^{(i)}\big\|^{2}
$$

**含义**: 通过最小化 forward kinematics 和估计 3D joints 之间的误差，恢复符合机器人运动学约束的关节角。

**符号说明**:
- $q$: 机器人关节角
- $q^{*}$: 优化后的关节角解
- $\mathrm{FK}_{i}(q)$: 第 $i$ 个关节在给定 $q$ 下的 forward kinematics 位置
- $\hat{P}_{3D}^{(i)}$: 第 $i$ 个目标 3D 关节位置

### 公式 4: [[Whole-Body Controller|根位姿投影对齐]]

$$
\min_{R,t}\sum_{i=1}^{N}\big\|P_{2D}^{(i)}-\pi\big(K(R\cdot P_{local}^{(i)}+t)\big)\big\|^{2}
$$

**含义**: 通过相机投影约束恢复全局根旋转 $R$ 与平移 $t$，让视觉观测和机器人局部几何对齐。

**符号说明**:
- $R$: 根旋转
- $t$: 根平移
- $K$: 相机内参矩阵
- $\pi(\cdot)$: 投影函数
- $P_{local}^{(i)}$: 机器人局部坐标下的第 $i$ 个点

---

## 关键图表

### Figure 1: Dream2Act 总览 / Zero-shot Humanoid Interaction

![](https://arxiv.org/html/2603.19709v1/figs/fig1.png)

**说明**: 图 1 直接把论文的核心论点说透了。上面是传统 human-centric retargeting 因 morphology gap 造成的空间错位，下面是 Dream2Act 直接在机器人原生空间里 hallucinate 交互结果。作者借这张图强调的是“不要先变成人再变回机器人”。

### Figure 2: System Architecture / 系统架构

![](https://arxiv.org/html/2603.19709v1/figs/pipeline.png)

**说明**: 三段式 pipeline 很清楚: Seedance 生成交互视频，原生 pose estimator + lifting 抽 3D joints，再走 morphology-aware recovery 和 Sonic execution。真正的贡献不是某一层网络更深，而是这三段组合后不再依赖 human intermediate。

### Figure 3: Hybrid Dataset Pipeline / 数据集构建

![](https://arxiv.org/html/2603.19709v1/figs/dataset.png)

**说明**: 作者把 simulation 的精确几何标注和真实世界的 HITL 修正绑在一起。9-camera Isaac Lab 渲染负责给干净 3D 真值，真实世界视频负责补视觉域偏差，这就是它 2D 检测能在 G1 上站住的原因。

### Figure 4: Diverse Real-World Tasks / 零样本交互定性结果

![[Dream2Act_fig4.png|600]]

**说明**: 四类任务分别是 kicking、hugging、punching、sitting。上排 baseline 主要死在空间错位和动态不稳定，下排 Dream2Act 至少能把接触点和身体关系对上，这也是它在真实任务上能出结果的关键。

### Figure 5: Spatial Generalization for Kicking / 多位置踢球泛化

![](https://arxiv.org/html/2603.19709v1/figs/balls.png)

**说明**: 作者把球摆在多个不同位置，检验是否还能保持空间对齐。Dream2Act 在更长的行走距离下仍能把误差压住，而传统 retargeting 会随着 locomotion 过程不断累积空间偏差。

### Figure 6: Text-to-Motion Qualitative Comparison / 自由空间动作生成对比

![](https://arxiv.org/html/2603.19709v1/figs/T2M.png)

**说明**: 作者拿 ViMogen、MDM、Dart 这类 human-centric T2M 作为对照。结论很毒但基本成立: human motion 里的一点点 foot sliding、腾空和 jitter，到了 G1 上会被放大成直接摔倒或动作冻结。

### Figure 7: Native Pose Estimation Ablation / 2D 检测消融

![](https://arxiv.org/html/2603.19709v1/figs/paper_vitpose.png)

**说明**: 零样本 COCO ViTPose 几乎看不懂 G1，sim-only 版本会有明显 domain shift，而 hybrid fine-tuned 版本才能达到像素级对齐。这张图几乎就是在公开处刑“拿现成人体 pose model 直接上机器人”的偷懒做法。

### Table 1: 四类零样本交互任务结果

| Method | Kick Succ | Kick Err | Hug Succ | Hug Err | Punch Succ | Punch Err | Sit Succ | Sit Err |
|--------|-----------|----------|----------|---------|------------|-----------|----------|---------|
| Baseline | 0% | 0.75 | 0% | 0.35 | 0% | 0.70 | 0% | 0.65 |
| **Dream2Act** | **40%** | **0.14** | **10%** | **0.11** | **30%** | **0.10** | **70%** | **0.28** |

**说明**: 这张表最重要的不是成功率本身，而是 baseline 全线 0%。Dream2Act 还不够稳，但它至少证明 robot-centric 规划确实能把空间误差压到可执行区间。

### Table 2: 多位置踢球结果

| Method | Ball a Succ | Ball a Err | Ball b Succ | Ball b Err | Ball c Succ | Ball c Err | Ball d Succ | Ball d Err |
|--------|-------------|------------|-------------|------------|-------------|------------|-------------|------------|
| Baseline | 0% | 0.53 | 0% | 0.82 | 0% | 0.84 | 0% | 0.79 |
| **Dream2Act** | **60%** | **0.19** | **20%** | **0.09** | **60%** | **0.09** | **20%** | **0.19** |

**说明**: 任务长度从 0.90m 到 2.18m 都有，Dream2Act 的误差大体还能维持在 0.09m 到 0.19m，而 baseline 已经漂到 0.79m。作者用这张表证明 locomotion 会放大 retargeting 的空间债。

### Table 3: Native Pose Estimation 结果

| Method | Sim AP | Sim PCK@0.05 | Internet AP | Internet PCK@0.05 |
|--------|--------|--------------|-------------|-------------------|
| Zero-shot ViTPose | 0.234 | 64.99% | 0.260 | 66.06% |
| Ours (Sim Only) | 0.940 | 99.76% | 0.497 | 91.61% |
| **Ours (Hybrid)** | **0.785** | **95.78%** | **0.613** | **97.02%** |

**说明**: Sim-only 模型在仿真里几乎完美，但到真实图像就露怯。Hybrid 版本把 Internet set 的 PCK 拉到 97.02%，说明真实世界少量人工修正对 robot-native perception 很关键。

---

## 实验

### 数据集

| 数据集 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| G1 Sim Hybrid Dataset | 5,337,514 初始帧，下采样为 5,338 keyframes | 9 相机 Isaac Lab，高精度 2D/3D 几何真值 | 2D pose + 3D lifting 训练 |
| G1 Real In-the-Wild Dataset | 真实 G1 视频，10% eval 为 341 帧 | HITL 修正标注，覆盖光照与纹理偏移 | 2D pose real-world 适配 |
| [[AMASS]] | 大规模 human motion | 提供 motion prior，先 retarget 到 G1 | 生成 sim 训练素材 |

### 实现细节

- **机器人平台**: Unitree G1，29 DoF
- **生成模型**: Seedance 2.0
- **2D 检测 Backbone**: [[ViTPose]] ViT-Base，冻结前 9 层，仅微调后 3 层和 heatmap head
- **仿真平台**: Isaac Lab，9-camera hemispherical rendering
- **执行器**: Sonic general-purpose motion tracker，50 Hz
- **3D 重建精度**: 2D-to-3D lifting 在 simulation benchmark 上 MPJPE 为 29mm

### 关键结果

1. **真实交互结果**: 四类任务总体成功率 37.5%，而 retarget baseline 是 0%。
2. **空间泛化**: 长距离 kicking 任务中，baseline 在最远目标上误差 0.79m，Dream2Act 仍能维持在 0.19m。
3. **感知稳健性**: Hybrid 训练把 Internet set 的 2D PCK@0.05 拉到 97.02%，明显优于 zero-shot ViTPose。
4. **自由空间动作质量**: 对比 human-centric T2M，robot-centric hallucination 在 balance 和 contact feasibility 上更可信。

### 可视化结果

最值得注意的不是某一个漂亮视频，而是作者一直在强调“空间关系是否对上”：

- kicking 看的是脚和球的几何关系。
- sitting 看的是臀部和沙发接触点。
- hugging / punching 看的是接触时身体和物体的相对位置。

Dream2Act 的优势不在 motion style 更优雅，而在它从一开始就把这些接触几何留在了机器人自己的坐标系里。

---

## 批判性思考

### 优点

1. 真正正面处理了 humanoid interaction 里的 morphology gap，而不是继续靠 retargeting 修修补补。
2. 方法链条很完整，从生成到 perception 到 kinematic recovery 再到 execution，逻辑闭环清楚。
3. 真机任务选择很对路，都是对空间接触敏感的任务，能真实暴露 retargeting 的问题。

### 局限性

1. 37.5% 的总成功率只能说明“方向成立”，离可靠系统还差得远。
2. 整个 pipeline 目前更像 offline zero-shot planner，扩展到在线交互或闭环修正还没有解决。
3. 大量能力依赖 Seedance 2.0 的视频质量，如果 hallucination 漂了，后端恢复再稳也救不回来。

### 潜在改进方向

1. 在 hallucination 后面加在线视觉反馈或 contact-aware correction，减少单次生成失误的放大。
2. 把当前单机器人、第三人称视角扩展到更复杂的多人/遮挡/动态场景。
3. 结合触觉或力反馈，让 interaction success 不只靠视觉几何对齐。

### 可复现性评估

- [ ] 代码开源
- [ ] 预训练模型
- [x] 训练细节完整
- [x] 数据构建流程清晰

---

## 关联笔记

### 基于

- [[SMPL]]: 论文对它的使用方式基本是“批评对象”，指出 human-centric 表示会引入 morphology gap。
- [[AMASS]]: 用作大规模 motion prior，再映射到 G1 生成模拟数据。

### 对比

- [[ZeroWBC]]: 都关心 whole-body motion execution，但 Dream2Act 先解决的是 motion source 的坐标系问题。
- [[Whole-Body Controller]]: Dream2Act 并不重新发明 controller，而是把更合理的轨迹喂给通用 tracker。

### 方法相关

- [[ViTPose]]: 作为 native 2D joint detector backbone，经 hybrid 数据微调后才能在 G1 上可用。
- [[URDF]]: 约束 inverse kinematics 和 root pose recovery 的核心结构先验。

### 硬件/数据相关

- [[MoCap]]: 整条 sim dataset 构造链的起点之一。
- [[AMASS]]: 提供从 human motion 到 robot-native synthetic dataset 的源数据。

---

## 速查卡片

> [!summary] Morphology-Consistent Humanoid Interaction through Robot-Centric Video Synthesis
> - **核心**: 直接在机器人原生空间 hallucinate interaction，再恢复成可执行 whole-body 轨迹。
> - **方法**: Seedance 2.0 + native [[ViTPose]] + 2D-to-3D lifting + [[URDF]]-constrained IK + Sonic execution
> - **结果**: G1 真机四类任务总成功率 37.5%，retarget baseline 为 0%
> - **判断**: 真正把 retargeting 的坐标系问题拿到台面上解决，虽然离稳定系统还远，但方向非常值得跟。

*笔记创建时间: 2026-03-23 12:00*
