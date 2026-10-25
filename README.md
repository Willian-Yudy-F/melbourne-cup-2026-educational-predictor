# Melbourne Cup 2026 Educational Predictor

An English-language Python project that turns a dated public snapshot of Melbourne
Cup 2026 contenders and prices into reproducible, auditable probabilities.

> **This is a learning project, not betting advice.** Read
> [DISCLAIMER.md](DISCLAIMER.md). The final field of up to 24 runners and the barrier
> draw are due on 31 October 2026. This analysis uses a pre-final-field snapshot from
> 22 October 2026.

## Results

| Rank | Horse | Market baseline | Educational scenario | Scenario fair odds | Recorded odds | Expected return |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Point Of Law | 11.19% | **13.58%** | **$7.36** | $6 | **-18.5%** |
| 2 | James J Braddock | 6.11% | 5.98% | $16.73 | $11 | -34.2% |
| 3 | Trustyourinstinct | 6.11% | 5.76% | $17.37 | $11 | -36.7% |
| 4 | Defiantly | 6.11% | 5.56% | $17.98 | $11 | -38.8% |
| 5 | Saint George | 4.48% | 4.91% | $20.38 | $15 | -26.4% |
| 6 | Stinger Glass | 5.17% | 4.85% | $20.61 | $13 | -36.9% |
| 7 | Enfjaar | 4.48% | 4.82% | $20.75 | $15 | -27.7% |
| 8 | Shockletz | 4.48% | 4.72% | $21.17 | $15 | -29.1% |
| 9 | Aeliana | 4.48% | 3.74% | $26.70 | $15 | -43.8% |
| 10 | Zakouma | 3.73% | 3.68% | $27.16 | $18 | -33.7% |

The complete generated table is available in:

- [`outputs/melbourne_cup_2026_projection.csv`](outputs/melbourne_cup_2026_projection.csv)
- [`outputs/melbourne_cup_2026_projection.md`](outputs/melbourne_cup_2026_projection.md)

## Model selection and strategy

### Winner selection: Point Of Law

Point Of Law ranks first because the snapshot combines:

- the strongest recorded market price;
- a major move from $18 to $6;
- a low carried weight of 51kg;
- ballot exemption after winning the Geelong Cup.

### Strategy recommendation: no bet at $6

The educational scenario assigns Point Of Law a 13.58% win probability. Its reciprocal
is fair decimal odds of approximately $7.36. A $6 price is shorter than the model's fair
price:

```text
expected return = probability × decimal odds - 1
                = 0.1358 × 6 - 1
                = -0.185, or -18.5%
```

Therefore, the project selects Point Of Law as the most likely winner but does **not**
recommend a wager at the recorded price. The educational strategy is:

1. Wait for the final field, veterinary checks and barrier draw on 31 October.
2. Refresh prices and rerun the model.
3. Require the offered price to exceed model fair odds by a safety margin.
4. With a 10% margin, Point Of Law would require approximately $8.10 or higher.
5. If no runner clears its required price, record a **no-bet** decision.

This price discipline matters: selecting the most likely winner and finding a positive
expected-value price are different tasks.

## What we used

- Python 3.11+
- `pandas` for ingestion, validation and tabular outputs
- `numpy` for probability normalization
- `pytest` for integrity tests
- Git and GitHub for versioning and documentation
- Public information from the VRC, Racing Victoria and a dated market snapshot

This repository responsibly adapts the larger horse-racing prediction pipeline. We do
not apply an XGBoost model trained on synthetic data to real horses, because that would
create false precision. The repository keeps the production structure — dated snapshot,
validation, explicit features, inference and versioned outputs — while using a transparent
baseline until a licensed historical dataset is available.

## How it works

1. Store a point-in-time snapshot containing horse, trainer, weight, current price,
   previous price and ballot-exemption status.
2. Validate duplicates, missing values, odds and plausible weights.
3. Calculate `1 / decimal_odds` and normalize the values to form a market baseline.
4. Build an educational sensitivity scenario using deliberately small adjustments:
   - weight: `exp(-0.018 × (weight - average_weight))`;
   - price movement: `(previous_odds / current_odds)^0.15`, capped to `[0.85, 1.15]`;
   - ballot exemption: multiplier `1.03`.
5. Normalize the adjusted scores to 100%.
6. Calculate model fair odds, expected return at the recorded price and the price required
   for a 10% safety margin.
7. Export CSV and Markdown reports and test the invariants.

These coefficients are educational hypotheses, not learned parameters. The market
already incorporates some of this information, so double counting is possible. Both the
market baseline and adjusted scenario are reported to make that limitation visible.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
pytest -q
```

## Project structure

```text
data/                         versioned market snapshot
src/melbourne_cup/            validation and projection logic
outputs/                      generated result tables
tests/                        probability and validation tests
main.py                       command-line interface
METHODOLOGY.md                assumptions and limitations
DISCLAIMER.md                 educational-use disclaimer
```

## Sources and cutoff

- [Victoria Racing Club — 58 horses remain, 13 October 2026](https://www.vrc.com.au/latest-news/58-horses-remain-in-the-race-for-cup-glory/)
- [VRC — Point Of Law earns a Golden Ticket, 21 October 2026](https://www.vrc.com.au/latest-news/point-of-law-earns-golden-ticket-into-the-2026-lexus-melbourne-cup/)
- [Racing Victoria — Feature Race Conditions and Order of Entry](https://www.racingvictoria.com.au/racing/feature-race-conditions)
- [Race.com.au — recorded market and weights, 22 October 2026](https://race.com.au/melbourne-cup/)

Prices are volatile and were transcribed only for this exercise. The project has no
affiliation with these sources and does not automatically scrape betting websites.

## Next technical steps

- Refresh the dataset after final acceptances and the barrier draw on 31 October.
- Acquire properly licensed historical race results.
- Use year-based temporal validation and out-of-sample calibration.
- Add recent form, distance, track, jockey and handicap features without temporal leakage.
- Publish uncertainty intervals, Brier score, log-loss and a calibration report.

