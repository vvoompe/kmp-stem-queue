# input_stream.py - ГЕНЕРАТОРИ випадкових величин
import numpy as np

# --- параметри часу обслуговування (хвилини) ---
TAU_LOOK = 0.5      # огляд одного товару
TAU_PAY = 2         # оплата замовлення
TAU_DENY = 3        # оформлення відмови від товару

# --- параметри розподілів (з умови теми) ---
P_ITEMS = 0.3       # геометричний: кількість товарів
P_DENY = 0.1        # ймовірність відмови від товару


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