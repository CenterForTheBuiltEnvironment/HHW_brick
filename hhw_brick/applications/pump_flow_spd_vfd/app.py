#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pump Differential Pressure Setpoint Tracking Analysis

Evaluates how well the secondary-loop pumps hold the end-of-line differential pressure (DP) at its
setpoint. Every operating point is classified with the signed relative error
e = (dp - dp_stpt) / dp_stpt as under-pressurised (e < -tol), within tolerance (|e| <= tol) or
over-pressurised (e > tol). Results are reported for the whole record, per flow bin and per pump
operating mode (pump 1 alone, pump 2 alone, both pumps). DP, DP setpoint and flow are loop-level
points shared by the pumps on the loop, so tracking is a property of the loop; pump speed, where
available, is only used to separate the operating modes. The DP setpoint is characterised as
single, stepwise (multiple stable values) or dynamically reset.

Author: SheltonXiao
"""

import sys
from contextlib import contextmanager
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import yaml
import argparse

# Setup paths
app_dir = Path(__file__).parent
package_dir = app_dir.parent.parent.parent
sys.path.insert(0, str(package_dir))

# Import universal utilities only
from hhw_brick.utils import (
    load_data,
    query_sensors,
    map_sensors_to_columns,
    extract_data_columns,
    filter_time_range,
)

# Export core user-facing functions
__all__ = ["qualify", "analyze", "load_config"]

SPEED_COLS = ["pmp1_spd", "pmp2_spd"]
CORE_COLS = ["dp", "dp_stpt", "flow"]
CLASSES = ["under", "within", "over"]


@contextmanager
def _plot_style():
    """Plot style used by the dashboard plots, applied locally so other apps are not restyled."""
    with plt.style.context("fivethirtyeight"), mpl.rc_context(
        {
            "figure.figsize": (4, 4),
            "figure.dpi": 150,
            "figure.facecolor": "white",
            "axes.grid": True,
            "font.size": 8,
            "grid.color": "lightgrey",
        }
    ):
        yield


def load_config(config_file=None):
    """Load configuration from YAML file"""
    # If no config file specified, use the default one in app directory
    if config_file is None:
        config_file = app_dir / "config.yaml"

    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please ensure config.yaml exists in the application directory."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config if config else {}


# ---------------------------------------------------------------------------
# Qualification (SPARQL)
# ---------------------------------------------------------------------------


def find_dp_flow_sensors(graph):
    """Find DP sensor, DP setpoint and flow sensor on the secondary loop (required), plus the
    supply / return water temperature sensors of that loop (optional, used for the loop load)."""
    query = """
    SELECT ?loop ?dp ?dp_stpt ?flow ?sup ?ret WHERE {
        ?loop rdf:type/rdfs:subClassOf* brick:Hot_Water_Loop .
        FILTER(CONTAINS(LCASE(STR(?loop)), "secondary"))

        ?loop brick:hasPart ?dp .
        ?dp rdf:type/rdfs:subClassOf* brick:Differential_Pressure_Sensor .

        ?loop brick:hasPart ?dp_stpt .
        ?dp_stpt rdf:type/rdfs:subClassOf* brick:Differential_Pressure_Setpoint .

        ?loop brick:hasPart ?flow .
        ?flow rdf:type/rdfs:subClassOf* brick:Flow_Sensor .

        OPTIONAL {
            ?loop brick:hasPart ?sup .
            ?sup rdf:type/rdfs:subClassOf* brick:Leaving_Hot_Water_Temperature_Sensor .
        }
        OPTIONAL {
            ?loop brick:hasPart ?ret .
            ?ret rdf:type/rdfs:subClassOf* brick:Entering_Hot_Water_Temperature_Sensor .
        }
    }
    """
    results = query_sensors(graph, [], custom_query=query)
    return results[0] if results else None


def find_pump_speed_sensors(graph, loop):
    """Find the speed command of each pump on the given loop, ordered by pump URI.

    Returns a list of distinct speed-command URIs (a generic speed point shared by all pumps
    appears once)."""
    query = f"""
    SELECT ?pump ?spd WHERE {{
        <{loop}> brick:hasPart ?pump .
        ?pump rdf:type/rdfs:subClassOf* brick:Pump .
        ?pump brick:hasPoint ?spd .
        ?spd rdf:type/rdfs:subClassOf* brick:Speed_Command .
    }}
    ORDER BY ?pump ?spd
    """
    results = query_sensors(graph, [], custom_query=query)
    speeds = []
    for _, spd in results:
        if str(spd) not in speeds:
            speeds.append(str(spd))
    return speeds


def find_enable_status(graph):
    """Find the operating status of the hot water system"""
    query = """
    SELECT ?oper WHERE {
        ?system rdf:type/rdfs:subClassOf* brick:Hot_Water_System .
        ?system brick:hasPart ?oper .
        ?oper rdf:type/rdfs:subClassOf* brick:Enable_Status .
    }
    """
    results = query_sensors(graph, [], custom_query=query)
    return results[0][0] if results else None


def find_oat_sensor(graph):
    """Find the outdoor air temperature sensor"""
    query = """
    SELECT ?wea_stat ?oat WHERE {
        ?wea_stat rdf:type/rdfs:subClassOf* brick:Weather_Station .
        ?wea_stat brick:hasPoint ?oat .
        ?oat rdf:type/rdfs:subClassOf* brick:Outside_Air_Temperature_Sensor .
    }
    """
    results = query_sensors(graph, [], custom_query=query)
    return results[0][1] if results else None


def qualify(brick_model_path):
    """Check if the building has the points required for the DP analysis.

    Required: DP sensor, DP setpoint and flow sensor on the secondary loop.
    Optional: pump speed commands (operating-mode split), system operating status (operating
    filter), supply / return temperature (loop load) and outdoor air temperature (setpoint reset).
    """
    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking DP, DP setpoint and flow on the secondary loop")
    print(f"{'='*60}\n")

    from rdflib import Graph

    g = Graph()
    g.parse(brick_model_path, format="turtle")

    result_basic = find_dp_flow_sensors(g)
    if not result_basic:
        print(f"[FAIL] Building NOT qualified")
        print(
            f"   Missing: differential pressure sensor, DP setpoint or flow sensor on the secondary loop\n"
        )
        return False, {}

    loop, dp, dp_stpt, flow, sup, ret = result_basic
    return_dic = {"loop": str(loop), "dp": str(dp), "dp_stpt": str(dp_stpt), "flow": str(flow)}
    print(f"[OK] Building qualified")
    print(f"   Secondary loop: {loop}")
    print(f"   End-of-line differential pressure: {dp}")
    print(f"   End-of-line differential pressure setpoint: {dp_stpt}")
    print(f"   Loop flow: {flow}")

    optional = {"sup": sup, "ret": ret}
    speeds = find_pump_speed_sensors(g, loop)
    for col, uri in zip(SPEED_COLS, speeds):
        optional[col] = uri
    optional["oper"] = find_enable_status(g)
    optional["oat"] = find_oat_sensor(g)

    labels = {
        "sup": "Supply water temperature",
        "ret": "Return water temperature",
        "pmp1_spd": "Pump 1 speed command",
        "pmp2_spd": "Pump 2 speed command",
        "oper": "System operating status",
        "oat": "Outdoor air temperature",
    }
    print(f"   Optional points:")
    for key, label in labels.items():
        uri = optional.get(key)
        if uri:
            return_dic[key] = str(uri)
        print(f"     {label}: {uri if uri else 'not found'}")
    if len(speeds) > len(SPEED_COLS):
        print(
            f"     Note: {len(speeds)} pump speed points found, the first {len(SPEED_COLS)} are used"
        )
    print()
    return True, return_dic


# ---------------------------------------------------------------------------
# Data cleaning
# ---------------------------------------------------------------------------


def _clean_ts_by_second_diff(
    se: pd.Series, threshold: str = None, mad_k: float = 5, iqr_k: float = 1.5
) -> pd.Series:
    """Remove spikes whose second difference exceeds a threshold.
    Args:
        se (pd.Series): Time series data with datetime index.
        threshold (str, optional): "iqr" for an IQR threshold, None for a MAD threshold.
        mad_k (float, optional): Multiplier for the MAD threshold. Defaults to 5.
        iqr_k (float, optional): Multiplier for the IQR threshold. Defaults to 1.5.
    Returns:
        pd.Series: Series with spikes set to NaN.
    """
    full_idx = pd.date_range(
        se.index.min(), se.index.max(), freq=se.index.to_series().diff().median()
    )
    s = se.reindex(full_idx)
    second_diff = s.shift(-1) - 2 * s + s.shift(1)
    if threshold is not None and threshold.lower() == "iqr":
        q1 = second_diff.quantile(0.25)
        q3 = second_diff.quantile(0.75)
        thr = iqr_k * (q3 - q1)
    else:
        med = second_diff.median()
        mad = (second_diff - med).abs().median()
        thr = mad_k * (mad if mad > 0 else second_diff.abs().median() + 1e-12)

    anomaly = (second_diff.abs() > thr).fillna(False)
    s[anomaly] = np.nan
    return s[se.index]


def _anomaly_iqr(a: pd.Series, k: float = 1.5) -> pd.Series:
    """Flag values outside [Q1 - k*IQR, Q3 + k*IQR]."""
    q1 = a.quantile(0.25)
    q3 = a.quantile(0.75)
    iqr = q3 - q1
    return ((a > q3 + k * iqr) | (a < q1 - k * iqr)).fillna(False)


def _data_preprocessing(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Select and clean the DP operating points.

    Rows are selected on DP, DP setpoint and flow only:
      1. keep operating periods (oper > 0) when the operating status is available;
      2. drop rows missing DP, DP setpoint or flow;
      3. remove DP outliers (IQR rule on the values, then on their second differences);
      4. keep positive DP, flow and DP setpoint.
    Optional columns (pump speed, temperatures) are attached afterwards and may be NaN, so a
    missing optional value never removes a DP row.
    """
    analysis = config["analysis"]
    if "oper" in df.columns:
        df = df[df["oper"] > 0]

    core = df[CORE_COLS].dropna(how="any", axis=0)
    core = core[~_anomaly_iqr(core["dp"], k=analysis.get("dp_outlier_iqr_k", 2.0))]
    core["dp"] = _clean_ts_by_second_diff(
        core["dp"], threshold="iqr", iqr_k=analysis.get("dp_spike_iqr_k", 1.5)
    )
    core = core.dropna(how="any", axis=0)
    core = core[(core["dp"] > 0) & (core["flow"] > 0)]
    core = core[core["dp_stpt"] > 0]

    optional = [c for c in df.columns if c not in CORE_COLS]
    return core.join(df[optional], how="left")


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def classify_tracking(df: pd.DataFrame, threshold: float = 0.10) -> pd.DataFrame:
    """Add the signed relative error and the tracking class of every operating point.

    err_rel = (dp - dp_stpt) / dp_stpt; class "under" if err_rel < -threshold, "over" if
    err_rel > threshold, otherwise "within" (two-sided band |dp - dp_stpt| <= threshold * dp_stpt).
    """
    df = df.copy()
    df["err_rel"] = (df["dp"] - df["dp_stpt"]) / df["dp_stpt"]
    df["cls"] = np.where(
        df["err_rel"] > threshold, "over", np.where(df["err_rel"] < -threshold, "under", "within")
    )
    df["meet_flag"] = df["cls"] == "within"
    return df


