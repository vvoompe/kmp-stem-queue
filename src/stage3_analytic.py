"""Стаціонарна аналітична модель СМО M/M/c/(c+m) пункту видачі."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

if __package__:
    from .analytics import run_analytics
    from .input_stream import lam_for_step, mean_arrival_rate, mean_service_time
    from .sim_core import DAY_MIN, STEP_MIN
else:
    from analytics import run_analytics
    from input_stream import lam_for_step, mean_arrival_rate, mean_service_time
    from sim_core import DAY_MIN, STEP_MIN


@dataclass(frozen=True)
class AnalyticMetrics:
    probabilities: tuple
    blocking_probability: float
    throughput_per_minute: float
    served_per_day: float
    lost_per_day: float
    mean_queue: float
    mean_wait_time: float
    idle_worker_fraction: float


def state_probabilities(C, queue_limit, lam, mean_service=None):
    """Розраховує стаціонарні ймовірності станів q0..q(C+queue_limit)."""
    if C < 1:
        raise ValueError("C must be at least 1")
    if queue_limit < 0:
        raise ValueError("queue_limit cannot be negative")
    if lam < 0:
        raise ValueError("lam cannot be negative")
    mean_service = mean_service_time() if mean_service is None else mean_service
    if mean_service <= 0:
        raise ValueError("mean_service must be positive")

    arrival_rate = lam / STEP_MIN
    service_rate = 1 / mean_service
    capacity = C + queue_limit

    weights = [1.0]
    for state in range(1, capacity + 1):
        active_servers = min(state, C)
        weights.append(
            weights[-1] * arrival_rate / (active_servers * service_rate)
        )
    total_weight = sum(weights)
    return tuple(weight / total_weight for weight in weights)


def calculate_analytic(C, queue_limit, lam, mean_service=None):
    """Розраховує блокування, пропускну здатність, чергу, очікування й простій."""
    probabilities = state_probabilities(C, queue_limit, lam, mean_service)
    blocking_probability = probabilities[-1]
    arrival_rate = lam / STEP_MIN
    throughput = arrival_rate * (1 - blocking_probability)
    mean_queue = sum(
        max(state - C, 0) * probability
        for state, probability in enumerate(probabilities)
    )
    mean_wait = mean_queue / throughput if throughput > 0 else 0.0
    idle_channels = sum(
        (C - state) * probability
        for state, probability in enumerate(probabilities[:C])
    )
    return AnalyticMetrics(
        probabilities=probabilities,
        blocking_probability=blocking_probability,
        throughput_per_minute=throughput,
        served_per_day=throughput * DAY_MIN,
        lost_per_day=arrival_rate * blocking_probability * DAY_MIN,
        mean_queue=mean_queue,
        mean_wait_time=mean_wait,
        idle_worker_fraction=idle_channels / C,
    )


def compare_with_simulation(
    queue_limit, lam, workers=range(1, 5), runs=100, seed=42
):
    """Порівнює середнє імітації з теоретичними значеннями для тих самих умов.

    У імітації λ може бути розкладом за періодами дня, а аналітична модель
    M/M/C/(C+m) однорідна за часом - тому для неї береться середнє λ за день.
    """
    simulation = run_analytics(
        queue_limit, lam, workers=workers, runs=runs, seed=seed
    )
    lam_analytic = mean_arrival_rate() if callable(lam) else lam
    analytic_rows = []
    for count in simulation["workers"]:
        result = calculate_analytic(count, queue_limit, lam_analytic)
        analytic_rows.append({
            "workers": count,
            "analytic_served_per_day": result.served_per_day,
            "analytic_lost_per_day": result.lost_per_day,
            "analytic_idle_worker_fraction": result.idle_worker_fraction,
            "analytic_mean_queue": result.mean_queue,
            "analytic_mean_wait_time": result.mean_wait_time,
        })
    return simulation.merge(pd.DataFrame(analytic_rows), on="workers")


if __name__ == "__main__":
    queue_limit = 5
    lam = lam_for_step      # λ за періодами дня (вимога умови); середнє = 3.0
    print("Параметри: lambda =", mean_arrival_rate(), "клієнтів за", STEP_MIN,
          "хв (середнє за день; у імітації - розклад за періодами);")
    print("m =", queue_limit, "місць у черзі;")
    print("E[S] =", round(mean_service_time(), 4), "хв; день =", DAY_MIN, "хв.")
    print(compare_with_simulation(queue_limit, lam).to_string(index=False))
