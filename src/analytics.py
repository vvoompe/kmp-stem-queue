"""Повторні прогони імітаційної моделі та середні показники."""

import numpy as np
import pandas as pd

if __package__:
    from .sim_core import simulate_day
else:
    from sim_core import simulate_day


def run_analytics(queue_limit, lam, workers=range(1, 5), runs=100, seed=42):
    """Повертає середні показники за runs днів для кожної кількості працівників."""
    worker_counts = list(workers)
    if not worker_counts or any(count < 1 for count in worker_counts):
        raise ValueError("workers must contain positive employee counts")
    if runs < 1:
        raise ValueError("runs must be at least 1")

    rng = np.random.default_rng(seed)
    rows = []
    for count in worker_counts:
        days = [
            simulate_day(count, queue_limit, lam, rng=rng)
            for _ in range(runs)
        ]
        rows.append({
            "workers": count,
            "served_mean": float(np.mean([day["served"] for day in days])),
            "lost_mean": float(np.mean([day["lost"] for day in days])),
            "idle_system_mean": float(np.mean([day["idle"] for day in days])),
            "idle_worker_fraction_mean": float(np.mean([
                day["idle_worker_fraction"] for day in days
            ])),
            "mean_queue": float(np.mean([day["mean_queue"] for day in days])),
            "mean_wait_time": float(np.mean([
                day["mean_wait_time"] for day in days
            ])),
            "runs": runs,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(run_analytics(queue_limit=5, lam=3).to_string(index=False))
