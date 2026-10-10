# sim_core.py - ЯДРО імітаційної моделі (модуль Сашка)
# Моделює один день роботи пункту видачі інтернет-замовлень.

import numpy as np
from input_stream import poisson_arrivals, service_time

STEP_MIN = 15       # крок модельного часу, хвилин
N_STEPS = 40        # кроків у дні (10 годин роботи 10:00-20:00 / 15 хв)


def simulate_day(C, queue_limit, lam):
    """
    Один прогін: цілий день роботи пункту з C працівниками.
    C            - кількість працівників (каналів)
    queue_limit  - максимум місць у черзі
    lam          - середня кількість клієнтів за крок (Пуассон)
    Повертає словник з показниками дня.
    """
    queue = []              # черга клієнтів (у кожного - свій час обслуговування)
    servers = [0] * C       # працівники: у кожного свій залишок часу (0 = вільний)
    served = 0              # обслужено за день
    lost = 0                # втрачено за день
    idle_steps = 0          # кроки, коли НІХТО не працював (простій системи)

    for step in range(N_STEPS):
        # --- 1. прийшли клієнти ---
        arrived = poisson_arrivals(lam)
        for _ in range(arrived):
            if len(queue) < queue_limit:
                queue.append(service_time())     # у чергу - з його часом обслуговування
            else:
                lost = lost + 1                  # черга повна - клієнт пішов

        # --- 2. кожен працівник працює 15 хвилин ---
        step_worked = 0
        for i in range(C):
            free = STEP_MIN                      # вільний час працівника на кроці
            while free > 0:
                if servers[i] == 0:              # працівник вільний?
                    if len(queue) == 0:
                        break                    # нема кого - простій
                    servers[i] = queue.pop(0)    # беремо першого зі спільної черги
                if servers[i] <= free:           # встигає завершити клієнта
                    free = free - servers[i]
                    step_worked = step_worked + servers[i]
                    servers[i] = 0
                    served = served + 1
                else:                            # не встигає - добере наступним кроком
                    servers[i] = servers[i] - free
                    step_worked = step_worked + free
                    free = 0
        if step_worked == 0:
            idle_steps = idle_steps + 1

    return {"served": served, "lost": lost, "idle": idle_steps / N_STEPS}
