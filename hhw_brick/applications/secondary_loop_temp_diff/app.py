#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Secondary Loop Temperature Differential Analysis

Analyzes temperature differential between supply and return water in secondary loops.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
    SPARQL_PREFIXES,
)

# Export core user-facing functions
__all__ = ['qualify', 'analyze', 'load_config']

# Plot settings
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# App-specific sensor types (defined in the app, not in utils)
SUPPLY_TEMP_SENSORS = [
    "Supply_Water_Temperature_Sensor",
    "Leaving_Hot_Water_Temperature_Sensor",
    "Hot_Water_Supply_Temperature_Sensor",
]

RETURN_TEMP_SENSORS = [
    "Return_Water_Temperature_Sensor",
    "Entering_Hot_Water_Temperature_Sensor",
    "Hot_Water_Return_Temperature_Sensor",
]


def load_config(config_file=None):
    """Load configuration with defaults"""
    default_config = {
        'analysis': {
            'threshold_min_delta': 0.5,
            'threshold_max_delta': 10.0,
        },
        'output': {
            'save_results': True,
            'output_dir': './results',
            'export_format': 'csv',
            'generate_plots': True,
            'plot_format': 'png',
        },
        'time_range': {
            'start_time': None,
            'end_time': None,
        }
    }

    if config_file and Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f) or {}
        for key in user_config:
            if key in default_config and isinstance(user_config[key], dict):
                default_config[key].update(user_config[key])
            else:
                default_config[key] = user_config[key]

    return default_config


def find_supply_return_sensors(graph):
    """
    App-specific function to find supply and return temperature sensors

    This is NOT a universal utility - it's specific to this app's needs.
    """
    # Build sensor type lists
    supply_types = ' '.join([f'brick:{st}' for st in SUPPLY_TEMP_SENSORS])
    return_types = ' '.join([f'brick:{rt}' for rt in RETURN_TEMP_SENSORS])

    # App-specific SPARQL query (PREFIX auto-added by utils)
    # Focus on SECONDARY loops - identify by checking if URI contains "secondary"
    query = f"""
    SELECT ?equipment ?supply ?return WHERE {{
        # Find loops that are Hot_Water_Loop
        ?equipment rdf:type/rdfs:subClassOf* brick:Hot_Water_Loop .
        
        # Filter to only secondary loops (by checking URI contains "secondary")
        FILTER(CONTAINS(LCASE(STR(?equipment)), "secondary"))
        
        # Find supply temperature sensor
        ?supply rdf:type/rdfs:subClassOf* ?supply_type .
        VALUES ?supply_type {{ {supply_types} }}
        
        # Find return temperature sensor
        ?return rdf:type/rdfs:subClassOf* ?return_type .
        VALUES ?return_type {{ {return_types} }}
        
        # Both sensors must be associated with the loop
        # Either as parts of the loop OR as points of the loop
        {{
            ?equipment brick:hasPart ?supply .
            ?equipment brick:hasPart ?return .
        }} UNION {{
            ?supply brick:isPointOf ?equipment .
            ?return brick:isPointOf ?equipment .
        }} UNION {{
            ?equipment brick:hasPart ?supply .
            ?return brick:isPointOf ?equipment .
        }} UNION {{
            ?supply brick:isPointOf ?equipment .
            ?equipment brick:hasPart ?return .
        }}
    }}
    """

    # Use universal utility for custom query
    results = query_sensors(graph, [], custom_query=query)
    return results[0] if results else None


def qualify(brick_model_path):
    """
    QUALIFY: Check if building has required sensors
    """
    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking required sensors")
    print(f"{'='*60}\n")

    # Load Brick model
    from rdflib import Graph
    g = Graph()
    g.parse(brick_model_path, format='turtle')

    # Use app-specific function
    result = find_supply_return_sensors(g)

    if result:
        loop, supply, return_sensor = result
        print(f"[OK] Building qualified")
        print(f"   Loop: {loop}")
        print(f"   Supply: {supply}")
        print(f"   Return: {return_sensor}\n")

        return True, {
            'loop': str(loop),
            'supply': str(supply),
            'return': str(return_sensor),
        }
    else:
        print(f"[FAIL] Building NOT qualified")
        print(f"   Missing: Supply and return temperature sensors on same loop\n")
        return False, {}


