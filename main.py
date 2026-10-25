from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from melbourne_cup import build_projection  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Educational Melbourne Cup 2026 projection")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "melbourne_cup_2026_candidates.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "outputs")
    return parser.parse_args()


def render_markdown(projection: pd.DataFrame) -> str:
    table = projection.copy()
    table["market"] = table["market_baseline_probability"].map(lambda value: f"{value:.2%}")
    table["scenario"] = table["educational_scenario_probability"].map(lambda value: f"{value:.2%}")
    rows = [
        "# Melbourne Cup 2026 — provisional educational projection",
        "",
        "Snapshot: 22 October 2026. Final field and barriers were not yet confirmed.",
        "This is a learning exercise, not betting advice.",
        "",
        "| Rank | Horse | Trainer | Weight | Odds | Market baseline | Educational scenario | Exempt |",
        "|---:|---|---|---:|---:|---:|---:|:---:|",
    ]
    for row in table.itertuples(index=False):
        rows.append(
            f"| {row.rank} | {row.horse} | {row.trainer} | {row.weight_kg:.1f}kg | "
            f"{row.current_decimal_odds:.0f} | {row.market} | {row.scenario} | "
            f"{'yes' if row.ballot_exempt else 'no'} |"
        )
    rows.extend(["", "See `METHODOLOGY.md` and `DISCLAIMER.md` before interpreting this table.", ""])
    return "\n".join(rows)


def main() -> int:
    args = parse_args()
    try:
        snapshot = pd.read_csv(args.input)
        projection = build_projection(snapshot)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = args.output_dir / "melbourne_cup_2026_projection.csv"
        markdown_path = args.output_dir / "melbourne_cup_2026_projection.md"
        projection.to_csv(csv_path, index=False)
        markdown_path.write_text(render_markdown(projection), encoding="utf-8")
        display = projection.head(10).copy()
        display["market_baseline_probability"] = display["market_baseline_probability"].map(lambda x: f"{x:.2%}")
        display["educational_scenario_probability"] = display["educational_scenario_probability"].map(lambda x: f"{x:.2%}")
        print(display[["rank", "horse", "market_baseline_probability", "educational_scenario_probability"]].to_string(index=False))
        print(f"\nSaved {csv_path}\nSaved {markdown_path}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

