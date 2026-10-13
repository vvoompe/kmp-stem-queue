# input_stream.py - ГЕНЕРАТОРИ випадкових величин
import numpy as np

# --- параметри часу обслуговування (хвилини) ---
TAU_LOOK = 0.5      # огляд одного товару
TAU_PAY = 2         # оплата замовлення
TAU_DENY = 3        # оформлення відмови від товару

# --- параметри розподілів (з умови теми) ---
P_ITEMS = 0.3       # геометричний: кількість товарів
P_DENY = 0.1        # ймовірність відмови від товару


# --- періоди дня: λ залежить від часу доби (пряма вимога умови теми 10) ---
# Межі - у кроках модельного часу (крок 15 хв, 40 кроків = 10:00-20:00).
# Формат: (назва, крок з, крок до, λ - середня кількість клієнтів за 15 хв)
PERIODS = [
    ("10:00-13:00", 0, 12, 1.5),     # ранок - спокійно
    ("13:00-17:00", 12, 28, 3.0),    # день - середнє навантаження
    ("17:00-19:30", 28, 38, 5.0),    # вечірній пік - потрібні всі працівники
    ("19:30-20:00", 38, 40, 2.0),    # закриття - спад
]


def lam_for_step(step):
    """λ для конкретного кроку модельного часу (Пуассон за періодами дня)."""
    for _name, start, end, value in PERIODS:
        if start <= step < end:
            return value
    return PERIODS[-1][3]


def mean_arrival_rate():
    """Середнє λ за день - потрібне аналітичній моделі M/M/C/(C+m)."""
    steps = PERIODS[-1][2]
    return sum((end - start) * value for _n, start, end, value in PERIODS) / steps


def poisson_arrivals(lam, rng=None):
    """Скільки клієнтів прийшло за один крок модельного часу (Пуассон)."""
    if rng is None:
        return int(np.random.poisson(lam))
    return int(rng.poisson(lam))


def service_time(rng=None):
    """Скільки хвилин займе обслуговування одного клієнта."""
    if rng is None:
        random = np.random
    else:
        random = rng
    n = random.geometric(P_ITEMS)             # кількість товарів у замовленні
    t = n * TAU_LOOK + TAU_PAY                # огляд усіх товарів + оплата
    if random.random() < P_DENY:              # з ймовірністю 0.1 - відмова
        t = t + TAU_DENY                     # дорощуємо час на оформлення
    return float(t)


def mean_service_time():
    """Теоретичний середній час обслуговування, хвилини."""
    return (TAU_LOOK / P_ITEMS) + TAU_PAY + (P_DENY * TAU_DENY)


if __name__ == "__main__":
    N = 10000
    print("poisson_arrivals(3):", np.mean([poisson_arrivals(3) for _ in range(N)]), "(теорія 3)")
    print("товарів:", np.random.geometric(P_ITEMS, size=N).mean(), "(теорія 3.33)")
    print("частка відмов:", (np.random.random(N) < P_DENY).mean(), "(теорія 0.1)")
    print("service_time:", np.mean([service_time() for _ in range(N)]), "хв (теорія 3.97)")