from typing import TYPE_CHECKING
from random import choice

if TYPE_CHECKING:
    from tonk.tank import Tank


def no_crit(tank: "Tank"):
    pass


def turret_ring_jam(tank: "Tank"):
    tank.turret_jammed = True


def optics_damaged(tank: "Tank"):
    tank.optics = max(0, tank.optics - 2)


def engine_damaged(tank: "Tank"):
    tank.movement = max(0, tank.movement - 2)


def track_damaged(tank: "Tank"):
    tank.movement = max(0, tank.movement - (tank.original_movement // 2))


def weapon_destroyed(tank: "Tank"):
    candidates = [weapon for weapon in tank.weapons if not weapon.destroyed]
    if not candidates:
        return
    weapon = choice(candidates)
    weapon.destroyed = True


def engine_destroyed(tank: "Tank"):
    tank.movement = 0


def on_fire(tank: "Tank"):
    tank.on_fire = True


def ammunition_explosion(tank: "Tank"):
    tank.damage = tank.hull
    tank.on_fire = True
    tank.exploded = True


def crew_killed(tank: "Tank"):
    tank.discipline = max(0, tank.discipline - 1)
