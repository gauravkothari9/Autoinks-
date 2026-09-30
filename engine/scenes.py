"""Registry of 2D stick-figure scenes.

A scene is a function scene(rng, palette, duration) -> draw(canvas, t). It does all its random
choices up front with rng, so draw is a pure function of t and every seed gives a new video.
Variants of one scene (a boxing ring vs a dojo, a snowboard vs a skateboard) are registered with
functools.partial. Scene ids must match engine/categories.json.
"""

from functools import partial

from .scenes_action import kung_fu, parkour, sword_duel
from .scenes_action2 import archery, laser_dodge, ninja_fruit, one_vs_all
from .scenes_comedy import prank_wars, stick_fail
from .scenes_dance import ballet, breakdance, dance_battle, dance_party, moonwalk, robot_dance
from .scenes_fitness import jump_rope, meditation, pull_ups, workout, yoga
from .scenes_life import dj_set, drummer, guitar_solo, juggler, lumberjack, pancake_chef
from .scenes_sports import basketball, race, skateboard, soccer
from .scenes_sports2 import (baseball, bowling, cricket, golf, high_jump, penalty, rally, trampoline,
                             weightlifting)

SCENES = {
    # Action
    "sword_duel": sword_duel,
    "staff_battle": partial(sword_duel, weapon="staff"),
    "laser_duel": partial(sword_duel, weapon="laser"),
    "kung_fu": kung_fu,
    "boxing": partial(kung_fu, mode="boxing"),
    "one_vs_all": one_vs_all,
    "parkour": parkour,
    "zombie_escape": partial(parkour, chasers=True),
    "archery": archery,
    "ninja_fruit": ninja_fruit,
    "laser_dodge": laser_dodge,
    # Sports
    "basketball": basketball,
    "soccer": soccer,
    "penalty_kick": penalty,
    "skateboard": skateboard,
    "snowboard": partial(skateboard, snow=True),
    "race": race,
    "hurdles": partial(race, hurdles=True),
    "tennis": partial(rally, kind="tennis"),
    "ping_pong": partial(rally, kind="pingpong"),
    "golf": golf,
    "baseball": baseball,
    "cricket": cricket,
    "bowling": bowling,
    "high_jump": high_jump,
    "weightlifting": weightlifting,
    "trampoline": trampoline,
    # Dance
    "dance_party": dance_party,
    "dance_battle": dance_battle,
    "breakdance": breakdance,
    "moonwalk": moonwalk,
    "ballet": ballet,
    "robot_dance": robot_dance,
    # Fitness
    "workout": workout,
    "abs_workout": partial(workout, kind="abs"),
    "hiit": partial(workout, kind="hiit"),
    "pull_ups": pull_ups,
    "jump_rope": jump_rope,
    "yoga": yoga,
    "tai_chi": partial(yoga, style="taichi"),
    "meditation": meditation,
    # Comedy
    "stick_fail": stick_fail,
    "cartoon_drops": partial(stick_fail, kind="drops"),
    "rake_trap": partial(stick_fail, kind="rakes"),
    "wet_floor": partial(stick_fail, kind="wet"),
    "prank_wars": prank_wars,
    # Music & Life
    "guitar_solo": guitar_solo,
    "drummer": drummer,
    "dj_set": dj_set,
    "pancake_chef": pancake_chef,
    "lumberjack": lumberjack,
    "juggler": juggler,
}
