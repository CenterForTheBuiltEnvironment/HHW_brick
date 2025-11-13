# Lib import
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.stats import gaussian_kde
import sys
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
__all__ = ["qualify", "run_hwst_analysis", "run_fire_analysis", "load_config"]


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
    """Find supply and return temperature sensors on secondary loop"""
    query = """
    SELECT ?equipment ?supply ?return WHERE {
        ?equipment rdf:type/rdfs:subClassOf* brick:Hot_Water_Loop .
        FILTER(CONTAINS(LCASE(STR(?equipment)), "secondary"))

        ?equipment brick:hasPart ?supply .
        ?supply rdf:type/rdfs:subClassOf* brick:Leaving_Hot_Water_Temperature_Sensor .

        ?equipment brick:hasPart ?return .
        ?return rdf:type/rdfs:subClassOf* brick:Entering_Hot_Water_Temperature_Sensor .
    }
    """

    results = query_sensors(graph, [], custom_query=query)
    return results[0] if results else None

def find_boiler_firing_sensors(graph):
    """Find boiler firing rate sensors"""
    query = """
    SELECT ?boiler ?firing_rate WHERE {
        ?boiler rdf:type/rdfs:subClassOf* brick:Condensing_Natural_Gas_Boiler .
        ?boiler brick:hasPoint ?firing_rate .
        ?firing_rate rdf:type/rdfs:subClassOf* brick:Firing_Rate_Sensor .
    }
    """
    
    results = query_sensors(graph, [], custom_query=query)
    return results if results else None

def find_boiler_oper_sensors(graph):
    """Find hhw operation status sensors"""
    query = """
    SELECT ?hws ?oper WHERE {
        ?hws rdf:type/rdfs:subClassOf* brick:Hot_Water_System .
        ?hws brick:hasPart ?oper .
        ?oper rdf:type/rdfs:subClassOf* brick:Enable_Status .
    }
    """

    results = query_sensors(graph, [], custom_query=query)
    return results[0] if results else None

def find_weather_station(graph):
    """Find associated weather station"""
    query = """
    SELECT ?ws ?oat WHERE {
        ?ws rdf:type/rdfs:subClassOf* brick:Weather_Station .
        ?ws brick:hasPoint ?oat .
        ?oat rdf:type/rdfs:subClassOf* brick:Outside_Air_Temperature_Sensor .
    }
    """

    results = query_sensors(graph, [], custom_query=query)
    return results[0] if results else None

def qualify(brick_model_path):
    """
    QUALIFY: Check if building has required sensors
    """
    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking required supply and return water temperature sensors")
    print(f"{'='*60}\n")

    # Load Brick model
    from rdflib import Graph

    g = Graph()
    g.parse(brick_model_path, format="turtle")
    semi_qualified = True
    qualified = False
    qualified_result = {}

    # Approach 1: Supply and return temperature sensors
    temp_sensors = find_supply_return_sensors(g)
    boiler_oper = find_boiler_oper_sensors(g)
    oat_sensor = find_weather_station(g)

    if temp_sensors:
        loop, supply, return_sensor = temp_sensors
        print(f"[OK] Building qualified")
        print(f"   Loop: {loop}")
        print(f"   Supply: {supply}")
        print(f"   Return: {return_sensor}\n")
        semi_qualified = True
        qualified_result = {"loop": str(loop), "supply": str(supply), "return": str(return_sensor)}
    else:
        print(f"[FAIL] Building NOT qualified")
        print(f"   Missing: Supply and return sensors on secondary loop\n")
        qualified = False
        qualified_result.update({})
    
    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking required hot water system operation status sensors")
    print(f"{'='*60}\n")

    if boiler_oper:
        hws, oper = boiler_oper
        print(f"[OK] Building qualified")
        print(f"   Hot Water System: {hws}")
        print(f"   Operation Status: {oper}\n")
        if semi_qualified:
            semi_qualified = True
            qualified_result.update({"hws": str(hws), "oper": str(oper)})
    else:
        print(f"[FAIL] Building NOT qualified")
        print(f"   Missing: Hot water system operation status sensor\n")
        qualified = False
        qualified_result.update({})

    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking required outdoor air temperature sensors")
    print(f"{'='*60}\n")

    if oat_sensor:
        ws, oat = oat_sensor
        print(f"[OK] Found weather station")
        print(f"   Weather Station: {ws}")
        print(f"   OAT Sensor: {oat}\n")
        if semi_qualified:
            qualified = True
            qualified_result.update({"weather_station": str(ws), "oat": str(oat)})
    else:
        print(f"[FAIL] Building NOT qualified")
        print(f"   Missing: Outdoor air temperature sensor\n")
        qualified = False
        qualified_result.update({})

    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking required boiler firing rate sensors")
    print(f"{'='*60}\n")

    # Approach 2: Boiler firing rate sensors
    boiler_fire = find_boiler_firing_sensors(g)

    if boiler_fire:
        print(f"[OK] Building qualified")
        qualified_result.update({"boiler": [], "firing_rate": []})
        for b in boiler_fire:
            boiler, firing_rate = b
            print(f"   Boiler: {boiler}")
            print(f"   Firing Rate: {firing_rate}\n")
            qualified_result["boiler"].append(str(boiler))
            qualified_result["firing_rate"].append(str(firing_rate))
        qualified = True

    else:
        print(f"[FAIL] Building NOT qualified")
        print(f"   Missing: Boiler firing rate sensor\n")
        qualified = qualified and False
        qualified_result.update({})
    
    return qualified, qualified_result

