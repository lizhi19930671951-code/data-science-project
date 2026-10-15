"""Northern Hemisphere temperature anomalies, 1880–2018.

Exact reproduction: use the supplied course CSV snapshot. Alternatively,
download NASA's current table; revised observations may change the results.
"""
from pathlib import Path
import argparse
import hashlib
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def load_data(path):
    """Read either the teaching CSV or NASA's two-line-header CSV."""
    with path.open(encoding="utf-8-sig") as stream:
        first = stream.readline()
    frame = pd.read_csv(path, skiprows=0 if first.startswith("Year,") else 1,
                        na_values=["***", "****", "NA", "N/A"])
    frame.columns = frame.columns.str.strip()
    required = ["Year", *MONTHS]
    if not set(required).issubset(frame.columns):
        raise ValueError(f"Required columns: {required}")
    frame = frame[required].copy()
    frame["Year"] = pd.to_numeric(frame["Year"], errors="raise")
    if frame["Year"].isna().any() or (frame["Year"] % 1 != 0).any():
        raise ValueError("Years must be nonmissing integers")
    frame["Year"] = frame["Year"].astype(int)
    frame = frame.loc[frame.Year.between(1880, 2018)].sort_values("Year")
    if frame.Year.duplicated().any():
        raise ValueError("Duplicate years: resolve source data; do not silently average")
    if frame.Year.tolist() != list(range(1880, 2019)):
        raise ValueError("Expected all years 1880–2018, without gaps")
    for month in MONTHS:
        frame[month] = pd.to_numeric(frame[month], errors="raise")
    values = frame[MONTHS].to_numpy(dtype=float)
    if np.isinf(values).any():
        raise ValueError("Infinite anomaly values")
    return frame.set_index("Year")


def run(input_path, outdir):
    monthly = load_data(input_path)
    complete = monthly.notna().all(axis=1)
    # Equal weighting of the 12 monthly anomaly values; NOT NASA's published
    # annual J-D statistic, and NOT an absolute surface temperature.
    annual = monthly.mean(axis=1).where(complete)
    rolling = annual.rolling(window=10, min_periods=10).mean()
    earlier = annual.loc[1880:1909].dropna()
    later = annual.loc[1989:2018].dropna()
    if len(earlier) != 30 or len(later) != 30:
        raise ValueError("The comparison periods require 30 complete years each")
    outdir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook", font_scale=1.05)
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})

    fig, ax = plt.subplots(figsize=(13, 5.5), layout="constrained")
    limit = float(np.nanmax(np.abs(monthly.to_numpy())))
    sns.heatmap(monthly.T, ax=ax, cmap=sns.diverging_palette(240, 15, s=99, as_cmap=True),
                center=0, vmin=-limit, vmax=limit, xticklabels=False,
                cbar_kws={"label": "Temperature anomaly (°C)"})
    years = monthly.index.to_numpy()
    indices = np.flatnonzero(years % 10 == 0)
    ax.set_xticks(indices + .5, labels=years[indices], rotation=0)
    ax.set_yticklabels(MONTHS, rotation=0)
    ax.set(xlabel="Year", ylabel="Month", title="Northern Hemisphere monthly temperature anomalies, 1880–2018")
    fig.supxlabel("Baseline: 1951–1980 average • Teaching snapshot attributed to NASA GISS", fontsize=10)
    fig.savefig(outdir / "monthly_heatmap.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5.5), layout="constrained")
    ax.axhline(0, color="#52525b", linestyle="--", linewidth=1, label="1951–1980 baseline")
    ax.plot(annual.index, annual, color="#0072B2", alpha=.65, linewidth=1.3, label="Mean of 12 monthly anomalies")
    ax.plot(rolling.index, rolling, color="#D55E00", linewidth=2.7, label="10-year trailing mean")
    warm = int(annual.idxmax())
    ax.scatter([warm], [annual.loc[warm]], color="#111827", s=30, zorder=3)
    ax.annotate(f"{warm}: {annual.loc[warm]:.2f} °C", (warm, annual.loc[warm]),
                xytext=(-110, -18), textcoords="offset points", fontsize=10)
    ax.set(xlabel="Year", ylabel="Temperature anomaly (°C)",
           title="Long-term warming with year-to-year variability", xlim=(1878, 2021))
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    sns.despine(ax=ax)
    fig.supxlabel("Northern Hemisphere • 1880–2018 • Baseline: 1951–1980", fontsize=10)
    fig.savefig(outdir / "annual_trend.png", dpi=180)
    plt.close(fig)

    pd.DataFrame({"monthly_mean_anomaly_c": annual, "trailing_10yr_mean_c": rolling}).to_csv(outdir / "annual_summary.csv")
    metrics = {
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "years": len(monthly), "year_start": int(monthly.index.min()), "year_end": int(monthly.index.max()),
        "monthly_observations": int(monthly.size), "missing_monthly_values": int(monthly.isna().sum().sum()),
        "complete_years": int(complete.sum()), "early_period": "1880–1909", "early_mean_c": float(earlier.mean()),
        "recent_period": "1989–2018", "recent_mean_c": float(later.mean()),
        "period_difference_c": float(later.mean() - earlier.mean()),
        "warmest_year_monthly_mean": warm, "warmest_year_anomaly_c": float(annual.max()),
        "last_year_anomaly_c": float(annual.loc[2018]), "annual_method": "Unweighted mean of 12 complete monthly anomalies",
        "baseline": "1951–1980", "snapshot_warning": "Historical teaching snapshot; current NASA revisions may differ"
    }
    (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "northern_surface_temperature.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "figures")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error("Input not found. See README: supply the course CSV or run fetch_data.py.")
    run(args.input, args.output)


if __name__ == "__main__":
    main()
