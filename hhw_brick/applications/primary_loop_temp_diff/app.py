#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Primary Loop Temperature Differential Analysis

Analyzes temperature differential between supply and return water in primary loops.
Specifically designed for boiler systems with primary loops.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Plot settings
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams["figure.figsize"] = (14, 8)
plt.rcParams["font.size"] = 10


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


def find_supply_return_sensors(graph):
    """Find supply and return temperature sensors on primary loop"""
    query = """
    SELECT ?loop ?supply ?return WHERE {
        ?loop rdf:type/rdfs:subClassOf* brick:Hot_Water_Loop .
        FILTER(CONTAINS(LCASE(STR(?loop)), "primary"))

        ?loop brick:hasPart ?supply .
        ?supply rdf:type/rdfs:subClassOf* brick:Leaving_Hot_Water_Temperature_Sensor .

        ?loop brick:hasPart ?return .
        ?return rdf:type/rdfs:subClassOf* brick:Entering_Hot_Water_Temperature_Sensor .
    }
    """

    results = query_sensors(graph, [], custom_query=query)
    return results[0] if results else None


def qualify(brick_model_path):
    """Check if building has required sensors on primary loop"""
    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking required sensors on primary loop")
    print(f"{'='*60}\n")

    from rdflib import Graph

    g = Graph()
    g.parse(brick_model_path, format="turtle")

    result = find_supply_return_sensors(g)

    if result:
        loop, supply, return_sensor = result
        print(f"[OK] Building qualified")
        print(f"   Primary Loop: {loop}")
        print(f"   Supply: {supply}")
        print(f"   Return: {return_sensor}\n")
        return True, {"loop": str(loop), "supply": str(supply), "return": str(return_sensor)}
    else:
        print(f"[FAIL] Building NOT qualified")
        print(f"   Missing: Supply and return sensors on primary loop\n")
        return False, {}


def analyze(brick_model_path, timeseries_data_path, config):
    """Execute analysis workflow"""
    # Step 1: Qualify
    qualified, qualify_result = qualify(brick_model_path)
    if not qualified:
        return None

    # Step 2: Load data
    print(f"{'='*60}")
    print(f"FETCH: Loading data")
    print(f"{'='*60}\n")

    g, df = load_data(brick_model_path, timeseries_data_path)
    print(f"[OK] Loaded {len(df)} data points")
    print(f"[OK] Time range: {df.index.min()} to {df.index.max()}\n")

    # Map sensors to columns
    supply_uri = qualify_result["supply"]
    return_uri = qualify_result["return"]
    sensor_mapping = map_sensors_to_columns(g, [supply_uri, return_uri], df)

    if len(sensor_mapping) != 2:
        print("[FAIL] Failed to map sensors to data columns\n")
        return None

    # Extract and filter data
    df_extracted = extract_data_columns(
        df, sensor_mapping, rename_map={supply_uri: "sup", return_uri: "ret"}
    )

    if config["time_range"]["start_time"] or config["time_range"]["end_time"]:
        df_extracted = filter_time_range(
            df_extracted, config["time_range"]["start_time"], config["time_range"]["end_time"]
        )
        print(f"[OK] Filtered to {len(df_extracted)} data points\n")

    # Step 3: Analyze
    print(f"{'='*60}")
    print(f"ANALYZE: Computing primary loop temperature differential")
    print(f"{'='*60}\n")

    df_extracted["temp_diff"] = df_extracted["sup"] - df_extracted["ret"]
    df_clean = df_extracted.dropna().copy()
    print(f"Valid data points: {len(df_clean)}")

    # Calculate statistics
    threshold_min = config["analysis"]["threshold_min_delta"]
    threshold_max = config["analysis"]["threshold_max_delta"]

    stats = {
        "count": len(df_clean),
        "mean_temp_diff": df_clean["temp_diff"].mean(),
        "std_temp_diff": df_clean["temp_diff"].std(),
        "min_temp_diff": df_clean["temp_diff"].min(),
        "max_temp_diff": df_clean["temp_diff"].max(),
        "median_temp_diff": df_clean["temp_diff"].median(),
        "q25_temp_diff": df_clean["temp_diff"].quantile(0.25),
        "q75_temp_diff": df_clean["temp_diff"].quantile(0.75),
        "mean_supply_temp": df_clean["sup"].mean(),
        "mean_return_temp": df_clean["ret"].mean(),
        "anomalies_below_threshold": len(df_clean[df_clean["temp_diff"] < threshold_min]),
        "anomalies_above_threshold": len(df_clean[df_clean["temp_diff"] > threshold_max]),
    }
    stats["anomaly_rate"] = (
        (stats["anomalies_below_threshold"] + stats["anomalies_above_threshold"])
        / stats["count"]
        * 100
    )

    df_clean.loc[:, "hour"] = df_clean.index.hour
    df_clean.loc[:, "weekday"] = df_clean.index.dayofweek
    df_clean.loc[:, "month"] = df_clean.index.month

    # Print summary
    print(f"\nPrimary Loop Statistics:")
    print(f"  Mean temp diff:   {stats['mean_temp_diff']:.2f} °C")
    print(f"  Std deviation:    {stats['std_temp_diff']:.2f} °C")
    print(f"  Range:            [{stats['min_temp_diff']:.2f}, {stats['max_temp_diff']:.2f}] °C")
    print(f"  Mean supply temp: {stats['mean_supply_temp']:.2f} °C")
    print(f"  Mean return temp: {stats['mean_return_temp']:.2f} °C")
    print(f"  Anomaly rate:     {stats['anomaly_rate']:.2f}%")

    results = {"stats": stats, "data": df_clean}

    # Step 4: Output
    if config["output"]["save_results"]:
        save_results(results, config)

    if config["output"]["generate_plots"]:
        generate_plots(results, config)

    if config["output"]["generate_plotly_html"]:
        generate_plotly_html(results, config)

    return results


