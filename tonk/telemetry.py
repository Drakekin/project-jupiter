from typing import Callable

from pydantic.main import BaseModel

from tonk.critical_damage import no_crit


class WeaponHitResult(BaseModel):
    hit: bool = False
    panicked: bool = False
    crit: bool = False
    damage: int = 0
    went_hull_down: bool = False
    critical_effect: Callable = no_crit


class ActivationResult(BaseModel):
    on_fire: bool = False
    panicked: bool = False
    exploded: bool = False
