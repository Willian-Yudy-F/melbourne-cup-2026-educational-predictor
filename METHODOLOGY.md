# Methodology and limitations

## Outputs

The project deliberately reports two distributions.

### Market baseline

For each tracked candidate, raw implied probability is `1 / decimal_odds`. Raw values
are divided by their total. This removes the aggregate margin within this snapshot,
but it is not a perfect fair-price estimate because this is an all-in market and the
final field is not known.

### Educational scenario

The scenario starts from the same raw implied probability, then applies bounded,
human-readable multipliers for carried weight, market movement and ballot exemption.
It is a sensitivity exercise, not a fitted machine-learning model.

## Major limitations

- Snapshot date: 22 October 2026; final field is due 31 October.
- The file tracks quoted contenders, not every nomination.
- All-in prices include the risk that a horse does not start.
- Barriers and most final jockey bookings were not available.
- Track condition and late veterinary information are absent.
- Market features can double-count public form information.
- No claim of profitability, accuracy or causal interpretation is made.

The correct production path is to acquire licensed historical race data, create
point-in-time features, split by race date, calibrate probabilities and evaluate with
log-loss, Brier score and ranking metrics before using the model prospectively.

