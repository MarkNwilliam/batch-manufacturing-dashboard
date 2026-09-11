#!/usr/bin/env python3
"""Batch manufacturing analytics for a pharmaceutical production unit.

Works on batch records — the same records a Production Officer reviews from
the BMR. Each record is a plain dict:

    {
      "batch": "QCIL-2416",
      "product": "Amoxicillin 500 mg",
      "month": "2026-01",          # or any ISO month key
      "theoretical_kg": 150.0,     # charge size (target output)
      "actual_kg":     147.0,      # packed / recovered output
      "hours": 8.5,                # total process time
      "status": "approved",        # approved | rejected | on-hold
      "operator": "M. Nkugwa",
      "reject_reason": None,       # set when status == rejected
    }

All helpers are pure and dependency-free.
"""
from collections import defaultdict


def yield_pct(actual_kg, theoretical_kg):
    """Material yield as a fraction of the theoretical / charge size."""
    if theoretical_kg <= 0:
        raise ValueError("theoretical_kg must be > 0")
    if actual_kg < 0:
        raise ValueError("actual_kg cannot be negative")
    return actual_kg / theoretical_kg


def rejection_rate(records):
    """Fraction of closed batches that were rejected."""
    records = list(records)
    if not records:
        return 0.0
    rejected = sum(1 for r in records if r["status"] == "rejected")
    return rejected / len(records)


def unreleased(records):
    """Batches not yet approved (on-hold or in progress)."""
    return [r for r in records if r["status"] in ("on-hold", "in-progress")]


def rejected(records):
    """Rejected batch records, newest month first."""
    rows = sorted(
        (r for r in records if r["status"] == "rejected"),
        key=lambda r: (r["month"], r.get("batch", "")),
        reverse=True,
    )
    return rows


def monthly_trend(records, metric="yield_pct"):
    """Mean of a per-batch metric, grouped by month (ISO month key).

    Returns a list of {'month', 'value', 'n'} ordered by month.
    """
    groups = defaultdict(list)
    for r in records:
        if metric not in r and metric != "yield_pct":
            raise KeyError(f"unknown metric {metric!r}")
        val = r.get(metric, yield_pct(r["actual_kg"], r["theoretical_kg"]))
        groups[r["month"]].append(val)
    return [{"month": m, "value": sum(v) / len(v), "n": len(v)}
            for m, v in sorted(groups.items())]


def mean_hours(records):
    """Average process time per batch (hours)."""
    records = list(records)
    if not records:
        return 0.0
    return sum(r["hours"] for r in records) / len(records)


def operator_productivity(records):
    """Per-operator productivity: batches, approvals, mean yield, hours.

    Returns rows sorted by batches handled (desc).
    """
    by_op = defaultdict(list)
    for r in records:
        by_op[r["operator"]].append(r)
    rows = []
    for op, rs in by_op.items():
        approved = sum(1 for r in rs if r["status"] == "approved")
        total_kg = sum(r["actual_kg"] for r in rs)
        rows.append({
            "operator": op,
            "batches": len(rs),
            "approved": approved,
            "rejected": len(rs) - approved,
            "avg_yield_pct": sum(yield_pct(r["actual_kg"], r["theoretical_kg"])
                                 for r in rs) / len(rs),
            "total_hours": round(sum(r["hours"] for r in rs), 1),
            "kg_per_hour": round(total_kg / sum(r["hours"] for r in rs), 1)
            if sum(r["hours"] for r in rs) else 0.0,
        })
    return sorted(rows, key=lambda row: -row["batches"])


def downtime_pareto(records):
    """Aggregate downtime minutes by reason, largest first.

    records: iterable of (reason, minutes).
    """
    total = defaultdict(float)
    for reason, minutes in records:
        if minutes < 0:
            raise ValueError("downtime minutes cannot be negative")
        total[reason] += minutes
    grand = sum(total.values())
    rows = []
    for reason, minutes in sorted(total.items(), key=lambda kv: -kv[1]):
        rows.append({
            "reason": reason,
            "minutes": round(minutes, 1),
            "pct": (minutes / grand) if grand else 0.0,
        })
    return rows