def add_operating_mode(df: pd.DataFrame) -> pd.DataFrame:
    """Add the pump operating mode of every point (a pump runs when its speed is > 0).

    Two speed points: "P1 only", "P2 only", "both" or "none"; one speed point: "single" or
    "none"; no speed point: "all"."""
    df = df.copy()
    spd_cols = [c for c in SPEED_COLS if c in df.columns]
    run = {c: df[c].fillna(0) > 0 for c in spd_cols}
    if len(spd_cols) == 2:
        p1, p2 = run["pmp1_spd"], run["pmp2_spd"]
        df["mode"] = np.select([p1 & p2, p1, p2], ["both", "P1 only", "P2 only"], default="none")
    elif len(spd_cols) == 1:
        df["mode"] = np.where(run[spd_cols[0]], "single", "none")
    else:
        df["mode"] = "all"
    return df


def _class_shares(group: pd.DataFrame) -> dict:
    n = len(group)
    shares = group["cls"].value_counts(normalize=True) if n else pd.Series(dtype=float)
    out = {"point_count": n}
    for c in CLASSES:
        out[f"{c}_ratio"] = float(shares.get(c, 0.0)) if n else np.nan
    out["median_err_rel"] = float(group["err_rel"].median()) if n else np.nan
    return out


def tracking_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Shares of under / within / over points for the whole record and per operating mode."""
    rows = [{"scope": "all points", **_class_shares(df)}]
    for mode in ["P1 only", "P2 only", "both", "single", "none"]:
        sub = df[df["mode"] == mode]
        if len(sub):
            rows.append({"scope": mode, **_class_shares(sub)})
    return pd.DataFrame(rows)


def meet_setpoint_percentage_flow(
    df: pd.DataFrame, flow_bins: int = 10, high_speed: float = 0.95
) -> pd.DataFrame:
    """Tracking by flow bin (equal-width bins between the minimum and maximum flow).

    Per bin: share of all points, the under / within / over shares and the median signed error;
    for each pump speed point, the points with that pump running, their within share
    ({spd}_meet_setpoint) and speed statistics.
    """
    df = df.copy()
    df["flow_bin"] = pd.cut(df["flow"], flow_bins, labels=False)
    edges = np.linspace(df["flow"].min(), df["flow"].max(), flow_bins + 1)
    spd_cols = [c for c in SPEED_COLS if c in df.columns]

    rows = []
    for b in range(flow_bins):
        group = df[df["flow_bin"] == b]
        row = {
            "flow_bin": b,
            "flow_bin_start": edges[b],
            "flow_bin_end": edges[b + 1],
            "flow_bin_medium": (edges[b] + edges[b + 1]) / 2,
            "flow_bin_ratio": len(group) / len(df) if len(df) else np.nan,
        }
        row.update(_class_shares(group))
        row["meet_setpoint_ratio"] = row["within_ratio"]
        for g_q, name in ((0.25, "q1_err_rel"), (0.75, "q3_err_rel")):
            row[name] = float(group["err_rel"].quantile(g_q)) if len(group) else np.nan
        for spd in spd_cols:
            running = group[group[spd].fillna(0) > 0]
            row[f"{spd}_point_count"] = len(running)
            row[f"{spd}_meet_setpoint"] = running["meet_flag"].mean() if len(running) else np.nan
            row[f"{spd}_mean"] = running[spd].mean() if len(running) else np.nan
            row[f"{spd}_95"] = running[spd].quantile(0.95) if len(running) else np.nan
            row[f"{spd}_95ratio"] = (running[spd] >= high_speed).mean() if len(running) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def meet_setpoint_percentage_setpoint(df: pd.DataFrame) -> pd.DataFrame:
    """Tracking per DP setpoint value: share of points and under / within / over shares."""
    rows = []
    for setpoint, group in df.groupby("dp_stpt"):
        row = {"setpoint": setpoint, "setpoint_bin_ratio": len(group) / len(df)}
        row.update(_class_shares(group))
        row["meet_setpoint_ratio"] = row["within_ratio"]
        rows.append(row)
    return pd.DataFrame(rows)


def cal_stpt_relationship(
    df: pd.DataFrame,
    min_ratio_threshold: float = 0.05,
    dynamic_coverage_threshold: float = 0.95,
    min_points: int = 30,
) -> dict:
    """Characterise the DP setpoint.

    A setpoint value is stable if it holds at least `min_ratio_threshold` of the operating points.
    The setpoint is "dynamic" if the stable values together cover less than
    `dynamic_coverage_threshold` of the points, otherwise "single" (one stable value) or
    "multiple stable (step)". For the non-stable values, the Spearman correlation with outdoor air
    temperature and with the loop load ((sup - ret) * flow * 4.18, kW) is computed when at least
    `min_points` complete pairs exist (NaN otherwise).
    """
    metric = dict()
    ratio = df["dp_stpt"].value_counts(normalize=True).sort_index()
    stable_setpoints = ratio[ratio >= min_ratio_threshold].index.tolist()
    coverage = float(ratio[stable_setpoints].sum())
    metric["n_unique_setpoints"] = int(ratio.size)
    metric["stable_setpoints_count"] = len(stable_setpoints)
    metric["stable_setpoints_ratio"] = coverage
    metric["stable_setpoints_list"] = stable_setpoints
    if coverage < dynamic_coverage_threshold:
        metric["setpoint_class"] = "dynamic"
    elif len(stable_setpoints) == 1:
        metric["setpoint_class"] = "single"
    else:
        metric["setpoint_class"] = "multiple stable (step)"

    sub = df[~df["dp_stpt"].isin(stable_setpoints)].copy()
    metric["n_non_stable"] = len(sub)
    if {"sup", "ret"}.issubset(sub.columns):
        sub["load"] = (sub["sup"] - sub["ret"]) * sub["flow"] * 4.18  # kW
    for key, col in (("spearman_oat", "oat"), ("spearman_load", "load")):
        pairs = sub[["dp_stpt", col]].dropna() if col in sub.columns else pd.DataFrame()
        metric[key] = (
            pairs["dp_stpt"].corr(pairs[col], method="spearman")
            if len(pairs) >= min_points
            else np.nan
        )
    return metric


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------


def analyze(brick_model_path, timeseries_data_path, config):
    """Execute the analysis workflow"""
    analysis = config["analysis"]

    # Step 1: Qualify
    qualified, qualify_result = qualify(brick_model_path)
    if not qualified:
        return None

    # Step 2: Load data
    print(f"{'='*60}")
    print(f"FETCH: Loading data")
    print(f"{'='*60}\n")

    g, df = load_data(brick_model_path, timeseries_data_path)
    time_range = config.get("time_range") or {}
    df = filter_time_range(df, time_range.get("start_time"), time_range.get("end_time"))
    print(f"[OK] Loaded {len(df)} data points")
    print(f"[OK] Time range: {df.index.min()} to {df.index.max()}\n")

    # Map sensors to data columns
    names = [
        k
        for k in ["dp", "dp_stpt", "flow", "sup", "ret", "pmp1_spd", "pmp2_spd", "oper", "oat"]
        if k in qualify_result
    ]
    uris = [qualify_result[k] for k in names]
    sensor_mapping = map_sensors_to_columns(g, uris, df)
    missing = [k for k in CORE_COLS if qualify_result[k] not in sensor_mapping]
    if missing:
        print(f"[FAIL] No data column found for: {', '.join(missing)}\n")
        return None
    rename_map = {qualify_result[k]: k for k in names}
    df_extracted = extract_data_columns(df, sensor_mapping, rename_map=rename_map)

    # Clean data
    df_cleaned = _data_preprocessing(df_extracted, config)
    print(f"[OK] Data after cleaning has {len(df_cleaned)} data points\n")
    if df_cleaned.empty:
        print("[FAIL] No operating points left after cleaning\n")
        return None

    # Step 3: Analyze
    print(f"{'='*60}")
    print(f"ANALYZE: DP setpoint tracking")
    print(f"{'='*60}\n")

    tol = analysis["sept_threshold"]
    df_cleaned = add_operating_mode(classify_tracking(df_cleaned, tol))
    summary = tracking_summary(df_cleaned)
    flow_bin_df = meet_setpoint_percentage_flow(
        df_cleaned, analysis["flow_bins"], analysis.get("high_speed_threshold", 0.95)
    )
    setpoint_bin_df = meet_setpoint_percentage_setpoint(df_cleaned)
    dp_metric = cal_stpt_relationship(
        df_cleaned,
        analysis["stable_setpoint_ratio_threshold"],
        analysis.get("dynamic_setpoint_coverage_threshold", 0.95),
        analysis.get("min_correlation_points", 30),
    )

    print(f"DP setpoint tracking (tolerance ±{tol:.0%}):")
    for _, r in summary.iterrows():
        print(
            f"  {r['scope']:<11} n={int(r['point_count']):>7}  within {r['within_ratio']:.1%}  "
            f"over {r['over_ratio']:.1%}  under {r['under_ratio']:.1%}"
        )
    print(f"\nDP setpoint characteristics:")
    print(
        f"  Stable setpoints (>= {analysis['stable_setpoint_ratio_threshold']:.0%} of points): "
        f"{dp_metric['stable_setpoints_count']} {dp_metric['stable_setpoints_list']}"
    )
    print(
        f"  Stable-setpoint coverage: {dp_metric['stable_setpoints_ratio']:.1%} -> {dp_metric['setpoint_class']}"
    )
    print(
        f"  Spearman (non-stable setpoints) vs outdoor air temperature: {dp_metric['spearman_oat']:.3f}, "
        f"vs loop load: {dp_metric['spearman_load']:.3f}"
    )

    results = {
        "df": df_cleaned,
        "summary": summary,
        "flow_bin_analysis": flow_bin_df,
        "overall_ratio": float(summary.iloc[0]["within_ratio"]),
        "setpoint_bin_analysis": setpoint_bin_df,
        "qualify_result": qualify_result,
    }
    results.update(dp_metric)

    # Step 4: Output
    if config["output"]["save_results"]:
        save_results(results, config)

    if config["output"]["generate_plots"]:
        generate_plots(results, config)

    return results


def _export(df, path, export_format):
    if export_format == "csv":
        df.to_csv(path, index=False)
    else:  # json
        df.to_json(path, orient="records", indent=2)
    print(f"  [OK] {path.name}")


def save_results(results, config):
    """Save analysis results"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    export_format = config["output"]["export_format"]

    print(f"\n{'='*60}")
    print(f"OUTPUT: Saving results to {output_dir}")
    print(f"{'='*60}\n")

    _export(
        results["summary"], output_dir / f"pump_dp_tracking_summary.{export_format}", export_format
    )
    _export(
        results["flow_bin_analysis"],
        output_dir / f"pump_dp_flow_bin.{export_format}",
        export_format,
    )
    _export(
        results["setpoint_bin_analysis"],
        output_dir / f"pump_dp_setpoint_bin.{export_format}",
        export_format,
    )
    keys = [
        "n_unique_setpoints",
        "stable_setpoints_count",
        "stable_setpoints_ratio",
        "setpoint_class",
        "n_non_stable",
        "spearman_oat",
        "spearman_load",
    ]
    setpoint = {k: results[k] for k in keys}
    setpoint["stable_setpoints_list"] = "; ".join(
        f"{v:g}" for v in results["stable_setpoints_list"]
    )
    _export(
        pd.DataFrame([setpoint]),
        output_dir / f"pump_dp_setpoint_characteristics.{export_format}",
        export_format,
    )


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------


