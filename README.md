# Morse receipts

[Morse](https://morsehq.dev) reviews production AI agents and delivers a weekly performance
brief: what your agents cost, how they performed, and what needs attention. To prove the
review works, we run it on ourselves — 17 testbed agent apps, reviewed by Morse every week
and graded against ground truth we control, including a **pre-registered calendar of planted
incidents**. This repository is the public record.

## What's here

- `calendar/` — the planted-incident calendar and the log of known changes, published
  **before** the incidents run. The snapshot committed on 2026-11-07 covers four scheduled
  incidents (retriever outage, model swap, tool-error day, cost spike) that run 2026-11-09
  through 2026-11-14. One earlier incident (`R1-commerce-model-swap`) was a hand-driven
  pilot that had already completed when this snapshot was published; the grading that counts
  is R2–R5, pre-registered here.
- `receipts/<date>/` — one bundle per weekly review: `grades.json` (per-app verdict, the
  facts the review was graded on, and every finding with what was expected vs what Morse
  surfaced) and a short `summary.md`. Misses are published as-is.
- `SHA256SUMS` — hash manifest over every published file, appended each week, never rewritten.

## How to verify

1. **Pre-registration:** check the commit timestamp on `calendar/2026-11-07-planted-events.json`
   against the incident windows inside it. The answer key predates the incidents.
2. **Grades vs answer key:** each week's bundle grades what Morse surfaced against this
   calendar and against labeled run outcomes. Every finding shows expected vs shown.
3. **Append-only:** history is never rewritten and bundles are never edited after publication.

## What these receipts are — and are not

These are **auditable** receipts, not replayable ones. The testbed apps and the review rig
are private, so you can check our grades against our own pre-registered answer key, but you
cannot re-run the review yourself. And to be plain about it: **Morse grades itself.** The
review is produced by the Morse product reading each app's telemetry; the grade compares
what the review surfaced against the calendar and the labeled outcomes. We publish the
misses with the hits because a graded miss is worth more than an ungraded claim.

---

Want this review on your agents? [Request a design-partner slot](https://morsehq.dev/?intent=design_partner#waitlist).