# --- demo dataset (12 months, 3 products, 5 operators) ---
DEMO_BATCHES = [
    {"batch": "QCIL-2401", "product": "Amoxicillin 500", "month": "2026-01",
     "theoretical_kg": 150.0, "actual_kg": 143.0, "hours": 8.2,
     "status": "approved", "operator": "M. Nkugwa"},
    {"batch": "QCIL-2402", "product": "Amoxicillin 500", "month": "2026-01",
     "theoretical_kg": 150.0, "actual_kg": 139.0, "hours": 9.0,
     "status": "on-hold", "operator": "A. Wamala"},
    {"batch": "QCIL-2403", "product": "Ciprofloxacin 250", "month": "2026-02",
     "theoretical_kg": 120.0, "actual_kg": 116.4, "hours": 7.1,
     "status": "approved", "operator": "M. Nkugwa"},
    {"batch": "QCIL-2404", "product": "Ciprofloxacin 250", "month": "2026-02",
     "theoretical_kg": 120.0, "actual_kg": 109.0, "hours": 8.0,
     "status": "rejected", "operator": "J. Kato", "reject_reason": "Disintegration failure — granule wet mass"},
    {"batch": "QCIL-2405", "product": "Metronidazole 400", "month": "2026-03",
     "theoretical_kg": 100.0, "actual_kg": 97.5, "hours": 6.4,
     "status": "approved", "operator": "S. Namuli"},
    {"batch": "QCIL-2406", "product": "Metronidazole 400", "month": "2026-03",
     "theoretical_kg": 100.0, "actual_kg": 93.0, "hours": 7.5,
     "status": "on-hold", "operator": "P. Ochieng"},
    {"batch": "QCIL-2407", "product": "Amoxicillin 500", "month": "2026-04",
     "theoretical_kg": 150.0, "actual_kg": 147.2, "hours": 8.0,
     "status": "approved", "operator": "A. Wamala"},
    {"batch": "QCIL-2408", "product": "Amoxicillin 500", "month": "2026-04",
     "theoretical_kg": 150.0, "actual_kg": 141.0, "hours": 9.2,
     "status": "approved", "operator": "J. Kato"},
    {"batch": "QCIL-2409", "product": "Ciprofloxacin 250", "month": "2026-05",
     "theoretical_kg": 120.0, "actual_kg": 117.6, "hours": 6.9,
     "status": "approved", "operator": "M. Nkugwa"},
    {"batch": "QCIL-2410", "product": "Ciprofloxacin 250", "month": "2026-05",
     "theoretical_kg": 120.0, "actual_kg": 105.0, "hours": 8.6,
     "status": "rejected", "operator": "S. Namuli", "reject_reason": "Assay out of spec — overmilled blend"},
    {"batch": "QCIL-2411", "product": "Metronidazole 400", "month": "2026-06",
     "theoretical_kg": 100.0, "actual_kg": 98.1, "hours": 6.1,
     "status": "approved", "operator": "P. Ochieng"},
    {"batch": "QCIL-2412", "product": "Metronidazole 400", "month": "2026-06",
     "theoretical_kg": 100.0, "actual_kg": 94.0, "hours": 7.2,
     "status": "approved", "operator": "A. Wamala"},
    {"batch": "QCIL-2413", "product": "Amoxicillin 500", "month": "2026-07",
     "theoretical_kg": 150.0, "actual_kg": 145.5, "hours": 8.1,
     "status": "approved", "operator": "M. Nkugwa"},
    {"batch": "QCIL-2414", "product": "Amoxicillin 500", "month": "2026-07",
     "theoretical_kg": 150.0, "actual_kg": 138.0, "hours": 9.4,
     "status": "on-hold", "operator": "J. Kato"},
    {"batch": "QCIL-2415", "product": "Ciprofloxacin 250", "month": "2026-08",
     "theoretical_kg": 120.0, "actual_kg": 118.1, "hours": 6.8,
     "status": "approved", "operator": "S. Namuli"},
    {"batch": "QCIL-2416", "product": "Ciprofloxacin 250", "month": "2026-08",
     "theoretical_kg": 120.0, "actual_kg": 111.0, "hours": 8.2,
     "status": "approved", "operator": "P. Ochieng"},
    {"batch": "QCIL-2417", "product": "Metronidazole 400", "month": "2026-09",
     "theoretical_kg": 100.0, "actual_kg": 98.8, "hours": 6.2,
     "status": "approved", "operator": "M. Nkugwa"},
    {"batch": "QCIL-2418", "product": "Metronidazole 400", "month": "2026-09",
     "theoretical_kg": 100.0, "actual_kg": 91.0, "hours": 7.7,
     "status": "rejected", "operator": "A. Wamala", "reject_reason": "Residue moisture above limit"},
    {"batch": "QCIL-2419", "product": "Amoxicillin 500", "month": "2026-10",
     "theoretical_kg": 150.0, "actual_kg": 148.0, "hours": 8.0,
     "status": "approved", "operator": "S. Namuli"},
    {"batch": "QCIL-2420", "product": "Amoxicillin 500", "month": "2026-11",
     "theoretical_kg": 150.0, "actual_kg": 146.3, "hours": 8.3,
     "status": "approved", "operator": "M. Nkugwa"},
    {"batch": "QCIL-2421", "product": "Ciprofloxacin 250", "month": "2026-12",
     "theoretical_kg": 120.0, "actual_kg": 117.0, "hours": 7.0,
     "status": "approved", "operator": "P. Ochieng"},
    {"batch": "QCIL-2422", "product": "Metronidazole 400", "month": "2026-12",
     "theoretical_kg": 100.0, "actual_kg": 96.0, "hours": 6.6,
     "status": "approved", "operator": "A. Wamala"},
]

DEMO_DOWNTIME = [
    ("Granulation mixer OOS — awaiting calibration", 95),
    ("Changeover between compressed products", 70),
    ("HVAC fault cleared (cleanroom alarm)", 55),
    ("Raw material quarantine release delay", 40),
    ("Compression station set-up", 35),
]


if __name__ == "__main__":
    print(f"Batches analysed: {len(DEMO_BATCHES)}")
    print(f"Rejection rate:   {rejection_rate(DEMO_BATCHES):.1%}")
    print(f"Mean process time: {mean_hours(DEMO_BATCHES):.1f} h")
    print("\nMonthly yield trend (avg material yield %)")
    for row in monthly_trend(DEMO_BATCHES):
        print(f"  {row['month']}: {row['value']:.1%}  (n={row['n']})")
    print("\nOperator productivity")
    for row in operator_productivity(DEMO_BATCHES):
        print(f"  {row['operator']:<12} {row['batches']:>2} batches  "
              f"yield {row['avg_yield_pct']:.1%}  {row['kg_per_hour']:>6.1f} kg/h")