def _plot_pump_speed_ax(
    df, speed_col, ax, high_speed=0.95, flow_col="flow", meet_col="meet_flag", total_ratio=None
):
    """Row 2: scatter of flow vs pump speed, coloured by setpoint compliance"""
    colors = df[meet_col].map({True: "gray", False: "red"})
    ax.scatter(df[flow_col], df[speed_col], c=colors, s=8, alpha=0.7, edgecolor="none")
    ax.plot([], [], color="gray", marker="o", linestyle="None", label="Compliant with setpoint")
    ax.plot([], [], color="red", marker="o", linestyle="None", label="Non-compliant with setpoint")
    ax.axhline(
        high_speed, color="coral", linestyle="--", linewidth=2, label=f"Speed = {high_speed:.0%}"
    )
    ax.legend(loc="lower right", fontsize=8)

    ax.set_ylabel("Pump Speed (-)")
    ax.set_ylim(0, 1.05)
    if total_ratio is not None:
        ax.text(
            0.60,
            0.40,
            f"Overall compliance ratio: {total_ratio:.1%}",
            transform=ax.transAxes,
            fontsize=10,
            va="center",
        )
    ax.grid(True, linestyle="--", alpha=0.3)


def _plot_flow_bin_performance_ax(flow_bin_df, speed_col, ax):
    """Row 3: bin-level compliance ratio vs flow, colour = share of points at high speed"""
    cmap_points = [0, 0.2, 0.5, 1.0]
    cmap_colors = ["darkgreen", "yellow", "red", "firebrick"]
    custom_cmap = mcolors.LinearSegmentedColormap.from_list(
        "custom_cmap", list(zip(cmap_points, cmap_colors))
    )

    sc = ax.scatter(
        flow_bin_df["flow_bin_medium"],
        flow_bin_df[f"{speed_col}_meet_setpoint"],
        c=flow_bin_df[f"{speed_col}_95ratio"],
        s=flow_bin_df[f"{speed_col}_point_count"] * 0.5,
        cmap=custom_cmap,
        vmin=0,
        vmax=1,
        alpha=0.8,
        edgecolor="k",
        linewidth=0.5,
    )
    ax.set_ylabel("Compliance Ratio (-)")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.3)
    return sc  # handle for the colour bar


