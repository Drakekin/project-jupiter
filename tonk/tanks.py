from tonk.misc import Arcs, D6Table
from tonk.tank import Tank
from tonk.tank_special_rules import TankSpecialRules
from tonk.weapon import TankHitLocations, WeaponListing, Weapon, WeaponSpecialRules, WeaponFacing

m4_sherman_main_gun = Weapon("75mm Cannon", 7)
vc_firefly_main_gun = Weapon("17pdr QF Gun", 12)
panzer_iv_main_gun = Weapon("75mm Cannon", 9)
medium_machine_gun = Weapon("MMG", 3, [WeaponSpecialRules.no_pen])

m4_sherman = Tank(
    "M4 Sherman",
    4, 8, 6, 3, 8,
    Arcs[int](3, 1, 1),
    Arcs[D6Table[TankHitLocations]](
        D6Table[TankHitLocations](*([TankHitLocations.hull]*4+[TankHitLocations.turret]*2)),
        D6Table[TankHitLocations](*([TankHitLocations.tracks]*3+[TankHitLocations.hull]+[TankHitLocations.turret]*2)),
        D6Table[TankHitLocations](*([TankHitLocations.hull]*4+[TankHitLocations.turret]*2)),
    ),
    [
        WeaponListing(m4_sherman_main_gun, WeaponFacing.turret),
        WeaponListing(medium_machine_gun, WeaponFacing.coaxial),
        WeaponListing(medium_machine_gun, WeaponFacing.hull),
    ],
    [TankSpecialRules.flammable]
)

vc_firefly = Tank(
    "Sherman VC Firefly",
    4, 8, 5, 3, 8,
    Arcs[int](3, 1, 1),
    Arcs[D6Table[TankHitLocations]](
        D6Table[TankHitLocations](*([TankHitLocations.hull]*4+[TankHitLocations.turret]*2)),
        D6Table[TankHitLocations](*([TankHitLocations.tracks]*3+[TankHitLocations.hull]+[TankHitLocations.turret]*2)),
        D6Table[TankHitLocations](*([TankHitLocations.hull]*4+[TankHitLocations.turret]*2)),
    ),
    [
        WeaponListing(vc_firefly_main_gun, WeaponFacing.turret),
        WeaponListing(medium_machine_gun, WeaponFacing.coaxial),
    ],
    [TankSpecialRules.flammable],
)

panzer_iv = Tank(
    "Panzer IV",
    3, 9, 6, 3, 10,
    Arcs[int](3, 2, 1),
    Arcs[D6Table[TankHitLocations]](
        D6Table[TankHitLocations](*([TankHitLocations.hull] * 4 + [TankHitLocations.turret] * 2)),
        D6Table[TankHitLocations]( *([TankHitLocations.tracks] * 3 + [TankHitLocations.hull] + [TankHitLocations.turret] * 2)),
        D6Table[TankHitLocations](*([TankHitLocations.hull] * 4 + [TankHitLocations.turret] * 2)),
    ),
    [
        WeaponListing(panzer_iv_main_gun, WeaponFacing.turret),
        WeaponListing(medium_machine_gun, WeaponFacing.coaxial),
        WeaponListing(medium_machine_gun, WeaponFacing.hull),
    ],
)

