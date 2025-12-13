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

# variables for optimisation
total_cost = 0 # cost is same as number of rolls done
                # can consider if catfood rolls should be twice as valuable as ticket rolls
                # also to consider if catfood 11 draws should be considered as 10 or 11 rolls
                # also consider if catfood and ticket costs should be separate, but that will have 
                # additional complications because Depth First Search can only optimise on one axis?


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


def get_cat_fn(seed: int, rarity: str):
    if rarity == "Rare":
        cat_num = seed % len(rare)
        return rare[cat_num], cat_num

    elif rarity == "Super Rare":
        cat_num = seed % len(super_rare)
        return super_rare[cat_num], cat_num

    elif rarity == "Uber":
        cat_num = seed % len(uber)
        return uber[cat_num], cat_num

    elif rarity == "Legendary":
        cat_num = seed % len(legendary)
        return legendary[cat_num], cat_num

    else:
        raise ValueError(f"Unknown rarity: {rarity}")


def get_non_dupe_rare(seed: int, previous_cat: str):
    key = next((k for k, v in rare.items() if v == previous_cat))
    cat_num = seed % (len(rare) - 1)
    if cat_num >= key:
        cat_num += 1
    return rare[cat_num], cat_num


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
    global current_position, previous_rarity, previous_cat, tickets_singles,  total_cost
    total_cost += 1
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
    global tickets_singles, catfood_11s, total_cost
    total_cost += 1 # the original 10 rolls are already accounted for
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


def get_next_seed(rarity_seed: int, unit_seed: int):
    next_rarity_seed = xorshift32(unit_seed)
    next_unit_seed = xorshift32(next_rarity_seed)
    return next_rarity_seed, next_unit_seed


def get_track_switch(rarity_seed: int, unit_seed: int, current_track: str, current_position: int):
    # print(f"Track switch: {current_position}{current_track}", end="")
    next_rarity_seed = unit_seed
    next_unit_seed = xorshift32(next_rarity_seed)
    if current_track == "A":
        next_track = "B"
        next_position = current_position
    elif current_track == "B":
        next_track = "A"
        next_position = current_position + 1
    else:
        raise ValueError(f"Unknown track: {current_track}")
    # print(f" -> {next_position}{next_track}")
    return next_rarity_seed, next_unit_seed, next_track, next_position

rares_wanted = 4
super_rares_wanted = 3
ubers_wanted = 8
legendaries_wanted = 1

def get_bit(rarity: str, cat_num: int) -> int:
    if rarity == "Rare":
        if cat_num < rares_wanted:
            return cat_num
        else:
            return -1
    elif rarity == "Super Rare":
        if cat_num < super_rares_wanted:
            return cat_num + rares_wanted
        else:
            return -1
    elif rarity == "Uber":
        if cat_num < ubers_wanted:
            return cat_num + rares_wanted + super_rares_wanted
        else:
            return -1
    elif rarity == "Legendary":
        if cat_num < legendaries_wanted:
            return cat_num + rares_wanted + super_rares_wanted + ubers_wanted
        else:
            return -1
    else:
        return -1


def get_bitmask(initial: int, rarity: str, cat_num: int) -> int:
    """Return the bit corresponding to labels 1..20, else 0."""
    bit = get_bit(rarity, cat_num)
    # print("!!!", bit)
    if bit == -1:
        # not interested in this cat
        return initial
    else:
        return initial | (1 << bit)


def get_roll_1(rarity_seed: int, unit_seed: int, current_track: str, current_position: int, previous_rarity: str, previous_cat: str, previous_bitmask: int):
    next_track = current_track
    next_position = current_position + 1
    next_rarity_seed, next_unit_seed = get_next_seed(rarity_seed, unit_seed)
    rarity = get_rarity(next_rarity_seed)
    cat, cat_num = get_cat_fn(next_unit_seed, rarity)
    # track switch if dupe rares
    if rarity == "Rare" and cat == previous_cat:
        next_rarity_seed, next_unit_seed, next_track, next_position = get_track_switch(next_rarity_seed, next_unit_seed, next_track, next_position)
        # rarity = get_rarity(next_rarity_seed)
        cat, cat_num = get_non_dupe_rare(next_unit_seed, previous_cat)

    bitmask = get_bitmask(previous_bitmask, rarity, cat_num)
    # rarity = rarity
    # previous_cat = cat
    # print(f"{next_position}{next_track}: ({next_rarity_seed}, {next_unit_seed})   {rarity} {cat}   Alt seed: {get_alt_seed()}")
    return next_rarity_seed, next_unit_seed, next_track, next_position, rarity, cat, bitmask


def get_roll_11_guarantee(rarity_seed: int, unit_seed: int, current_track: str, current_position: int, previous_rarity: str, previous_cat: str, previous_bitmask: int):
    next_rarity_seed, next_unit_seed = rarity_seed, unit_seed
    next_track, next_position = current_track, current_position
    rarity, cat = previous_rarity, previous_cat
    bitmask = previous_bitmask
    # print(f"Starting a guaranteed 11 roll from {current_position+1}{current_track}")
    for _ in range(10):
        next_rarity_seed, next_unit_seed, next_track, next_position, rarity, cat, bitmask = get_roll_1(next_rarity_seed, next_unit_seed, next_track, next_position, rarity, cat, bitmask)

    # get your guaranteed uber
    next_rarity_seed, next_unit_seed, next_track, next_position = get_track_switch(next_rarity_seed, next_unit_seed, next_track, next_position)
    rarity = "Uber"
    cat, cat_num = get_cat_fn(next_unit_seed, rarity)
    bitmask = get_bitmask(bitmask, rarity, cat_num)

    # print(f"Guaranteed: {next_position}{next_track}: ({next_rarity_seed}, {next_unit_seed})   {cat}")
    # print(f" -> {next_position+1}{next_track}")
    return next_rarity_seed, next_unit_seed, next_track, next_position, rarity, cat, bitmask