def plot_flow_analysis(
    flow_df, flow_bin_df, speed_cols, config, overall_ratios=None, pump_labels=None
):
    """Dashboard plot, 3 rows x N pumps (columns), each column using the points where that pump runs:
    Row 1: point count per flow bin
    Row 2: flow vs pump speed scatter
    Row 3: bin-level compliance ratio + colour bar
    """
    output_dir = Path(config["output"]["output_dir"])
    plot_format = config["output"]["plot_format"]
    high_speed = config["analysis"].get("high_speed_threshold", 0.95)

    if isinstance(speed_cols, str):
        speed_cols = [speed_cols]
    n_pumps = len(speed_cols)
    if pump_labels is None:
        pump_labels = speed_cols
    if overall_ratios is None:
        overall_ratios = [
            flow_df.loc[flow_df[c].fillna(0) > 0, "meet_flag"].mean() for c in speed_cols
        ]

    with _plot_style():
        fig, axes = plt.subplots(
            3,
            n_pumps,
            figsize=(10 + 4 * (n_pumps - 1), 11.5),
            sharex="col",
            gridspec_kw={"height_ratios": [1.1, 2.8, 1.8]},
            dpi=300,
            squeeze=False,
        )
        fig.patch.set_facecolor("white")
        title = "Pump flow performance dashboard – " + " vs ".join(pump_labels)
        fig.suptitle(title, fontsize=14, fontweight="bold", y=0.97)

        edges = sorted(
            set(flow_bin_df["flow_bin_start"].tolist()) | set(flow_bin_df["flow_bin_end"].tolist())
        )

        for j, (spd_col, ratio, label) in enumerate(zip(speed_cols, overall_ratios, pump_labels)):
            ax1, ax2, ax3 = axes[0, j], axes[1, j], axes[2, j]
            for ax in (ax1, ax2, ax3):
                ax.set_facecolor("white")
                for spine in ax.spines.values():
                    spine.set_visible(False)

            # 1) Point count
            ax1.bar(
                flow_bin_df["flow_bin_medium"],
                flow_bin_df[f"{spd_col}_point_count"],
                width=(flow_bin_df["flow_bin_end"] - flow_bin_df["flow_bin_start"]),
                color="#8fb6d9",
                edgecolor="#2f2f2f",
                linewidth=0.8,
            )
            ax1.set_ylabel("Point Count")
            ax1.set_title(f"Point count per flow bin – {label}", pad=6)
            ax1.grid(True, linestyle="--", alpha=0.3)

            for edge in edges:
                for ax in (ax1, ax2, ax3):
                    ax.axvline(edge, color="lightgray", linestyle=":", linewidth=1)

            # 2) Flow vs speed, points with this pump running
            running = flow_df[flow_df[spd_col].fillna(0) > 0]
            _plot_pump_speed_ax(running, spd_col, ax=ax2, high_speed=high_speed, total_ratio=ratio)
            ax2.set_title(f"Sample points: {label} speed vs flow", pad=6)
            ax2.text(0.02, 0.23, "Compliance ratio of every flow bin:", fontsize=8)
            for _, row in flow_bin_df.iterrows():
                value = row[f"{spd_col}_meet_setpoint"]
                if pd.notna(value):
                    ax2.text(
                        row["flow_bin_medium"],
                        0.17,
                        f"{value * 100:.1f}%",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )

            # 3) Bin-level compliance ratio
            sc = _plot_flow_bin_performance_ax(flow_bin_df, spd_col, ax=ax3)
            ax3.set_title(f"Bin-level compliance ratio vs flow – {label}", pad=6)
            ax3.set_xticks(edges)
            ax3.set_xticklabels([f"{x:.1f}" for x in edges])
            for ax in (ax1, ax2, ax3):
                ax.set_xlabel("Flow (L/s)")
                ax.tick_params(axis="x", labelbottom=True)

            # colour bar
            bbox = ax3.get_position()
            cbar_width = bbox.width * 0.6
            cbar_ax = fig.add_axes(
                [bbox.x0 + (bbox.width - cbar_width) / 2, bbox.y0 - 0.06, cbar_width, 0.018]
            )
            cbar = fig.colorbar(sc, cax=cbar_ax, orientation="horizontal")
            cbar.set_label(f"{label} speed ≥ {high_speed:.0%} ratio", fontsize=10)

        plt.subplots_adjust(top=0.92, bottom=0.08, hspace=0.22)
        filepath = output_dir / f"flow_bin.{plot_format}"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"  [OK] {filepath.name}")


