import math
from copy import deepcopy
from random import random
from typing import List

from tonk.misc import Arc
from tonk.tank import Tank
from tonk.utils import log_weapon_result, test_tank, TankException


def basic_strategy(logs: List[str], current_tanks: List[Tank], current_name: str, opposing_tanks: List[Tank], opposing_name: str):
    for tank in current_tanks:
        if tank.alive:
            tank.activation_start()

    actions = 3
    while actions > 0 and any(tank.alive and tank.orders > 0 for tank in current_tanks):
        maybe_targets = [t for t in opposing_tanks if t.alive]
        if len(maybe_targets) == 0:
            break

        actions -= 1
        acted = False
        maybe_actors = [t for t in current_tanks if t.alive and t.orders > 0 and not (t.moved and t.shot and t.repaired)]
        if len(maybe_actors) == 0:
            continue
        tank = sorted(maybe_actors, key=lambda t: random())[0]

        logs.append(f"Activating {tank.name} ({tank.damage}/{tank.hull}, {tank.panic} panic, {tank.critical_damage} crits)")

        was_on_file = tank.on_fire
        if tank.on_fire:
            logs.append(f"\t{tank.name} is on fire")
        active_result = tank.activate()
        if was_on_file and not active_result.on_fire:
            logs.append(f"\t{tank.name} was put out")
        if active_result.panicked:
            logs.append(f"\t{tank.name} panicked!")

        try:
            test_tank(tank, 0, logs)
        except TankException:
            continue

        if tank.panic > 0:
            if not tank.moved:
                logs.append(f"\t{tank.name} has panicked and retreated!")
                tank.panicked_move(opposing_tanks)
                tank.moved = True
            elif not tank.repaired:
                logs.append(f"\t{tank.name} has panicked and popped hatches!")
                tank.panicked_repair()
            continue

        if not tank.shot:
            for enemy in maybe_targets:
                if enemy.distance_from_tank(tank) < tank.optics * 2 and enemy.arc_from_tank(tank) in (Arc.side, Arc.rear):
                    acted = True
                    result = tank.shoot(0, enemy)
                    log_weapon_result(tank, enemy, tank.weapons[0], logs, result)
                    try:
                        test_tank(enemy, 0, logs)
                    except TankException:
                        pass
                    break
            if acted:
                continue
        if not tank.moved:
            closest_enemy = min(maybe_targets, key=lambda t: t.distance_from_tank(tank))
            if closest_enemy.distance_from_tank(tank) < closest_enemy.optics:
                theta = tank.angle_from(closest_enemy.x, closest_enemy.y)
                logs.append(f"\t{tank.name} has retreated from {closest_enemy.name}")
                tank.move(theta, -tank.movement/2)
                continue
            else:
                logs.append(f"\t{tank.name} drove towards {closest_enemy.name}")
                pos_a, pos_b = closest_enemy.positions_to_side(tank.optics * 1.5)
                dist_a = tank.distance_from(*pos_a)
                dist_b = tank.distance_from(*pos_b)
                if dist_a < dist_b:
                    target = pos_a
                    dist = dist_a
                else:
                    target = pos_b
                    dist = dist_b

                angle_to = tank.angle_from(*target)
                if angle_to > math.pi:
                    angle_to -= math.pi * 2

                if abs(angle_to) < math.pi / 4:
                    remaining = math.pi / 4 - abs(angle_to)
                    tank.manoeuvre(angle_to, min(tank.movement, dist))
                    target_correction = tank.angle_from(closest_enemy.x, closest_enemy.y)
                    if target_correction > math.pi:
                        target_correction -= math.pi * 2
                    correction = math.copysign(min(abs(target_correction), abs(remaining)), target_correction)
                    tank.rotate(correction)
                elif abs(angle_to) < math.pi / 2:
                    remaining = math.pi / 2 - abs(angle_to)
                    tank.manoeuvre(angle_to, min(tank.movement / 2, dist))
                    target_correction = tank.angle_from(closest_enemy.x, closest_enemy.y)
                    if target_correction > math.pi:
                        target_correction -= math.pi * 2
                    correction = math.copysign(min(abs(target_correction), abs(remaining)), target_correction)
                    tank.rotate(correction)
                else:
                    tank.pivot(angle_to)
                continue
        if not tank.repaired and tank.damage > 0:
            logs.append(f"\t{tank.name} repaired")
            tank.repair()
            continue
        if not tank.shot:
            enemy = min(maybe_targets, key=lambda t: t.distance_from_tank(tank))
            result = tank.shoot(0, enemy)
            log_weapon_result(tank, enemy, tank.weapons[0], logs, result)
            try:
                test_tank(enemy, 0, logs)
            except TankException:
                pass
            continue


def duel(player_1_tanks: List[Tank], player_1_name: str, player_2_tanks: List[Tank], player_2_name: str):
    player_1 = [deepcopy(tank) for tank in player_1_tanks]
    for n, tank in enumerate(player_1):
        tank.name += f" #{n}"
        tank.x = n * 6
        tank.y = -18
    player_2 = [deepcopy(tank) for tank in player_2_tanks]
    for n, tank in enumerate(player_2):
        tank.name += f" #{n}"
        tank.x = n * 6
        tank.y = 18
        tank.rotation = math.pi

    logs = []

    turn_number = 0
    while any(tank.alive for tank in player_1) and any(tank.alive for tank in player_2):
        turn_number += 1
        logs.append(f"Turn {turn_number}")
        logs.append(f"===============================")
        for tank in player_1 + player_2:
            if not tank.alive:
                continue
            tank.turn_start()

        current_player_name = player_2_name
        opposing_player_name = player_1_name
        current_player = player_2
        opposing_player = player_1

        while any(tank.alive and tank.orders > 0 for tank in player_1 + player_2) and any(tank.alive for tank in player_1) and any(tank.alive for tank in player_2):
            temp = current_player
            current_player = opposing_player
            opposing_player = temp

            temp_name = current_player_name
            current_player_name = opposing_player_name
            opposing_player_name = temp_name

            if not any(tank.alive and tank.orders > 0 for tank in current_player):
                logs.append(f"{current_player_name} has no more actions to take")
                break

            logs.append(f"{current_player_name}'s turn")
            basic_strategy(logs, current_player, current_player_name, opposing_player, opposing_player_name)


    return logs, player_1, player_2, turn_number



