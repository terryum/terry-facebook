"""Build local review manuscripts without modifying the source vault.

Outputs:
- _workspace/book_review/full_manuscript_before.md
- _workspace/book_review/full_manuscript_current.md

The current version uses the plan-oriented structure:
Prologue -> Part 1 -> Part 2 -> Part 3 -> Part 4 -> Interlude -> Epilogue.
It preserves the existing "인생의 시간" chapters as an interlude so the
read-through still contains every available chapter.
"""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT_BOOK = Path(
    "/Users/terrytaewoongum/Codes/personal/context/terry-obsidian/vault/Private/Facebook/_book"
)
SOURCE = VAULT_BOOK / "manuscript"
LOCAL_YJ = ROOT / "_workspace" / "yj"
OUT = ROOT / "_workspace" / "book_review"


FRONTMATTER = """---
title: 대학원생, 그 후 10년
subtitle: 연구와 창업, 그리고 계획대로 되지 않는 인생 앞에서
author: 엄태웅 (Terry)
review: plan-structured-full-read
---

"""


SECTIONS = [
    ("Prologue. 첫 책 이후, 내가 몰랐던 것들", [("root", "prologue")]),
    (
        "Part 1. 대학원생이던 나는 무엇을 믿었나",
        [("1", "1.1"), ("1", "1.2"), ("1", "1.3")],
    ),
    (
        "Part 2. 박사를 멈추며 무엇이 깨졌나",
        [("1", "1.4"), ("1", "1.5")],
    ),
    (
        "Part 3. 창업은 나를 어떻게 드러냈나",
        [("2", "2.1"), ("2", "2.2"), ("2", "2.3"), ("2", "2.4")],
    ),
    ("Part 4. ART Lab을 끝내며 무엇을 배웠나", [("2", "2.5")]),
    (
        "Interlude. 그 사이를 흐른 인생의 시간",
        [("3", "3.1"), ("3", "3.2"), ("3", "3.3"), ("3", "3.4"), ("3", "3.5"), ("3", "3.6")],
    ),
    (
        "Epilogue. 연장전: 더 큰 운동장으로",
        [("yj-local", "yj.1"), ("yj-local", "yj.2"), ("yj-local", "yj.3"), ("yj-local", "yj.4")],
    ),
]

MAIN_TEXT_REPLACEMENTS = [
    ("코스맥스 AI혁신본부장", "새 조직에서 AI와 로봇을 다루는 사람"),
    ("코스맥스 AI혁신그룹장", "새 조직에서 AI와 로봇을 다루는 사람"),
    ("코스맥스 본사 한쪽 사무실의 책상", "지금의 책상"),
    ("코스맥스가 ART Lab 을 인수했고", "ART Lab의 인수가 결정됐고"),
    ("코스맥스가 ART Lab을 인수", "ART Lab의 인수가 결정"),
    ("코스맥스의 인수 제안", "인수 제안"),
    ("코스맥스 인수", "인수"),
    ("코스맥스 합류", "새 조직 합류"),
    ("코스맥스로", "새 조직으로"),
    ("코스맥스 입사 첫날", "새 조직에 들어간 첫날"),
    ("코스맥스 이야기가", "인수 이야기가"),
    ("코스맥스 강연", "새 조직에서의 강연"),
    ("코스맥스 회장님", "새 조직에서 만난 한 리더"),
    ("코스맥스라는 운동장", "더 큰 운동장"),
    ("코스맥스라는 플랫폼", "더 큰 제조 플랫폼"),
    ("코스맥스라는 더 큰 판", "더 큰 판"),
    ("코스맥스라는 더 큰 운동장", "더 큰 운동장"),
    ("코스맥스라는", "더 큰"),
    ("코스맥스에서", "새 조직에서"),
    ("코스맥스에", "새 조직에"),
    ("코스맥스는", "새 조직은"),
    ("코스맥스의", "새 조직의"),
    ("코스맥스를", "새 조직을"),
    ("코스맥스와", "새 조직과"),
]


def read_chapter(part: str, chapter: str) -> str:
    if part == "root":
        path = SOURCE / f"{chapter}.md"
    elif part == "yj-local":
        path = LOCAL_YJ / chapter / "draft_v2_final.md"
    else:
        path = SOURCE / part / f"{chapter}.md"
    text = path.read_text(encoding="utf-8").strip()
    if part == "root" and text.startswith("# Prologue\n"):
        text = text.split("\n", 1)[1].strip()
    return text