# Matplotlib defaults (similar to theme_minimal)
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.grid": False,
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.titlecolor": "#333333",
    "axes.labelsize": 12,
    "text.color": "#333333",
})

# Colors (matplotlib compatible)
LS_COLORS = {
    "Potential cycling": "#FF6666",
    "Others": "#CCCCCC",  # Changed from "grey80" to valid hex color
}

def directional_run_lengths(arr):
    """Return run-length encoding like R's rle() function.
    Equivalent to R code: rep(rle(changed)$length, rle(changed)$length)
    """
    arr = np.asarray(arr)
    if arr.size <= 1:
        return np.ones(arr.size, dtype=int)
    arr_str = arr.astype(str)
    changes = np.concatenate(([True], arr_str[1:] != arr_str[:-1]))
    change_indices = np.where(changes)[0]
    change_indices = np.concatenate([change_indices, [len(arr)]])
    run_lengths = np.diff(change_indices)
    result = np.repeat(run_lengths, run_lengths)
    
    return result

def safe_kde(vals, xs):
    """Compute KDE if scipy is available and there's enough data."""
    if gaussian_kde is None or len(vals) < 5:
        return None, None
    try:
        kde = gaussian_kde(vals)
        return xs, kde(xs)
    except Exception:
        return None, None
    
