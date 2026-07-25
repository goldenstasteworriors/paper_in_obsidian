---
type: concept
aliases: [度量尺度恢复, Metric Scale Alignment]
---

# Metric Scale Recovery

## 定义

将单目视觉得到的无尺度轨迹或结构锚定到物理单位的过程。

## 数学形式

$$
s=\operatorname{median}\frac{D_{\mathrm{metric}}}{D_{\mathrm{up\text{-}to\text{-}scale}}}
$$

## 核心要点

1. 应排除动态前景和不可靠区域。
2. 尺度误差会直接污染世界系动作标签。

## 代表工作

- [[EgoSteer]]：以 Any4D 深度校准 DPVO 轨迹。

## 相关概念

- [[First-Person Video]]
