---
title: "PaliGemma: A versatile 3B VLM for transfer"
method_name: "PaliGemma"
authors: [Lucas Beyer, Andreas Steiner, Andre Susano Pinto, Alexander Kolesnikov, Xiao Wang, Xiaohua Zhai]
year: 2024
venue: arXiv
tags: [vision-language-model, multimodal-pretraining, transfer-learning, image-language, segmentation, vqa]
zotero_collection: 多模态
image_source: local
arxiv_html: https://ar5iv.labs.arxiv.org/html/2407.07726v2
created: 2026-04-29
---

# 论文笔记：PaliGemma: A versatile 3B VLM for transfer

## 元信息

| 项目 | 内容 |
|------|------|
| 机构 | Google DeepMind |
| 日期 | 2024-10-10 v2 |
| 项目主页 | https://huggingface.co/google/paligemma-3b-pt-224 |
| 对比基线 | [[PaLI-3]], [[PaLI-X]], [[PaLM-E]], [[BLIP-2]], [[LLaVA]] |
| 链接 | [arXiv](https://arxiv.org/abs/2407.07726) / [PDF](https://arxiv.org/pdf/2407.07726) / [Code](https://github.com/google-research/big_vision) |

---

## 一句话总结

> PaliGemma 用小于 3B 参数做了一个强可迁移的开放式 VLM 基座。

---

## 核心贡献

1. **开放的 3B 级 VLM 基座**: 将 [[SigLIP]] ViT-So400m 图像编码器和 [[Gemma]]-2B decoder-only 语言模型连接成 [[Vision-Language Model|视觉语言模型]]，提供 224/448/896 三种分辨率 checkpoint。
2. **面向 transfer 的训练范式**: 目标不是开箱即用的聊天模型，而是通过 [[Multimodal Pretraining|多模态预训练]] 学到 caption、OCR、VQA、detection、segmentation 等技能，再在下游任务上全量微调。
3. **系统性消融**: 研究了 Stage1 时长、[[Prefix-LM]] masking、任务前缀、新 token 初始化、冻结策略、connector、图像编码器、分辨率和少样本 transfer 的影响。
4. **宽任务评估**: 在接近 40 个任务上评测，包括 captioning、VQA、文档/图表/OCR、[[Referring Expression Segmentation|指代表达分割]]、video QA/caption、remote sensing 和 Objaverse 多视角识别。

---

## 问题背景

### 要解决的问题

大模型 VLM 往往参数巨大，或者主要面向 instruction/chat 的零样本使用。PaliGemma 关注另一个目标：做一个小而强的 [[Vision-Language Model]] 基座，让用户可以针对具体视觉语言任务高效 fine-tune。

### 现有方法的局限

- [[PaLI-X]]、[[PaLM-E]] 规模很大，推理与训练成本高。
- [[LLaVA]] 类方法强调 instruction-following 数据，适合聊天界面，但不一定是最强的任务迁移基座。
- 很多 VLM 冻结视觉编码器，可能限制空间关系、定位、分割等能力。
- 高分辨率、prefix masking、connector、新 token 初始化等设计在 VLM transfer 场景下缺少统一消融。

### 本文的动机

PaLI-3 已经证明更好的视觉预训练和数据配比可以让 5B 模型接近更大模型。PaliGemma 继续压缩规模：复用公开的 [[SigLIP]] 和 [[Gemma]]，但通过足够长且任务多样的 [[Multimodal Pretraining]] 让小模型具备广泛可迁移技能。

---

## 方法详解

### 模型架构

[[PaliGemma]] 是一个 image+text in、text out 的 [[Vision-Language Model]]：

- **输入**: 一张或多张图像 + 文本 prefix，如问题、任务描述或检测类别。
- **视觉端**: [[SigLIP]] ViT-So400m，把固定方形图像转成 image tokens。
- **语言端**: [[Gemma]]-2B raw pretrained [[Decoder-only Transformer]]，自回归生成 suffix。
- **连接器**: 一个零初始化线性投影，把 SigLIP token 投影到 Gemma token embedding 维度。
- **输出**: 自然语言答案，或被文本化的结构化输出，如 bbox 位置 token、segmentation token。
- **参数量**: 约 400M vision encoder + 2B language model，总量小于 3B。

输入序列为：

```text
[image tokens..., BOS, prefix tokens..., SEP, suffix tokens..., EOS, PAD...]
```

224/448/896 输入分别产生 256/1024/4096 个 image tokens。多图像或视频任务中，每帧独立编码后直接拼接 image tokens；16 帧 224px 与单张 896px 都是 4096 image tokens。

### 训练阶段

#### Stage0: 单模态预训练

不重新训练单模态模型，直接使用公开 checkpoint：

- [[SigLIP]] ViT-So400m 作为视觉编码器。
- [[Gemma]]-2B raw pretrained checkpoint 作为语言模型。

#### Stage1: 多模态预训练

把视觉和语言模型接起来后，对整个模型做 1B examples 的 [[Multimodal Pretraining]]。关键点：

- **不冻结视觉编码器**，但给 SigLIP 使用慢线性 warm-up，避免初期未对齐语言梯度破坏视觉表征。
- 分辨率为 224px，文本长度 $N_{txt}=128$。
- 使用 task prefix 区分任务，降低不同任务输出语法冲突。
- 训练任务包含 caption、OCR、VQA/VQG、open-world detection、instance segmentation、grounded captioning。
- 训练集不包含 transfer 评测数据，并移除近重复图像。

#### Stage2: 分辨率提升

从 Stage1 checkpoint 继续训练到更高分辨率：

- 448px: 额外 50M examples，image tokens 从 256 增加到 1024。
- 896px: 再额外 10M examples，image tokens 增加到 4096。
- 文本长度提高到 $N_{txt}=512$，并提高 OCR、detection、segmentation 等高分辨率敏感任务的采样权重。

#### Stage3: Transfer

针对每个下游任务全参数 fine-tune。作者推荐优先调的超参顺序是：

1. 分辨率 checkpoint: 224/448/896。
2. Epochs: 1/3/10/30/100。
3. Learning rate: $3e^{-5}$、$1e^{-5}$、$3e^{-6}$。
4. Label smoothing: 0.0/0.1/0.3。
5. LLM dropout: 0.0/0.1/0.3。
6. Weight decay: 0 或 $0.1\times lr$。
7. 是否冻结 ViT。
8. Captioning 可考虑 beam search。

---

## 关键公式

### 公式1: [[Prefix-LM|输入 token 序列]]

$$
x = [v_1,\ldots,v_{N_{img}}, \mathrm{BOS}, p_1,\ldots,p_{N_p}, \mathrm{SEP}, y_1,\ldots,y_{N_y}, \mathrm{EOS}, \mathrm{PAD},\ldots]
$$

**含义**: 图像 token、任务 prefix 和输出 suffix 被拼接后送入 [[Gemma]] decoder。

**符号说明**:
- $v_i$: [[SigLIP]] 输出并经过线性投影后的图像 token。
- $p_i$: prefix token，表示任务、问题或提示。
- $y_i$: suffix token，是模型需要生成和监督的答案。
- $N_{img}$: 图像 token 数，224/448/896 分别为 256/1024/4096。

### 公式2: [[Prefix-LM|attention mask]]

$$
M_{ij} =
\begin{cases}
1, & i \in I \cup P,\ j \in I \cup P \\
1, & i \in Y,\ j \le i \\
0, & \text{otherwise}
\end{cases}
$$

**含义**: image 和 prefix 之间做全注意力，suffix 只做自回归注意力；这样 image tokens 可以看到任务 prefix。

**符号说明**:
- $I$: image token 位置集合。
- $P$: prefix token 位置集合。
- $Y$: suffix、EOS、PAD token 位置集合。
- $M_{ij}=1$: 第 $i$ 个 token 可以 attend 到第 $j$ 个 token。

### 公式3: [[Transfer Learning|transfer 监督目标]]

$$
\mathcal{L}_{\mathrm{transfer}} =
-\sum_{t=1}^{N_y}\log p_\theta(y_t \mid v_{1:N_{img}}, p_{1:N_p}, y_{<t})
$$

**含义**: 只对输出 suffix 做 next-token prediction loss；prefix 是条件，不要求模型“猜问题”。

**符号说明**:
- $\theta$: PaliGemma 全部可训练参数。
- $y_t$: 第 $t$ 个输出 token。
- $v_{1:N_{img}}$: 图像 token 序列。
- $p_{1:N_p}$: 任务 prefix。

### 公式4: [[SigLIP|分辨率与 image token 数]]

$$
N_{img}(R)=\left(\frac{R}{14}\right)^2
$$

**含义**: 对 ViT-So400m 的 14px patch 设置，固定方形输入 $R$ 会产生固定数量的 image tokens。

**符号说明**:
- $R$: 输入分辨率，取 224、448、896。
- $N_{img}$: 输入 Gemma 前的图像 token 数。

---

## 关键图表

### Figure 1: Architecture

![[assets/PaliGemma/PaliGemma_fig1_architecture.png]]

**说明**: [[SigLIP]] 图像编码器接线性投影后，把 image tokens 拼到 [[Gemma]] decoder 输入前端；整体 API 是 image+text 到 text。

### Figure 2: Prefix-LM masking

![[assets/PaliGemma/PaliGemma_fig2_prefix_lm_mask.png]]

**说明**: image/prefix 做双向注意力，suffix 做自回归注意力，是后续 masking 消融的基准设置。

### Figure 3: Learning-rate schedule

![[assets/PaliGemma/PaliGemma_fig3_lr_schedule.png]]

**说明**: SigLIP 学习率慢 warm-up，Gemma 学习率更早进入主 schedule；Stage2 接续 Stage1，transfer 作为 cooldown。

### Figure 4: Stage1 duration regret

![[assets/PaliGemma/PaliGemma_fig4_pretraining_duration_regret.png]]

**说明**: Stage1 越短，transfer regret 越高；100M examples 是消融的成本/质量折中，最终模型使用 1B examples。

### Figure 5: Stage1 learning setup

![[assets/PaliGemma/PaliGemma_fig5_stage1_learning_setup.png]]

**说明**: suffix-only autoregressive mask 和 suffix-only loss 最稳；task prefix 对某些歧义任务有帮助。

### Figure 6: New token initialization

![[assets/PaliGemma/PaliGemma_fig6_new_token_init.png]]

**说明**: 对新增 `<loc>` 和 `<seg>` token，均值 embedding 初始化初期 loss 更低，但标准 $\sigma=0.02$ 初始化最终 transfer 更好。

### Figure 7: Freezing setup

![[assets/PaliGemma/PaliGemma_fig7_freezing_setup.png]]

**说明**: Stage1 中 tune-tune 最好；冻结/重置语言模型或视觉模型会显著降低迁移能力，说明 Stage0 预训练组件很关键。

### Figure 8: Fuyu-style encoder ablation

![[assets/PaliGemma/PaliGemma_fig8_fuyu_style_encoder_ablation.png]]

**说明**: 不用 [[SigLIP]]，直接把 RGB patches 投影给 decoder 也能工作，但样本效率明显差。

### Figure 9: Resolution versus sequence length

![[assets/PaliGemma/PaliGemma_fig9_resolution_sequence_length.png]]

**说明**: 高分辨率收益来自两部分：图像信息更多，以及 token 序列更长带来的模型计算/容量增加。

### Figure 10: Resolution variants

![[assets/PaliGemma/PaliGemma_fig10_resolution_variants.png]]

**说明**: 原生 448px checkpoint 优于只在 transfer 时升分辨率或 windowing，支持发布多个分辨率 checkpoint。

### Figure 11: Repeatability

![[assets/PaliGemma/PaliGemma_fig11_repeatability.png]]

**说明**: 大多数任务在不同 seed 下标准差低于 0.5，transfer 和 Stage1 预训练都较稳定。

### Figure 12: Limited transfer examples

![[assets/PaliGemma/PaliGemma_fig12_limited_examples_regret.png]]

**说明**: 4k 样本多数任务能接近 full-data 结果；256 样本通常也可到 20% regret 内，适合新任务原型。

### Figure 13: RefCOCO resize modes

![[assets/PaliGemma/PaliGemma_fig13_refcoco_resize_modes.png]]

**说明**: 对 RefCOCO segmentation，简单 resize-to-square 配合一致的推理策略可以很好地工作。

### Figure 14: Label smoothing and dropout

![[assets/PaliGemma/PaliGemma_fig14_label_smoothing_dropout.png]]

**说明**: 224px/短训练下 label smoothing + dropout 可能伤害性能，但 448px/长训练时能抑制过拟合。

### Figure 15: Objaverse example

![[assets/PaliGemma/PaliGemma_fig15_objaverse_example.png]]

**说明**: 多视角、多 prompt 下的 Objaverse object-type prediction，使用 ScoreAgg 聚合答案。

### Figure 16: Full pretraining duration results

![[assets/PaliGemma/PaliGemma_fig16_pretraining_duration_full.png]]

**说明**: 大多数任务受益于更长 Stage1，remote sensing 是例外，可能因为图像分布与 web-scale 预训练不同。

### Figure 17: Full learning objective results

![[assets/PaliGemma/PaliGemma_fig17_learning_objective_full.png]]

**说明**: 把自回归 mask 或 loss 扩展到 prefix/image 整体不如 PaliGemma 的 suffix-only 设定。

### Figure 18: Task prefix ablation

![[assets/PaliGemma/PaliGemma_fig18_task_prefix_full.png]]

**说明**: pretraining 有无 task prefix 对多数 transfer 指标影响不大，但对训练中任务歧义的 perplexity 有影响。

### Figure 19: Full freezing patterns

![[assets/PaliGemma/PaliGemma_fig19_freezing_patterns_full.png]]

**说明**: 训练所有参数通常最好；冻结视觉端对最终 transfer 平均值影响小，但会伤害空间任务 pretraining perplexity。

### Figure 20: Full image encoder ablation

![[assets/PaliGemma/PaliGemma_fig20_image_encoder_full.png]]

**说明**: Fuyu-style 无视觉编码器架构随数据量增长有潜力，但在本文训练预算下明显落后于复用 SigLIP。

### Figure 21: Resolution or sequence length full

![[assets/PaliGemma/PaliGemma_fig21_resolution_or_sequence_full.png]]

**说明**: 对分辨率敏感任务，信息量和序列长度两类收益大致各占一半。

### Figure 22: Resolution checkpoints and windowing

![[assets/PaliGemma/PaliGemma_fig22_resolution_checkpoints_windowing.png]]

**说明**: 448 native checkpoint 最好；windowing 可作为没有高分辨率 checkpoint 时的替代。

### Figure 23: Stage2 mixture re-weighting

![[assets/PaliGemma/PaliGemma_fig23_stage2_mixture_reweight.png]]

**说明**: Stage2 使用相同 mixture 与重加权 mixture 的差距大多在噪声范围内，DocVQA/ChartQA/XM3600 更受影响。

### Figure 24: Simple transfer hyper-parameters

![[assets/PaliGemma/PaliGemma_fig24_simple_hparams_full.png]]

**说明**: 统一简单超参对大多数任务足够好，RefCOCO 和 SciCap 这类任务更依赖定制 epoch、dropout、label smoothing。

### Figure 25: Full limited-example transfer

![[assets/PaliGemma/PaliGemma_fig25_limited_examples_full.png]]

**说明**: 少样本 transfer 存在较高方差，但多数任务不需要万级数据才能达到可用水平。

### Table 1: 主结果

| 类别 | 任务 | 224px | 448px | 896px |
|------|------|------:|------:|------:|
| Captioning | COCOcap | 141.9 | 144.6 | - |
| Captioning | NoCaps | 121.7 | 123.6 | - |
| Captioning | COCO-35L en/avg34 | 139.2 / 113.7 | 141.2 / 115.8 | - |
| Captioning | Screen2Words | 117.6 | 119.6 | - |
| Captioning | TextCaps | 127.5 | 153.9 | - |
| Captioning | SciCap | 162.3 | 181.5 | - |
| Captioning | WidgetCap | 136.1 | 148.4 | - |
| VQA | VQAv2 | 83.2 | 85.6 | - |
| VQA | OKVQA / AOKVQA-MC / AOKVQA-DA | 63.5 / 76.4 / 61.9 | 63.2 / 76.9 / 63.2 | - |
| VQA | GQA / xGQA | 65.6 / 57.3 | 67.0 / 57.9 | - |
| VQA | NLVR2 / MARVL | 90.0 / 80.6 | 88.9 / 76.8 | - |
| VQA | AI2D / ScienceQA | 72.1 / 95.4 | 73.3 / 95.9 | - |
| VQA | RSVQA-lr / RSVQA-hr test/test2 | 92.6 / 92.6 / 90.6 | 93.1 / 92.8 / 90.5 | - |
| VQA | ChartQA human/aug | 40.0 / 74.2 | 54.2 / 88.5 | - |
| VQA | TallyQA simple/complex | 81.7 / 69.6 | 84.9 / 72.3 | - |
| VQA | OCR-VQA | 72.3 | 74.6 | 74.9 |
| VQA | TextVQA / DocVQA / InfoVQA / ST-VQA | 55.5 / 43.7 / 28.5 / 63.3 | 73.2 / 78.0 / 40.5 / 81.8 | 76.5 / 84.8 / 47.8 / 84.4 |
| Segmentation | RefCOCO testA/testB | 75.7 / 70.7 | 77.9 / 72.4 | 78.7 / 73.9 |
| Segmentation | RefCOCO+ testA/testB | 71.9 / 64.5 | 74.2 / 64.5 | 76.1 / 66.9 |
| Segmentation | RefCOCOg test | 68.2 | 71.0 | 72.7 |
| Video | ActivityNet-QA/CAP | 50.8 / 34.6 | - | - |
| Video | MSRVTT-QA/CAP, MSVD-QA, VATEX | 50.1 / 70.5 / 60.2 / 79.7 | - | - |

**关键发现**: 文本密集任务最吃分辨率，例如 DocVQA 从 43.7 到 84.8，TextVQA 从 55.5 到 76.5；remote sensing、普通 VQA 对高分辨率不敏感。

### Table 2: 简单 transfer 超参的 regret

| Relative Regret | 任务数 | 任务 |
|-----------------|------:|------|
| [None, 2.5%) | 37 | 其余多数任务 |
| [2.5%, 5.0%) | 2 | ChartQA human 3.2%, RefCOCO val 4.8% |
| [5.0%, 10.0%) | 2 | RefCOCOg val 5.8%, ScienceQA 6.7% |
| [10.0%, 100%] | 2 | RefCOCO+ val 10.7%, SciCap 60.5% |

**关键发现**: 一个统一的起始 transfer recipe 大多够用，但 SciCap 和 RefCOCO 系列需要更认真调参。

### Table 3: Objaverse 多视角识别

| Model | Score mean | stddev | stderr |
|------|-----------:|-------:|-------:|
| CAP3D | 36.6 | - | - |
| PaLI-X 55B, mixed VQA transfer | 59.0 | 29.1 | 0.1 |
| PaLI-3 5B, mixed VQA transfer | 64.3 | 29.2 | 0.1 |
| PaliGemma 3B, 224px | 58.4 | 29.5 | 0.1 |
| PaliGemma 3B, 224px, VQAv2 transfer | 62.7 | 28.2 | 0.1 |
| PaliGemma 3B, 448px | 60.4 | 28.9 | 0.1 |
| PaliGemma 3B, 448px, VQAv2 transfer | 62.8 | 28.3 | 0.1 |

**关键发现**: PaliGemma base 已有不错 3D object understanding；VQAv2 transfer 进一步提升。

### Table 4: Multitask transfer

| 指标 | Table 1 best | Single Simple | Multi Prefix | Multi No Prefix |
|------|-------------:|--------------:|-------------:|----------------:|
| Average | 84.6 | 80.2 | 78.9 | 77.6 |
| VQAv2 minival | 82.1 | 81.9 | 83.4 | 82.9 |
| OKVQA | 63.5 | 63.1 | 67.0 | 58.9 |
| DocVQA val | 37.8 | 38.6 | 32.2 | 31.3 |
| InfoVQA val | 25.5 | 25.0 | 20.8 | 21.4 |
| NoCaps | 121.7 | 121.6 | 118.4 | 98.9 |
| RefCOCO val | 73.4 | 69.9 | 68.4 | 68.3 |
| RSVQA-lr | 92.6 | 93.7 | 93.4 | 93.0 |

**关键发现**: 多任务 transfer 可行，但平均分主要损失来自统一超参，其次才是 multitask 本身；去掉 task prefix 进一步小幅退化。

### Table 5: Inference 测量

| Sharding | Params | Batch | Prefill ms | Extend ms | Prefill tok/s | Extend tok/s | Prefill GiB | Extend GiB |
|----------|--------|------:|-----------:|----------:|--------------:|-------------:|------------:|-----------:|
| FSDP | float32 | 1 | 107 | 14.6 | 4785 | 68 | 2.04 | 1.69 |
| FSDP | bfloat16 | 1 | 101 | 8.2 | 5073 | 122 | 0.84 | 0.64 |
| Megatron | float32 | 1 | 22 | 8.2 | 23018 | 122 | 2.23 | 1.61 |
| Megatron | bfloat16 | 1 | 17 | 5.3 | 30006 | 189 | 0.92 | 0.82 |
| FSDP | bfloat16 | 512 | 6235 | 30.8 | 42043 | 16601 | 6.28 | 2.14 |
| Megatron | bfloat16 | 512 | 6348 | 34.9 | 41297 | 14677 | 6.54 | 2.41 |

**关键发现**: 单样本时 Megatron-style sharding 明显降低 prefill walltime；大 batch 下吞吐差异变小。bfloat16 显著降低内存并提升 extend。

---

## 实验

### 数据集/任务族

| 任务族 | 数据集示例 | 用途 |
|--------|------------|------|
| Captioning | COCOcap, NoCaps, COCO-35L, XM3600, TextCaps, SciCap, WidgetCap | 图像描述、多语言描述、UI 描述、科学图描述 |
| VQA | VQAv2, OKVQA, AOKVQA, GQA, xGQA, NLVR2, MARVL, AI2D, ScienceQA | 问答、推理、多图像、多语言 |
| 文本密集视觉 | ChartQA, OCR-VQA, TextVQA, DocVQA, InfoVQA, ST-VQA | OCR、文档、图表、信息图 |
| Counting | TallyQA, CountBenchQA | 计数能力 |
| Segmentation | RefCOCO, RefCOCO+, RefCOCOg | [[Referring Expression Segmentation]] |
| Remote sensing | RSVQA-lr, RSVQA-hr | 遥感图像 VQA |
| Video | ActivityNet, MSRVTT, MSVD, VATEX | 多帧 caption/QA |
| 3D object | Objaverse-LVIS | 多视角物体类别识别 |

### 实现细节

- **Backbone**: [[SigLIP]] ViT-So400m + [[Gemma]]-2B。
- **Connector**: 线性投影，优于或持平 MLP connector。
- **训练框架**: open-source `big_vision`，[[JAX]] + [[GSPMD]]。
- **硬件**: Stage1/2 在 Cloud [[TPUv5e]] 上训练；最终 Stage1 TPUv5e-256 少于 3 天，Stage2 每个分辨率约 15 小时。
- **并行策略**: 训练时使用 [[FSDP]]/Zero-DP 风格 sharding。
- **预训练规模**: Stage1 1B examples，约 350B tokens；Stage2 合计约 90B tokens。
- **Transfer 时间**: 20 分钟到 10 小时不等，取决于任务。

### 重要消融结论

- **Stage1 长度**: 长预训练几乎普遍有利，100M examples 是可接受消融规模，但最终 1B 更强。
- **Masking/loss**: image+prefix full attention、suffix autoregressive、suffix-only loss 是最佳默认。
- **Task prefix**: 对最终 transfer 平均影响不大，但对 pretraining 中任务歧义有帮助。
- **新 token 初始化**: 标准小高斯初始化优于平均 embedding 初始化。
- **冻结策略**: 全部训练通常最优；冻结语言模型或重置任何组件都明显差。
- **Connector**: 线性 connector 足够，MLP 没有收益。
- **图像编码器**: 没有 SigLIP 的 Fuyu-style 方案能跑，但样本效率差。
- **分辨率**: 文本密集任务和分割任务强依赖高分辨率；native 高分辨率 checkpoint 优于临时升分辨率。
- **少样本迁移**: 64 样本可用于 prototype，4k 样本对多数任务已经接近 full-data。

---

## 批判性思考

### 优点

1. **工程上实用**: 3B 级别、公开 checkpoint、明确 transfer recipe，比超大闭源 VLM 更适合二次开发。
2. **任务覆盖广**: 不只做通用 VQA/caption，还包含文档、图表、分割、视频、遥感和 3D object。
3. **消融扎实**: 论文真正回答了 VLM transfer 中很多常见设计问题，而不只是报 benchmark。
4. **结论对机器人 VLA 有参考价值**: [[PaliGemma]] 后续常被当作视觉语言 backbone，用于机器人策略模型继承互联网尺度语义知识。

### 局限性

1. **不是 instruction/chat model**: base checkpoint 不是给直接对话使用的，需要 downstream transfer 或额外 instruction tuning。
2. **预训练数据不完全公开**: 代码和模型开放，但部分 pretraining datasets 私有，完全复现仍困难。
3. **输出统一为文本有代价**: detection/segmentation 通过 location/seg tokens 文本化，灵活但可能不如专门结构化头高效。
4. **高分辨率成本上升明显**: 896px 带来 4096 image tokens，文本密集任务收益大，但推理和显存成本也上升。
5. **多任务 generalist 还未充分调优**: Table 4 的 multitask transfer 只是验证可行性，不是最强 instruction-tuned generalist。

### 潜在改进方向

1. 结合 [[NaViT]]/FlexiViT 类可变分辨率机制，减少多 checkpoint 维护成本。
2. 用更强开放语言模型替换 Gemma-2B，探索 PaliGemma 2 式 scaling。
3. 针对机器人 VLA 引入 action expert，而不是直接让 VLM 生成动作 token。
4. 使用公开可复现的数据混合重建 PaliGemma-style base VLM。
5. 改进少样本 fine-tuning 的稳定性，降低 seed 和样本选择方差。

### 可复现性评估

- [x] 代码开源：`google-research/big_vision`
- [x] 预训练模型：Hugging Face 发布多个 checkpoint
- [x] 训练细节较完整：stage、分辨率、任务、超参和消融较详细
- [ ] 预训练数据完全可获取：部分数据私有
- [x] 下游超参完整：Appendix J 给出每个 transfer 任务配置

---

## 关联笔记

### 基于

- [[SigLIP]]: 视觉编码器，提供强对比预训练图像表征。
- [[Gemma]]: decoder-only 语言模型，负责文本条件生成。
- [[PaLI-3]]: 证明较小 VLM 在精心预训练下能接近大模型。

### 对比

- [[PaLI-X]]: 更大规模 PaLI 系列模型。
- [[PaLM-E]]: 大规模 embodied/multimodal language model。
- [[BLIP-2]]: 使用 Q-Former 连接视觉和语言模型。
- [[LLaVA]]: 更偏 instruction-following 的 VLM 路线。
- [[Fuyu]]: 无显式图像编码器的 decoder-only VLM 路线。

### 方法相关

- [[Vision-Language Model]]: 本文的模型类别。
- [[Multimodal Pretraining]]: PaliGemma 的核心训练范式。
- [[Prefix-LM]]: 本文使用的 attention/loss 组织方式。
- [[Transfer Learning]]: PaliGemma 的主要使用方式。
- [[Referring Expression Segmentation]]: PaliGemma 支持的结构化视觉任务。

### 工程相关

- [[JAX]]: 训练框架。
- [[GSPMD]]: 分布式切分机制。
- [[FSDP]]: 训练参数/优化器状态 sharding。
- [[TPUv5e]]: 预训练硬件。

---

## 速查卡片

> [!summary] PaliGemma
> - **核心**: 小于 3B 的开放 VLM transfer 基座。
> - **方法**: SigLIP image encoder + linear projector + Gemma-2B decoder，Prefix-LM masking，三阶段预训练/升分辨率/迁移。
> - **结果**: 在 captioning、VQA、文档 OCR、RefCOCO segmentation、video、remote sensing 等近 40 个任务上有强 transfer 表现。
> - **代码**: https://github.com/google-research/big_vision

---

*笔记创建时间: 2026-04-29*