def run_hwst_analysis(dataframe, config, plot_options=False):

    """dataframe: the dataframe should contain the following columns:
        - datetime_UTC
        - sup (supply water temperature of the hot water plant)
        - ret (return water temperature of the hot water plant)
        - t_out (outdoor air temperature)
        - oper (operation status of the boiler, 1 for on, 0 for off)
        - (OPTIONAL) sup_stpt (supply water temperature setpoint, optional)
    config: dictionary containing threshold values:
        - TOUT_MILD: outdoor temperature threshold for mild conditions
        - CYC_THR: minimum number of consecutive cycles
        - SPT_THR: setpoint deviation threshold
        - DET_THR: delta T threshold
    plot_options: boolean flag to enable/disable plotting"""

    TOUT_MILD = config['analysis']["TOUT_MILD"]
    CYC_THR = config['analysis']["CYC_THR"]
    SPT_THR = config['analysis']["SPT_THR"]
    DET_THR = config['analysis']["DET_THR"]

    # Output directories (a folder for csv and a folder for figures if plotting is enabled)
    OUT_DIR = Path(config['output'].get("output_dir", "./results"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if plot_options:

        fig_dir = OUT_DIR / "figs"
        fig_dir.mkdir(parents=True, exist_ok=True)

    df = dataframe.copy()

    # Sort by time and compute cadence
    consec = df["datetime_UTC"].diff().dt.total_seconds() / 60.0
    consec_dt = df["datetime_UTC"].diff().dt.days
    df["deltaT"] = df["sup"] - df["ret"]
    delta_sup = df["sup"].diff()
    df["deltaT_sup"] = np.where((consec == 15) & (consec_dt.isin([0, 1])), delta_sup, np.nan)

    comp_next = np.where(df["deltaT_sup"] >= 0, 1, np.where(df["deltaT_sup"] < 0, 0, np.nan))
    changed = pd.Series(comp_next, index=df.index).diff().abs()
    df['changed'] = changed
    df["rle"] = directional_run_lengths(changed)  # Use .values and handle NaN
    df["cycle"] = df["rle"] * changed  # Handle NaN in multiplication
    df["tout_lev"] = np.where(df["t_out"] >= TOUT_MILD, 1, 0)

    # Create csv subdirectory if it doesn't exist
    csv_dir = OUT_DIR / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)

    # HWST setpoint path
    if "sup_stpt" in df.columns:
        spt_na = df["sup_stpt"].isna().mean() * 100.0
    else:
        spt_na = 100.0

    if spt_na < 40:
        df["deltaT_sp"] = (df["sup"] - df["sup_stpt"]).abs()
        df["flag_hwst"] = np.where(
            (df["cycle"] >= CYC_THR) &
            (df["deltaT_sp"] <= SPT_THR) &
            (df["deltaT"] <= DET_THR) &
            (df["tout_lev"] == 1) &
            (df["oper"] == 1),
            1, 0
        )
        
        # Export csv file
        df[['tag', 'datetime_UTC', 'sup', 'sup_stpt', 'ret', 't_out', 'flag_hwst']].to_csv(csv_dir / 'hwst_spt.csv', index=False)

        # Plot
        if plot_options:
            fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
            m = (df["flag_hwst"] == 0)
            ax.scatter(df.loc[m, "t_out"], df.loc[m, "deltaT"], s=4, c=LS_COLORS["Others"], alpha=0.2, label="Others")
            m = (df["flag_hwst"] == 1)
            ax.scatter(df.loc[m, "t_out"], df.loc[m, "deltaT"], s=12, c=LS_COLORS["Potential cycling"], alpha=0.8, label="Potential cycling")
            ax.set_xlabel("Outdoor temperature (°C)")
            ax.set_ylabel("Delta T between supply and return water temperature (°C)")
            ax.set_title("Boiler operating conditions\nusing HWST setpoint and plant HWST")
            ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
            ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
            ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
            ax.grid(axis="y", color="grey", alpha=0.2, linewidth=0.5)
            fig.tight_layout()
            fig.savefig(fig_dir / "spt_result.png", bbox_inches="tight")
            plt.close(fig)

    # HWST-only path
    df["flag_hwst"] = np.where(
        (df["cycle"] >= CYC_THR) &
        (df["deltaT"] <= DET_THR) &
        (df["tout_lev"] == 1) &
        (df["oper"] == 1),
        1, 0
    )

    # Plot
    if plot_options:
        fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
        m = (df["flag_hwst"] == 0)
        ax.scatter(df.loc[m, "t_out"], df.loc[m, "deltaT"], s=4, c=LS_COLORS["Others"], alpha=0.2, label="Others")
        m = (df["flag_hwst"] == 1)
        ax.scatter(df.loc[m, "t_out"], df.loc[m, "deltaT"], s=12, c=LS_COLORS["Potential cycling"], alpha=0.8, label="Potential cycling")
        ax.set_xlabel("Outdoor temperature (°C)")
        ax.set_ylabel("Delta T between supply and return water temperature (°C)")
        ax.set_title("Boiler operating conditions\nusing only plant HWST")
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        ax.grid(axis="y", color="grey", alpha=0.2, linewidth=0.5)
        fig.tight_layout()
        fig.savefig(fig_dir / "hwst_result.png", bbox_inches="tight")
        plt.close(fig)
    
    # Export csv file
    df[['tag', 'datetime_UTC', 'sup', 'sup_stpt', 'ret', 't_out', 'flag_hwst']].to_csv(csv_dir / 'hwst.csv', index=False)
    
    return df

def run_fire_analysis(dataframe, config, plot_options=False):
    """dataframe: the dataframe should contain the following columns:
        - datetime_UTC
        - value (boiler firing rate value in percentage, e.g., 0-100)
        - boiler (boiler identifier)
        - (Optional) sup (supply water temperature of the hot water plant)
        - (Optional) ret (return water temperature of the hot water plant)
        - (Optional) t_out (outdoor air temperature)
    config: dictionary containing threshold values:
        - N_CYC_THR: daily cycle threshold for potential cycling detection
    plot_options: boolean flag to enable/disable plotting"""

    df = dataframe.copy()
    boiler = df['boiler'].unique()[0]
    N_CYC_THR = config['analysis']["N_CYC_THR"]
    turndown_candi = np.array([10, 20, 25, 33.33], dtype=float)

    # Output directories (a folder for csv and a folder for figures if plotting is enabled)
    OUT_DIR = Path(config['output'].get("output_dir", "./results"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create csv subdirectory if it doesn't exist
    csv_dir = OUT_DIR / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)

    fig_dir = OUT_DIR / "figs"
    fig_dir.mkdir(parents=True, exist_ok=True)

    daily_cycle_rows = []
    df = dataframe.copy()
    
    # scale up to percentage if value <= 1.0
    if df["value"].max(skipna=True) <= 1:
        df["value"] = df["value"] * 100.0

    # Find minimum turndown ratio
    df["rounded"] = np.round(df["value"] / 2.5) * 2.5
    vc = df.loc[df["rounded"] > 0, "rounded"].value_counts().sort_values(ascending=False).head(5)
    if vc.empty:
        min_turndown = np.nan
    else:
        min_top = vc.index.min()
        min_turndown = float(turndown_candi[np.argmin(np.abs(turndown_candi - min_top))])

    # Plot distribution
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    vals = df.loc[df["rounded"] > 0, "value"].dropna().values
    if vals.size > 0:
        bins = max(10, int((vals.max() - vals.min()) / 2.5)) if (vals.max() > vals.min()) else 10
        ax.hist(vals, bins=bins, density=True, edgecolor="black", facecolor="white")
        if gaussian_kde is not None and len(vals) > 5:
            xs = np.linspace(vals.min(), vals.max(), 200)
            xs, ys = safe_kde(vals, xs)
            if xs is not None:
                ax.plot(xs, ys, alpha=0.6)
        if not np.isnan(min_turndown):
            ax.axvline(min_turndown, linestyle="--", color="red")
            ax.text(min_turndown, ax.get_ylim()[1]*0.8, f"estimated turndown: {min_turndown:.1f} %",
                    ha="left", va="center", color="red")
    ax.set_title(f"{boiler} firing rate distribution\n(filtered during operation)")
    ax.set_xlabel("Firing rate (%)")
    ax.set_ylabel("Probability density")
    fig.tight_layout()
    fig.savefig(fig_dir / f"fire_rate_{boiler}.png", bbox_inches="tight")
    plt.close(fig)

    # Daily potential cycles: value < min_turndown
    thr = 20.0 if np.isnan(min_turndown) else min_turndown
    df["dt"] = pd.to_datetime(df["datetime_UTC"]).dt.date
    df["cyc"] = np.where(df["value"] < thr, 1, 0)

    df["flag_fire"] = np.where((df["value"] > 0) & (df["value"] < thr), 1, 0)
    df[['datetime_UTC', 'value', 'flag_fire']].to_csv(csv_dir / f"fire_{boiler}.csv", index=False)

    # rle duplicate adjustment (collapse long zero runs)
    for dt_val, grp in df.sort_values("datetime_UTC").groupby("dt"):
        v = grp["value"].fillna(-1).values
        zero = (v == 0).astype(int)
        lens = directional_run_lengths(zero)
        dup = np.where(zero == 1, lens - 1, 0)
        all_cyc = np.nansum(grp["cyc"].values)
        daily_dup = np.nansum(np.unique(dup))
        daily_cyc = all_cyc - daily_dup
        daily_cycle_rows.append({
            "dt": dt_val,
            "all_cyc": all_cyc,
            "daily_dup": daily_dup,
            "daily_cyc": daily_cyc,
            "exceed": 1 if daily_cyc > N_CYC_THR else 0,
        })

    # import pdb; pdb.set_trace()
    daily_cyc_df = pd.DataFrame(daily_cycle_rows)

    # Plot histogram of daily cycles
    if plot_options:
        fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
        vals = daily_cyc_df["daily_cyc"].values
        if vals.size > 0:
            bins = max(10, int((vals.max() - vals.min()) / 4)) if (vals.max() > vals.min()) else 10
            ax.hist(vals, bins=bins, density=True, edgecolor="black", facecolor="white")
            if gaussian_kde is not None and len(vals) > 5:
                xs = np.linspace(vals.min(), vals.max(), 200)
                xs, ys = safe_kde(vals, xs)
                if xs is not None:
                    ax.plot(xs, ys, alpha=0.6)
            ax.axvline(N_CYC_THR, linestyle="--", color="red")
        ax.set_title(f"{boiler} daily potential cycle number\n(assuming {thr:.1f}% as minimum turndown ratio)")
        ax.set_xlabel("Daily potential cycles")
        ax.set_ylabel("Probability density")
        fig.tight_layout()
        fig.savefig(fig_dir / f"daily_cyc_{boiler}.png", bbox_inches="tight")
        plt.close(fig)

    daily_cyc_df.to_csv(csv_dir / f"daily_fire_cycles_{boiler}.csv", index=False)


    if plot_options:
        df["deltaT"] = df["sup"] - df["ret"]
        fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
        m = (df["flag_fire"] == 0)
        ax.scatter(df.loc[m, "t_out"], df.loc[m, "deltaT"], s=4, c=LS_COLORS["Others"], alpha=0.2, label="Others")
        m = (df["flag_fire"] == 1)
        ax.scatter(df.loc[m, "t_out"], df.loc[m, "deltaT"], s=8, c=LS_COLORS["Potential cycling"], alpha=0.8, label="Potential cycling")
        ax.set_title(f"{boiler} operation conditions\n(using boiler firing rate)")
        ax.set_xlabel("Outdoor temperature (°C)")
        ax.set_ylabel("Plant delta T (sup - ret) (°C)")
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        ax.grid(axis="y", color="grey", alpha=0.2, linewidth=0.5)
        fig.tight_layout()
        fig.savefig(fig_dir / f"firing_wt_results_{boiler}.png", bbox_inches="tight")
        plt.close(fig)

    return df

def load_df(brick_model_path, timeseries_data_path, config):

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
    oper_uri = qualify_result["oper"]
    firing_uri = qualify_result["firing_rate"]
    oat_uri = qualify_result["oat"]

    sensor_mapping = map_sensors_to_columns(g, [supply_uri, return_uri, oper_uri, oat_uri] + firing_uri, df)
    app = 0
    if len(sensor_mapping) == 0:
        print("[FAIL] Failed to map sensors to data columns\n")
        return None
    elif set(firing_uri).issubset(sensor_mapping.keys()):
        print(f"[Firing Rate Sensors] Mapped: {firing_uri}\n")
        app = 2
    else:
        print(f"[Supply/Return/Oper/OAT Sensors] Mapped: {supply_uri}, {return_uri}, {oper_uri}, {oat_uri}\n")
        app = 1

    # Extract and filter data
    df_extracted = extract_data_columns(
        df, sensor_mapping
    ).reset_index()

    if config["time_range"]["start_time"] or config["time_range"]["end_time"]:
        df_extracted = filter_time_range(
            df_extracted, config["time_range"]["start_time"], config["time_range"]["end_time"]
        )
        print(f"[OK] Filtered to {len(df_extracted)} data points\n")
        
    return df_extracted, app

def main():
    """Command-line interface"""

    parser = argparse.ArgumentParser(
        description="Boiler Short Cycling Analysis",
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
    print(f"Boiler Short Cycling Analysis")
    print(f"{'='*60}")
    print(f"Brick model: {args.brick_model}")
    print(f"Timeseries:  {args.timeseries_data}")
    print(f"{'='*60}")

    print("Running HWST analysis...")

    df, app = load_df(args.brick_model, args.timeseries_data, config)
    
    # import pdb; pdb.set_trace()
    if app == 0:
        return(f"[FAIL] Analysis cannot proceed due to no sensor data.")
    elif app == 1:
        run_hwst_analysis(df, config, plot_options=False)
    else:
        # Get all fire columns
        fire_columns = [col for col in df.columns if col != 'datetime_UTC']
        for fire_col in fire_columns:
            sub_df = df[['datetime_UTC', fire_col]].copy()
            sub_df = sub_df.rename(columns={fire_col: 'value'})
            sub_df['boiler'] = fire_col
            run_fire_analysis(sub_df, config, plot_options=False)

    # Process notification
    print(f"\n{'='*60}")
    print(f"[SUCCESS] Analysis completed successfully!")
    print(f"   Results saved to: {config['output']['output_dir']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()