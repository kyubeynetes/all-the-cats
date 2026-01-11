import argparse
import json
import sys
import importlib.util
import pathlib

# config dicts
rare = {}
super_rare = {}
uber = {}
legendary = {}
rarity = {}

# units gotten
rares_gotten = {}
super_rares_gotten = {}
ubers_gotten = {}
legendaries_gotten = {}
total_gotten = 0

# units wanted
rares_wanted = 0
super_rares_wanted = 0
ubers_wanted = 0
legendaries_wanted = 0
total_wanted = 0

# variable to note if search is completed. if it is complete,
# print out each step. else, dont print so much because i/o
# is costly
is_finalized = False


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


def get_cat_fn(seed: int, rarity: str):
    global total_gotten
    if rarity == "Rare":
        cat_num = seed % len(rare)
        if is_finalized:
            if cat_num < len(rares_gotten):
                if not rares_gotten[cat_num]:
                    total_gotten += 1
                rares_gotten[cat_num] = True
        return rare[cat_num], cat_num

    elif rarity == "Super Rare":
        cat_num = seed % len(super_rare)
        if is_finalized:
            if cat_num < len(super_rares_gotten):
                if not super_rares_gotten[cat_num]:
                    total_gotten += 1
                super_rares_gotten[cat_num] = True
        return super_rare[cat_num], cat_num

    elif rarity == "Uber":
        cat_num = seed % len(uber)
        if is_finalized:
            if cat_num < len(ubers_gotten):
                if not ubers_gotten[cat_num]:
                    total_gotten += 1
                ubers_gotten[cat_num] = True
        return uber[cat_num], cat_num

    elif rarity == "Legendary":
        cat_num = seed % len(legendary)
        if is_finalized:
            if cat_num < len(legendaries_gotten):
                if not legendaries_gotten[cat_num]:
                    total_gotten += 1
                legendaries_gotten[cat_num] = True
        return legendary[cat_num], cat_num

    else:
        raise ValueError(f"Unknown rarity: {rarity}")


def get_non_dupe_rare(seed: int, previous_cat: str):
    key = next((k for k, v in rare.items() if v == previous_cat))
    cat_num = seed % (len(rare) - 1)
    if cat_num >= key:
        cat_num += 1
    return rare[cat_num], cat_num


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
    if is_finalized:
        print(f" -> {next_position}{next_track}")
    return next_rarity_seed, next_unit_seed, next_track, next_position


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
    if is_finalized:
        # print(f"{next_position}{next_track}: ({next_rarity_seed}, {next_unit_seed})   {rarity} {cat}   Alt seed: {get_alt_seed()}")
        print(f"{next_position}{next_track}: ({next_rarity_seed}, {next_unit_seed})   {rarity} {cat}")
    return next_rarity_seed, next_unit_seed, next_track, next_position, rarity, cat, bitmask


def get_roll_11_guarantee(rarity_seed: int, unit_seed: int, current_track: str, current_position: int, previous_rarity: str, previous_cat: str, previous_bitmask: int):
    next_rarity_seed, next_unit_seed = rarity_seed, unit_seed
    next_track, next_position = current_track, current_position
    rarity, cat = previous_rarity, previous_cat
    bitmask = previous_bitmask
    if is_finalized:
        print(f"Starting a guaranteed 11 roll from {current_position+1}{current_track}")
    for _ in range(10):
        next_rarity_seed, next_unit_seed, next_track, next_position, rarity, cat, bitmask = get_roll_1(next_rarity_seed, next_unit_seed, next_track, next_position, rarity, cat, bitmask)

    # get your guaranteed uber
    next_rarity_seed, next_unit_seed, next_track, next_position = get_track_switch(next_rarity_seed, next_unit_seed, next_track, next_position)
    rarity = "Uber"
    cat, cat_num = get_cat_fn(next_unit_seed, rarity)
    bitmask = get_bitmask(bitmask, rarity, cat_num)

    if is_finalized:
        print(f"Guaranteed: {next_position}{next_track}: ({next_rarity_seed}, {next_unit_seed})   {cat}")
        print(f" -> {next_position+1}{next_track}")
    return next_rarity_seed, next_unit_seed, next_track, next_position, rarity, cat, bitmask


def dfs(rarity_seed: int, unit_seed: int, current_track: str, current_position: int, previous_rarity: str, previous_cat: str, bitmask: int, tickets_singles: int, catfood_11s: int, ideal_bitmask: int):
    best_trace = []
    best_cost = 999

    current_trace = []
    current_cost = 0

    improvements = 0

    stack = []
    stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 11))
    stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 1))
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

        # TODO: fix edge case error that happens when all available resources / wanted cats
        # are zero because condition fulfilled check happens after a step is taken.
        if bitmask == ideal_bitmask:
            # all wanted cats found
            # also this MUST happen after a step == 11 or 1 block, rather than a backtracking block.
            # because a backtracking block does not add any new cats to the bitmask. path ends here, and
            # this must be the final cat that is needed, because if this isnt the final cat that is needed,
            # and it is now true that all needed cats are found, then this condition must have been met earlier.
            if current_cost < best_cost:
                best_trace = current_trace[:]
                best_cost = current_cost
                print(f"current best: cost={best_cost} trace={best_trace} {improvements} previous solutions")
                improvements += 1
                if improvements > 30:
                    break
            continue # dont append new stuff after, path ends here because all cats found
            # break # for testing
        # for backtracking
        if current_cost > 100:
            continue
        if catfood_11s > 0:
            stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 11))
        if tickets_singles > 0:
            stack.append((rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, 1))

    return best_trace, best_cost


