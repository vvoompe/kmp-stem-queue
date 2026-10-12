# sim_core.py - ЯДРО імітаційної моделі (модуль Сашка)
# Моделює один день роботи пункту видачі інтернет-замовлень.

import numpy as np

if __package__:
    from .input_stream import poisson_arrivals, service_time
else:
    from input_stream import poisson_arrivals, service_time

STEP_MIN = 15       # крок модельного часу, хвилин
N_STEPS = 40        # кроків у дні (10 годин роботи 10:00-20:00 / 15 хв)
DAY_MIN = STEP_MIN * N_STEPS


def simulate_day(C, queue_limit, lam, rng=None):
    """
    Один прогін: цілий день роботи пункту з C працівниками.
    C            - кількість працівників (каналів)
    queue_limit  - максимум місць у черзі
    lam          - середня кількість клієнтів за крок (Пуассон)
    rng          - необов'язковий генератор numpy для відтворюваних прогонів
    Повертає словник з показниками дня.
    """
    if C < 1:
        raise ValueError("C must be at least 1")
    if queue_limit < 0:
        raise ValueError("queue_limit cannot be negative")
    if lam < 0:
        raise ValueError("lam cannot be negative")

    queue = []              # черга клієнтів (у кожного - свій час обслуговування)
    servers = [0] * C       # працівники: у кожного свій залишок часу (0 = вільний)
    served = 0              # обслужено за день
    lost = 0                # втрачено за день
    idle_steps = 0          # кроки, коли НІХТО не працював (простій системи)
    total_work_minutes = 0.0
    queue_history = []
    waiting_times = []

    for step in range(N_STEPS):
        # --- 1. прийшли клієнти ---
        arrived = poisson_arrivals(lam, rng)
        for _ in range(arrived):
            busy_servers = sum(remaining > 0 for remaining in servers)
            if len(queue) + busy_servers < C + queue_limit:
                queue.append((service_time(rng), step * STEP_MIN))
            else:
                lost = lost + 1                  # черга повна - клієнт пішов

        # --- 2. працівники обслуговують клієнтів паралельно ---
        step_worked = 0
        elapsed = 0.0
        while elapsed < STEP_MIN:
            for i in range(C):
                if servers[i] == 0 and queue:
                    service_duration, arrived_at = queue.pop(0)
                    waiting_times.append(step * STEP_MIN + elapsed - arrived_at)
                    servers[i] = service_duration

            busy_servers = [i for i, remaining in enumerate(servers) if remaining > 0]
            if not busy_servers:
                break

            elapsed_work = min(
                STEP_MIN - elapsed,
                min(servers[i] for i in busy_servers),
            )
            for i in busy_servers:
                servers[i] -= elapsed_work
                if servers[i] <= 1e-12:
                    servers[i] = 0
                    served += 1
            worked = elapsed_work * len(busy_servers)
            elapsed += elapsed_work
            step_worked += worked
            total_work_minutes += worked

        if step_worked == 0:
            idle_steps = idle_steps + 1
        queue_history.append(len(queue))

    return {
        "served": served,
        "lost": lost,
        "idle": idle_steps / N_STEPS,
        "idle_worker_fraction": 1 - total_work_minutes / (C * DAY_MIN),
        "mean_queue": (
            sum(waiting_times)
            + sum(DAY_MIN - arrived_at for _, arrived_at in queue)
        ) / DAY_MIN,
        "mean_wait_time": float(np.mean(waiting_times)) if waiting_times else 0.0,
        "queue_history": queue_history,
        "time_minutes": [(step + 1) * STEP_MIN for step in range(N_STEPS)],
    }
