from config import rare, super_rare, uber, legendary, rarity

# how many tickets you have
tickets_singles = 110

# how many times you can roll a 11 roll. usually 1500 catfood required per 11 roll.
catfood_11s = 11

seed_tuple: tuple = None

current_track = "A" # "A" or "B" 
                    # we can probably do without this, just gotta keep track of when track switch happens
                    # i guess its purely for display purposes
current_position = 0

previous_rarity = "Legendary" # oh maybe i dont need this as well
previous_cat = "Kyosaka Nanaho"

rares_gotten = {}
super_rares_gotten = {}
ubers_gotten = {}
legendaries_gotten = {}
total_wanted = 0
total_gotten = 0


def xorshift32(seed: int) -> int:
    """Generate the next xorshift32 value from a 32-bit seed."""
    x = seed & 0xFFFFFFFF  # ensure 32-bit unsigned

    x ^= (x << 13) & 0xFFFFFFFF
    x ^= (x >> 17)
    x ^= (x << 15) & 0xFFFFFFFF

    return x


def get_rarity(seed: int) -> str:
    remainder = seed % 10000
    if remainder < rarity["Rare"]:
        return "Rare"
    elif remainder < rarity["Super Rare"]:
        return "Super Rare"
    elif remainder < rarity["Uber"]:
        return "Uber"
    elif remainder < rarity["Legendary"]:
        return "Legendary"


def get_cat(seed: int, rarity: str) -> str:
    global rares_gotten, super_rares_gotten, ubers_gotten, legendaries_gotten, total_gotten
    if rarity == "Rare":
        cat_num = seed % len(rare)
        if cat_num < len(rares_gotten):
            if not rares_gotten[cat_num]:
                total_gotten += 1
            rares_gotten[cat_num] = True
        return rare[cat_num]

    elif rarity == "Super Rare":
        cat_num = seed % len(super_rare)
        if cat_num < len(super_rares_gotten):
            if not super_rares_gotten[cat_num]:
                total_gotten += 1
            super_rares_gotten[cat_num] = True
        return super_rare[cat_num]

    elif rarity == "Uber":
        cat_num = seed % len(uber)
        if cat_num < len(ubers_gotten):
            if not ubers_gotten[cat_num]:
                total_gotten += 1
            ubers_gotten[cat_num] = True
        return uber[cat_num]

    elif rarity == "Legendary":
        cat_num = seed % len(legendary)
        if cat_num < len(legendaries_gotten):
            if not legendaries_gotten[cat_num]:
                total_gotten += 1
            legendaries_gotten[cat_num] = True
        return legendary[cat_num]

    else:
        raise ValueError(f"Unknown rarity: {rarity}")


def advance_seed() -> None:
    global seed_tuple
    next_one = xorshift32(seed_tuple[1])
    next_two = xorshift32(next_one)
    seed_tuple = (next_one, next_two)
    return


def switch_track() -> None:
    global seed_tuple, current_track, current_position
    print(f"Track switch: {current_position}{current_track}", end="")
    seed_tuple = (seed_tuple[1], xorshift32(seed_tuple[1]))
    if current_track == "A":
        current_track = "B"
    elif current_track == "B":
        current_track = "A"
        current_position += 1
    else:
        raise ValueError(f"Unknown track: {current_track}")
    print(f" -> {current_position}{current_track}")
    return


# get alt seed for current seed, does not actually modify your seed
def get_alt_seed() -> tuple:
    alt_seed = (seed_tuple[1], xorshift32(seed_tuple[1]))
    return alt_seed


def roll_1() -> None:
    global current_position, previous_rarity, previous_cat, tickets_singles
    tickets_singles -= 1
    current_position += 1
    advance_seed()
    rarity = get_rarity(seed_tuple[0])
    cat = get_cat(seed_tuple[1], rarity)

    # track switch if dupe rares
    if rarity == "Rare" and cat == previous_cat:
        switch_track()
        rarity = get_rarity(seed_tuple[0])
        cat = get_cat(seed_tuple[1], rarity)

    previous_rarity = rarity
    previous_cat = cat
    print(f"{current_position}{current_track}: {seed_tuple}   {rarity} {cat}   Alt seed: {get_alt_seed()}")
    return


def roll_11_guarantee() -> None:
    global tickets_singles, catfood_11s
    tickets_singles += 10
    catfood_11s -= 1
    print(f"Starting a guaranteed 11 roll from {current_position+1}{current_track}")
    for _ in range(10):
        roll_1()

    # get your guaranteed uber
    switch_track()
    cat = get_cat(seed_tuple[1], "Uber")
    previous_rarity = "Uber"
    previous_cat = cat
    print(f"Guaranteed: {current_position}{current_track}: {seed_tuple}   {cat}")
    print(f" -> {current_position+1}{current_track}")
    return


def main():
    global seed_tuple, current_track, current_position, previous_cat, tickets_singles, catfood_11s,\
    rares_gotten, super_rares_gotten, ubers_gotten, legendaries_gotten, total_wanted, total_gotten

    # initialise your variables
    seed = 0  # initial seed TODO: add your seed here
    current_track = "A"
    current_position = 0
    previous_cat = "Kyosaka Nanaho"
    seed_tuple = (0, seed)
    tickets_singles = 110
    catfood_11s = 11

    # things you wanna try to get
    rares_wanted, super_rares_wanted, ubers_wanted, legendaries_wanted = 4, 3, 8, 1
    total_wanted = rares_wanted + super_rares_wanted + ubers_wanted + legendaries_wanted
    rares_gotten = {i: False for i in range(rares_wanted)}
    super_rares_gotten = {i: False for i in range(super_rares_wanted)}
    ubers_gotten = {i: False for i in range(ubers_wanted)}
    legendaries_gotten = {i: False for i in range(legendaries_wanted)}
    total_gotton = 0
    print(rares_wanted, super_rares_wanted, ubers_wanted, legendaries_wanted)
    print(rares_gotten)
    print(super_rares_gotten)
    print(ubers_gotten)
    print(legendaries_gotten)
    # if you in fact already have some, then here is when you should update the above dicts

    # print("Xorshift32 random sequence:")
    # for i in range(4):
    #     # roll_1()
    #     roll_11_guarantee()
    while total_gotten < total_wanted and catfood_11s > 0:
        roll_11_guarantee()
    while total_gotten < total_wanted and tickets_singles > 0:
        roll_1()
    
    # your bounty
    print(rares_gotten)
    print(super_rares_gotten)
    print(ubers_gotten)
    print(legendaries_gotten)
    print(f"{total_gotten}/{total_wanted}")


if __name__ == "__main__":
    main()
