import argparse
import json
import re
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def discover_route_files(output_dir: Path) -> List[Path]:
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    return sorted(output_dir.glob("*_routes.json"))


def load_routes(route_files: List[Path]) -> pd.DataFrame:
    records = []

    for file_path in route_files:
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        instance_name = payload.get(
            "instance_name",
            file_path.stem.replace("_routes", ""),
        )

        for route in payload.get("routes", []):
            records.append(
                {
                    "instance_name": instance_name,
                    "solver_name": route.get("solver_name", "Unknown"),
                    "total_distance_km": route.get("total_distance_km"),
                    "solve_time_seconds": route.get("solve_time_seconds"),
                    "optimality_gap_percent": route.get(
                        "optimality_gap_percent"
                    ),
                    "num_locations": route.get("num_locations"),
                    "source_file": str(file_path),
                }
            )

    if not records:
        raise ValueError(
            "No solver records found. Ensure JSON route files contain the 'routes' key."
        )

    df = pd.DataFrame.from_records(records)
    return df.sort_values(["instance_name", "solver_name"]).reset_index(drop=True)


def ensure_analysis_dir(base_output_dir: Path) -> Path:
    analysis_dir = base_output_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    return analysis_dir


def print_summary(df: pd.DataFrame) -> None:
    summary_columns = [
        "instance_name",
        "solver_name",
        "total_distance_km",
        "solve_time_seconds",
        "optimality_gap_percent",
        "num_locations",
    ]

    print("\n=== Solver Metrics by Instance ===")
    print(df[summary_columns].to_string(index=False))

    best_by_metric = {}
    for metric in ["total_distance_km", "solve_time_seconds", "optimality_gap_percent"]:
        idx = df.groupby("instance_name")[metric].idxmin()
        best_by_metric[metric] = df.loc[idx, ["instance_name", "solver_name", metric]]

    print("\n=== Best Solvers by Metric ===")
    for metric, metric_df in best_by_metric.items():
        print(f"\n-- {metric} --")
        print(metric_df.to_string(index=False))


def save_summary(df: pd.DataFrame, analysis_dir: Path) -> None:
    summary_csv = analysis_dir / "solver_metrics_summary.csv"

    grouped_frames: List[pd.DataFrame] = []
    for instance_name, instance_df in df.groupby("instance_name"):
        grouped_frames.append(instance_df)
        # Insert a blank separator row for readability
        blank_row = {column: None for column in df.columns}
        grouped_frames.append(pd.DataFrame([blank_row]))

    concatenated = pd.concat(grouped_frames, ignore_index=True)
    concatenated.to_csv(summary_csv, index=False)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s-]+", "_", value)
    return value


def render_charts(df: pd.DataFrame, analysis_dir: Path) -> None:
    sns.set_theme(style="whitegrid")
    metrics = [
        ("total_distance_km", "Total Distance (km)"),
        ("solve_time_seconds", "Solve Time (s)"),
        ("optimality_gap_percent", "Optimality Gap (%)"),
    ]

    for instance_name, instance_df in df.groupby("instance_name"):
        instance_slug = slugify(instance_name)
        instance_dir = analysis_dir / instance_slug
        instance_dir.mkdir(parents=True, exist_ok=True)

        for metric, label in metrics:
            plt.figure(figsize=(8, 5))
            sns.barplot(
                data=instance_df,
                x="solver_name",
                y=metric,
                palette="viridis",
            )
            plt.title(f"{label} - {instance_name}")
            plt.xlabel("Solver")
            plt.ylabel(label)
            plt.xticks(rotation=15, ha="right")
            plt.tight_layout()
            output_path = instance_dir / f"{metric}_comparison.png"
            plt.savefig(output_path, dpi=200)
            plt.close()


def analyze_routes(output_dir: Path) -> None:
    route_files = discover_route_files(output_dir)
    if not route_files:
        raise FileNotFoundError(
            f"No route files found in {output_dir}. Run solvers before analysis."
        )

    df = load_routes(route_files)
    analysis_dir = ensure_analysis_dir(output_dir)

    print_summary(df)
    save_summary(df, analysis_dir)
    render_charts(df, analysis_dir)

    print(f"\nSummary saved to: {analysis_dir / 'solver_metrics_summary.csv'}")
    print(f"Charts saved to: {analysis_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze solver outputs and visualize performance metrics."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
        help="Directory containing *_routes.json files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analyze_routes(args.output_dir)


if __name__ == "__main__":
    main()