def analyze(brick_model_path, timeseries_data_path, config):
    """Execute analysis workflow"""

    # Step 1: QUALIFY
    qualified, qualify_result = qualify(brick_model_path)
    if not qualified:
        return None

    # Step 2: FETCH
    print(f"{'='*60}")
    print(f"FETCH: Loading data")
    print(f"{'='*60}\n")

    g, df = load_data(brick_model_path, timeseries_data_path)

    print(f"[OK] Loaded {len(df)} data points")
    print(f"[OK] Time range: {df.index.min()} to {df.index.max()}\n")

    # Map sensors to columns
    supply_uri = qualify_result['supply']
    return_uri = qualify_result['return']

    sensor_mapping = map_sensors_to_columns(g, [supply_uri, return_uri], df)

    if len(sensor_mapping) != 2:
        print("[FAIL] Failed to map sensors to data columns\n")
        return None

    # Extract data
    df_extracted = extract_data_columns(
        df,
        sensor_mapping,
        rename_map={supply_uri: 'sup', return_uri: 'ret'}
    )

    # Filter time range if specified
    if config['time_range']['start_time'] or config['time_range']['end_time']:
        df_extracted = filter_time_range(
            df_extracted,
            config['time_range']['start_time'],
            config['time_range']['end_time']
        )
        print(f"[OK] Filtered to {len(df_extracted)} data points\n")

    # Step 3: ANALYZE
    print(f"{'='*60}")
    print(f"ANALYZE: Computing temperature differential")
    print(f"{'='*60}\n")

    # Calculate temperature differential
    df_extracted['temp_diff'] = df_extracted['sup'] - df_extracted['ret']
    df_clean = df_extracted.dropna().copy()  # Use .copy() to avoid warnings

    print(f"Valid data points: {len(df_clean)}")

    # Statistical analysis
    threshold_min = config['analysis']['threshold_min_delta']
    threshold_max = config['analysis']['threshold_max_delta']

    stats = {
        'count': len(df_clean),
        'mean_temp_diff': df_clean['temp_diff'].mean(),
        'std_temp_diff': df_clean['temp_diff'].std(),
        'min_temp_diff': df_clean['temp_diff'].min(),
        'max_temp_diff': df_clean['temp_diff'].max(),
        'median_temp_diff': df_clean['temp_diff'].median(),
        'q25_temp_diff': df_clean['temp_diff'].quantile(0.25),
        'q75_temp_diff': df_clean['temp_diff'].quantile(0.75),
        'mean_supply_temp': df_clean['sup'].mean(),
        'mean_return_temp': df_clean['ret'].mean(),
        'anomalies_below_threshold': len(df_clean[df_clean['temp_diff'] < threshold_min]),
        'anomalies_above_threshold': len(df_clean[df_clean['temp_diff'] > threshold_max]),
    }
    stats['anomaly_rate'] = (stats['anomalies_below_threshold'] + stats['anomalies_above_threshold']) / stats['count'] * 100

    # Add time-based statistics
    df_clean.loc[:, 'hour'] = df_clean.index.hour
    df_clean.loc[:, 'weekday'] = df_clean.index.dayofweek
    df_clean.loc[:, 'month'] = df_clean.index.month

    # Print summary
    print(f"\nStatistics:")
    print(f"  Mean temp diff:   {stats['mean_temp_diff']:.2f} °C")
    print(f"  Std deviation:    {stats['std_temp_diff']:.2f} °C")
    print(f"  Range:            [{stats['min_temp_diff']:.2f}, {stats['max_temp_diff']:.2f}] °C")
    print(f"  Mean supply temp: {stats['mean_supply_temp']:.2f} °C")
    print(f"  Mean return temp: {stats['mean_return_temp']:.2f} °C")
    print(f"  Anomaly rate:     {stats['anomaly_rate']:.2f}%")

    results = {'stats': stats, 'data': df_clean}

    # Step 4: OUTPUT
    if config['output']['save_results']:
        save_results(results, config)

    if config['output']['generate_plots']:
        generate_plots(results, config)

    return results