def plot_dp_setpoint_change(df, metric, config):
    """Time series of DP and DP setpoint, and the histogram of the DP setpoint with the stable values"""
    output_dir = Path(config["output"]["output_dir"])
    plot_format = config["output"]["plot_format"]

    with _plot_style():
        fig, ax = plt.subplots(1, 2, figsize=(12, 4), width_ratios=[2, 1])
        ax[0].plot(
            df.index,
            df["dp"],
            linestyle="None",
            marker=".",
            markersize=2,
            alpha=0.5,
            label="Δp (measured)",
        )
        ax[0].plot(
            df.index,
            df["dp_stpt"],
            marker=".",
            linestyle="-",
            linewidth=1.0,
            alpha=0.4,
            label="Δp setpoint",
        )

        start_month = df.index.min().month
        major_months = sorted({(start_month - 1 + 6 * i) % 12 + 1 for i in range(2)})
        ax[0].set_title("Time series of Δp and Δp setpoint")
        ax[0].set_xlabel("Time")
        ax[0].set_ylabel("End-of-Line differential pressure (Pa)")
        ax[0].xaxis.set_major_locator(mdates.MonthLocator(bymonth=major_months))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax[0].xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
        ax[0].grid(True, which="minor", linestyle="--", alpha=0.5)
        ax[0].tick_params(axis="x", labelrotation=15)
        ax[0].legend()

        weights = np.ones_like(df["dp_stpt"]) / len(df["dp_stpt"])
        stable = metric["stable_setpoints_list"]
        if metric["stable_setpoints_count"] == 1:
            hist_range = (stable[0] * 0.85, stable[0] * 1.15)
        else:
            hist_range = (df["dp_stpt"].min() * 0.85, df["dp_stpt"].max() * 1.15)
        df["dp_stpt"].hist(bins=50, ax=ax[1], weights=weights, range=hist_range)
        ax[1].set_title("Histogram of Δp setpoint")
        ax[1].set_xlabel("End-of-Line differential pressure (Pa)")
        ax[1].set_ylabel("Fraction")
        ax[1].tick_params(axis="x", labelrotation=15)
        ymin, ymax = ax[1].get_ylim()
        ax[1].set_ylim(0, ymax * 1.25)
        for i, sp in enumerate(stable):
            ax[1].axvline(
                sp,
                color="red",
                linestyle="--",
                linewidth=1.5,
                alpha=0.8,
                label="Stable setpoints" if i == 0 else None,
            )
        ax[1].plot(
            [], [], " ", label=f"Stable setpoints ratio: {metric['stable_setpoints_ratio']:.1%}"
        )
        ax[1].plot([], [], " ", label=f"Setpoint: {metric['setpoint_class']}")
        ax[1].legend(loc="upper right")
        fig.suptitle("Δp and Δp setpoint reset analysis", fontsize=14, fontweight="bold", y=0.97)
        plt.tight_layout()
        filepath = output_dir / f"sp_setpoint_change.{plot_format}"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"  [OK] {filepath.name}")


