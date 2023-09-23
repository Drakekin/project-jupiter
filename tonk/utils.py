from typing import List

from tonk.tank import Tank


class TankException(Exception):
    def __init__(self, tank: Tank, turns: int, log):
        self.tank = tank
        self.turns = turns
        self.log = log


class TankDead(TankException):
    pass


class TankExploded(TankException):
    pass


class TankBailed(TankException):
    pass


def test_tank(tank: Tank, turns: int, log: List[str]):
    if tank.exploded:
        log.append(f"{tank.name} has exploded!")
        raise TankExploded(tank, turns, log)
    if tank.damage >= tank.hull:
        log.append(f"{tank.name} has been wrecked!")
        raise TankDead(tank, turns, log)
    if tank.panic >= 3:
        log.append(f"{tank.name} has bailed!")
        raise TankBailed(tank, turns, log)


def log_weapon_result(current, target, weapon, log, weapon_result):
    log.append(f"\t{current.name} fired {weapon.weapon.name} at {target.name}")
    if weapon_result.went_hull_down:
        log.append(f"\t\t{target.name} went hull down")
    if weapon_result.hit:
        if weapon_result.crit:
            log.append(
                f"\t\tPenetrating hit! Did {weapon_result.damage} damage and {weapon_result.critical_effect.__name__}")
        elif weapon_result.panicked:
            if weapon_result.damage > 0:
                log.append(f"\t\tHit! Did {weapon_result.damage} damage and {target.name} panicked!")
            else:
                log.append(f"\t\tGlancing hit! {target.name} panicked!")
        elif weapon_result.damage > 0:
            log.append(f"\t\tHit! Did {weapon_result.damage} damage")
    else:
        log.append("\t\tMissed")
