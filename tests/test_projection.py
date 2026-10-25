from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from melbourne_cup.projection import ProjectionDataError, build_projection


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


def test_invalid_odds_are_rejected() -> None:
    frame = sample()
    frame.loc[0, "current_decimal_odds"] = 1.0
    with pytest.raises(ProjectionDataError, match="greater than 1"):
        build_projection(frame)

