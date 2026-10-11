"""Integrate per-chapter markdown drafts into a single manuscript.md.

Reads:
- vault/Private/Facebook/_book/manuscript/{1,2,3,yj}/{ch}.md
- vault/Private/Facebook/_book/04_B_outline_revised_v4.md (for part intros / structure)

Writes:
- vault/Private/Facebook/_book/manuscript.md
- vault/Private/Facebook/_book/_quality_report.md (from _harness_logs/*.json)
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

VAULT = Path("/Users/terrytaewoongum/Codes/personal/context/terry-obsidian/vault/Private/Facebook/_book")
MANU = VAULT / "manuscript"
LOGS = VAULT / "_harness_logs"
OUTLINE = VAULT / "04_B_outline_revised_v4.md"
ROOT = Path(__file__).resolve().parents[1]
LOCAL_YJ = ROOT / "_workspace" / "yj"

PART_ORDER = [
    ("1", "Part 1. 대학원생이던 나는 무엇을 믿었나", ["1.1", "1.2", "1.3"]),
    ("1", "Part 2. 박사를 멈추며 무엇이 깨졌나", ["1.4", "1.5"]),
    ("2", "Part 3. 창업은 나를 어떻게 드러냈나", ["2.1", "2.2", "2.3", "2.4"]),
    ("2", "Part 4. ART Lab을 끝내며 무엇을 배웠나", ["2.5"]),
    ("3", "Interlude. 그 사이를 흐른 인생의 시간", ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6"]),
    ("yj", "Epilogue. 연장전: 더 큰 운동장으로",
     ["yj.1", "yj.2", "yj.3", "yj.4"]),
]

FRONTMATTER = """---
title: 대학원생, 그 후 10년
subtitle: 연구와 창업, 그리고 계획대로 되지 않는 인생 앞에서
author: 엄태웅 (Terry)
draft: v1
created: {created}
---

"""


def read_chapter(part_id: str, ch: str) -> str | None:
    if part_id == "yj":
        local = LOCAL_YJ / ch / "draft_v2_final.md"
        if local.exists():
            return local.read_text(encoding="utf-8").strip()

    p = MANU / part_id / f"{ch}.md"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").strip()


def integrate() -> dict:
    parts: list[str] = []
    missing: list[str] = []
    word_count = 0

    parts.append(FRONTMATTER.format(created=date.today().isoformat()))
    parts.append("# 대학원생, 그 후 10년\n")
    parts.append("## 연구와 창업, 그리고 계획대로 되지 않는 인생 앞에서\n\n")

    prologue = MANU / "prologue.md"
    if prologue.exists():
        parts.append(prologue.read_text(encoding="utf-8").strip() + "\n\n")

    for part_id, part_title, ch_list in PART_ORDER:
        parts.append(f"\n# {part_title}\n\n")
        for ch in ch_list:
            body = read_chapter(part_id, ch)
            if body is None:
                missing.append(ch)
                parts.append(f"\n<!-- MISSING: {ch}.md -->\n\n")
                continue
            parts.append(body + "\n\n")
            word_count += len(body.split())

    out = MANU.parent / "manuscript.md"
    out.write_text("".join(parts), encoding="utf-8")
    return {"missing": missing, "word_count": word_count, "out": str(out)}


def quality_report() -> dict:
    if not LOGS.exists():
        return {"logs": 0, "out": None}

    rows = []
    for p in sorted(LOGS.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({"id": p.stem, "error": str(exc)})
            continue
        rows.append(d)

    if not rows:
        return {"logs": 0, "out": None}

    lines = ["# Quality Report — 대학원생, 그 후 10년 (v1 draft)\n"]
    lines.append(f"\n생성일: {date.today().isoformat()}\n")
    lines.append(f"\n총 챕터: {len(rows)}\n\n")
    lines.append("| chapter | final_avg | rounds | reader_main | specialist | outsider | critic | editor |\n")
    lines.append("|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        cid = r.get("chapter_id", r.get("id", "?"))
        fa = r.get("final_avg", r.get("avg_score", "-"))
        rd = r.get("rounds", r.get("cycle_count", "-"))
        s = r.get("scores", {})
        lines.append(
            f"| {cid} | {fa} | {rd} | {s.get('reader_mainstream','-')} | "
            f"{s.get('reader_specialist','-')} | {s.get('reader_outsider','-')} | "
            f"{s.get('critic','-')} | {s.get('editor','-')} |\n"
        )

    out = VAULT / "_quality_report.md"
    out.write_text("".join(lines), encoding="utf-8")
    return {"logs": len(rows), "out": str(out)}


if __name__ == "__main__":
    res_int = integrate()
    res_q = quality_report()
    print(json.dumps({"integrate": res_int, "quality": res_q}, ensure_ascii=False, indent=2))