def save_results(results, config):
    """Save analysis results"""
    output_dir = Path(config['output']['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    export_format = config['output']['export_format']

    print(f"\n{'='*60}")
    print(f"OUTPUT: Saving results to {output_dir}")
    print(f"{'='*60}\n")

    # Save statistics
    stats_df = pd.DataFrame([results['stats']])
    stats_file = output_dir / f'temp_diff_stats.{export_format}'

    if export_format == 'csv':
        stats_df.to_csv(stats_file, index=False)
    elif export_format == 'json':
        stats_df.to_json(stats_file, orient='records', indent=2)

    print(f"  [OK] {stats_file.name}")

    # Save timeseries
    ts_file = output_dir / f'temp_diff_timeseries.{export_format}'
    if export_format == 'csv':
        results['data'].to_csv(ts_file)
    elif export_format == 'json':
        results['data'].to_json(ts_file, orient='index', date_format='iso')

    print(f"  [OK] {ts_file.name}")


def generate_plots(results, config):
    """Generate comprehensive visualization plots"""
    output_dir = Path(config['output']['output_dir'])
    plot_format = config['output']['plot_format']

    print(f"\n{'='*60}")
    print(f"Generating plots")
    print(f"{'='*60}\n")

    df = results['data']
    stats = results['stats']

    # Plot 1: Timeseries with dual y-axis
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))

    # Supply and Return temperatures
    ax1 = axes[0]
    ax1.plot(df.index, df['sup'], label='Supply Temp', color='#e74c3c', linewidth=1.5, alpha=0.8)
    ax1.plot(df.index, df['ret'], label='Return Temp', color='#3498db', linewidth=1.5, alpha=0.8)
    ax1.set_ylabel('Temperature (°C)', fontsize=12, fontweight='bold')
    ax1.set_title('Supply and Return Temperature Over Time', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Temperature differential
    ax2 = axes[1]
    ax2.plot(df.index, df['temp_diff'], color='#9b59b6', linewidth=1, alpha=0.7)
    ax2.axhline(y=stats['mean_temp_diff'], color='#27ae60', linestyle='--', linewidth=2, label=f'Mean: {stats["mean_temp_diff"]:.2f}C')
    ax2.axhline(y=stats['median_temp_diff'], color='#f39c12', linestyle=':', linewidth=2, label=f'Median: {stats["median_temp_diff"]:.2f}C')
    ax2.fill_between(df.index, stats['q25_temp_diff'], stats['q75_temp_diff'], alpha=0.2, color='#9b59b6', label='IQR')
    ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Temperature Difference (C)', fontsize=12, fontweight='bold')
    ax2.set_title('Temperature Differential Over Time', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    filepath = output_dir / f'timeseries.{plot_format}'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {filepath.name}")

    # Plot 2: Distribution and Box Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Histogram
    axes[0].hist(df['temp_diff'], bins=60, edgecolor='black', alpha=0.7, color='#3498db')
    axes[0].axvline(x=stats['mean_temp_diff'], color='#e74c3c', linestyle='--', linewidth=2, label=f'Mean: {stats["mean_temp_diff"]:.2f}C')
    axes[0].axvline(x=stats['median_temp_diff'], color='#27ae60', linestyle=':', linewidth=2, label=f'Median: {stats["median_temp_diff"]:.2f}C')
    axes[0].set_xlabel('Temperature Difference (°C)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0].set_title('Distribution of Temperature Differential', fontsize=12, fontweight='bold')
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3, axis='y')

    # Box plot
    box = axes[1].boxplot(df['temp_diff'], patch_artist=True)
    box['boxes'][0].set_facecolor('#3498db')
    box['boxes'][0].set_alpha(0.7)
    axes[1].set_ylabel('Temperature Difference (°C)', fontsize=11, fontweight='bold')
    axes[1].set_title('Box Plot', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')

    # Cumulative distribution
    sorted_data = np.sort(df['temp_diff'])
    cumulative = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    axes[2].plot(sorted_data, cumulative, linewidth=2, color='#3498db')
    axes[2].set_xlabel('Temperature Difference (°C)', fontsize=11, fontweight='bold')
    axes[2].set_ylabel('Cumulative Probability', fontsize=11, fontweight='bold')
    axes[2].set_title('Cumulative Distribution Function', fontsize=12, fontweight='bold')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    filepath = output_dir / f'distribution.{plot_format}'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {filepath.name}")

    # Plot 3: Time-based analysis
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # By hour of day
    hourly = df.groupby('hour')['temp_diff'].agg(['mean', 'std'])
    axes[0, 0].bar(hourly.index, hourly['mean'], color='#3498db', alpha=0.7, edgecolor='black')
    axes[0, 0].errorbar(hourly.index, hourly['mean'], yerr=hourly['std'], fmt='none', ecolor='#e74c3c', capsize=3)
    axes[0, 0].set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Mean Temp Diff (C)', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Temperature Differential by Hour of Day', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    axes[0, 0].set_xticks(range(24))

    # By day of week
    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekly = df.groupby('weekday')['temp_diff'].agg(['mean', 'std'])
    axes[0, 1].bar(range(7), weekly['mean'], color='#27ae60', alpha=0.7, edgecolor='black')
    axes[0, 1].errorbar(range(7), weekly['mean'], yerr=weekly['std'], fmt='none', ecolor='#e74c3c', capsize=3)
    axes[0, 1].set_xlabel('Day of Week', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Mean Temp Diff (C)', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Temperature Differential by Day of Week', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    axes[0, 1].set_xticks(range(7))
    axes[0, 1].set_xticklabels(weekday_names)

    # By month
    monthly = df.groupby('month')['temp_diff'].agg(['mean', 'std'])
    axes[1, 0].bar(monthly.index, monthly['mean'], color='#f39c12', alpha=0.7, edgecolor='black')
    axes[1, 0].errorbar(monthly.index, monthly['mean'], yerr=monthly['std'], fmt='none', ecolor='#e74c3c', capsize=3)
    axes[1, 0].set_xlabel('Month', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Mean Temp Diff (C)', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Temperature Differential by Month', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    axes[1, 0].set_xticks(range(1, 13))

    # Scatter: Supply vs Return
    axes[1, 1].scatter(df['sup'], df['ret'], alpha=0.3, s=10, c=df['temp_diff'], cmap='RdYlBu_r')
    axes[1, 1].plot([df['sup'].min(), df['sup'].max()], [df['sup'].min(), df['sup'].max()],
                    'k--', linewidth=2, label='Perfect Match')
    axes[1, 1].set_xlabel('Supply Temperature (C)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Return Temperature (C)', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Supply vs Return Temperature', fontsize=12, fontweight='bold')
    axes[1, 1].legend(fontsize=9)
    axes[1, 1].grid(True, alpha=0.3)
    cbar = plt.colorbar(axes[1, 1].collections[0], ax=axes[1, 1])
    cbar.set_label('Temp Diff (C)', fontsize=10)

    plt.tight_layout()
    filepath = output_dir / f'time_analysis.{plot_format}'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {filepath.name}")

    # Plot 4: Heatmap - Hour vs Day of Week
    fig, ax = plt.subplots(figsize=(12, 8))

    pivot_data = df.pivot_table(values='temp_diff', index='hour', columns='weekday', aggfunc='mean')
    im = ax.imshow(pivot_data, cmap='RdYlBu_r', aspect='auto', interpolation='nearest')

    ax.set_xticks(range(7))
    ax.set_xticklabels(weekday_names, fontsize=10)
    ax.set_yticks(range(24))
    ax.set_yticklabels(range(24), fontsize=8)
    ax.set_xlabel('Day of Week', fontsize=12, fontweight='bold')
    ax.set_ylabel('Hour of Day', fontsize=12, fontweight='bold')
    ax.set_title('Temperature Differential Heatmap (Hour vs Day of Week)', fontsize=14, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Mean Temp Diff (C)', fontsize=11)

    plt.tight_layout()
    filepath = output_dir / f'heatmap.{plot_format}'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {filepath.name}")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Secondary Loop Temperature Differential Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python app.py brick_model.ttl timeseries_data.csv
  
  # With config
  python app.py model.ttl data.csv --config config.yaml
  
  # Custom output
  python app.py model.ttl data.csv --output-dir ./results
        """
    )

    parser.add_argument('brick_model', help='Path to Brick model (.ttl)')
    parser.add_argument('timeseries_data', help='Path to timeseries data (.csv)')
    parser.add_argument('--config', help='Config file (optional)', default=None)
    parser.add_argument('--output-dir', help='Output directory (optional)', default=None)

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    if args.output_dir:
        config['output']['output_dir'] = args.output_dir

    # Run analysis
    print(f"\n{'='*60}")
    print(f"Secondary Loop Temperature Differential Analysis")
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
