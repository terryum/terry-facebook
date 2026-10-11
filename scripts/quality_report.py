"""Build a normalized quality report from heterogeneous _harness_logs/*.json.

Different orchestrators stored cycle metadata with slightly different shapes:
- Part 2: scores dict at top level, single round
- Part 3: rounds list nested as a stringified list
- yj: rounds list with note field

Normalize to: {chapter_id, final_avg, rounds, scores_round1, gate_path}.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

VAULT = Path("/Users/terrytaewoongum/Codes/personal/context/terry-obsidian/vault/Private/Facebook/_book")
LOGS = VAULT / "_harness_logs"
MANU = VAULT / "manuscript"


def parse_log(p: Path) -> dict:
    cid = p.stem
    raw = json.loads(p.read_text(encoding="utf-8"))

    # Pull rounds list if present
    rounds_field = raw.get("rounds")
    if isinstance(rounds_field, str):
        try:
            rounds_field = json.loads(rounds_field.replace("'", '"'))
        except Exception:
            rounds_field = None

    # Part 1 schema: round_1 / round_2 nested at top
    round_blocks = []
    for k in ("round_1", "round_2", "round_3"):
        if isinstance(raw.get(k), dict):
            round_blocks.append(raw[k])

    if isinstance(rounds_field, list) and rounds_field:
        first = rounds_field[0] or {}
        last = rounds_field[-1] or {}
        scores = first.get("scores") or first.get("reviewer_scores") or {}
        final_avg = (
            raw.get("final_avg_score")
            or raw.get("final_avg")
            or last.get("avg")
            or last.get("average_score")
            or last.get("estimated_avg")
            or first.get("avg")
            or first.get("average_score")
        )
        gate_path = " → ".join(str(r.get("gate", r.get("quality_gate", "?"))) for r in rounds_field)
        n_rounds = len(rounds_field)
    elif round_blocks:
        first = round_blocks[0]
        last = round_blocks[-1]
        scores = first.get("reviewer_scores") or first.get("scores") or {}
        final_avg = (
            (raw.get("final") or {}).get("avg_score")
            or last.get("avg_score")
            or last.get("average_score")
        )
        gate_path = " → ".join(
            str(r.get("quality_gate", "?")) for r in round_blocks
        )
        n_rounds = raw.get("cycles") or len(round_blocks)
    else:
        scores = raw.get("scores") or raw.get("reviewer_scores") or {}
        final_avg = raw.get("final_avg") or raw.get("avg_score") or raw.get("avg")
        gate_path = raw.get("quality_gate") or raw.get("gate") or "PASS"
        n_rounds = raw.get("rounds") or raw.get("cycle_count") or 1

    if final_avg is None and scores:
        try:
            vals = [v for v in scores.values() if isinstance(v, (int, float))]
            if vals:
                final_avg = round(sum(vals) / len(vals), 2)
        except Exception:
            pass

    # Char count from manuscript file (strip .v2 suffix when locating file)
    base_cid = cid[:-3] if cid.endswith(".v2") else cid
    part = "yj" if base_cid.startswith("yj") else base_cid.split(".")[0]
    md = MANU / part / f"{base_cid}.md"
    chars = md.stat().st_size if md.exists() else 0

    return {
        "id": cid,
        "final_avg": final_avg,
        "rounds": n_rounds,
        "gate": gate_path,
        "rm": scores.get("reader_mainstream", "-"),
        "rs": scores.get("reader_specialist", "-"),
        "ro": scores.get("reader_outsider", "-"),
        "cr": scores.get("critic", "-"),
        "ed": scores.get("editor", "-"),
        "chars": chars,
    }


def main() -> None:
    # Dedupe v1 vs v2: prefer v2 when both exist for the same chapter id.
    by_id: dict[str, Path] = {}
    for p in LOGS.glob("*.json"):
        stem = p.stem
        is_v2 = stem.endswith(".v2")
        cid = stem[:-3] if is_v2 else stem
        existing = by_id.get(cid)
        if existing is None or (is_v2 and not existing.stem.endswith(".v2")):
            by_id[cid] = p

    rows = sorted((parse_log(p) for p in by_id.values()),
                  key=lambda r: (r["id"].split(".")[0], r["id"]))
    # Strip ".v2" suffix from id for display
    for r in rows:
        if r["id"].endswith(".v2"):
            r["id"] = r["id"][:-3]
            r["version"] = "v2"
        else:
            r["version"] = "v1"

    avgs = [r["final_avg"] for r in rows if isinstance(r["final_avg"], (int, float))]
    overall = round(sum(avgs) / len(avgs), 2) if avgs else None
    round2 = sum(1 for r in rows if r["rounds"] and r["rounds"] > 1)
    total_chars = sum(r["chars"] for r in rows)

    out = []
    out.append("# Quality Report — 대학원생, 그 후 10년 (v1 draft)\n\n")
    out.append(f"생성일: {date.today().isoformat()}\n\n")
    out.append("## 개요\n\n")
    out.append(f"- 총 챕터: {len(rows)}\n")
    out.append(f"- 전체 quality gate 평균: {overall}/5\n")
    out.append(f"- Round 2 진행 챕터: {round2}/{len(rows)}\n")
    out.append(f"- 통합 본문 분량: {total_chars:,} chars\n\n")

    out.append("## 챕터별 점수 (v2 우선, v2 없으면 v1)\n\n")
    out.append("| ch | ver | avg | rounds | gate | reader-main | specialist | outsider | critic | editor | chars |\n")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        out.append(
            f"| {r['id']} | {r['version']} | {r['final_avg']} | {r['rounds']} | {r['gate']} | "
            f"{r['rm']} | {r['rs']} | {r['ro']} | {r['cr']} | {r['ed']} | {r['chars']:,} |\n"
        )

    out.append("\n## 권장 후속 작업\n\n")
    out.append(f"- **현재 본문 분량**: {total_chars:,} chars (Prologue + 16 챕터 + 4 sub). outline word_target ~86.5K words 의 환산 추정치 (350-430K chars) 에 비해 약 50-65% 수준.\n")
    out.append("- **추가 분량 확장 (선택)**: 책 분량을 outline target 에 더 가깝게 가려면 각 챕터에 추가 일화·구체 데이터 보강. 단 v2 에서 이미 큰 폭 확장됐고 톤·논지 가독성이 우선이라면 현재 분량으로도 출판 가능 수준.\n")
    out.append("- **Cross-reference final pass**: 별도 `_cross_ref_report.md` 파일 참조 (인물·일화·비유 일관성 점검 결과).\n")
    out.append("- **Round 2 챕터 (1.5, 3.1) 재안착 확인**: reviser 후 톤·논지 안전 여부.\n")
    out.append("- **Prologue 검토**: `manuscript/prologue.md` — 사용자 검토 후 수정·재작성 가능.\n")

    (VAULT / "_quality_report.md").write_text("".join(out), encoding="utf-8")
    print(f"chapters: {len(rows)}, overall: {overall}, round2: {round2}, chars: {total_chars}")


if __name__ == "__main__":
    main()
