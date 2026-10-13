# stage2_multi.py - ЕТАП 2: БАГАТОКАНАЛЬНА система (кілька працівників)
# Показує, як змінюються показники залежно від кількості працівників.

import os
import sys

# додаємо теку src/ до шляху пошуку модулів, щоб знайти sim_core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import numpy as np
from sim_core import simulate_day

# --- параметри (підбираються командою) ---
LAM = 3             # середня кількість клієнтів за крок (15 хв)
QUEUE_LIMIT = 5     # максимум місць у черзі
C_VALUES = [1, 2, 3, 4]   # скільки працівників пробуємо

N_RUNS = 100        # прогонів на кожен варіант

print("=" * 64)
print("ЕТАП 2: багатоканальна система")
print("=" * 64)
print(f"{'Працівників':>12} | {'Обслужено':>10} | {'Втрачено':>9} | {'Простій':>8}")
print("-" * 64)

for C in C_VALUES:
    runs = [simulate_day(C, QUEUE_LIMIT, LAM) for _ in range(N_RUNS)]
    served = np.mean([r["served"] for r in runs])
    lost = np.mean([r["lost"] for r in runs])
    idle = np.mean([r["idle"] for r in runs])
    print(f"{C:>12} | {served:>10.1f} | {lost:>9.1f} | {idle:>8.3f}")

print("-" * 64)
print("Головне завдання: мінімум втрачених клієнтів за простою <= 0.15")
