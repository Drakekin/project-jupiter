from multiprocessing import Pool
from random import Random, randint
from typing import Callable, Any, Tuple, Dict, Iterable, List
from math import log10, floor

from blackjack.game import play_blackjack, StrategicPlayer, CautiousPlayer


def calculate_confidence_(val_a: float, val_b: float) -> int:
    difference = abs(val_a - val_b)
    return floor(-log10(difference))


def simulate(func: Callable[..., Tuple[float, ...]], args: Any, kwargs: Any,
             discriminator: Callable[[Tuple[float, ...]], float], confidence: int = 4, required_stability: int = 10,
             step: int = 1000) -> Tuple[float, List[Tuple[float, ...]]]:
    statistics = []
    confidence_test: float = 0
    n = 0
    stability = 0

    while stability < required_stability:
        old_confidence_test = confidence_test / n if n > 0 else 0
        for _ in range(step):
            n += 1
            result = func(*args, **kwargs)
            statistics.append(result)
            confidence_test += discriminator(result)
        new_confidence_test = confidence_test / n

        calculated_confidence = calculate_confidence(old_confidence_test, new_confidence_test)

        iteration = n // step

        if calculated_confidence >= confidence:
            stability += 1
            print(f"Stability {stability} at iteration {iteration}")
        else:
            deviation = round(abs(old_confidence_test - new_confidence_test), confidence)
            if stability:
                print(f"Stability lost at iteration {iteration} - {deviation} deviation")
            else:
                print(f"Current confidence at {calculated_confidence} at iteration {iteration} - {deviation} deviation")
            stability = 0

    return new_confidence_test, statistics




def monte_carlo(
        func: Callable[..., int | float],
        iterations: int,
        *args: Any, **kwargs: Any
) -> float:
    accumulator = 0
    for _ in range(iterations):
        accumulator += func(*args, **kwargs)
    return accumulator / iterations


def monte_carlo_improved(
        func: Callable[..., Tuple[int | float, ...]],
        discriminator: Callable[[Tuple[int | float]], int | float],
        iterations: int,
        *args: Any, **kwargs: Any
) -> Tuple[float, List[Tuple[float | int, ...]]]:
    accumulator = 0
    results = []

    for _ in range(iterations):
        result = func(*args, **kwargs)
        accumulator += discriminator(result)
        results.append(result)

    return accumulator / iterations, results


def calculate_confidence(val_a: float, val_b: float) -> int:
    difference = abs(val_a - val_b)
    return floor(-log10(difference))


def monte_carlo_self_stabalising(
        func: Callable[..., Tuple[int | float, ...]],
        discriminator: Callable[[Tuple[int | float]], int | float],
        required_confidence: int = 3,
        required_stability: int = 10,
        iterations_per_round: int = 1000,
        *args: Any, **kwargs: Any
) -> Tuple[float, List[Tuple[float | int, ...]]]:
    accumulator = 0
    results = []
    new_accumulator = 0
    stability = 0
    iterations = 0
    new_iterations = 0

    while stability < required_stability:
        for _ in range(iterations_per_round):
            result = func(*args, **kwargs)
            new_accumulator += discriminator(result)
            results.append(result)
            new_iterations += 1

        if iterations:
            confidence = calculate_confidence(accumulator / iterations, new_accumulator / new_iterations)
        else:
            confidence = 0

        if confidence >= required_confidence:
            stability += 1
        else:
            stability = 0

        accumulator = new_accumulator
        iterations = new_iterations

    return accumulator / iterations, results


from multiprocessing import Pool


def monte_carlo_self_stabalising_parallel(
        func: Callable[..., Tuple[int | float, ...]],
        discriminator: Callable[[Tuple[int | float]], int | float],
        required_confidence: int = 3,
        required_stability: int = 10,
        iterations_per_round: int = 1000,
        *args: Any
) -> Tuple[float, List[Tuple[float | int, ...]]]:
    accumulator = 0
    results = []
    new_accumulator = 0
    stability = 0
    iterations = 0
    new_iterations = 0
    pool = Pool()

    while stability < required_stability:
        round_results = pool.starmap(func, (args for _ in range(iterations_per_round)))
        new_accumulator += sum(pool.map(discriminator, round_results))
        results.extend(round_results)
        new_iterations += iterations_per_round

        if iterations:
            confidence = calculate_confidence(accumulator / iterations, new_accumulator / new_iterations)
        else:
            confidence = 0

        if confidence >= required_confidence:
            stability += 1
            print(f"Iteration {iterations}: stability {stability} at confidence {confidence}")
        else:
            stability = 0
            print(f"Iteration {iterations}: no stability at confidence {confidence}")

        accumulator = new_accumulator
        iterations = new_iterations

    return accumulator / iterations, results


def roll_die():
    return (randint(1, 6),)


def die_discriminator(result):
    roll, = result
    return roll


if __name__ == "__main__":
    average_die_roll, _ = monte_carlo_self_stabalising_parallel(
        roll_die,
        die_discriminator,
        iterations_per_round=10_000,
        required_stability=5
    )
    print(f"Average die roll is {average_die_roll}")


from random import Random


if __name__ == '__main__':
    # def discriminator(result):
    #     turns, panzer_victory, sherman_victory, panzer_destroy, sherman_destroy, panzer_bail, sherman_bail, panzer_explode, sherman_explode = result
    #     return panzer_victory
    #
    # simulate(duel_instrumented, [], {}, discriminator)

    def blackjack_instrumented() -> Tuple[float, ...]:
        winnings = play_blackjack(Random(), CautiousPlayer(Random()))
        return winnings, winnings > 0

    def blackjack_discriminator(result):
        winnings, won = result
        return winnings

    won, stats = simulate(blackjack_instrumented, [], {}, blackjack_discriminator)
    print(f"Average winnings {won}")


