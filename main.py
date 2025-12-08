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
    if rarity == "Rare":
        return rare[seed % len(rare)]
    elif rarity == "Super Rare":
        return super_rare[seed % len(super_rare)]
    elif rarity == "Uber":
        return uber[seed % len(uber)]
    elif rarity == "Legendary":
        return legendary[seed % len(legendary)]
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


def roll_1():
    global current_position, previous_rarity, previous_cat
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


def roll_11_guarantee(seed_tuple) -> tuple:
    return ()


def main():
    global seed_tuple
    seed = 0  # initial seed TODO: add your seed here
    seed_tuple = (0, seed)

    # print("Xorshift32 random sequence:")
    for i in range(100):
        roll_1()


if __name__ == "__main__":
    main()
