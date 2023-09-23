import math
from enum import StrEnum
from typing import List, TYPE_CHECKING

from tonk.critical_damage import no_crit
from tonk.dice import ShootingResult, d6, count
from tonk.misc import Arc
from tonk import critical_damage
from tonk.tank_special_rules import TankSpecialRules
from tonk.telemetry import WeaponHitResult

if TYPE_CHECKING:
    from tonk.tank import Tank


class WeaponSpecialRules(StrEnum):
    no_pen = "No Pen"
    stable = "Stable"


class TankHitLocations(StrEnum):
    turret = "Turret"
    hull = "Hull"
    tracks = "Tracks"
    crew = "Crew Compartment"


HULL_CRITICAL_DAMAGE_ROLL = [
    critical_damage.optics_damaged,
    critical_damage.engine_damaged,
    critical_damage.weapon_destroyed,
    critical_damage.engine_destroyed,
    critical_damage.on_fire,
    critical_damage.ammunition_explosion,
]
TRACK_CRITICAL_DAMAGE_ROLL = [
    critical_damage.no_crit,
    critical_damage.engine_damaged,
    critical_damage.engine_damaged,
    critical_damage.track_damaged,
    critical_damage.track_damaged,
    critical_damage.engine_destroyed,
]
TURRET_CRITICAL_DAMAGE_ROLL = [
    critical_damage.crew_killed,
    critical_damage.turret_ring_jam,
    critical_damage.optics_damaged,
    critical_damage.weapon_destroyed,
    critical_damage.on_fire,
    critical_damage.ammunition_explosion,
]
CREW_COMPARTMENT_DAMAGE_ROLL = [
    critical_damage.no_crit,
    critical_damage.crew_killed,
    critical_damage.crew_killed,
    critical_damage.optics_damaged,
    critical_damage.on_fire,
    critical_damage.ammunition_explosion,
]


class Weapon:
    name: str
    rating: int
    special: List[WeaponSpecialRules]

    def __init__(self, name: str, rating: int, special: List[WeaponSpecialRules] = None):
        self.name = name
        self.rating = rating
        self.special = special if special else []

    def naive_expected_damage(self, against_armour: int, penalty: int = 0) -> float:
        dice = max(0, self.rating - penalty)
        if dice < against_armour:
            crit_damage = 0
            regular_damage_dice = dice
        else:
            remaining_dice = dice - against_armour
            any_outcome_likelyhood = 0.5 ** remaining_dice
            crit_damage = 0
            for hits in range(remaining_dice + 1):
                chance = ((1.0 / 6) ** against_armour) * any_outcome_likelyhood * math.comb(dice, hits + against_armour)
                crit_damage = (against_armour + hits) * chance
            regular_damage_dice = against_armour

        regular_damage = 0
        for n in range(regular_damage_dice):
            hits = n + 1
            misses = dice - hits
            chance = ((1 / 6) ** hits) * ((5 / 6) ** misses) * math.comb(dice, hits)
            regular_damage += hits * chance

        return regular_damage + crit_damage

    def fire(self, host: "Tank", target: "Tank", distance: float, arc: Arc, cover: int = 0, hull_down: bool = False) -> WeaponHitResult:
        optics = host.optics
        if WeaponSpecialRules.stable in self.special:
            optics += 3

        result = WeaponHitResult()

        if optics == 0:
            return result

        pool = self.rating - (math.floor(distance / optics) - 1)
        pool -= cover

        if pool <= 0:
            return result

        results = ShootingResult.from_(*(d6() for _ in range(pool)))
        armour_pen = count(results, ShootingResult.direct_hit)
        glances = count(results, ShootingResult.hit)

        if WeaponSpecialRules.no_pen in self.special:
            armour_pen = 0

        armour = target.armour[arc]
        if hull_down:
            hull_down_pool = target.speed + armour
            hull_down_dice = ShootingResult.from_(*(d6() for _ in range(hull_down_pool)))
            hull_down_pen = count(hull_down_dice, ShootingResult.direct_hit)
            hull_down_glances = count(hull_down_dice, ShootingResult.hit)
            armour_pen -= hull_down_pen
            glances -= hull_down_glances

        hits = glances + armour_pen

        discipline = target.discipline
        if TankSpecialRules.tiger_fear in host.special_rules:
            discipline -= 1

        critical = None
        if armour_pen >= armour:
            result.hit = True
            if arc == Arc.side and TankSpecialRules.schurzen in target.special_rules:
                target.special_rules.remove(TankSpecialRules.schurzen)
            else:
                hit_location = target.damage_locations[arc][d6()]
                critical_result = min(d6(target.critical_damage), 6)
                if hit_location == TankHitLocations.turret:
                    critical = TURRET_CRITICAL_DAMAGE_ROLL[critical_result - 1]
                if hit_location == TankHitLocations.hull:
                    critical = HULL_CRITICAL_DAMAGE_ROLL[critical_result - 1]
                if hit_location == TankHitLocations.tracks:
                    critical = TRACK_CRITICAL_DAMAGE_ROLL[critical_result - 1]
                if hit_location == TankHitLocations.crew:
                    critical = CREW_COMPARTMENT_DAMAGE_ROLL[critical_result - 1]
                critical(target)
                target.critical_damage += 1

                result.crit = True
                result.critical_effect = critical

            result.damage = hits
            result.panicked = True

            target.damage += hits
            target.panic += 1
        else:
            if armour_pen >= 1:
                result.hit = True
                target.damage += armour_pen
                result.damage = armour_pen
            if hits >= discipline:
                result.hit = True
                result.panicked = True
                target.panic += 1
        return result


class WeaponFacing(StrEnum):
    turret = "Turret"
    coaxial = "Coaxial"
    hull = "Hull"
    front = "Front"
    side = "Side"
    rear = "Rear"
    front_side = "Front/Side"


class WeaponListing:
    weapon: Weapon
    facing: WeaponFacing
    destroyed: bool = False

    def __init__(self, weapon: Weapon, facing: WeaponFacing):
        self.weapon = weapon
        self.facing = facing


