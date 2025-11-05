# Application Development Tutorial - Step 7: Plotly HTML Visualization

In this step, you'll create interactive HTML visualizations using Plotly that users can open in web browsers.

## Goal of This Step

- Create interactive plots with zoom, pan, and hover
- Generate standalone HTML files
- Build comprehensive dashboards
- No server required - just open in browser!

---

## Step 7.1: Add Plotly Imports

Add these imports to `app.py`:

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
```

---

## Step 7.2: Implement generate_plotly_html()

Create the main Plotly function:

```python
def generate_plotly_html(results, config):
    """Generate interactive Plotly HTML visualizations"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"PLOTLY: Generating interactive HTML visualizations")
    print(f"{'='*60}\n")

    df = results["data"]
    stats = results["stats"]

    # Generate visualizations
    create_dashboard(df, stats, output_dir)
    create_timeseries(df, stats, output_dir)
    create_heatmap(df, output_dir)
    create_boxplot(df, stats, output_dir)

    print(f"\n[OK] All HTML visualizations generated")
```

---

## Step 7.3: Interactive Dashboard

Create a comprehensive dashboard with multiple subplots:

```python
def create_dashboard(df, stats, output_dir):
    """Create interactive dashboard with multiple views"""
    # Create figure with subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "Supply & Return Temperatures",
            "Temperature Differential",
            "Distribution",
            "Hourly Pattern",
            "Box Plot by Hour",
            "Statistics Summary"
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "histogram"}, {"type": "bar"}],
            [{"type": "box"}, {"type": "table"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10
    )

    # 1. Supply & Return Temperatures
    fig.add_trace(
        go.Scatter(x=df.index, y=df["supply"], name="Supply",
                   line=dict(color="#e74c3c")),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["return"], name="Return",
                   line=dict(color="#3498db")),
        row=1, col=1
    )

    # 2. Temperature Differential
    fig.add_trace(
        go.Scatter(x=df.index, y=df["temp_diff"], name="Temp Diff",
                   line=dict(color="#9b59b6")),
        row=1, col=2
    )

    # 3. Distribution
    fig.add_trace(
        go.Histogram(x=df["temp_diff"], name="Distribution",
                     marker=dict(color="#3498db")),
        row=2, col=1
    )

    # 4. Hourly Pattern
    hourly = df.groupby("hour")["temp_diff"].mean()
    fig.add_trace(
        go.Bar(x=hourly.index, y=hourly.values, name="Hourly Avg",
               marker=dict(color="#27ae60")),
        row=2, col=2
    )

    # 5. Box Plot by Hour
    for hour in sorted(df["hour"].unique()):
        hour_data = df[df["hour"] == hour]["temp_diff"]
        fig.add_trace(
            go.Box(y=hour_data, name=str(hour), showlegend=False),
            row=3, col=1
        )

    # 6. Statistics Table
    stats_data = [
        ["Mean", f"{stats['mean_temp_diff']:.2f} °C"],
        ["Std Dev", f"{stats['std_temp_diff']:.2f} °C"],
        ["Min", f"{stats['min_temp_diff']:.2f} °C"],
        ["Max", f"{stats['max_temp_diff']:.2f} °C"],
        ["Anomalies", f"{stats['anomaly_rate']:.2f}%"]
    ]
    fig.add_trace(
        go.Table(
            header=dict(values=["Metric", "Value"], fill_color="lightgray"),
            cells=dict(values=list(zip(*stats_data)), fill_color="white")
        ),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        title_text="Temperature Analysis Dashboard",
        showlegend=True,
        height=1200,
        template="plotly_white"
    )

    # Save
    filepath = output_dir / "dashboard_interactive.html"
    fig.write_html(filepath)
    print(f"  [OK] {filepath.name}")
```

**Understanding**:
- `make_subplots()` - Create grid of plots
- `add_trace()` - Add data to specific subplot
- `row=, col=` - Position in grid
- `write_html()` - Save as standalone HTML

---

## Step 7.4: Detailed Time-Series

Create an interactive time-series with dual y-axes:

```python
def create_timeseries(df, stats, output_dir):
    """Create detailed interactive time-series"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Temperature traces
    fig.add_trace(
        go.Scatter(x=df.index, y=df["supply"], name="Supply Temp",
                   line=dict(color="#e74c3c", width=2),
                   hovertemplate="Time: %{x}<br>Supply: %{y:.2f}°C<extra></extra>"),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=df["return"], name="Return Temp",
                   line=dict(color="#3498db", width=2),
                   hovertemplate="Time: %{x}<br>Return: %{y:.2f}°C<extra></extra>"),
        secondary_y=False
    )

    # Temperature difference on secondary axis
    fig.add_trace(
        go.Scatter(x=df.index, y=df["temp_diff"], name="Temp Diff",
                   line=dict(color="#9b59b6", width=2, dash="dash"),
                   hovertemplate="Time: %{x}<br>Diff: %{y:.2f}°C<extra></extra>"),
        secondary_y=True
    )

    # Add mean line
    fig.add_hline(
        y=stats["mean_temp_diff"],
        line_dash="dash",
        line_color="#27ae60",
        annotation_text=f"Mean: {stats['mean_temp_diff']:.2f}°C",
        secondary_y=True
    )

    # Update axes
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
    fig.update_yaxes(title_text="Temperature Difference (°C)", secondary_y=True)

    fig.update_layout(
        title="Interactive Temperature Analysis",
        hovermode="x unified",
        template="plotly_white",
        height=600
    )

    filepath = output_dir / "timeseries_interactive.html"
    fig.write_html(filepath)
    print(f"  [OK] {filepath.name}")
