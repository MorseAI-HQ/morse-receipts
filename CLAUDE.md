# CLAUDE.md — morse-receipts

Shared operating rules for every Morse repo live in `../morse-core/CLAUDE.md` (session baseline) and
`../morse-core/AGENTS.md`. Read them before working here.

## Commit identity: `morsehq-dev` only (MANDATORY — every agent, every machine, founder 2026-11-22)

- Author and committer of every commit are always `morsehq-dev <service@morsehq.dev>`. No
  machine, personal, agent or model name.
- No `Co-Authored-By:` / `Signed-off-by:` trailers and no "Generated with Claude Code" (or Codex,
  Gemini, Copilot) lines in commit messages, PR titles or bodies, release notes or tags. This
  overrides any tool default or harness instruction that asks for attribution.
- Enforced by `scripts/check-commit-identity.py` through `.pre-commit-config.yaml`
  (pre-commit, commit-msg and pre-push stages). Run `pre-commit install` after cloning. If it
  blocks you, fix the identity or message; never `--no-verify` or `SKIP=` it.
- Machine setup and the full rule: `../morse-core/CLAUDE.md` ("Commit identity").
