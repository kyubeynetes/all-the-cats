import sys
import re

rare = {}
super_rare = {}
uber = {}
legendary = {}
rarity = {}

if __name__ == "__main__":
    file = sys.argv[1]
    with open(file) as f:
        lines = f.read().split("\n")
        lines = [l.strip() for l in lines if len(l) > 0]
        for line in lines:
            parts = re.split('\:|\(|\)', line)
            parts = [str.strip(p) for p in parts]
            # print(parts)
            percentage = parts[1]
            percentage = percentage.rstrip("%")
            rarity_num = int(float(percentage) * 100)
            rarity_type = parts[0]
            if rarity_type == "Rare":
                dict_to_edit = rare
                rarity["Rare"] = rarity_num
            elif rarity_type == "Super":
                dict_to_edit = super_rare
                rarity["Super Rare"] = rarity_num + rarity["Rare"]
            elif rarity_type == "Uber":
                dict_to_edit = uber
                rarity["Uber"] = rarity_num + rarity["Super Rare"]
            elif rarity_type == "Legendary":
                dict_to_edit = legendary
                rarity["Legendary"] = rarity_num + rarity["Uber"]
            else:
                continue            
            num_cats = int(parts[2].split()[0])
            if num_cats == 0:
                continue
            # print(num_cats)
            cats = parts[3].split(",")
            cats = [str.strip(c) for c in cats]
            # print(cats)
            for cat in cats:
                num_and_cat_name = cat.split(" ", 1)
                num = int(num_and_cat_name[0])
                cat_name = num_and_cat_name[1]
                dict_to_edit[num] = cat_name
    print(f"{rare = }")
    print(f"{super_rare = }")
    print(f"{uber = }")
    print(f"{legendary = }")
    print(f"{rarity = }")

'''
to run:
python3 generate_configs.py ./gacha_information.txt > ./output_config.py
'''
