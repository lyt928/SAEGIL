from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


METRIC_KEYS = ("precision", "recall", "map50", "map50_95")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two experiment directories.")
    parser.add_argument("--baseline", required=True, help="Baseline experiment directory.")
    parser.add_argument("--candidate", required=True, help="Candidate experiment directory.")
    parser.add_argument("--output", default=None, help="Output directory. Defaults to the candidate directory.")
    return parser.parse_args()


def read_json(path: Path) -> dict | list:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_metric(value: object) -> float:
    if value is None:
        return 0.0
    return float(value)


def compare_overall_metrics(baseline: dict, candidate: dict) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for key in METRIC_KEYS:
        baseline_value = normalize_metric(baseline.get(key))
        candidate_value = normalize_metric(candidate.get(key))
        summary[key] = {
            "baseline": baseline_value,
            "candidate": candidate_value,
            "delta": candidate_value - baseline_value,
        }
    return summary


def compare_class_metrics(baseline_rows: list[dict], candidate_rows: list[dict]) -> list[dict]:
    baseline_map = {row["class_name"]: row for row in baseline_rows}
    candidate_map = {row["class_name"]: row for row in candidate_rows}
    class_names = sorted(set(baseline_map) | set(candidate_map))

    rows = []
    for class_name in class_names:
        baseline_row = baseline_map.get(class_name, {})
        candidate_row = candidate_map.get(class_name, {})
        row = {"class_name": class_name}
        for key in METRIC_KEYS:
            baseline_value = normalize_metric(baseline_row.get(key))
            candidate_value = normalize_metric(candidate_row.get(key))
            row[f"{key}_baseline"] = baseline_value
            row[f"{key}_candidate"] = candidate_value
            row[f"{key}_delta"] = candidate_value - baseline_value
        rows.append(row)
    return rows


def save_overall_plot(summary: dict[str, dict[str, float]], output_path: Path) -> None:
    labels = list(summary.keys())
    baseline_values = [summary[key]["baseline"] for key in labels]
    candidate_values = [summary[key]["candidate"] for key in labels]

    fig, ax = plt.subplots(figsize=(10, 6))
    positions = range(len(labels))
    width = 0.35
    ax.bar([position - width / 2 for position in positions], baseline_values, width=width, label="baseline")
    ax.bar([position + width / 2 for position in positions], candidate_values, width=width, label="candidate")
    ax.set_xticks(list(positions))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("score")
    ax.set_title("Overall Metric Comparison")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def save_class_map_plot(rows: list[dict], output_path: Path) -> None:
    if not rows:
        return

    labels = [row["class_name"] for row in rows]
    baseline_values = [row["map50_baseline"] for row in rows]
    candidate_values = [row["map50_candidate"] for row in rows]

    fig, ax = plt.subplots(figsize=(12, 6))
    positions = range(len(labels))
    width = 0.35
    ax.bar([position - width / 2 for position in positions], baseline_values, width=width, label="baseline")
    ax.bar([position + width / 2 for position in positions], candidate_values, width=width, label="candidate")
    ax.set_xticks(list(positions))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("mAP50")
    ax.set_title("Class Metric Comparison")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def write_markdown_report(
    baseline_dir: Path,
    candidate_dir: Path,
    overall_summary: dict[str, dict[str, float]],
    class_rows: list[dict],
    output_path: Path,
) -> None:
    lines = [
        "# Experiment Comparison",
        "",
        f"- baseline: `{baseline_dir.name}`",
        f"- candidate: `{candidate_dir.name}`",
        "",
        "## Overall Metrics",
        "",
        "| metric | baseline | candidate | delta |",
        "|---|---:|---:|---:|",
    ]
    for key, values in overall_summary.items():
        lines.append(
            f"| {key} | {values['baseline']:.4f} | {values['candidate']:.4f} | {values['delta']:+.4f} |"
        )

    if class_rows:
        lines.extend(
            [
                "",
                "## Class Metrics",
                "",
                "| class | map50 baseline | map50 candidate | delta |",
                "|---|---:|---:|---:|",
            ]
        )
        for row in class_rows:
            lines.append(
                f"| {row['class_name']} | {row['map50_baseline']:.4f} | {row['map50_candidate']:.4f} | {row['map50_delta']:+.4f} |"
            )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    baseline_dir = Path(args.baseline)
    candidate_dir = Path(args.candidate)
    output_dir = Path(args.output) if args.output else candidate_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_metrics = read_json(baseline_dir / "metrics.json")
    candidate_metrics = read_json(candidate_dir / "metrics.json")
    baseline_class_metrics = read_json(baseline_dir / "class_metrics.json")
    candidate_class_metrics = read_json(candidate_dir / "class_metrics.json")

    overall_summary = compare_overall_metrics(baseline_metrics, candidate_metrics)
    class_rows = compare_class_metrics(baseline_class_metrics, candidate_class_metrics)

    with (output_dir / "comparison_summary.json").open("w", encoding="utf-8") as file:
        json.dump(
            {
                "baseline": baseline_dir.name,
                "candidate": candidate_dir.name,
                "overall": overall_summary,
                "classes": class_rows,
            },
            file,
            ensure_ascii=False,
            indent=2,
        )

    save_overall_plot(overall_summary, output_dir / "comparison_overall.png")
    save_class_map_plot(class_rows, output_dir / "comparison_classes_map50.png")
    write_markdown_report(
        baseline_dir,
        candidate_dir,
        overall_summary,
        class_rows,
        output_dir / "comparison_report.md",
    )

    print(f"Comparison summary saved to: {output_dir}")


if __name__ == "__main__":
    main()
