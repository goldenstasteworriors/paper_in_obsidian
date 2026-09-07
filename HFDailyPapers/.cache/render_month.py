#!/usr/bin/env python3
"""Render the reviewed September HF snapshots; standard-library only."""
import datetime as dt
import json
from pathlib import Path
import re

VAULT = Path("/home/ykj/Documents/ObsidianVault-dailypaper-skills")
ROOT = VAULT / "HFDailyPapers"
CACHE = ROOT / ".cache"
CONCEPTS = {
    "OPD": ("On-Policy Distillation", "11-深度学习基础/On-Policy Distillation.md", "学生先采样，教师在学生访问的前缀上给密集监督；本篇进一步考察监督或数据如何起作用。"),
    "Harness": ("Agent Harness", "11-深度学习基础/Agent Harness.md", "框架组织工具、上下文、控制与验证，模型权重之外的这些程序也影响最终能力。"),
    "LoRA": ("LoRA", "11-深度学习基础/LoRA.md", "用低秩矩阵表示权重增量，以少量训练参数适配任务；本篇改变的是适配机制或使用场景。"),
    "World": ("World Model", "2-强化学习/World Model.md", "预测动作条件下的状态或观察；可生成视频不自动意味着具备完整动力学。"),
    "WAM": ("World Action Model", "3-机器人策略/World Action Model.md", "联合利用未来环境动态与动作，本文进一步用分阶段数据和快慢分支处理泛化与延迟。"),
    "VLM": ("Vision-Language Model", "11-深度学习基础/Vision-Language Model.md", "VLM 连接图像与语言，但观察理解、执行动作和验证结果仍是不同能力。"),
    "RQ": ("Residual Quantization", "11-深度学习基础/Residual Quantization.md", "多个码本逐级编码残差，以短 token 序列表示较细的连续动作结构。"),
    "KL": ("KL Divergence", "11-深度学习基础/KL Divergence.md", "KL 衡量非对称分布差异；训练、正则与蒸馏中的方向和权重需要分别说明。"),
    "Flow": ("Flow Matching", "1-生成模型/Flow Matching.md", "学习把噪声送到数据的速度场，可生成图像、视频或动作；少步推理通常需额外蒸馏。"),
    "CoT": ("Chain-of-Thought Prompting", "11-深度学习基础/Chain-of-Thought Prompting.md", "思维链保存中间步骤，但可见文本不保证完整反映因果推理，也可能含冗余。"),
    "Action": ("Action Chunking", "3-机器人策略/Action Chunking.md", "动作块可降低决策频率，但接触反馈、时序与执行速度仍需单独验证。"),
    "RAG": ("Retrieval-Augmented Generation", "11-深度学习基础/Retrieval-Augmented Generation.md", "先检索证据再回答；检索、表示压缩与读出推理是不同环节，不能混为同一能力。"),
}
THEMES = {
    "2026-09-01": "推理蒸馏、可编辑三维场景、音视频生成、VLM 导航与科研评价并行。后半榜单还有长期记忆、物理导航和视频驱动动画；社区关注度不是证据强度。",
    "2026-09-02": "从学生模拟延伸到驾驶、世界动作模型、游戏控制与无人机。另有持续记忆、奖励质量和执行协议研究：理解空间和维持动作协议需要分别评价。",
    "2026-09-03": "自我改进是最集中的主题：技能、执行框架、模糊目标、经验与权重共同影响效果。多篇基准发现收益不稳定或不迁移，应和技能复用的正面结果一起看。",
    "2026-09-04": "重点包括将轨迹变环境、规格变函数、视频变示范，以及减少推理与上下文成本。世界模型开始强调可控三维结构和可审计物理评价。",
}


