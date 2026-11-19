# GTA VI Trophy Rarity Forecaster

Forecast of every GTA VI PlayStation 5 trophy's earn rate on Exophase at a target time, five quantiles each. Built for [make.fun](https://make.fun/?ref=jakadul&utm_source=github&utm_medium=readme&utm_campaign=gta6-trophy-rarity-forecast-01)'s bounty, $250 in USDC.

[![make.fun bounty](https://make.fun/badge/gta6-trophy-rarity-forecast-01.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01)
[![rank](https://make.fun/badge/gta6-trophy-rarity-forecast-01/jakadul/gta6-trophy-forecast/rank.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01)
[![reward](https://make.fun/badge/gta6-trophy-rarity-forecast-01/jakadul/gta6-trophy-forecast/reward.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01)

## Model

- Median = last observed earn rate from the case history (the page shows rates as of Exophase's last refresh).
- Spread = logit random walk, sigma = **1.1 per root-day** (the house baseline uses 0.5; the practice failure mode is under-dispersion across Exophase's refresh, so this is deliberately wider).
- Rare-trophy boost: spread scales up to 3.2x for low-rate trophies, where a week can move the logit far.
- Deterministic: no randomness, no clock, no network. Two runs byte-identical.

## Run

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Standard library only (Python 3.13). Reads every `.in` case in name order, writes one `.out` per case: an object with a `trophies` list, one row per trophy, each row an id plus five quantiles at 0.05/0.25/0.50/0.75/0.95.

## License

MIT — see LICENSE.
