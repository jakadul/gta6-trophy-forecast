"""gta6-trophy-rarity-forecast-01 entry.

Forecast model for every GTA VI PlayStation 5 trophy's earn rate on Exophase,
at each case's target, written as five quantiles (0.05, 0.25, 0.50, 0.75, 0.95)
in percent.

The house baseline forecasts each trophy's rate stays where the last read put it
with a random-walk logit spread (sigma = 0.5 per root-day). That baseline scored
about 1.51 on the practice, because the launch-night refresh moved every rate far
outside its narrow 90-minute band: the practice cases' last read is the stale
launch-night page and their answer is the refreshed page, so the failure mode is
almost entirely under-dispersed uncertainty, not a wrong median.

This entry keeps the same logit-scale structure (the score is the pinball loss on
the logit scale, so an honest spread beats a confident miss) but:

  * widens the random-walk sigma to 1.1 per root-day, which is what a real
    launch-week trophy curve does, not what a quiet 90 minutes does;
  * widens further for rare trophies: a bronze that nobody has earned yet can
    move from 0.01% to several percent in a week, and on the logit scale that
    is a large jump, so its spread scales with 1 / sqrt(median rate) capped;
  * keeps the median pinned to the last observed rate (the rules say the page
    shows rates as of Exophase's last refresh, so the last read is the best
    point estimate before the target);
  * is fully deterministic: no randomness, no clock, no network, no files
    beyond the case itself, so two runs are byte-identical.

The program reads every *.in in the input directory in name order and writes
<id>.out beside the output directory, exactly one row per trophy.
"""

import json
import math
import os
import statistics
from pathlib import Path

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]

# Standard normal quantiles for LEVELS, in that order. The pinball loss is
# minimised at the true quantile, so the five numbers have to sit at these
# exact probabilities. Python's statistics.NormalDist gives them without a
# lookup table: inv_cdf(0.5) is 0.0, inv_cdf(0.025) is -1.959964, and so on.
# LEVELS is fixed, so the five values are computed once at import.
NORMAL = statistics.NormalDist()
Z = [NORMAL.inv_cdf(q) for q in LEVELS]

# Random-walk logit spread per root-day. The house baseline uses 0.5; a launch
# week moves trophies far more than that, and the practice failure is exactly
# under-dispersion, so this is deliberately wider.
BASE_SIGMA = 1.1

# A trophy whose median rate is r% gets a spread multiplier of
# 1 + RARE_BOOST / sqrt(max(r, 0.05)) capped at RARE_CAP: a rare trophy (0.01%)
# can jump from near-zero to a few percent, which is several logit units, while
# a common trophy (60%) moves less in relative terms.
RARE_BOOST = 0.30
RARE_CAP = 3.2


def clamp(x):
    return min(99.99, max(0.01, x))


def logit(pct):
    """Percent to log-odds, clamped to the page's 0.01..99.99 range."""
    p = clamp(pct)
    return math.log(p / (100.0 - p))


def sigmoid(lg):
    """Log-odds back to a percent."""
    return 100.0 / (1.0 + math.exp(-lg))


def spread_for(med, base):
    """Logit sd for one trophy over the case's horizon.

    Rare trophies move further on the logit scale than common ones: 0.01% to
    1% is 4.6 logit units, 50% to 60% is 0.4. The boost scales with
    1/sqrt(rate) and is capped so a 0.01% bronze does not get an absurd band.
    """
    return base * min(RARE_CAP, 1.0 + RARE_BOOST / math.sqrt(max(med, 0.05)))


def ordered(qs):
    """Clamp to 0..100 and make the row non-decreasing.

    Rounding near the ends can invert a row (99.99 before 99.9917), and an
    inverted row invalidates the whole case, so the order is enforced after
    rounding rather than before.
    """
    qs = [min(100.0, max(0.0, float(q))) for q in qs]
    for k in range(1, len(qs)):
        if qs[k] < qs[k - 1]:
            qs[k] = qs[k - 1]
    return [round(float(q), 4) for q in qs]


def round4(x):
    """Round half-up to 4 decimals.

    Python's round() is banker's rounding, so round(0.00005, 4) is 0.0 and
    round(0.00015, 4) is 0.0002: the same distance rounds two ways depending
    on the digit before it. The board scores exact values, so the forecast
    should not inherit that coin flip.
    """
    scaled = x * 10000.0
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1.0
    return whole / 10000.0


def forecast_case(case):
    if case.get("levels") != LEVELS:
        raise ValueError(f"{case.get('id')}: levels {case.get('levels')} != {LEVELS}")
    history = case.get("history")
    if not history:
        raise ValueError(f"{case.get('id')}: no history")

    last = history[-1]
    rates = last["rates"]
    horizon_days = case["horizon_minutes"] / 1440.0

    # The spread of the logit move over the horizon. Rate changes compound, so
    # they grow with the square root of elapsed time; a 90-minute horizon is
    # 0.0625 of a root-day. The floor keeps a zero-minute case from collapsing
    # to a delta row.
    horizon_days = max(horizon_days, 1.0 / 1440.0)
    base = BASE_SIGMA * math.sqrt(horizon_days)

    rows = []
    for i, trophy in enumerate(case["trophies"]):
        rate = rates[i] if i < len(rates) else None
        if rate is None:
            # The last read lacked this trophy (it was added since): start from a
            # low prior with a very wide spread rather than from zero.
            med = 0.05
        else:
            med = clamp(rate)

        sigma = spread_for(med, base)
        med_lg = logit(med)
        # Five quantiles: the median row is the last rate itself (z = 0), the
        # tails walk out symmetrically on the logit scale, where the pinball
        # loss is scored.
        qs = ordered([round4(sigmoid(med_lg + z * sigma)) for z in Z])
        rows.append({"id": trophy["id"], "q": qs})
    return {"trophies": rows}


def main():
    """Write one <id>.out per case in the input directory, in name order.

    The grader runs this once per case with only that case's file present, so
    globbing the directory rather than naming cases keeps it correct for the
    practice pair and for the single final case alike.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()