def main():
    days = json.loads((CACHE / "month-data.json").read_text())
    resources = json.loads((CACHE / "resource-checks.json").read_text())["papers"]
    cards, briefs = {}, {}
    for file in CACHE.glob("cards-*.json"):
        cards.update(json.loads(file.read_text()))
    for file in CACHE.glob("briefs-*.json"):
        briefs.update(json.loads(file.read_text()))
    ids = [p["id"] for d in days for p in d.get("papers", [])]
    assert len(cards) == 40 and len(briefs) == 95
    assert len(ids) == len(set(ids)) == 135
    assert set(ids) == set(cards) | set(briefs)
    assert {c[-1] for c in cards.values()} <= set(CONCEPTS)
    for _, path, _ in CONCEPTS.values():
        assert (VAULT / "PaperNotes/_concepts" / path).is_file()
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    memory = {"schema_version": 1, "days": {}, "papers": {}, "concepts": {}}
    for day in days:
        date, papers = day["date"], day.get("papers", [])
        status = "complete" if papers else day["status"]
        report = "HFDailyPapers/" + date + "-HF日报.md"
        top = [p["id"] for p in papers[:10]]
        lines = [
            "---", "source: huggingface-daily", "date: " + date,
            "status: " + status, "source_count: " + str(len(papers)),
            "summarized_count: " + str(len(papers)), "updated_at: " + now,
            "ranking_source: " + day["ranking_url"],
            "ranking_fetched_at: " + day["fetched_at"],
            "top_ten_ids: " + json.dumps(top), "---", "",
            "# " + date + " HF Daily Papers", "",
        ]
        if not papers:
            message = (
                "日期 API 成功返回空列表，本次没有收录论文。未来补更应重查，空响应不代表永远不会补录。"
                if status == "empty" else
                "日期 API 多次返回 HTTP 400，本次未取得当日榜单。状态为抓取失败，不能报告为零篇或已读完成。"
            )
            lines += [
                message, "",
                "日期网页实际回退至 2026-09-04（31 篇），未将旧榜内容冒充本日论文。",
                "", f"[日期 API]({day['source_url']}) · [日期网页]({day['ranking_url']})",
                "", "本日没有论文卡片或新增概念，需后续重新核查榜单。",
                "", "[[HFDailyPapers/2026-09-HF月度总结|本月总览]]",
            ]
        else:
            assert day["ranking_verified"]
            lines += [
                THEMES[date], "",
                f"全榜 **{len(papers)} 篇**：前十详解，其余逐篇简述。已核对网页和 API 的 ID 集合与网页标题顺序。",
                "", f"排名、点赞是 {day['fetched_at']} 查询快照，不是历史当天最终排名。上榜日与论文发表日分别记录。",
                "", f"[网页榜单]({day['ranking_url']}) · [全榜 API]({day['source_url']})",
                "", "阅读口径：前十已读摘要并核对原文方法与实验设置，不等于逐页精读或实验复现。其余默认仅摘要，结果表述为作者报告。资源页面可访问不等于权重齐全、代码可运行或数据可完全重建。",
                "", "已按标题/arXiv ID 检索 Zotero 只读快照与现有 PaperNotes，无命中；概念复用已有笔记，论文内容来自公开原文。",
                "", "## 榜单前十详解", "",
            ]
            for rank, paper in enumerate(papers, 1):
                ident = paper["id"]
                title = re.sub(r"\s+", " ", paper["title"]).strip()
                if rank == 11:
                    lines += ["## 其余论文简述", ""]
                topic = (cards[ident] if rank <= 10 else briefs[ident])[0]
                lines += [
                    f"### {rank}. {title}", "",
                    f"**arXiv：{ident} · 方向：{topic} · 点赞：{paper['upvotes']}**", "",
                    f"上榜：{date}；API 记录的论文发表时间：{paper.get('published_at') or '未提供'}。",
                    "", f"[HF]({paper['hf_url']}) · [原文]({paper['arxiv_url']})", "",
                ]
                if rank <= 10:
                    _, summary, method, evidence, judgment, key = cards[ident]
                    method = method.replace("这些前缀对教师本身是分布外的", "这些前缀并非教师自身采样得到")
                    name, path, review = CONCEPTS[key]
                    lines += [
                        "**一句话**：" + summary, "",
                        "**问题与方法**：" + method, "",
                        "**证据与边界**：" + evidence, "",
                        "**怎么看**：" + judgment, "",
                        f"**概念衔接**：[[PaperNotes/_concepts/{path[:-3]}|{name}]]。" + review, "",
                    ]
                    checked = resources.get(ident, [])
                    if checked:
                        labels = [
                            f"[资源页面]({r['url']})（HTTP {r['http_status']}，可访问；完整发布与运行未验证）"
                            if "http_status" in r else
                            f"[资源线索]({r['url']})（访问失败：{r.get('error')}）"
                            for r in checked
                        ]
                        lines += ["**资源核验**（2026-09-07）：" + "；".join(labels) + "。"]
                    else:
                        lines += ["**资源核验**（2026-09-07）：未取得可单独确认的官方代码/模型/数据地址，发布状态未核实。"]
                    original = "https://arxiv.org/pdf/" + ident if ident == "2608.29335" else paper["html_url"]
                    lines += ["", f"**阅读深度：方法与实验已核对（非全文精读）**。[核对原文]({original})。未逐项核实的细节已在卡片注明。", ""]
                    memory["concepts"][name] = {
                        "path": "PaperNotes/_concepts/" + path,
                        "aliases": [], "explained_dates": ["2026-09-07"], "user_feedback": [],
                    }
                else:
                    lines += [briefs[ident][1], "", "**阅读深度：仅摘要**；具体数字均为作者报告。", ""]
                memory["papers"][ident] = {
                    "title": paper["title"], "seen_dates": [date], "reports": [report],
                    "note": None, "reading_depth": "method_experiments" if rank <= 10 else "abstract",
                }
            lines += ["## 概念与往日联系", ""]
            for key in sorted({cards[p["id"]][-1] for p in papers[:10]}):
                name, path, review = CONCEPTS[key]
                lines += [f"- [[PaperNotes/_concepts/{path[:-3]}|{name}]]：{review}"]
            lines += [
                "", "这四天无重复上榜 ID；跨论文主题联系见 [[HFDailyPapers/2026-09-HF月度总结|月度总览]]。已有论文无标题/ID 命中，因此没有附会旧论文链接。",
                "", "## 完成状态与范围", "",
                f"来源 {len(papers)} 个 ID 均有卡片；前十已核对原文方法与实验，其余已读作者摘要，无缺摘要待办。complete 仅表示约定阅读层级已完成，不表示所有论文全文精读或实验复现。",
            ]
        (VAULT / report).write_text("\n".join(lines) + "\n")
        memory["days"][date] = {
            "status": status, "report": report,
            "source_ids": [p["id"] for p in papers],
            "summarized_ids": [p["id"] for p in papers],
            "pending_ids": [], "fetched_at": day["fetched_at"],
            "ranking_source": day["ranking_url"], "ranking_fetched_at": day["fetched_at"],
            "top_ten_ids": top,
        }
    pending = ROOT / ".memory.write.json"
    pending.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n")
    pending.replace(ROOT / ".memory.json")
    nav = ["# 本次 HF 阅读的概念导航", "", "解释日期：2026-09-07。不推断用户掌握程度。", ""]
    for name, path, review in CONCEPTS.values():
        nav += [f"- [[PaperNotes/_concepts/{path[:-3]}|{name}]]：{review}"]
    nav += [
        "", "新增 On-Policy Distillation 与 Agent Harness，其余复用已有定义。",
        "", "全库 MOC 脚本会整页覆盖已有目录，库中有用户未提交修改。本次遵守保留原内容的要求，采用本独立概念导航，不重写旧目录页。",
    ]
    (ROOT / "2026-09-概念导航.md").write_text("\n".join(nav) + "\n")
    print("Rendered 7 daily reports; 40 detailed + 95 brief cards; ledger and concept navigation.")


if __name__ == "__main__":
    main()