def save_results(results, config):
    """Save analysis results"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    export_format = config["output"]["export_format"]

    print(f"\n{'='*60}")
    print(f"OUTPUT: Saving results to {output_dir}")
    print(f"{'='*60}\n")

    # Save statistics
    stats_file = output_dir / f"primary_loop_temp_diff_stats.{export_format}"
    stats_df = pd.DataFrame([results["stats"]])

    if export_format == "csv":
        stats_df.to_csv(stats_file, index=False)
    else:  # json
        stats_df.to_json(stats_file, orient="records", indent=2)
    print(f"  [OK] {stats_file.name}")

    # Save timeseries
    ts_file = output_dir / f"primary_loop_temp_diff_timeseries.{export_format}"

    if export_format == "csv":
        results["data"].to_csv(ts_file)
    else:  # json
        results["data"].to_json(ts_file, orient="index", date_format="iso")

    print(f"  [OK] {ts_file.name}")


def generate_plots(results, config):
    """Generate comprehensive visualization plots for primary loop"""
    output_dir = Path(config["output"]["output_dir"])
    plot_format = config["output"]["plot_format"]

    print(f"\n{'='*60}")
    print(f"Generating plots")
    print(f"{'='*60}\n")

    df = results["data"]
    stats = results["stats"]

    # Plot 1: Timeseries with dual y-axis
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))

    # Supply and Return temperatures
    ax1 = axes[0]
    ax1.plot(
        df.index, df["sup"], label="Primary Supply Temp", color="#e74c3c", linewidth=1.5, alpha=0.8
    )
    ax1.plot(
        df.index, df["ret"], label="Primary Return Temp", color="#3498db", linewidth=1.5, alpha=0.8
    )
    ax1.set_ylabel("Temperature (°C)", fontsize=12, fontweight="bold")
    ax1.set_title(
        "Primary Loop: Supply and Return Temperature Over Time", fontsize=14, fontweight="bold"
    )
    ax1.legend(loc="upper left", fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle="--")

    # Temperature differential
    ax2 = axes[1]
    ax2.plot(df.index, df["temp_diff"], color="#9b59b6", linewidth=1, alpha=0.7)
    ax2.axhline(
        y=stats["mean_temp_diff"],
        color="#27ae60",
        linestyle="--",
        linewidth=2,
        label=f'Mean: {stats["mean_temp_diff"]:.2f}°C',
    )
    ax2.axhline(
        y=stats["median_temp_diff"],
        color="#f39c12",
        linestyle=":",
        linewidth=2,
        label=f'Median: {stats["median_temp_diff"]:.2f}°C',
    )
    ax2.fill_between(
        df.index,
        stats["q25_temp_diff"],
        stats["q75_temp_diff"],
        alpha=0.2,
        color="#9b59b6",
        label="IQR",
    )
    ax2.set_xlabel("Date", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Temperature Difference (°C)", fontsize=12, fontweight="bold")
    ax2.set_title(
        "Primary Loop: Temperature Differential Over Time", fontsize=14, fontweight="bold"
    )
    ax2.legend(loc="upper left", fontsize=10)
    ax2.grid(True, alpha=0.3, linestyle="--")

    plt.tight_layout()
    filepath = output_dir / f"primary_loop_timeseries.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [OK] {filepath.name}")

    # Plot 2: Distribution and Box Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Histogram
    axes[0].hist(df["temp_diff"], bins=60, edgecolor="black", alpha=0.7, color="#3498db")
    axes[0].axvline(
        x=stats["mean_temp_diff"],
        color="#e74c3c",
        linestyle="--",
        linewidth=2,
        label=f'Mean: {stats["mean_temp_diff"]:.2f}°C',
    )
    axes[0].axvline(
        x=stats["median_temp_diff"],
        color="#27ae60",
        linestyle=":",
        linewidth=2,
        label=f'Median: {stats["median_temp_diff"]:.2f}°C',
    )
    axes[0].set_xlabel("Temperature Difference (°C)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Frequency", fontsize=11, fontweight="bold")
    axes[0].set_title(
        "Primary Loop: Distribution of Temperature Differential", fontsize=12, fontweight="bold"
    )
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3, axis="y")

    # Box plot
    box = axes[1].boxplot(df["temp_diff"], patch_artist=True)
    box["boxes"][0].set_facecolor("#3498db")
    box["boxes"][0].set_alpha(0.7)
    axes[1].set_ylabel("Temperature Difference (°C)", fontsize=11, fontweight="bold")
    axes[1].set_title("Primary Loop: Box Plot", fontsize=12, fontweight="bold")
    axes[1].grid(True, alpha=0.3, axis="y")

    # Cumulative distribution
    sorted_data = np.sort(df["temp_diff"])
    cumulative = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    axes[2].plot(sorted_data, cumulative, linewidth=2, color="#3498db")
    axes[2].set_xlabel("Temperature Difference (°C)", fontsize=11, fontweight="bold")
    axes[2].set_ylabel("Cumulative Probability", fontsize=11, fontweight="bold")
    axes[2].set_title("Primary Loop: Cumulative Distribution", fontsize=12, fontweight="bold")
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    filepath = output_dir / f"primary_loop_distribution.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [OK] {filepath.name}")

    # Plot 3: Time-based analysis
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # By hour of day
    hourly = df.groupby("hour")["temp_diff"].agg(["mean", "std"])
    axes[0, 0].bar(hourly.index, hourly["mean"], color="#3498db", alpha=0.7, edgecolor="black")
    axes[0, 0].errorbar(
        hourly.index, hourly["mean"], yerr=hourly["std"], fmt="none", ecolor="#e74c3c", capsize=3
    )
    axes[0, 0].set_xlabel("Hour of Day", fontsize=11, fontweight="bold")
    axes[0, 0].set_ylabel("Mean Temp Diff (°C)", fontsize=11, fontweight="bold")
    axes[0, 0].set_title("Primary Loop: Temp Diff by Hour of Day", fontsize=12, fontweight="bold")
    axes[0, 0].grid(True, alpha=0.3, axis="y")
    axes[0, 0].set_xticks(range(24))

    # By day of week
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly = df.groupby("weekday")["temp_diff"].agg(["mean", "std"])
    axes[0, 1].bar(range(7), weekly["mean"], color="#27ae60", alpha=0.7, edgecolor="black")
    axes[0, 1].errorbar(
        range(7), weekly["mean"], yerr=weekly["std"], fmt="none", ecolor="#e74c3c", capsize=3
    )
    axes[0, 1].set_xlabel("Day of Week", fontsize=11, fontweight="bold")
    axes[0, 1].set_ylabel("Mean Temp Diff (°C)", fontsize=11, fontweight="bold")
    axes[0, 1].set_title("Primary Loop: Temp Diff by Day of Week", fontsize=12, fontweight="bold")
    axes[0, 1].grid(True, alpha=0.3, axis="y")
    axes[0, 1].set_xticks(range(7))
    axes[0, 1].set_xticklabels(weekday_names)

    # By month
    monthly = df.groupby("month")["temp_diff"].agg(["mean", "std"])
    axes[1, 0].bar(monthly.index, monthly["mean"], color="#f39c12", alpha=0.7, edgecolor="black")
    axes[1, 0].errorbar(
        monthly.index, monthly["mean"], yerr=monthly["std"], fmt="none", ecolor="#e74c3c", capsize=3
    )
    axes[1, 0].set_xlabel("Month", fontsize=11, fontweight="bold")
    axes[1, 0].set_ylabel("Mean Temp Diff (°C)", fontsize=11, fontweight="bold")
    axes[1, 0].set_title("Primary Loop: Temp Diff by Month", fontsize=12, fontweight="bold")
    axes[1, 0].grid(True, alpha=0.3, axis="y")
    axes[1, 0].set_xticks(range(1, 13))

    # Scatter: Supply vs Return
    axes[1, 1].scatter(df["sup"], df["ret"], alpha=0.3, s=10, c=df["temp_diff"], cmap="RdYlBu_r")
    axes[1, 1].plot(
        [df["sup"].min(), df["sup"].max()],
        [df["sup"].min(), df["sup"].max()],
        "k--",
        linewidth=2,
        label="Perfect Match",
    )
    axes[1, 1].set_xlabel("Supply Temperature (°C)", fontsize=11, fontweight="bold")
    axes[1, 1].set_ylabel("Return Temperature (°C)", fontsize=11, fontweight="bold")
    axes[1, 1].set_title(
        "Primary Loop: Supply vs Return Temperature", fontsize=12, fontweight="bold"
    )
    axes[1, 1].legend(fontsize=9)
    axes[1, 1].grid(True, alpha=0.3)
    cbar = plt.colorbar(axes[1, 1].collections[0], ax=axes[1, 1])
    cbar.set_label("Temp Diff (°C)", fontsize=10)

    plt.tight_layout()
    filepath = output_dir / f"primary_loop_time_analysis.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [OK] {filepath.name}")

    # Plot 4: Heatmap - Hour vs Day of Week
    fig, ax = plt.subplots(figsize=(12, 8))

    pivot_data = df.pivot_table(values="temp_diff", index="hour", columns="weekday", aggfunc="mean")
    im = ax.imshow(pivot_data, cmap="RdYlBu_r", aspect="auto", interpolation="nearest")

    ax.set_xticks(range(7))
    ax.set_xticklabels(weekday_names, fontsize=10)
    ax.set_yticks(range(24))
    ax.set_yticklabels(range(24), fontsize=8)
    ax.set_xlabel("Day of Week", fontsize=12, fontweight="bold")
    ax.set_ylabel("Hour of Day", fontsize=12, fontweight="bold")
    ax.set_title(
        "Primary Loop: Temperature Differential Heatmap (Hour vs Day of Week)",
        fontsize=14,
        fontweight="bold",
    )

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Mean Temp Diff (°C)", fontsize=11)

    plt.tight_layout()
    filepath = output_dir / f"primary_loop_heatmap.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [OK] {filepath.name}")


def generate_plotly_html(results, config):
    """Generate interactive HTML visualizations using Plotly"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Generating interactive Plotly HTML visualizations")
    print(f"{'='*60}\n")

    df = results["data"]
    stats = results["stats"]
    threshold_min = config["analysis"]["threshold_min_delta"]
    threshold_max = config["analysis"]["threshold_max_delta"]

    # Create a comprehensive dashboard with multiple subplots
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            "Supply and Return Temperature Over Time",
            "Temperature Differential Over Time",
            "Temperature Differential Distribution",
            "Supply vs Return Temperature",
            "Hourly Pattern Analysis",
            "Weekly Pattern Analysis",
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10,
    )

    # Plot 1: Supply and Return temperatures
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["sup"],
            mode="lines",
            name="Supply Temp",
            line=dict(color="#e74c3c", width=2),
            hovertemplate="Time: %{x}<br>Supply: %{y:.2f}°C<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["ret"],
            mode="lines",
            name="Return Temp",
            line=dict(color="#3498db", width=2),
            hovertemplate="Time: %{x}<br>Return: %{y:.2f}°C<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Plot 2: Temperature differential
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["temp_diff"],
            mode="lines",
            name="Temp Diff",
            line=dict(color="#9b59b6", width=1.5),
            fill="tozeroy",
            fillcolor="rgba(155, 89, 182, 0.2)",
            hovertemplate="Time: %{x}<br>Diff: %{y:.2f}°C<extra></extra>",
        ),
        row=1,
        col=2,
    )
    # Add mean line
    fig.add_hline(
        y=stats["mean_temp_diff"],
        line_dash="dash",
        line_color="#27ae60",
        annotation_text=f"Mean: {stats['mean_temp_diff']:.2f}°C",
        row=1,
        col=2,
    )

    # Plot 3: Distribution histogram
    fig.add_trace(
        go.Histogram(
            x=df["temp_diff"],
            nbinsx=50,
            name="Distribution",
            marker_color="#3498db",
            opacity=0.7,
            hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Plot 4: Scatter - Supply vs Return
    fig.add_trace(
        go.Scatter(
            x=df["sup"],
            y=df["ret"],
            mode="markers",
            name="Supply vs Return",
            marker=dict(
                size=4,
                color=df["temp_diff"],
                colorscale="RdYlBu_r",
                showscale=True,
                colorbar=dict(title="Temp Diff (°C)", x=1.15, len=0.3, y=0.5),
            ),
            hovertemplate="Supply: %{x:.2f}°C<br>Return: %{y:.2f}°C<extra></extra>",
        ),
        row=2,
        col=2,
    )
    # Add perfect match line
    min_temp = min(df["sup"].min(), df["ret"].min())
    max_temp = max(df["sup"].max(), df["ret"].max())
    fig.add_trace(
        go.Scatter(
            x=[min_temp, max_temp],
            y=[min_temp, max_temp],
            mode="lines",
            name="Perfect Match",
            line=dict(color="black", dash="dash", width=2),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    # Plot 5: Hourly pattern
    hourly = df.groupby("hour")["temp_diff"].agg(["mean", "std"]).reset_index()
    fig.add_trace(
        go.Bar(
            x=hourly["hour"],
            y=hourly["mean"],
            name="Hourly Avg",
            marker_color="#3498db",
            error_y=dict(type="data", array=hourly["std"], color="#e74c3c"),
            hovertemplate="Hour: %{x}<br>Mean: %{y:.2f}°C<extra></extra>",
        ),
        row=3,
        col=1,
    )

    # Plot 6: Weekly pattern
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly = df.groupby("weekday")["temp_diff"].agg(["mean", "std"]).reset_index()
    fig.add_trace(
        go.Bar(
            x=[weekday_names[i] for i in weekly["weekday"]],
            y=weekly["mean"],
            name="Weekly Avg",
            marker_color="#27ae60",
            error_y=dict(type="data", array=weekly["std"], color="#e74c3c"),
            hovertemplate="Day: %{x}<br>Mean: %{y:.2f}°C<extra></extra>",
        ),
        row=3,
        col=2,
    )

    # Update layout
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_xaxes(title_text="Time", row=1, col=2)
    fig.update_yaxes(title_text="Temp Diff (°C)", row=1, col=2)
    fig.update_xaxes(title_text="Temp Diff (°C)", row=2, col=1)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    fig.update_xaxes(title_text="Supply Temp (°C)", row=2, col=2)
    fig.update_yaxes(title_text="Return Temp (°C)", row=2, col=2)
    fig.update_xaxes(title_text="Hour of Day", row=3, col=1)
    fig.update_yaxes(title_text="Mean Temp Diff (°C)", row=3, col=1)
    fig.update_xaxes(title_text="Day of Week", row=3, col=2)
    fig.update_yaxes(title_text="Mean Temp Diff (°C)", row=3, col=2)

    fig.update_layout(
        title_text="Primary Loop Temperature Differential Analysis - Interactive Dashboard",
        title_font_size=20,
        height=1400,
        showlegend=True,
        hovermode="closest",
        template="plotly_white",
    )

    # Save the comprehensive dashboard
    dashboard_file = output_dir / "primary_loop_interactive_dashboard.html"
    fig.write_html(dashboard_file)
    print(f"  [OK] {dashboard_file.name}")

    # Create a separate detailed timeseries visualization
    fig_timeseries = go.Figure()

    # Add supply temperature
    fig_timeseries.add_trace(
        go.Scatter(
            x=df.index,
            y=df["sup"],
            mode="lines",
            name="Supply Temperature",
            line=dict(color="#e74c3c", width=2),
            hovertemplate="<b>Supply Temp</b><br>Time: %{x}<br>Temp: %{y:.2f}°C<extra></extra>",
        )
    )

    # Add return temperature
    fig_timeseries.add_trace(
        go.Scatter(
            x=df.index,
            y=df["ret"],
            mode="lines",
            name="Return Temperature",
            line=dict(color="#3498db", width=2),
            hovertemplate="<b>Return Temp</b><br>Time: %{x}<br>Temp: %{y:.2f}°C<extra></extra>",
        )
    )

    # Add temperature differential on secondary y-axis
    fig_timeseries.add_trace(
        go.Scatter(
            x=df.index,
            y=df["temp_diff"],
            mode="lines",
            name="Temperature Differential",
            line=dict(color="#9b59b6", width=2),
            yaxis="y2",
            hovertemplate="<b>Temp Diff</b><br>Time: %{x}<br>Diff: %{y:.2f}°C<extra></extra>",
        )
    )

    # Add threshold lines on secondary y-axis
    fig_timeseries.add_hline(
        y=threshold_min,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Min Threshold: {threshold_min}°C",
        yref="y2",
    )
    fig_timeseries.add_hline(
        y=threshold_max,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Max Threshold: {threshold_max}°C",
        yref="y2",
    )

    # Update layout with dual y-axes
    fig_timeseries.update_layout(
        title="Primary Loop: Detailed Temperature Analysis Over Time",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        yaxis2=dict(title="Temperature Differential (°C)", overlaying="y", side="right"),
        hovermode="x unified",
        template="plotly_white",
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    timeseries_file = output_dir / "primary_loop_timeseries_interactive.html"
    fig_timeseries.write_html(timeseries_file)
    print(f"  [OK] {timeseries_file.name}")

    # Create a 3D surface plot for hour vs day of week heatmap
    pivot_data = df.pivot_table(values="temp_diff", index="hour", columns="weekday", aggfunc="mean")
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=pivot_data.values,
            x=[weekday_names[i] for i in pivot_data.columns],
            y=pivot_data.index,
            colorscale="RdYlBu_r",
            colorbar=dict(title="Mean Temp Diff (°C)"),
            hovertemplate="Day: %{x}<br>Hour: %{y}<br>Temp Diff: %{z:.2f}°C<extra></extra>",
        )
    )

    fig_heatmap.update_layout(
        title="Primary Loop: Temperature Differential Pattern (Hour vs Day of Week)",
        xaxis_title="Day of Week",
        yaxis_title="Hour of Day",
        height=600,
        template="plotly_white",
    )

    heatmap_file = output_dir / "primary_loop_heatmap_interactive.html"
    fig_heatmap.write_html(heatmap_file)
    print(f"  [OK] {heatmap_file.name}")

    # Create a box plot for distribution analysis
    fig_box = go.Figure()

    fig_box.add_trace(
        go.Box(
            y=df["temp_diff"],
            name="Temperature Differential",
            marker_color="#3498db",
            boxmean="sd",
            hovertemplate="<b>Stats</b><br>Value: %{y:.2f}°C<extra></extra>",
        )
    )

    fig_box.update_layout(
        title="Primary Loop: Temperature Differential Distribution (Box Plot)",
        yaxis_title="Temperature Differential (°C)",
        height=500,
        template="plotly_white",
        showlegend=False,
    )

    # Add annotations for statistics
    fig_box.add_annotation(
        xref="paper",
        yref="y",
        x=0.5,
        y=stats["mean_temp_diff"],
        text=f"Mean: {stats['mean_temp_diff']:.2f}°C",
        showarrow=True,
        arrowhead=2,
        ax=80,
        ay=0,
    )

    boxplot_file = output_dir / "primary_loop_boxplot_interactive.html"
    fig_box.write_html(boxplot_file)
    print(f"  [OK] {boxplot_file.name}")

    print(f"\n  Generated 4 interactive HTML files with Plotly visualizations!")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Primary Loop Temperature Differential Analysis",
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

    # Load config
    config = load_config(args.config)

    if args.output_dir:
        config["output"]["output_dir"] = args.output_dir

    # Run analysis
    print(f"\n{'='*60}")
    print(f"Primary Loop Temperature Differential Analysis")
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
