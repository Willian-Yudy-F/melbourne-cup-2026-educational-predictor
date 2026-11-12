from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from melbourne_cup.projection import (
    ProjectionConfig,
    ProjectionDataError,
    build_projection,
)


def sample() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"horse": "A", "trainer": "T1", "weight_kg": 52, "current_decimal_odds": 4, "previous_decimal_odds": 6, "ballot_exempt": True, "snapshot_at": "2026-10-22T01:06:00Z"},
            {"horse": "B", "trainer": "T2", "weight_kg": 56, "current_decimal_odds": 8, "previous_decimal_odds": 8, "ballot_exempt": False, "snapshot_at": "2026-10-22T01:06:00Z"},
        ]
    )


def test_probabilities_sum_to_one_and_rank_favourite_first() -> None:
    output = build_projection(sample())
    assert output["market_baseline_probability"].sum() == pytest.approx(1.0)
    assert output["educational_scenario_probability"].sum() == pytest.approx(1.0)
    assert output.iloc[0]["horse"] == "A"
    assert output.iloc[0]["scenario_fair_odds"] == pytest.approx(
        1 / output.iloc[0]["educational_scenario_probability"]
    )
    assert output.iloc[0]["minimum_odds_for_10pct_margin"] > output.iloc[0][
        "scenario_fair_odds"
    ]


def test_invalid_odds_are_rejected() -> None:
    frame = sample()
    frame.loc[0, "current_decimal_odds"] = 1.0
    with pytest.raises(ProjectionDataError, match="greater than 1"):
        build_projection(frame)


@pytest.mark.parametrize("column", ["horse", "trainer"])
def test_blank_text_fields_are_rejected(column: str) -> None:
    frame = sample()
    frame.loc[0, column] = "  "
    with pytest.raises(ProjectionDataError, match=f"{column} cannot be blank"):
        build_projection(frame)


def test_horse_names_are_unique_ignoring_case_and_whitespace() -> None:
    frame = sample()
    frame.loc[1, "horse"] = " a "
    with pytest.raises(ProjectionDataError, match="exactly once"):
        build_projection(frame)


def test_invalid_boolean_is_rejected() -> None:
    frame = sample()
    frame["ballot_exempt"] = frame["ballot_exempt"].astype(object)
    frame.loc[0, "ballot_exempt"] = "unknown"
    with pytest.raises(ProjectionDataError, match="true or false"):
        build_projection(frame)


def test_mixed_snapshot_times_are_rejected() -> None:
    frame = sample()
    frame.loc[1, "snapshot_at"] = "2026-10-23T01:06:00Z"
    with pytest.raises(ProjectionDataError, match="one point-in-time snapshot"):
        build_projection(frame)


def test_invalid_config_is_rejected() -> None:
    config = ProjectionConfig(movement_floor=1.2, movement_ceiling=1.1)
    with pytest.raises(ValueError, match="movement_ceiling"):
        build_projection(sample(), config)