def plot_setpoint_correlation_analysis(df, metric, config):
    """Non-stable DP setpoint values vs outdoor air temperature and vs loop load"""
    output_dir = Path(config["output"]["output_dir"])
    plot_format = config["output"]["plot_format"]

    df_sub = df[~df["dp_stpt"].isin(metric["stable_setpoints_list"])].copy()
    if {"sup", "ret"}.issubset(df_sub.columns):
        df_sub["load"] = (df_sub["sup"] - df_sub["ret"]) * df_sub["flow"] * 4.18  # kW
    panels = [
        (col, label, metric[key])
        for col, label, key in (
            ("oat", "Outdoor temperature (°C)", "spearman_oat"),
            ("load", "Load (kW)", "spearman_load"),
        )
        if col in df_sub.columns and pd.notna(metric[key])
    ]
    if not panels:
        print(
            "  [SKIP] sp_setpoint_corr: not enough non-stable setpoint points with temperature or load data"
        )
        return

    with _plot_style():
        fig, ax = plt.subplots(1, len(panels), figsize=(4 * len(panels), 4), squeeze=False)
        for a, (col, label, rho) in zip(ax[0], panels):
            a.scatter(df_sub["dp_stpt"], df_sub[col], s=2)
            a.text(0.3, 0.8, f"Spearman corr: {rho:.2f}", transform=a.transAxes, fontsize=10)
            a.set_xlabel("End-of-line differential pressure setpoint (Pa)")
            a.set_ylabel(label)
        fig.suptitle("Δp setpoint correlation analysis", fontsize=14, fontweight="bold", y=0.97)
        plt.tight_layout()
        filepath = output_dir / f"sp_setpoint_corr.{plot_format}"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"  [OK] {filepath.name}")


