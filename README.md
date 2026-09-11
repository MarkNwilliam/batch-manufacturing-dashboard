<div align="center">

# Batch Manufacturing Dashboard

**Batch yield, processing times, rejections, downtime and operator productivity for a solid-dose plant**

Built for the Production Officer looking at the same records the BMR produces —
charge size, packed output, process hours and disposition — and needing to
answer *"are the last twelve months going in the right direction?"* in one view.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](#)
[![No deps](https://img.shields.io/badge/python-dependencies-none-blue)](#)
[![Stack](https://img.shields.io/badge/stack-HTML%20%2B%20CSS%20%2B%20JS-f59e0b)](#)
[![Tests](https://img.shields.io/badge/tests-10%20passing-green)](#)
[![License](https://img.shields.io/badge/license-MIT-green)](#)

</div>

---

## Why this exists

A batch record answers "did *this* batch pass?". A batch **analytics layer**
answers "are the *trends* drifting?" — is yield creeping down, are process
times stretching, is one operator's rejection rate climbing, and is downtime
concentrated in one equipment class. These are the signals a production
department reviews months after a batch has left the plant, and the same
signals a Planner uses to size capacity.

## What it computes

- **Material yield** `= actual recovered kg / theoretical (charge) kg` per batch.
- **Monthly yield trend** — mean yield grouped by ISO month, with batch counts.
- **Rejection rate** — rejected / closed batches, plus the *rejected batch list*
  (newest first) with the reason recorded from the investigation.
- **Unreleased inventory** — batches on-hold or in-progress (the ones that still
  owe the warehouse output).
- **Mean process time** per batch (hours).
- **Operator productivity** — batches handled, approvals, rejections, mean yield,
  total hours and **kg/h** per operator. Useful for spotting training gaps or
  over-allocation on one line.
- **Downtime Pareto** — aggregated lost minutes by reason, largest first.

## What's in the repo

- **`batch_analysis.py`** — dependency-free library + CLI with a 22-batch demo
  year (3 products, 5 operators) and a downtime list.
- **`test_batch_analysis.py`** — 10 unit tests covering the math and the
  grouping/sorting logic.
- **`index.html`** — standalone interactive dashboard: yield trend chart,
  downtime Pareto, batch log with disposition pills, operator leaderboard,
  CSV export. No build step, works offline.

## Quick start

```bash
# web dashboard
open index.html

# CLI (12 months of demo batches)
python3 batch_analysis.py

# library
python3 -c "
import batch_analysis as ba
print(f\"Rejection rate: {ba.rejection_rate(ba.DEMO_BATCHES):.1%}\")
print(ba.monthly_trend(ba.DEMO_BATCHES)[:3])"

# tests
python3 -m unittest test_batch_analysis -v
```

## Example output

```
Batches analysed: 22
Rejection rate:   13.6%
Mean process time: 7.7 h

Monthly yield trend (avg material yield %)
  2026-01: 94.0%  (n=2)
  2026-02: 93.9%  (n=2)
  ...

Operator productivity
  M. Nkugwa     6 batches  yield 97.3%    17.1 kg/h
  A. Wamala     5 batches  yield 94.4%    14.7 kg/h
```

## Repository layout

```
batch-manufacturing-dashboard/
├── index.html               # interactive dashboard (open this)
├── batch_analysis.py        # analytics library + CLI
├── test_batch_analysis.py   # unit tests
└── README.md
```

## License

MIT.