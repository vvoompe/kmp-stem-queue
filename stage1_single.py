# stage1_single.py - ЕТАП 1: імітація ОДНОГО каналу обслуговування
# Демонструє роботу пункту видачі, коли працює один працівник (C=1).

import os
import sys

# додаємо теку src/ до шляху пошуку модулів, щоб знайти sim_core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import numpy as np
from input_stream import PERIODS, lam_for_step
from sim_core import simulate_day

# --- параметри (підбираються командою) ---
# λ залежить від часу доби (вимога умови теми 10) - див. PERIODS у input_stream.py
LAM = lam_for_step
QUEUE_LIMIT = 5     # максимум місць у черзі
C = 1               # ОДИН канал - це і є суть етапу 1

print("=" * 50)
print("ЕТАП 1: імітація одного каналу")
print("=" * 50)
print("\nПеріоди дня (λ - середня кількість клієнтів за крок 15 хв):")
for _name, _start, _end, _value in PERIODS:
    print(f"  {_name}: кроки {_start}-{_end - 1}, лямбда = {_value}")

# --- 1) один прогін: показуємо, як минув один день ---
day = simulate_day(C, QUEUE_LIMIT, LAM)
print("\nОдин прогін:")
print(f"  обслужено: {day['served']}")
print(f"  втрачено:  {day['lost']}")
print(f"  простій:   {day['idle']:.3f}")

# --- 2) 100 прогонів: усереднені показники ---
N_RUNS = 100
runs = [simulate_day(C, QUEUE_LIMIT, LAM) for _ in range(N_RUNS)]
print(f"\nСереднє за {N_RUNS} прогонів:")
print(f"  обслужено: {np.mean([r['served'] for r in runs]):.1f}")
print(f"  втрачено:  {np.mean([r['lost'] for r in runs]):.1f}")
print(f"  простій:   {np.mean([r['idle'] for r in runs]):.3f}")