def plot_dp_signed_error_grid(df, config):
    """Signed DP error by pump operating mode (3 rows x up to 3 columns).

    Rows: (a) point count per flow bin stacked by tracking class, (b) pump speed vs flow,
    (c) signed relative DP error (dp - dp_stpt) / dp_stpt vs flow with bin median and IQR.
    Columns: pump 1 running alone / pump 2 running alone / both pumps running (only modes with
    data are drawn; one "all points" column when no pump speed is available).
    Expects the columns added by classify_tracking and add_operating_mode.
    """
    output_dir = Path(config["output"]["output_dir"])
    plot_format = config["output"]["plot_format"]
    analysis = config["analysis"]
    tol = analysis["sept_threshold"]
    n_bins = analysis["flow_bins"]
    min_bin_points = analysis.get("min_bin_points", 30)
    high_speed = analysis.get("high_speed_threshold", 0.95)
    c_under, c_over, c_within = "#2a78d6", "#e34948", "#a8a79f"
    ink, ink2, grid_c = "#1f1f1d", "#5f5e58", "#e6e5e0"
    classes = [
        ("under", c_under, f"Under-pressurised (Δp < {1 - tol:.2g}·Δp$_{{set}}$)"),
        ("within", c_within, f"Within ±{tol:.0%} of Δp$_{{set}}$"),
        ("over", c_over, f"Over-pressurised (Δp > {1 + tol:.2g}·Δp$_{{set}}$)"),
    ]

    d = df.copy()
    d["err_pct"] = d["err_rel"] * 100
    edges = np.linspace(d["flow"].min(), d["flow"].max(), n_bins + 1)
    d["fbin"] = pd.cut(d["flow"], n_bins, labels=False)
    centers = (edges[:-1] + edges[1:]) / 2
    width = edges[1] - edges[0]

    spd_cols = [c for c in SPEED_COLS if c in d.columns]
    if len(spd_cols) == 2:
        candidates = [
            ("P1 only", "pmp1_spd", "Pump 1 running alone"),
            ("P2 only", "pmp2_spd", "Pump 2 running alone"),
            ("both", "pmp1_spd", "Both pumps running"),
        ]
    elif len(spd_cols) == 1:
        candidates = [("single", spd_cols[0], "Pump running")]
    else:
        candidates = [("all", None, "All operating points (no pump speed data)")]
    cols = [m for m in candidates if (d["mode"] == m[0]).any()]
    n_none = int((d["mode"] == "none").sum())
    if spd_cols:
        speed_vals = pd.concat([d.loc[d["mode"] == m, s] for m, s, _ in cols])
        speed_floor = float(speed_vals.quantile(0.01)) if len(speed_vals) else np.nan
    else:
        speed_floor = np.nan

    span = edges[-1] - edges[0]
    xlim = (edges[0] - 0.02 * span, edges[-1] + 0.02 * span)
    lo, hi = np.nanpercentile(d["err_pct"], [0.5, 99.5])
    err_lim = (min(lo, -tol * 100) - 5, max(hi, tol * 100) + 5)
    clipped = int(((d["err_pct"] < err_lim[0]) | (d["err_pct"] > err_lim[1])).sum())

    with plt.style.context("default"), mpl.rc_context(
        {"font.size": 8, "axes.labelcolor": ink, "text.color": ink}
    ):
        ncol = len(cols)
        fig, axes = plt.subplots(
            3,
            ncol,
            figsize=(max(2.5 * ncol + 0.5, 6.0), 7.6),
            dpi=300,
            sharex=True,
            sharey="row",
            squeeze=False,
            gridspec_kw={"height_ratios": [1.0, 1.5, 1.5], "hspace": 0.18, "wspace": 0.08},
        )
        fig.patch.set_facecolor("white")
        count_max = 1
        for j, (mode, spd, name) in enumerate(cols):
            sub = d[d["mode"] == mode]
            a0, a1, a2 = axes[:, j]
            for ax in (a0, a1, a2):
                ax.set_facecolor("white")
                for s in ("top", "right"):
                    ax.spines[s].set_visible(False)
                for s in ("left", "bottom"):
                    ax.spines[s].set_color(ink2)
                ax.tick_params(colors=ink2, labelsize=7, length=3)
                ax.grid(axis="y", color=grid_c, linewidth=0.8)
                ax.set_axisbelow(True)
                for e in edges:
                    ax.axvline(e, color=grid_c, linewidth=0.6, zorder=0)
                ax.set_xlim(*xlim)
            bottom = np.zeros(n_bins)
            for key, color, label in classes:
                cnt = np.array(
                    [((sub["fbin"] == b) & (sub["cls"] == key)).sum() for b in range(n_bins)]
                )
                a0.bar(
                    centers,
                    cnt,
                    width=width * 0.9,
                    bottom=bottom,
                    color=color,
                    edgecolor="white",
                    linewidth=0.8,
                    label=label,
                )
                bottom += cnt
            count_max = max(count_max, bottom.max())
            sh = sub["cls"].value_counts(normalize=True)
            a0.set_title(
                f"{name} (n={len(sub)})\nwithin {sh.get('within', 0):.0%} · over {sh.get('over', 0):.0%} · "
                f"under {sh.get('under', 0):.0%}",
                fontsize=7,
                loc="left",
            )
            if spd is not None:
                for key, color, _ in classes:
                    s = sub[sub["cls"] == key]
                    a1.scatter(
                        s["flow"],
                        s[spd],
                        s=2.5,
                        color=color,
                        alpha=0.35,
                        linewidths=0,
                        rasterized=True,
                    )
                a1.axhline(high_speed, color=ink2, linestyle="--", linewidth=1.0)
                a1.axhline(speed_floor, color=ink2, linestyle=":", linewidth=1.0)
            else:
                a1.text(
                    0.5,
                    0.5,
                    "No pump speed points",
                    transform=a1.transAxes,
                    ha="center",
                    color=ink2,
                )
            a2.axhspan(-tol * 100, tol * 100, color="#f0efec", zorder=0)
            a2.axhline(0, color=ink2, linewidth=0.9)
            for key, color, _ in classes:
                s = sub[sub["cls"] == key]
                a2.scatter(
                    s["flow"],
                    s["err_pct"],
                    s=2.5,
                    color=color,
                    alpha=0.3,
                    linewidths=0,
                    rasterized=True,
                )
            stats = [
                (centers[b], g.median(), g.quantile(0.25), g.quantile(0.75))
                for b in range(n_bins)
                for g in [sub.loc[sub["fbin"] == b, "err_pct"]]
                if len(g) >= min_bin_points
            ]
            if stats:
                cx, med, q1, q3 = map(np.array, zip(*stats))
                a2.errorbar(
                    cx,
                    med,
                    yerr=[med - q1, q3 - med],
                    color=ink,
                    marker="o",
                    markersize=3,
                    linewidth=1.2,
                    capsize=2,
                    label=f"Bin median (IQR), bins with n ≥ {min_bin_points}",
                )
            a2.set_xlabel("Loop flow (L/s)")
            if j > 0:
                for ax in (a0, a1, a2):
                    ax.tick_params(axis="y", labelleft=False)
        axes[0, 0].set_ylim(0, count_max * 1.05)
        if not np.isnan(speed_floor):
            axes[1, 0].set_ylim(max(0, speed_floor - 0.12), 1.04)
        axes[2, 0].set_ylim(*err_lim)
        axes[0, 0].set_ylabel("Point count")
        axes[1, 0].set_ylabel("Pump speed (–)")
        axes[2, 0].set_ylabel("(Δp − Δp$_{set}$) / Δp$_{set}$ (%)")
        for i, t in enumerate(
            [
                "(a) Point count per flow bin, by tracking class",
                "(b) Pump speed vs flow",
                "(c) Signed DP error vs flow",
            ]
        ):
            axes[i, 0].annotate(
                t,
                xy=(0, 1),
                xycoords="axes fraction",
                xytext=(0, 26 if i == 0 else 4),
                textcoords="offset points",
                fontsize=8.5,
                fontweight="bold",
                va="bottom",
            )
        handles, labels = axes[0, 0].get_legend_handles_labels()
        h2, l2 = [], []
        for ax in axes[2, :]:
            h2, l2 = ax.get_legend_handles_labels()
            if h2:
                break
        fig.legend(
            handles + h2,
            labels + l2,
            loc="lower center",
            ncol=2,
            fontsize=7,
            frameon=False,
            bbox_to_anchor=(0.5, 0.0),
        )
        note = (
            ""
            if np.isnan(speed_floor)
            else f"Dashed: speed = {high_speed:.0%}; dotted: lowest observed speed (1st pct.) ≈ {speed_floor:.2f}, "
            "configured minimum not verified. "
        )
        note += f"Shaded: ±{tol:.0%} tolerance. DP, DP setpoint and flow are loop-level points."
        if clipped:
            note += f" {clipped} points outside the y-range of row (c) not shown."
        if n_none:
            note += f" {n_none} points with no pump speed > 0 not shown."
        fig.text(0.98, 0.075, note, ha="right", fontsize=6.3, color=ink2, wrap=True)
        fig.suptitle(
            "DP setpoint tracking by pump operating mode", fontsize=11, fontweight="bold", y=0.99
        )
        fig.subplots_adjust(top=0.865, bottom=0.15, left=0.1 if ncol > 1 else 0.13, right=0.98)
        filepath = output_dir / f"dp_signed_error_grid.{plot_format}"
        fig.savefig(filepath, dpi=300)
        plt.close(fig)
    print(f"  [OK] {filepath.name}")


