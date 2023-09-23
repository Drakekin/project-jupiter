from montecarlo.sim import monte_carlo_self_stabalising_parallel
from tonk.duel import duel
from tonk.tanks import m4_sherman, panzer_iv, vc_firefly


def duel_instrumented():
    logs, shermans, panzer, turns = duel([m4_sherman, m4_sherman, vc_firefly, vc_firefly, m4_sherman], "Shermans",
             [panzer_iv, panzer_iv, panzer_iv, panzer_iv], "Panzers")

    if all(not t.alive for t in shermans):
        panzer_victory = 1
    else:
        panzer_victory = 0
    if all(not t.alive for t in panzer):
        sherman_victory = 1
    else:
        sherman_victory = 0

    panzer_destroy = sum([1 if not t.alive else 0 for t in shermans])
    panzer_bail = sum([1 if t.bailed else 0 for t in shermans])
    panzer_explode = sum([1 if t.exploded else 0 for t in shermans])
    sherman_destroy = sum([1 if not t.alive else 0 for t in panzer])
    sherman_bail = sum([1 if t.bailed else 0 for t in panzer])
    sherman_explode = sum([1 if t.exploded else 0 for t in panzer])

    return (turns, panzer_victory, sherman_victory, panzer_destroy, sherman_destroy, panzer_bail, sherman_bail, panzer_explode, sherman_explode)


def discriminator(result):
    turns, panzer_victory, sherman_victory, panzer_destroy, sherman_destroy, panzer_bail, sherman_bail, panzer_explode, sherman_explode = result
    return panzer_victory


def simulate():

    win_rate, results = monte_carlo_self_stabalising_parallel(duel_instrumented, discriminator, required_stability=5)

    print(f"Panzers win {win_rate * 100:.2f}% of the time")


if __name__ == "__main__":
    simulate()