def print_units_gotten():
    symbol = lambda x: "YES" if x else "---"
    rares_named = {f"{k} ({rare[k]})":symbol(v) for k, v in rares_gotten.items()}
    print(json.dumps(rares_named, indent=4))
    super_rares_named = {f"{k} ({super_rare[k]})":symbol(v) for k, v in super_rares_gotten.items()}
    print(json.dumps(super_rares_named, indent=4))
    ubers_named = {f"{k} ({uber[k]})":symbol(v) for k, v in ubers_gotten.items()}
    print(json.dumps(ubers_named, indent=4))
    legendaries_named = {f"{k} ({legendary[k]})":symbol(v) for k, v in legendaries_gotten.items()}
    print(json.dumps(legendaries_named, indent=4))
    return


def load_config(path):
    path = pathlib.Path(path).resolve()

    spec = importlib.util.spec_from_file_location("config", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config .py file")
    parser.add_argument("--output", help="Path to output file, writes to stdout if absent")
    parser.add_argument("-r", "--rares-wanted", type=int, default=0)
    parser.add_argument("-s", "--super-rares-wanted", type=int, default=0)
    parser.add_argument("-u", "--ubers-wanted", type=int, default=0)
    parser.add_argument("-l", "--legendaries-wanted", type=int, default=0)
    parser.add_argument("--starting-bitmask", type=str, default="0b0")
    parser.add_argument("--starting-seed", required=True, type=int)
    parser.add_argument("--starting-track", type=str, default="A")
    parser.add_argument("--starting-position", type=int, default=0)
    parser.add_argument("--previous-rarity", type=str, default="Legendary")
    parser.add_argument("--previous-cat", type=str, default="")
    parser.add_argument("--available-tickets", type=int, default=0)
    parser.add_argument("--available-catfood-11s", type=int, default=0)
    args = parser.parse_args()

    config = load_config(args.config)
    global rare, super_rare, uber, legendary, rarity
    rare = config.rare
    super_rare = config.super_rare
    uber = config.uber
    legendary = config.legendary
    rarity = config.rarity

    if args.output:
        f = open(args.output, "w")
        sys.stdout = f

    global rares_gotten, super_rares_gotten, ubers_gotten, legendaries_gotten, total_gotten
    global rares_wanted, super_rares_wanted, ubers_wanted, legendaries_wanted, total_wanted
    rares_wanted = args.rares_wanted
    super_rares_wanted = args.super_rares_wanted
    ubers_wanted = args.ubers_wanted
    legendaries_wanted = args.legendaries_wanted
    bitmask = int(args.starting_bitmask, base=0)
    total_wanted = rares_wanted + super_rares_wanted + ubers_wanted + legendaries_wanted
    rares_gotten = {i: False for i in range(rares_wanted)}
    super_rares_gotten = {i: False for i in range(super_rares_wanted)}
    ubers_gotten = {i: False for i in range(ubers_wanted)}
    legendaries_gotten = {i: False for i in range(legendaries_wanted)}
    total_gotten = 0
    print(rares_wanted, super_rares_wanted, ubers_wanted, legendaries_wanted)
    # if you in fact already have some, then here is when you should update the above dicts
    # alternatively, if there are cats in the cat_num range that you are interested in, but you dont mind not getting those particular cats, change their bit to "1", it will appear as it you have already gotten it.
    ideal_bitmask = 2**total_wanted-1

    rarity_seed = 0
    unit_seed = args.starting_seed
    current_track = args.starting_track
    current_position = args.starting_position
    previous_rarity = args.previous_rarity
    previous_cat = args.previous_cat
    tickets_singles = args.available_tickets
    catfood_11s = args.available_catfood_11s

    print(f"starting with {tickets_singles} tickets and {catfood_11s} catfood 11 draws")
    steps, total_cost = dfs(rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask, tickets_singles, catfood_11s, ideal_bitmask)
    print()
    print("final steps: ", steps)
    global is_finalized
    is_finalized = True

    for step in steps:
        if bitmask == ideal_bitmask:
            break
        if step == 1:
            rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask = get_roll_1(rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask)
            tickets_singles -= 1
        elif step == 11:
            rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask = get_roll_11_guarantee(rarity_seed, unit_seed, current_track, current_position, previous_rarity, previous_cat, bitmask)
            catfood_11s -= 1
    
    # your bounty
    print_units_gotten()
    print(f"{total_gotten}/{total_wanted}")
    print(f"Remaining Resources: {tickets_singles} tickets and {catfood_11s} catfood 11 draws")
    print(f"Total Cost: {total_cost}")
    print(f"Final Seed: {unit_seed}")

    print(bin(bitmask))

    if args.output:
        f.close()

if __name__ == "__main__":
    main()