def generate_plots(results, config):
    """Generate the visualisation plots"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Generating plots")
    print(f"{'='*60}\n")

    df = results["df"]
    metric = {
        k: results[k]
        for k in (
            "stable_setpoints_ratio",
            "stable_setpoints_list",
            "stable_setpoints_count",
            "setpoint_class",
            "spearman_oat",
            "spearman_load",
        )
    }

    # Plot 1: signed DP error by pump operating mode (main figure)
    plot_dp_signed_error_grid(df=df, config=config)

    # Plot 2: per-pump dashboard (only with pump speed data)
    speed_cols = [c for c in SPEED_COLS if c in df.columns]
    if speed_cols:
        plot_flow_analysis(
            flow_df=df,
            flow_bin_df=results["flow_bin_analysis"],
            speed_cols=speed_cols,
            config=config,
            pump_labels=[f"Pump {c[3]}" for c in speed_cols],
        )
    else:
        print("  [SKIP] flow_bin: no pump speed data")

    # Plot 3: DP and DP setpoint time series / setpoint histogram
    plot_dp_setpoint_change(df=df, metric=metric, config=config)

    # Plot 4: setpoint correlation with outdoor air temperature and loop load
    plot_setpoint_correlation_analysis(df=df, metric=metric, config=config)


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Pump Differential Pressure Setpoint Tracking Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python app.py brick_model.ttl timeseries_data.csv

  # With config
  python app.py model.ttl data.csv --config config.yaml

  # Custom output
  python app.py model.ttl data.csv --output-dir ./results
        """,
    )

    parser.add_argument("brick_model", help="Path to Brick model (.ttl)")
    parser.add_argument("timeseries_data", help="Path to timeseries data (.csv)")
    parser.add_argument("--config", help="Config file (optional)", default=None)
    parser.add_argument("--output-dir", help="Output directory (optional)", default=None)

    args = parser.parse_args()

    config = load_config(args.config)
    if args.output_dir:
        config["output"]["output_dir"] = args.output_dir

    print(f"\n{'='*60}")
    print(f"Pump Differential Pressure Setpoint Tracking Analysis")
    print(f"{'='*60}")
    print(f"Brick model: {args.brick_model}")
    print(f"Timeseries:  {args.timeseries_data}")
    print(f"{'='*60}")

    results = analyze(args.brick_model, args.timeseries_data, config)

    if results:
        print(f"\n{'='*60}")
        print(f"[SUCCESS] Analysis completed successfully!")
        print(f"   Results saved to: {config['output']['output_dir']}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"[FAILED] Analysis failed")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