def dfs_rec():
    return


def dfs(rarity_seed: int, unit_seed: int, current_track: str, current_position: int, previous_rarity: str, previous_cat: str, bitmask: int, tickets_singles: int, catfood_11s: int, ideal_bitmask: int) -> list:
    best_trace = []
    best_cost = 999

    current_trace = []
    current_cost = 0

    improvements = 0

    stack = []
    stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 11))
    stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 1))
    print(stack)
    # return best_steps
    while True:
        if len(stack) == 0:
            break
        rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, step = stack.pop()

        if step != 0:
            # not backtracking step, that means its a new node
            stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 0))

        if step == 11:
            rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask = get_roll_11_guarantee(rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask)
            current_cost += 11
            catfood_11s -= 1
            current_trace.append(11)

        elif step == 1:
            rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask = get_roll_1(rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask)
            current_cost += 1
            tickets_singles -= 1
            current_trace.append(1)
        else:
            # backtrack
            # step == 0
            prev_step = current_trace.pop()
            if prev_step == 11:
                catfood_11s += 1
                current_cost -= 11
            elif prev_step == 1:
                tickets_singles += 1
                current_cost -= 1
            continue # dont append new stuff after bactracking if not you'll go in circles

        if bitmask == ideal_bitmask:
            # all wanted cats found
            # also this MUST happen after a step == 11 or 1 block, rather than a backtracking block.
            # because a backtracking block does not add any new cats to the bitmask. path ends here, and
            # this must be the final cat that is needed, because if this isnt the final cat that is needed,
            # and it is now true that all needed cats are found, then this condition must have been met earlier.
            if current_cost < best_cost:
                print("current best_trace:", best_trace)
                print("current best_cost:", best_cost)
                best_trace = current_trace[:]
                best_cost = current_cost
                improvements += 1
                if improvements > 10:
                    break
            continue # dont append new stuff after, path ends here because all cats found
            # break # for testing


        # for backtracking
        if current_cost > 90:
            continue
        if catfood_11s > 0:
            stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 11))
        if tickets_singles > 0:
            stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 1))

    return best_trace


def main():
    global seed_tuple, current_track, current_position, previous_cat, tickets_singles, catfood_11s,\
    rares_gotten, super_rares_gotten, ubers_gotten, legendaries_gotten, total_wanted, total_gotten

    # initialise your variables
    seed = 1022507091  # initial seed TODO: add your seed here
    current_track = "A"
    current_position = 0
    previous_cat = "Kyosaka Nanaho"
    seed_tuple = (0, seed)
    tickets_singles = 110
    catfood_11s = 11

    # things you wanna try to get
    global rares_wanted, super_rares_wanted, ubers_wanted, legendaries_wanted
    rares_wanted, super_rares_wanted, ubers_wanted, legendaries_wanted = 4, 3, 8, 1
    bitmask_bin = 0b0000000000000000
    bitmask = int(bitmask_bin)
    print(bitmask)
    print(bin(bitmask))
    total_wanted = rares_wanted + super_rares_wanted + ubers_wanted + legendaries_wanted
    rares_gotten = {i: False for i in range(rares_wanted)}
    super_rares_gotten = {i: False for i in range(super_rares_wanted)}
    ubers_gotten = {i: False for i in range(ubers_wanted)}
    legendaries_gotten = {i: False for i in range(legendaries_wanted)}
    total_gotten = 0
    print(rares_wanted, super_rares_wanted, ubers_wanted, legendaries_wanted)
    print(rares_gotten)
    print(super_rares_gotten)
    print(ubers_gotten)
    print(legendaries_gotten)
    # if you in fact already have some, then here is when you should update the above dicts
    # alternatively, if there are cats in the cat_num range that you are interested in, but you dont mind not getting those particular cats, change their bit to "1", it will appear as it you have already gotten it.
    ideal_bitmask = 0b1111111111111111 

    rarity_seed = 0
    unit_seed = 
    current_track = "A"
    current_position = 0
    previous_rarity = "Legendary"
    previous_cat = "Kyosaka Nanaho"

    steps = dfs(rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, tickets_singles, catfood_11s, ideal_bitmask)
    print("Steps: ", steps)

    total_cost = 0
    for step in steps:
        if bitmask == ideal_bitmask:
            break
        if step == 1:
            roll_1()
            # rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask = get_roll_1(rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask)
            total_cost += 1
        elif step == 11:
            roll_11_guarantee()
            # rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask = get_roll_11_guarantee(rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask)
            total_cost += 11

    # while total_gotten < total_wanted and tickets_singles > 0:
    #     roll_1()
    # while total_gotten < total_wanted and catfood_11s > 0:
    #     roll_11_guarantee()
    
    # your bounty
    print(rares_gotten)
    print(super_rares_gotten)
    print(ubers_gotten)
    print(legendaries_gotten)
    print(f"{total_gotten}/{total_wanted}")
    print(f"Remaining Resources: {tickets_singles} tickets and {catfood_11s} catfood 11 draws")
    print(f"Total Cost: {total_cost}")
    print(f"Final Seed: {seed_tuple[1]}")

    print(bitmask)
    print(bin(bitmask))

if __name__ == "__main__":
    main()
