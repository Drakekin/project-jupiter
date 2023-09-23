from enum import StrEnum
from random import randrange
from typing import Iterable, List, TypeVar


def d6(modifier: int = 0) -> int:
    return randrange(1, 7) + modifier


class ShootingResult(StrEnum):
    miss = "Miss"
    hit = "Hit"
    direct_hit = "Direct Hit"

    @classmethod
    def from_(cls, *rolls: int) -> List["ShootingResult"]:
        results = []
        for roll in rolls:
            if roll <= 3:
                results.append(cls.miss)
            elif roll <= 5:
                results.append(cls.hit)
            else:
                results.append(cls.direct_hit)
        return results


T = TypeVar("T")


def count(pool: Iterable[T], *values: T):
    accumulator: int = 0
    for val in pool:
        if val in values:
            accumulator += 1
    return accumulator