def build_current() -> str:
    chunks: list[str] = [
        FRONTMATTER,
        "# 대학원생, 그 후 10년\n",
        "## 연구와 창업, 그리고 계획대로 되지 않는 인생 앞에서\n\n",
    ]

    for title, chapters in SECTIONS:
        chunks.append(f"\n# {title}\n\n")
        for part, chapter in chapters:
            chunks.append(read_chapter(part, chapter))
            chunks.append("\n\n")

    text = "".join(chunks).rstrip() + "\n"
    return post_process_current(text)


def post_process_current(text: str) -> str:
    marker = "\n# Epilogue. 연장전: 더 큰 운동장으로\n"
    main, sep, epilogue = text.partition(marker)
    for before, after in MAIN_TEXT_REPLACEMENTS:
        main = main.replace(before, after)

    main = main.replace(
        "이 책의 구조도 그래서 단순하다. 학문의 시간, 창업의 시간, 그리고 그 두 시간과 평행하게 흘러간 인생의 시간 — 세 갈래로 나누고, 각 갈래의 변곡점들을 한 챕터씩 짚어가는 방식이다. 그리고 그 세 갈래가 한 번 매듭지어진 자리 뒤에, 새로 시작되어 아직 진행 중인 시간이 한 챕터 더 붙어 있다. 더 큰 운동장에서 다시 학습자가 되어 있는 지금의 시간인데, 정리된 회고가 아니라 진행 중인 메모에 가까워서 책의 다른 부분과는 결이 조금 다를 수도 있을 것 같다.",
        "이 책의 구조도 그래서 단순하다. 대학원생이던 내가 믿었던 것들, 박사를 멈추며 깨진 것들, 창업이 드러낸 나의 모순, 그리고 ART Lab을 끝내며 배운 것들을 차례로 짚는다. 그 뒤에는 그 시간들의 뒤편에서 함께 흐르던 인생의 이야기와, 아직 결론을 내릴 수 없는 연장전의 시간이 붙어 있다.",
    )
    main = main.replace(
        "Part 1과 Part 2에서 학문과 창업이라는 일렬의 시간을 따라갔다면, 이 Part 3은 그 시간들의 뒤편에서 언제나 함께 흐르던 또 다른 축이다.",
        "앞선 장들에서 학문과 창업이라는 일렬의 시간을 따라갔다면, 이 Interlude는 그 시간들의 뒤편에서 언제나 함께 흐르던 또 다른 축이다.",
    )
    main = main.replace(
        "Part 1에서 회사 내 작은 사무실 책상에서 밤마다 GRE 문제지를 풀던 그 사람과, Part 2에서 투자 미팅 후 돌아오는 지하철 안에서 다음 분기 계획을 다시 쓰던 그 사람이 같은 사람이었다.",
        "회사 내 작은 사무실 책상에서 밤마다 GRE 문제지를 풀던 학문기의 나와, 투자 미팅 후 돌아오는 지하철 안에서 다음 분기 계획을 다시 쓰던 창업기의 내가 같은 사람이었다.",
    )
    main = main.replace(
        "Part 1에서 학문의 시간이 있었고, Part 2에서 창업의 시간이 있었다. 그 두 시절을 관통하던 이 Part 3의 이야기",
        "앞선 장들에는 학문의 시간과 창업의 시간이 있었다. 그 두 시절을 관통하던 이 Interlude의 이야기",
    )
    main = main.replace("지금 지금의 책상에서", "지금의 책상에서")

    return main + sep + epilogue


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    before = (VAULT_BOOK / "manuscript.md").read_text(encoding="utf-8")
    current = build_current()

    before_path = OUT / "full_manuscript_before.md"
    current_path = OUT / "full_manuscript_current.md"
    readme_path = OUT / "README.md"

    before_path.write_text(before, encoding="utf-8")
    current_path.write_text(current, encoding="utf-8")
    readme_path.write_text(
        "\n".join(
            [
                "# 전체 원고 검토용 파일",
                "",
                "- `full_manuscript_current.md`: 계획 구조와 수정된 에필로그를 반영한 전체 읽기본",
                "- `full_manuscript_before.md`: vault에 있던 기존 통합본",
                "",
                "Diff 확인:",
                "",
                "```bash",
                "git diff --no-index _workspace/book_review/full_manuscript_before.md _workspace/book_review/full_manuscript_current.md",
                "```",
                "",
                "현재 읽기본은 기존 `Part 3. 인생의 시간` 여섯 장을 `Interlude`로 보존한다.",
                "이렇게 해야 계획의 본편 4부 구조를 살리면서도 기존 원고 전체를 빠짐없이 읽을 수 있다.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(current_path)
    print(before_path)


if __name__ == "__main__":
    main()
