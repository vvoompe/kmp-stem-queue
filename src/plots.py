"""Побудова гістограм і діаграм для аналізу пункту видачі."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

if __package__:
    from .analytics import run_analytics
    from .input_stream import P_ITEMS, lam_for_step, service_time
    from .sim_core import STEP_MIN, simulate_day
else:
    from analytics import run_analytics
    from input_stream import P_ITEMS, lam_for_step, service_time
    from sim_core import STEP_MIN, simulate_day


def _save_figure(fig, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_input_distributions(output_dir="plots", sample_size=10000, seed=42):
    """Зберігає гістограми кількості товарів і часу обслуговування."""
    if sample_size < 1:
        raise ValueError("sample_size must be at least 1")
    rng = np.random.default_rng(seed)
    output_dir = Path(output_dir)

    items = rng.geometric(P_ITEMS, size=sample_size)
    fig, ax = plt.subplots()
    ax.hist(items, bins=np.arange(0.5, max(items) + 1.5, 1), label="Кількість товарів")
    ax.set_title("Розподіл кількості товарів у замовленні")
    ax.set_xlabel("Кількість товарів, шт.")
    ax.set_ylabel("Кількість замовлень, од.")
    ax.legend()
    items_path = _save_figure(fig, output_dir / "item_count_histogram.png")

    service_times = [service_time(rng) for _ in range(sample_size)]
    fig, ax = plt.subplots()
    ax.hist(service_times, bins=30, label="Час обслуговування")
    ax.set_title("Розподіл часу обслуговування клієнтів")
    ax.set_xlabel("Час обслуговування, хв")
    ax.set_ylabel("Кількість клієнтів, осіб")
    ax.legend()
    service_path = _save_figure(fig, output_dir / "service_time_histogram.png")
    return items_path, service_path


def plot_lost_customers(analytics, output_path="plots/lost_customers.png"):
    """Будує стовпчикову діаграму середньої кількості втрачених клієнтів."""
    required = {"workers", "lost_mean"}
    if not required.issubset(analytics.columns):
        raise ValueError("analytics must contain workers and lost_mean columns")

    fig, ax = plt.subplots()
    ax.bar(analytics["workers"], analytics["lost_mean"], label="Втрачені клієнти")
    ax.set_title("Залежність втрат клієнтів від кількості працівників")
    ax.set_xlabel("Кількість працівників, осіб")
    ax.set_ylabel("Середні втрати за день, осіб")
    ax.set_xticks(analytics["workers"])
    ax.legend()
    return _save_figure(fig, output_path)


def plot_queue_dynamics(
    C, queue_limit, lam, output_path="plots/queue_dynamics.png", seed=42
):
    """Будує графік кількості клієнтів у черзі протягом одного дня."""
    result = simulate_day(C, queue_limit, lam, rng=np.random.default_rng(seed))
    fig, ax = plt.subplots()
    ax.plot(
        result["time_minutes"],
        result["queue_history"],
        label="Клієнти, що очікують",
    )
    ax.set_title("Динаміка черги протягом робочого дня")
    ax.set_xlabel("Час від початку робочого дня, хв")
    ax.set_ylabel("Кількість клієнтів у черзі, осіб")
    ax.set_xlim(0, STEP_MIN * len(result["time_minutes"]))
    ax.legend()
    return _save_figure(fig, output_path)


if __name__ == "__main__":
    # λ за періодами дня - та сама конфігурація, що в звіті (етапи 1-2)
    summary = run_analytics(queue_limit=5, lam=lam_for_step)
    plot_input_distributions()
    plot_lost_customers(summary)
    plot_queue_dynamics(C=1, queue_limit=5, lam=lam_for_step)
