import unittest

import batch_analysis as ba


def mkbatch(batch, month, actual, theoretical=100.0, hours=7.0,
            status="approved", operator="Ops", product="X"):
    return {"batch": batch, "product": product, "month": month,
            "theoretical_kg": theoretical, "actual_kg": actual, "hours": hours,
            "status": status, "operator": operator}


class YieldAndRatesTests(unittest.TestCase):
    def test_yield_pct(self):
        self.assertAlmostEqual(ba.yield_pct(147.0, 150.0), 0.98)
        self.assertAlmostEqual(ba.yield_pct(0.0, 150.0), 0.0)

    def test_yield_pct_guards(self):
        with self.assertRaises(ValueError):
            ba.yield_pct(100, 0)
        with self.assertRaises(ValueError):
            ba.yield_pct(-5, 100)

    def test_rejection_rate(self):
        recs = [
            mkbatch("A", "2026-01", 98, status="approved"),
            mkbatch("B", "2026-01", 99, status="rejected"),
            mkbatch("C", "2026-02", 97, status="rejected"),
        ]
        self.assertAlmostEqual(ba.rejection_rate(recs), 2 / 3)

    def test_rejection_rate_empty(self):
        self.assertEqual(ba.rejection_rate([]), 0.0)


class TrendTests(unittest.TestCase):
    def test_monthly_trend_mean(self):
        recs = [
            mkbatch("A", "2026-01", 90, theoretical=100),
            mkbatch("B", "2026-01", 100),
            mkbatch("C", "2026-02", 83, status="rejected"),
        ]
        rows = ba.monthly_trend(recs)
        self.assertEqual([r["month"] for r in rows], ["2026-01", "2026-02"])
        self.assertAlmostEqual(rows[0]["value"], 0.95)
        self.assertAlmostEqual(rows[1]["value"], 0.83)
        self.assertEqual(rows[0]["n"], 2)

    def test_mean_hours(self):
        recs = [mkbatch("A", "2026-01", 98, hours=8.0),
                mkbatch("B", "2026-01", 96, hours=10.0)]
        self.assertAlmostEqual(ba.mean_hours(recs), 9.0)


class StatusTests(unittest.TestCase):
    def test_rejected_filters_and_sorts(self):
        recs = [
            mkbatch("A", "2026-09", 91, status="rejected"),
            mkbatch("B", "2026-02", 92, status="rejected"),
            mkbatch("C", "2026-05", 95, status="approved"),
        ]
        rows = ba.rejected(recs)
        self.assertEqual([r["batch"] for r in rows], ["A", "B"])

    def test_unreleased(self):
        recs = [
            mkbatch("A", "2026-01", 98, status="on-hold"),
            mkbatch("B", "2026-01", 98, status="in-progress"),
            mkbatch("C", "2026-01", 98, status="approved"),
        ]
        self.assertEqual(len(ba.unreleased(recs)), 2)
        self.assertEqual(ba.unreleased(recs)[1]["status"], "in-progress")


class ProductivityTests(unittest.TestCase):
    def test_operator_productivity(self):
        recs = [
            mkbatch("A", "2026-01", 95, hours=5.0, status="approved", operator="Ops1"),
            mkbatch("B", "2026-01", 90, hours=5.0, status="rejected", operator="Ops2"),
            mkbatch("C", "2026-02", 98, hours=4.0, status="approved", operator="Ops1"),
        ]
        rows = ba.operator_productivity(recs)
        self.assertEqual(rows[0]["operator"], "Ops1")
        self.assertEqual(rows[0]["batches"], 2)
        self.assertEqual(rows[0]["approved"], 2)
        self.assertAlmostEqual(rows[0]["avg_yield_pct"], (0.95 + 0.98) / 2)
        self.assertAlmostEqual(rows[0]["kg_per_hour"], round((95 + 98) / 9, 1))
        self.assertEqual(rows[1]["rejected"], 1)


class DowntimeTests(unittest.TestCase):
    def test_pareto(self):
        rows = ba.downtime_pareto([("A", 20), ("B", 50), ("A", 10)])
        self.assertEqual([r["reason"] for r in rows], ["B", "A"])
        self.assertEqual(rows[1]["minutes"], 30.0)
        self.assertAlmostEqual(rows[1]["pct"], 0.375)


if __name__ == "__main__":
    unittest.main()