#!/usr/bin/env python3
"""Commit identity guard (founder rule, 2026-11-22).

Every commit in every Morse repo is authored AND committed as

    morsehq-dev <service@morsehq.dev>

and no commit message credits anyone else: no Co-authored-by / Signed-off-by
style trailers and no AI-tool attribution ("Generated with Claude Code",
noreply@anthropic.com, ...). Agents (Claude Code, Codex, Gemini, Cowork) and
humans alike. The canonical copy lives in morse-core/scripts/; every repo
carries an identical copy wired into its .pre-commit-config.yaml.

Why: on 2026-11-22 both SDK repos had to be replaced with rewritten history
before going public, because commits carried a machine-specific author name
and "Co-Authored-By: Claude" trailers. A public repo's commits cannot be
cleaned without replacing the repo.

Modes (one per git hook stage):
  identity          pre-commit: the author and committer git is about to use
  message <file>    commit-msg: the message being written
  push              pre-push: every commit about to leave this machine
  --selftest        pin the message rules in both directions

Skipping is deliberate and visible (SKIP=commit-identity git commit ...).
Never --no-verify.
"""

import os
import re
import subprocess
import sys

NAME = "morsehq-dev"
EMAIL = "service@morsehq.dev"
IDENT = f"{NAME} <{EMAIL}>"

# Any trailer that credits a person or tool other than the commit author.
TRAILER = re.compile(
    r"^\s*(co-authored-by|signed-off-by|reviewed-by|helped-by|assisted-by|"
    r"suggested-by|acked-by|tested-by|generated-by)\s*:",
    re.I,
)
# AI-tool attribution lines, with or without a trailer key.
ATTRIBUTION = re.compile(
    r"(noreply@anthropic\.com|claude\.com/claude-code|claude\.ai/code|"
    r"generated (with|by) \[?(claude|codex|gemini|copilot|cursor|chatgpt|openai)|"
    r"🤖 generated)",
    re.I,
)
SCISSORS = "# ------------------------ >8 ------------------------"
ZERO = re.compile(r"^0+$")

FIX_IDENT = f"""
  Fix (once per machine):
    git config --global user.name {NAME}
    git config --global user.email {EMAIL}
  and remove any per-repo override:  git config --local --unset user.name; git config --local --unset user.email
  and unset GIT_AUTHOR_NAME / GIT_AUTHOR_EMAIL / GIT_COMMITTER_NAME / GIT_COMMITTER_EMAIL if set.
  Claude Code: set "attribution": {{"commit": "", "pr": "", "sessionUrl": false}} in ~/.claude/settings.json."""


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def parse_ident(raw: str) -> str:
    m = re.match(r"^(.*?) <(.*?)>", raw.strip())
    return f"{m.group(1)} <{m.group(2)}>" if m else raw.strip()


def message_problems(text: str) -> list[str]:
    problems = []
    for line in text.split(SCISSORS, 1)[0].splitlines():
        if line.startswith("#"):
            continue
        if TRAILER.search(line) or ATTRIBUTION.search(line):
            problems.append(line.strip())
    return problems


def check_identity() -> int:
    bad = []
    for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        who = parse_ident(git("var", var))
        if who != IDENT:
            bad.append(f"  {var.split('_')[1].lower()}: {who}")
    if not bad:
        return 0
    print(f"Commit identity must be {IDENT} (founder rule, 2026-11-22). Found:")
    print("\n".join(bad))
    print(FIX_IDENT)
    return 1


def check_message(path: str) -> int:
    with open(path, encoding="utf-8", errors="replace") as fh:
        problems = message_problems(fh.read())
    if not problems:
        return 0
    print("Commit messages carry no co-author or AI-attribution lines (founder rule, 2026-11-22).")
    print("Remove these lines and commit again:")
    for p in problems:
        print(f"  {p}")
    print('Claude Code: set "attribution": {"commit": "", "pr": "", "sessionUrl": false} in ~/.claude/settings.json.')
    return 1


def check_push() -> int:
    to_ref = os.environ.get("PRE_COMMIT_TO_REF") or "HEAD"
    if ZERO.match(to_ref):  # branch deletion: nothing leaves the machine
        return 0
    out = git("rev-list", "--format=%H%x00%an <%ae>%x00%cn <%ce>%x00%B%x01", "--no-commit-header",
              to_ref, "--not", "--remotes")
    bad = []
    for rec in filter(str.strip, out.split("\x01")):
        sha, author, committer, body = rec.strip("\n").split("\x00", 3)
        why = []
        if author != IDENT:
            why.append(f"author {author}")
        if committer != IDENT:
            why.append(f"committer {committer}")
        why += [f"message line: {p}" for p in message_problems(body)]
        if why:
            bad.append(f"  {sha[:10]} {body.splitlines()[0] if body.strip() else ''}\n      " + "\n      ".join(why))
    if not bad:
        return 0
    print(f"Refusing to push commits that are not {IDENT} or that carry attribution lines:")
    print("\n".join(bad))
    print(f"""
  Rewrite them before pushing (unpushed commits only), e.g.:
    git rebase -r <base> --exec 'git commit --amend --no-edit --reset-author'
  and edit any message still listed with `git rebase -r -i <base>` (reword).{FIX_IDENT}""")
    return 1


def selftest() -> int:
    must_flag = [
        "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
        "co-authored-by: someone <a@b.c>",
        "Signed-off-by: Jane <jane@example.com>",
        "🤖 Generated with [Claude Code](https://claude.com/claude-code)",
        "Generated with Codex",
        "  Co-authored-by: x <y>",
    ]
    must_pass = [
        "fix(sdk): record the provider response id on Anthropic and LangChain llm spans",
        "Claude and LangChain calls behind a gateway were counted twice.",
        "wrapAnthropic reads the response body once",
        "# Co-Authored-By: comment lines are stripped by git",
        "docs: explain how co-authored commits are rejected",
    ]
    failed = [m for m in must_flag if not message_problems(m)]
    failed += [m for m in must_pass if message_problems(m)]
    for m in failed:
        print(f"selftest FAILED on: {m}")
    print("selftest ok" if not failed else f"{len(failed)} selftest failure(s)")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    mode = argv[0]
    if mode == "identity":
        return check_identity()
    if mode == "message" and len(argv) > 1:
        return check_message(argv[1])
    if mode == "push":
        return check_push()
    if mode == "--selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
