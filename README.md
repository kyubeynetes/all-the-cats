# all-the-cats
## Motivation
Given a golden The Battle Cats banner (e.g., collabs) with x number of new legendaries / ubers / super rares / rares, find the most cost efficient method of getting all the cats that you want.

## Instructions
1. Copy banner details from godfat website to `gacha_information.txt`.
2. Run: `python3 generate_configs.py ./gacha_information.txt > ./output_config.py`
3. Run:

```
    python3 main.py \
    --config output_config.py --output output.txt --starting-seed <starting seed> \
    -r <rares wanted> -s <supers wanted> -u <ubers wanted> -l <legnedaries wanted> \
    --starting-bitmask 0b0 \
    --starting-track A \
    --starting-position 0 \
    --available-tickets <golden tickets available> \
    --available-catfood-11s <number of times you can afford a 11-roll, up to 4>
```

4. View the optimal steps in `output.txt`, if available.
