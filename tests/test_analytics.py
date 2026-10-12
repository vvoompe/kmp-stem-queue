import unittest

import numpy as np

from src.analytics import run_analytics
from src.sim_core import simulate_day
from src.stage3_analytic import calculate_analytic, state_probabilities


class AnalyticsTests(unittest.TestCase):
    class FixedRandom:
        def poisson(self, _mean):
            return 4

        def geometric(self, _probability):
            return 1

        def random(self):
            return 0.9

    def test_analytics_is_reproducible(self):
        first = run_analytics(queue_limit=3, lam=2, workers=[1, 2], runs=5)
        second = run_analytics(queue_limit=3, lam=2, workers=[1, 2], runs=5)
        self.assertTrue(first.equals(second))
        self.assertEqual(first["runs"].tolist(), [5, 5])

    def test_simulation_includes_queue_and_idle_metrics(self):
        result = simulate_day(
            C=2, queue_limit=3, lam=2, rng=np.random.default_rng(7)
        )
        self.assertEqual(len(result["queue_history"]), 40)
        self.assertEqual(len(result["time_minutes"]), 40)
        self.assertGreaterEqual(result["idle_worker_fraction"], 0)
        self.assertLessEqual(result["idle_worker_fraction"], 1)
        self.assertGreaterEqual(result["mean_queue"], 0)

    def test_workers_process_customers_in_parallel(self):
        result = simulate_day(
            C=2, queue_limit=2, lam=3, rng=self.FixedRandom()
        )
        self.assertEqual(result["served"], 160)
        self.assertEqual(result["lost"], 0)
        self.assertAlmostEqual(result["idle_worker_fraction"], 2 / 3)

    def test_state_probabilities_are_normalized_and_finite(self):
        probabilities = state_probabilities(C=2, queue_limit=3, lam=3)
        self.assertEqual(len(probabilities), 6)
        self.assertAlmostEqual(sum(probabilities), 1)
        self.assertTrue(all(value >= 0 for value in probabilities))

    def test_zero_arrivals_leave_the_system_idle(self):
        result = calculate_analytic(C=2, queue_limit=3, lam=0)
        self.assertEqual(result.probabilities, (1, 0, 0, 0, 0, 0))
        self.assertEqual(result.blocking_probability, 0)
        self.assertEqual(result.served_per_day, 0)
        self.assertEqual(result.idle_worker_fraction, 1)

    def test_one_server_without_queue_matches_mm11(self):
        result = calculate_analytic(C=1, queue_limit=0, lam=3, mean_service=4)
        offered_load = (3 / 15) * 4
        self.assertAlmostEqual(
            result.blocking_probability, offered_load / (1 + offered_load)
        )
        self.assertAlmostEqual(
            result.throughput_per_minute, (3 / 15) / (1 + offered_load)
        )
        self.assertAlmostEqual(result.mean_queue, 0)
        self.assertAlmostEqual(result.mean_wait_time, 0)

    def test_invalid_model_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            state_probabilities(C=0, queue_limit=1, lam=2)
        with self.assertRaises(ValueError):
            state_probabilities(C=1, queue_limit=-1, lam=2)


if __name__ == "__main__":
    unittest.main()
