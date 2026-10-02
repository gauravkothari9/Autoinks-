"""Registry of drawing scenes.

A scene is a function scene(rng, palette, duration, hold) -> draw(canvas, t). It makes all its random
choices up front with rng, so draw is a pure function of t and every seed gives a new video.
Scene ids must match engine/categories.json.
"""

from . import drawings, drawings2, drawings3, drawings4

SCENES = {
    # Speed Drawing: pen outlines, marker coloring, shading, final touches
    "mountain_lake": drawings.mountain_lake,
    "sunset_beach": drawings.sunset_beach,
    "lighthouse": drawings.lighthouse,
    "cottage": drawings.cottage,
    "hot_air_balloon": drawings.hot_air_balloon,
    "rocket": drawings.rocket,
    "windmill": drawings2.windmill,
    "campfire": drawings2.campfire,
    "volcano": drawings2.volcano,
    "castle": drawings2.castle,
    "sailboat": drawings3.sailboat,
    "rainbow_hills": drawings3.rainbow_hills,
    "igloo": drawings3.igloo,
    "pyramids": drawings3.pyramids,
    "mushroom_house": drawings3.mushroom_house,
    "waterfall": drawings4.waterfall,
    "treehouse": drawings4.treehouse,
    "city_night": drawings4.city_night,
    # Cute Animals
    "cute_cat": drawings.cute_cat,
    "owl": drawings.owl,
    "koi_pond": drawings.koi_pond,
    "whale": drawings.whale,
    "butterfly": drawings.butterfly,
    "fox": drawings2.fox,
    "penguin": drawings2.penguin,
    "panda": drawings2.panda,
    "sea_turtle": drawings2.sea_turtle,
    "bunny": drawings3.bunny,
    "frog": drawings3.frog,
    "bee": drawings3.bee,
    "snail": drawings3.snail,
    "octopus": drawings3.octopus,
    "dinosaur": drawings4.dinosaur,
    "hedgehog": drawings4.hedgehog,
    "jellyfish": drawings4.jellyfish,
    "puppy": drawings4.puppy,
    # Plants & Treats
    "sunflower": drawings.sunflower,
    "cactus": drawings.cactus,
    "ice_cream": drawings.ice_cream,
    "cupcake": drawings2.cupcake,
    "tulip_vase": drawings2.tulip_vase,
    "strawberry": drawings3.strawberry,
    "donut": drawings3.donut,
    "watermelon": drawings3.watermelon,
    "pizza": drawings4.pizza,
    "bonsai": drawings4.bonsai,
    "birthday_cake": drawings4.birthday_cake,
    # Things
    "car": drawings3.car,
    "teacup": drawings3.teacup,
    "gift_box": drawings3.gift_box,
    "guitar": drawings4.guitar,
    "robot": drawings4.robot,
}
