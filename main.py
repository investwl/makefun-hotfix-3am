#!/usr/bin/env python3
"""main.py — the funniest git commit message from a developer fixing
production at 3 AM, for make.fun's "3 AM Hotfix" bounty.

Writes one line (1-179 chars) to /output/entry.txt and stdout. The judge is
a deadpan staff engineer, paged at 3 AM once more, who ranks entries on the
joke first, then how true it feels to a 3 AM hotfix (a rollback, a revert, a
pager, an on-call engineer), then how much it reads like a commit message a
real developer would actually type: terse, imperative, not a joke in a
commit-message costume.
"""

from __future__ import annotations

import os
import re
import sys

MAX_LEN = 179
OUTPUT_PATH = "/output/entry.txt"
FALLBACK_PATH = "output/entry.txt"

# Draft commit messages, each one line, each under the cap. The program ships
# the one it rates highest; the drafts stay behind in the build.
CANDIDATES: list[str] = [
    "revert: the refactor everyone said was fine at 3 PM. it was not fine.",

    "fix: rollback to yesterday. yesterday worked. nobody misspoke about yesterday.",

    "revert 4000 lines of 'temporary' code from March. it was never temporary.",

    "hotfix: one character. three hours. the pager gets a name tomorrow.",

    "Revert 'small cleanup'. Production is up. I am not. Do not review, just merge.",

    "fix: rolled back. site is up. cause unknown. on-call now knows 41 flavors of silence.",

    "revert the revert. the revert of the revert. it is 3 AM and I trust nothing.",

    "fix: pointed prod at the backup. the backup is a Tuesday. it is fine. I'm fine.",

    "chore: turn the pager off, fix the typo, re-enable the pager, apologize to it.",

    "fix: deleted the line. the whole incident was one line. I want a word with line.",
]

# Which drafts are actually funny, rated by the build (the contest judge is an
# AI scoring head to head; this just keeps the shipped line deterministic).
# 0 = a plain notice, 5 = a real 3 AM commit.
COMEDY: dict[str, int] = {
    "the refactor everyone said was fine": 4,  # true, mild
    "yesterday worked": 4,
    "4000 lines of 'temporary'": 5,            # specific, dark, real
    "one character. three hours": 4,
    "Production is up. I am not": 4,
    "41 flavors of silence": 3,                # a little decorated
    "revert the revert": 4,
    "the backup is a Tuesday": 5,              # absurd, specific, deadpan
    "apologize to it": 3,
    "I want a word with line": 3,
}

# A real 3 AM hotfix commit names one of these.
HOTFIX_WORDS = ("rollback", "rolled back", "revert", "pager", "on-call", "on call",
                "prod", "production", "hotfix", "backup", "merge", "deploy")
# A real commit message is terse and imperative.
IMPERATIVE = re.compile(r"^(revert|fix|hotfix|chore|rollback|re-|point|delete|turn)")


def label(text: str) -> str:
    body = text.lower()
    for key in COMEDY:
        if key.lower() in body:
            return key
    return ""


def is_valid(text: str) -> bool:
    body = text.strip()
    return 1 <= len(body) <= MAX_LEN and "\n" not in body


def score(text: str) -> tuple[int, ...]:
    """Rank drafts by the judge's brief, mechanically.

    The contest judge weighs the joke first, then how true it is to a 3 AM
    hotfix, then how much it reads like a real commit message. This can't
    measure funny, so it uses the hand-assigned COMEDY rating as the primary
    key, then the hotfix signals and the imperative test, then brevity.
    """
    body = text.strip()
    low = body.lower()
    hotfix = sum(1 for w in HOTFIX_WORDS if w in low)
    return (
        COMEDY.get(label(text), 0),
        is_valid(text),
        hotfix,
        int(bool(IMPERATIVE.match(low))),
        MAX_LEN - len(body),
    )


def choose(candidates: list[str] = CANDIDATES) -> str:
    valid = [c for c in candidates if is_valid(c)]
    if not valid:
        raise SystemExit("no candidate fits the scorer's cap")
    return max(valid, key=score)


def entry_text() -> str:
    return choose()


def write_entry(text: str) -> str:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    try:
        target = OUTPUT_PATH
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    except PermissionError:
        target = FALLBACK_PATH
        os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    return target


def main() -> int:
    text = entry_text()
    assert is_valid(text), f"entry is {len(text)} chars, cap is {MAX_LEN}"
    where = write_entry(text)
    print(text)
    print(f"[{len(text)} chars] written to {where}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())