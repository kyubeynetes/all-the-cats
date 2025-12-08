from config import rare, super_rare, uber, legendary, rarity

# how many tickets you have
tickets_singles = 110

# how many times you can roll a 11 roll. usually 1500 catfood required per 11 roll.
catfood_11s = 11

seed: tuple = None

current_track = "A" # "A" or "B"

previous_rarity = "Legendary"

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


def advance_seed(seed: tuple) -> tuple:
    next_one = xorshift32(seed[1])
    next_two = xorshift32(next_one)
    return (next_one, next_two)


def switch_track(seed: tuple) -> tuple:
    return (seed[1], xorshift32(seed[1]))





def roll_10_guarantee(seed_tuple) -> tuple:
    return ()


def main():
    seed = 1  # initial seed
    seed_tuple = (0, seed)

    # print("Xorshift32 random sequence:")
    for i in range(200):
        seed_tuple = advance_seed(seed_tuple)
        rarity = get_rarity(seed_tuple[0])
        cat = get_cat(seed_tuple[1], rarity)
        print(f"{i+1}: {seed_tuple}   {rarity} {cat}   Alt seed: {switch_track(seed_tuple)}")

if __name__ == "__main__":
    main()
