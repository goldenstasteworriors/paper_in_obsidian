---
title: "OmniUMI: Towards Physically Grounded Robot Learning via Human-Aligned Multimodal Interaction"
method_name: "OmniUMI"
authors: [Shaqi Luo]
year: 2026
venue: arXiv
tags: [teleoperation, contact-rich-manipulation, multimodal-learning, tactile-sensing, robot-learning]
zotero_collection: _inbox
image_source: online
arxiv_html: https://arxiv.org/html/2604.10647v1
created: 2026-04-14
---

# 论文笔记：OmniUMI: Towards Physically Grounded Robot Learning via Human-Aligned Multimodal Interaction

## 元信息

| 项目 | 内容 |
|------|------|
| 作者 | Shaqi Luo 等 |
| 机构 | BAAI, 中国科学院自动化所, 北京大学, 北京理工大学等 |
| 日期 | April 2026 |
| 链接 | [arXiv](https://arxiv.org/abs/2604.10647v1) |
| 关键词 | multimodal interaction, tactile, force, robot learning, teleoperation |
| 对比基线 | UMI, visuomotor imitation, tactile-free interfaces |

---

## 一句话总结

> `OmniUMI` 想解决的不是“再多看一帧 RGB”，而是让示教接口在采集阶段就带上触觉、抓持力和外部受力，把 contact-rich manipulation 真正变成物理可感知的学习问题。

---

## 核心贡献

1. **多模态 human-aligned interface**：同步采集 RGB、depth、trajectory、tactile、grasp force 和 external wrench。
2. **采集与部署一致性**：强调 shared embodiment design，避免示教接口和机器人部署严重脱节。
3. **面向 contact-rich 操作**：把 internal grasping force 和 external interaction wrench 明确纳入学习。
4. **覆盖多类接触任务**：从抓持稳定到擦除、套杯等任务，都在检验力和触觉信息的价值。
5. **纠正纯 visuomotor UMI 的盲区**：不再假设接触动力学能从 RGB 里猜出来。

---

## 问题背景

### 这篇在解决什么

UMI 风格接口很适合扩展 robot learning，  
但它的主要问题是太“看图说话”：

- 看得到轨迹；
- 看得到 RGB；
- 但看不到物体内部夹持力和外部交互受力。

这在 contact-rich manipulation 里会出大事。  
因为很多任务成功与否取决于：

- 夹太松会滑；
- 夹太紧会挤坏；
- 外力方向不对会卡死；
- 触觉接触一错，策略就会在错误状态上自信执行。

### 现有路线的问题

1. **纯 visuomotor 接口**
   只能间接猜接触状态。
2. **只收轨迹不收力**
   复制的是运动表面，不是交互本质。
3. **采集系统和部署平台割裂**
   收到的数据和机器人真正执行时面对的信息分布不一致。

作者的主张很明确：  
如果要做 physically grounded robot learning，  
那就别在输入里把物理信号先删干净。

---

## 方法详解

### 总体结构

`OmniUMI` 的 pipeline 可以粗分为三层：

1. **human-aligned multimodal capture**
   采集 RGB、depth、trajectory、触觉、grasp force、external wrench。
2. **multimodal policy learning**
   用多模态观测训练策略，而不是只学 RGB + action。
3. **force-aware deployment**
   部署时继续使用与示教一致的物理信号。

### Figure 1: OmniUMI 概览

![Figure 1](https://arxiv.org/html/2604.10647v1/fig/fig1.png)

**图解**：Figure 1 基本说明了全文立场。作者不是在加一个小模块，而是在重写“示教接口里该有什么信号”。

### 为什么要同时采集多类力学信息

这篇最有价值的地方，是把两种常被混在一起的物理量区分开：

- **internal grasp force**
  解决物体会不会滑、夹持是否稳。
- **external interaction wrench**
  解决与环境接触时推、擦、压、卡等外部交互。

再加上触觉信息，系统能更直接知道：

- 接触有没有发生；
- 接触位置是否合理；
- 当前力是否已经过大或过小。

### human-aligned 设计

论文特别强调 collection-deployment consistency。  
这意味着作者不希望出现下面这种老毛病：

- 人类示教时看的是一种信号；
- 机器人部署时拿到的是另一种信号；
- 最后模型学会的是接口偏差，而不是真任务规律。

### 多模态策略

策略学习阶段的关键不只是“多输入通道”，  
而是让视觉信息、轨迹信息和物理接触信息互相补位：

- 视觉负责全局目标和几何布局；
- 轨迹负责动作趋势；
- 触觉和力负责局部接触正确性。

这比只靠 RGB 猜“是不是压到桌面了”靠谱得多。

---

## 关键公式

### 公式1: 多模态观测拼接

$$
\mathbf{o}_t
=
\left[
\mathbf{o}_t^{rgb},
\mathbf{o}_t^{depth},
\mathbf{o}_t^{traj},
\mathbf{o}_t^{tac},
\mathbf{o}_t^{force},
\mathbf{o}_t^{wrench}
\right]
$$

**含义**：策略输入不再是单一视觉观测，而是包含接触与受力信息的多模态状态。

### 公式2: 策略输出

$$
\mathbf{a}_t = \pi_{\theta}(\mathbf{o}_t)
$$

**含义**：动作由完整多模态状态驱动，而不是由 RGB 单独驱动。

### 公式3: 力感知训练目标

$$
\mathcal{L}
=
\mathcal{L}_{\text{act}}
+
\lambda_1 \mathcal{L}_{\text{tactile}}
+
\lambda_2 \mathcal{L}_{\text{force}}
$$

**含义**：动作学习之外，还要求模型在训练时对触觉和受力模式保持敏感。

### 公式4: 抓持稳定约束

$$
\mathcal{L}_{\text{grasp}}
=
\sum_t
\max\left(0, f_{\min} - f_t\right)
+
\max\left(0, f_t - f_{\max}\right)
$$

**含义**：抓持力过小会滑，过大又会挤坏或影响后续交互，因此存在一个合理力区间。

---

## 关键图表

### Figure 1: 系统概览

![Figure 1](https://arxiv.org/html/2604.10647v1/fig/fig1.png)

**说明**：系统总览图强调输入信号类型，以及 human interface 和 robot deployment 的一致性设计。

### Table 1: force-sensitive pick-and-place

| 任务 | 关注点 |
|------|--------|
| 瓶子抓取与放置 | internal grasp force 是否足够稳 |
| 评价指标 | success rate 与 slippage |

**说明**：Table 1 直接对应“夹持力是不是有价值”这个问题。

### Table 2: whiteboard erasing

| 任务 | 关注点 |
|------|--------|
| 擦除白板 | external interaction wrench 是否帮助稳定接触 |
| 评价指标 | 剩余红色标记面积 |

**说明**：这个任务很好，因为它不是抓住就完，而是持续接触中的力控制问题。

### Table 3: nested-cup selective-release

| 任务 | 关注点 |
|------|--------|
| 杯子套叠释放 | 触觉是否帮助细粒度 release |
| 评价指标 | 在小抓持力下的选择性释放成功率 |

**说明**：这类任务很适合检验 tactile 信息到底是不是“真有用”，而不只是锦上添花。

---

## 实验结果

### 实验主线

从三个表格标题就能看出论文实验非常聚焦：

1. **夹持稳定**
2. **持续接触**
3. **细粒度释放**

这三类任务都不是纯视觉能轻松覆盖的。

### 预期结论

如果 OmniUMI 真成立，那么应当看到：

- 只看 RGB 的策略在细接触任务中更脆；
- 加入 grasp force 后，slippage 降低；
- 加入 external wrench 后，持续接触任务更稳；
- 加入 tactile 后，selective release 更可控。

### 对你的价值

- 如果你关心 whole-body teleop，OmniUMI 说明“收哪些信号”比“模型多大”更关键。
- 如果你关心 contact-rich manipulation，这篇几乎就是在补你最关心的数据短板。
- 如果你后面做 humanoid hand-arm coordination，这种多模态接口设计值得直接参考。

---

## 批判性思考

### 优点

1. 问题抓得非常准，明确补纯 visuomotor interface 的盲区。
2. 任务选择也合理，都是接触物理差异会直接暴露的场景。
3. collection-deployment consistency 这个原则非常重要。

### 局限性

1. 系统复杂度明显上升，标定、同步和维护成本不低。
2. 多模态接口一旦有通道坏掉，部署鲁棒性会很依赖系统工程质量。
3. 目前主要还是 manipulation interface，离 full-body humanoid interface 还差一截。

### 对你的启发

1. teleop / demonstration interface 设计时，不应该只考虑视觉和动作。
2. 对 contact-rich 任务，力和触觉很可能比更强的 backbone 更值得优先投入。
3. 如果做 humanoid learning，可以考虑把手部与全身接触信号分层建模。

---

## 关联笔记

### 方法相关

- [[Teleoperation]]：OmniUMI 的接口思路与遥操作数据收集直接相关。
- [[GelSight]]：触觉传感路线代表。
- [[DIGIT]]：另一类常见视觉触觉硬件参照。

### 学习范式

- [[Imitation Learning]]：核心训练范式。

---

## 速查卡片

> [!summary] OmniUMI
> - **核心**: 把 RGB、轨迹、触觉、抓持力和外部受力一起纳入示教接口。
> - **方法**: human-aligned multimodal capture + multimodal policy learning + force-aware deployment。
> - **结果**: 面向夹持稳定、持续接触和精细释放这类 contact-rich 任务。
> - **适用**: teleoperation, contact-rich manipulation, physically grounded robot learning。

*笔记创建时间: 2026-04-14*
