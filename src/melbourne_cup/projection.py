from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "horse",
    "trainer",
    "weight_kg",
    "current_decimal_odds",
    "previous_decimal_odds",
    "ballot_exempt",
    "snapshot_at",
}


class ProjectionDataError(ValueError):
    """Raised when the input snapshot cannot support a valid projection."""


@dataclass(frozen=True)
class ProjectionConfig:
    weight_coefficient: float = 0.018
    movement_exponent: float = 0.15
    movement_floor: float = 0.85
    movement_ceiling: float = 1.15
    ballot_exempt_multiplier: float = 1.03


def validate_snapshot(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ProjectionDataError(f"Missing columns: {sorted(missing)}")
    result = frame.copy()
    if result.empty:
        raise ProjectionDataError("Snapshot is empty")
    if result["horse"].duplicated().any():
        raise ProjectionDataError("Every horse must appear exactly once")
    numeric = ["weight_kg", "current_decimal_odds", "previous_decimal_odds"]
    result[numeric] = result[numeric].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(result[numeric].to_numpy()).all():
        raise ProjectionDataError("Numeric values must be finite")
    if (result[["current_decimal_odds", "previous_decimal_odds"]] <= 1).any().any():
        raise ProjectionDataError("Decimal odds must be greater than 1")
    if not result["weight_kg"].between(45, 65).all():
        raise ProjectionDataError("Weights must be between 45kg and 65kg")
    result["ballot_exempt"] = result["ballot_exempt"].astype(str).str.lower().map(
        {"true": True, "false": False, "1": True, "0": False}
    )
    if result["ballot_exempt"].isna().any():
        raise ProjectionDataError("ballot_exempt must be true or false")
    result["snapshot_at"] = pd.to_datetime(result["snapshot_at"], utc=True, errors="raise")
    if result["snapshot_at"].nunique() != 1:
        raise ProjectionDataError("All rows must belong to one point-in-time snapshot")
    return result


def build_projection(
    snapshot: pd.DataFrame,
    config: ProjectionConfig = ProjectionConfig(),
) -> pd.DataFrame:
    """Return market and transparent educational scenario probabilities."""
    frame = validate_snapshot(snapshot)
    raw_market = 1.0 / frame["current_decimal_odds"]
    frame["market_baseline_probability"] = raw_market / raw_market.sum()

    mean_weight = float(frame["weight_kg"].mean())
    frame["weight_factor"] = np.exp(
        -config.weight_coefficient * (frame["weight_kg"] - mean_weight)
    )
    frame["market_movement_factor"] = (
        frame["previous_decimal_odds"] / frame["current_decimal_odds"]
    ).pow(config.movement_exponent).clip(config.movement_floor, config.movement_ceiling)
    frame["ballot_factor"] = np.where(
        frame["ballot_exempt"], config.ballot_exempt_multiplier, 1.0
    )
    raw_scenario = raw_market * frame["weight_factor"] * frame["market_movement_factor"] * frame["ballot_factor"]
    frame["educational_scenario_probability"] = raw_scenario / raw_scenario.sum()
    frame["rank"] = frame["educational_scenario_probability"].rank(
        method="first", ascending=False
    ).astype(int)
    columns = [
        "rank",
        "horse",
        "trainer",
        "weight_kg",
        "current_decimal_odds",
        "ballot_exempt",
        "market_baseline_probability",
        "educational_scenario_probability",
        "weight_factor",
        "market_movement_factor",
        "ballot_factor",
        "snapshot_at",
    ]
    return frame[columns].sort_values("rank").reset_index(drop=True)