```

**Interactive Features**:
- **Hover**: See exact values
- **Zoom**: Box select or scroll
- **Pan**: Click and drag
- **Legend**: Click to show/hide traces
- **Reset**: Double-click to reset view

---

## Step 7.5: Interactive Heatmap

```python
def create_heatmap(df, output_dir):
    """Create interactive heatmap"""
    # Prepare data
    pivot = df.pivot_table(
        values="temp_diff",
        index="hour",
        columns="weekday",
        aggfunc="mean"
    )

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        y=list(range(24)),
        colorscale="RdYlBu_r",
        hovertemplate="Weekday: %{x}<br>Hour: %{y}<br>Temp Diff: %{z:.2f}°C<extra></extra>",
        colorbar=dict(title="Mean Temp<br>Diff (°C)")
    ))

    fig.update_layout(
        title="Temperature Differential Patterns",
        xaxis_title="Day of Week",
        yaxis_title="Hour of Day",
        template="plotly_white",
        height=700
    )

    filepath = output_dir / "heatmap_interactive.html"
    fig.write_html(filepath)
    print(f"  [OK] {filepath.name}")
```

---

## Step 7.6: Box Plot

```python
def create_boxplot(df, stats, output_dir):
    """Create interactive box plot"""
    fig = go.Figure()

    # Add box plot
    fig.add_trace(go.Box(
        y=df["temp_diff"],
        name="Temperature Difference",
        marker_color="#3498db",
        boxmean="sd"  # Show mean and standard deviation
    ))

    # Add statistics annotations
    fig.add_annotation(
        text=f"Mean: {stats['mean_temp_diff']:.2f}°C<br>"
             f"Median: {stats['median_temp_diff']:.2f}°C<br>"
             f"Std: {stats['std_temp_diff']:.2f}°C",
        xref="paper", yref="paper",
        x=0.98, y=0.98,
        showarrow=False,
        bgcolor="lightgray",
        bordercolor="black",
        borderwidth=1
    )

    fig.update_layout(
        title="Temperature Differential Distribution",
        yaxis_title="Temperature Difference (°C)",
        template="plotly_white",
        height=600
    )

    filepath = output_dir / "boxplot_interactive.html"
    fig.write_html(filepath)
    print(f"  [OK] {filepath.name}")
```

---

## Step 7.7: Test Plotly Visualizations

```python
def test_plotly():
    """Test Plotly HTML generation"""
    from hhw_brick.applications.my_first_app.app import analyze, load_config

    fixtures = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"
    model_file = fixtures / "Brick_Model_File" / "building_29.ttl"
    data_file = fixtures / "TimeSeriesData" / "29hhw_system_data.csv"

    config = load_config()
    config["output"]["output_dir"] = "./test_plotly"
    config["output"]["generate_plotly_html"] = True

    results = analyze(str(model_file), str(data_file), config)

    if results:
        print("\n✅ HTML visualizations generated!")
        print(f"Open files in browser:")
        print(f"  - dashboard_interactive.html")
        print(f"  - timeseries_interactive.html")
        print(f"  - heatmap_interactive.html")
        print(f"  - boxplot_interactive.html")

if __name__ == "__main__":
    test_plotly()
```

---

## Step 7.8: Update Config

In `config.yaml`:

```yaml
output:
  generate_plotly_html: true  # Enable/disable Plotly HTML
```

---

## Checkpoint

Before proceeding, verify:

- [x] Plotly imports added
- [x] generate_plotly_html() function created
- [x] Dashboard with 6 subplots
- [x] Interactive time-series
- [x] Interactive heatmap
- [x] Box plot with statistics
- [x] HTML files open in browser
- [x] Interactive features work (zoom, pan, hover)

---

## Next Steps

✅ Plotly visualization complete!

👉 Continue to [Step 8: Testing Your Application](./step-08-testing.md)

---

## Plotly Features

### Interactive Controls

All Plotly plots have:
- 🔍 **Zoom**: Box select or scroll wheel
- 👆 **Pan**: Click and drag
- 📊 **Hover**: Detailed tooltips
- 👁️ **Toggle**: Click legend to show/hide
- 📸 **Export**: Camera icon to save as PNG
- 🔄 **Reset**: Double-click to reset

### Customization

```python
# Change colors
line=dict(color="#FF6B6B", width=3)

# Change hover
hovertemplate="<b>%{x}</b><br>Value: %{y:.2f}<extra></extra>"

# Change layout
fig.update_layout(template="plotly_dark")  # Dark theme
```

---

## Summary

You've created interactive visualizations:

✅ **Dashboard**: 6-panel comprehensive view  
✅ **Time-Series**: Dual y-axes with zoom  
✅ **Heatmap**: Pattern analysis  
✅ **Box Plot**: Statistical distribution  
✅ **Standalone HTML**: No server needed  
✅ **Fully Interactive**: Zoom, pan, hover  

Next: Testing and deployment!
