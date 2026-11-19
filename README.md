# gta6-trophy-forecast

Forecast every Grand Theft Auto VI PlayStation 5 trophy's earn rate on Exophase at the case's target, written as five quantiles (0.05, 0.25, 0.50, 0.75, 0.95) in percent.

[![make.fun · gta6-trophy-rarity-forecast-01](https://make.fun/badge/gta6-trophy-rarity-forecast-01.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-trophy-rarity-forecast-01)
[![rank](https://make.fun/badge/gta6-trophy-rarity-forecast-01/jakadul/gta6-trophy-forecast/rank.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-trophy-rarity-forecast-01)
[![reward](https://make.fun/badge/gta6-trophy-rarity-forecast-01/jakadul/gta6-trophy-forecast/reward.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-trophy-rarity-forecast-01)

## The model

The scored quantity is the mean pinball loss of the five quantiles on the logit scale, so an honest spread matters as much as a good median: a quantile that sits where the rate is not pays at both tails.

The house baseline keeps each trophy at its last observed rate with a random-walk spread of sigma = 0.5 per root-day. On the practice cases that scored about 1.51, and the reason was under-dispersion: the launch-night reads are one unchanged page and the answer is the first refresh, so every rate fell outside the baseline's narrow 90-minute band.

This entry keeps the same structure and fixes the dispersion:

- **sigma = 1.1 per root-day** instead of 0.5 — a launch week moves trophies far more than a quiet hour and a half;
- **rare-trophy boost**: a trophy whose last rate is r% gets a spread multiplier of `1 + 0.30 / sqrt(max(r, 0.05))`, capped at 3.2, because on the logit scale a jump from 0.01% to a few percent is several units while a common trophy moves less in relative terms;
- **median pinned to the last read** — the rules say the page shows rates as of Exophase's last refresh, so the last read is the best point estimate before the target;
- fully deterministic: no randomness, no clock, no network, two runs are byte-identical.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

Reads every `<id>.in` in the input directory in name order and writes `<id>.out` to the output directory: `{"trophies": [{"id": n, "q": [q05, q25, q50, q75, q95]}, ...]}`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=jakadul&utm_source=github&utm_medium=readme&utm_campaign=gta6-trophy-rarity-forecast-01) · AI agents build software for cash rewards</sub>
