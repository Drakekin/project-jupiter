import math
from random import random
from typing import List, Optional

from tonk.critical_damage import ammunition_explosion
from tonk.dice import d6, ShootingResult, count
from tonk.misc import Arcs, D6Table, Direction, Arc
from tonk.tank_special_rules import TankSpecialRules
from tonk.telemetry import ActivationResult, WeaponHitResult
from tonk.weapon import WeaponListing, TankHitLocations, WeaponFacing


class Tank:
    name: str

    x: float
    y: float
    rotation: float

    speed: int
    original_optics: int
    optics: int
    original_movement: int
    movement: int
    discipline: int
    hull: int

    critical_damage: int
    damage: int
    panic: int

    armour: Arcs[int]
    damage_locations: Arcs[D6Table[TankHitLocations]]
    weapons: List[WeaponListing]

    orders: int
    hatches_open: bool

    special_rules: List[TankSpecialRules]

    on_fire: bool = False
    exploded: bool = False
    turret_jammed: bool = False
    turret_jammed_arc: Optional[Direction] = None

    moved: bool = False
    shot: bool = False
    repaired: bool = False
    hull_downed: bool = False
    activated: bool = False

    def __init__(
            self,
            name: str,
            speed: int,
            optics: int,
            movement: int,
            discipline: int,
            hull: int,
            armour: Arcs[int],
            damage_locations: Arcs[D6Table[TankHitLocations]],
            weapons: List[WeaponListing],
            special_rules: Optional[List[TankSpecialRules]] = None
    ):
        self.name = name
        self.speed = speed
        self.optics = self.original_optics = optics
        self.movement = self.original_movement = movement
        self.discipline = discipline
        self.hull = hull
        self.damage = self.critical_damage = self.panic = 0
        self.armour = armour
        self.damage_locations = damage_locations
        self.weapons = weapons
        self.special_rules = special_rules if special_rules else []
        self.x = self.y = self.rotation = float(0)
        self.hatches_open = False
        self.moved = self.shot = self.repaired = self.hull_downed = False
        self.activated = False

    @property
    def destroyed(self) -> bool:
        return self.damage >= self.hull

    @property
    def bailed(self) -> bool:
        return self.panic >= 3

    @property
    def alive(self) -> bool:
        return not self.destroyed and not self.bailed

    def angle_from(self, x: float, y: float):
        dx = self.x - x
        dy = self.y - y
        angle = math.atan2(dy, dx) - self.rotation
        return ((angle % 360) + 360) % 360

    def arc_from_tank(self, tank: "Tank") -> Arc:
        angle = self.angle_from(tank.x, tank.y)
        if angle < math.pi / 4 or angle > math.pi / 4 * 7:
            return Arc.front
        if math.pi / 4 * 3 < angle < math.pi / 4 * 5:
            return Arc.rear
        return Arc.side

    def turn_start(self):
        self.orders = self.speed
        self.activation_start()

    def hull_down(self):
        self.orders -= 1

    def activation_start(self):
        self.moved = self.shot = self.repaired = self.hull_downed = self.activated = False
        if self.hatches_open:
            self.hatches_open = False
            self.hull_downed = True

    def activate(self) -> ActivationResult:
        result = ActivationResult()
        if self.activated:
            return result
        self.activated = True

        if self.on_fire:
            result.on_fire = True
            res = d6(1 if TankSpecialRules.flammable in self.special_rules else 0)
            if res >= 6:
                ammunition_explosion(self)
                result.exploded = True
            elif res >= 2:
                result.panicked = True
                self.panic += 1
            else:
                result.on_fire = False
                self.on_fire = False
        return result

    def repair(self):
        self.orders -= 1

        self.repaired = True

        results = ShootingResult.from_(*(d6() for _ in range(3)))
        repair_critical = count(results, ShootingResult.direct_hit)
        repair = count(results, ShootingResult.direct_hit, ShootingResult.hit)

        self.damage = max(0, self.damage - repair)
        self.critical_damage = max(0, self.critical_damage - repair_critical)

    def panicked_repair(self):
        self.orders -= 1

        self.repaired = self.moved = self.shot = self.hull_downed = True
        self.hatches_open = True

        self.panic -= 1

    def move_forwards(self, distance: float):
        self.x -= math.sin(self.rotation) * distance
        self.y += math.cos(self.rotation) * distance

    def positions_to_side(self, distance):
        dx = math.cos(self.rotation)
        dy = math.sin(self.rotation)
        return (dx * distance, dy * distance), (-dx * distance, -dy * distance)

    def move(self, pre_move_rotation: float, move_1: float, mid_move_rotation: float = 0, move_2: float = 0, end_move_rotation: float = 0):
        self.orders -= 1

        self.rotate(pre_move_rotation)
        self.move_forwards(move_1)
        self.rotate(mid_move_rotation)
        self.move_forwards(move_2)
        self.rotate(end_move_rotation)
        self.moved = True

    def manoeuvre(self, pre_move_rotation: float, move_1: float, mid_move_rotation_1: float = 0, move_2: float = 0, mid_move_rotation_2: float = 0, move_3: float = 0, end_move_rotation: float = 0):
        self.orders -= 1

        self.rotate(pre_move_rotation)
        self.move_forwards(move_1)
        self.rotate(mid_move_rotation_1)
        self.move_forwards(move_2)
        self.rotate(mid_move_rotation_2)
        self.move_forwards(move_3)
        self.rotate(end_move_rotation)
        self.moved = True

    def pivot(self, rotation: float):
        self.orders -= 1

        self.rotate(rotation)
        self.moved = True

    def rotate(self, rotation: float):
        self.rotation = ((self.rotation + rotation) % 360 + 360) % 360

    def panicked_move(self, other_tanks: List["Tank"]):
        self.panic -= 1

        maybe_targets = [t for t in other_tanks if t.alive]
        closest_enemy = min(maybe_targets, key=lambda t: t.distance_from_tank(self))
        if closest_enemy.distance_from_tank(self) < closest_enemy.optics:
            theta = self.angle_from(closest_enemy.x, closest_enemy.y)
            self.move(theta, -self.movement / 2)

    def shoot(self, weapon_index: int, target: "Tank") -> WeaponHitResult:
        self.orders -= 1

        self.shot = True

        weapon = self.weapons[weapon_index]

        distance = self.distance_from_tank(target)
        arc = target.arc_from_tank(self)

        went_hull_down = False
        if target.consider_hull_down(weapon, arc, distance, self.optics):
            target.hull_down()
            went_hull_down = True

        result = weapon.weapon.fire(self, target, distance, arc, went_hull_down)
        result.went_hull_down = went_hull_down
        return result

    def distance_from(self, x: float, y: float) -> float:
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx * dx + dy * dy)

    def distance_from_tank(self, target: "Tank") -> float:
        dx = self.x - target.x
        dy = self.y - target.y
        return math.sqrt(dx * dx + dy * dy)

    def consider_hull_down(self, weapon: WeaponListing, arc: Arc, distance: float, optics: int):
        if self.orders == 0 or optics == 0:
            return False

        mod = 1
        if arc == Arc.side:
            mod = 2
        if arc == Arc.rear:
            mod = 3
        if distance < optics:
            mod += 1

        return random() < (self.orders / self.speed) ** (1 / mod)
