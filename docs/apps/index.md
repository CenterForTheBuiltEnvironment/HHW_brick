# Available Applications

HHW Brick includes portable analytics applications that work across different buildings using semantic queries.

## Application List

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin: 2rem 0;">

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">🔄 Secondary Loop Temperature Analysis</h3>
    <p><strong>Status</strong>: Production Ready</p>
    <p><strong>Complexity</strong>: ⭐⭐ Medium</p>
    <p>Analyzes temperature differentials in secondary hot water loops to identify efficiency issues and operating patterns.</p>
    <a href="secondary-loop/" style="color: #3f51b5; font-weight: bold;">View Details →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">🔥 Primary Loop Temperature Analysis</h3>
    <p><strong>Status</strong>: Production Ready</p>
    <p><strong>Complexity</strong>: ⭐⭐ Medium</p>
    <p>Analyzes temperature differentials in primary loops with boilers, including anomaly detection and performance metrics.</p>
    <a href="primary-loop/" style="color: #3f51b5; font-weight: bold;">View Details →</a>
  </div>

</div>

---

## How Applications Work

**Qualification**: Each app checks if a building has required sensors using SPARQL queries.

**Analysis**: Apps automatically discover sensors in Brick models and map them to time-series data.

**Outputs**: Statistical reports, CSV files, and interactive visualizations (PNG + HTML).

---

## Running Applications

```python
from hhw_brick import apps

# Load application
app = apps.load_app("secondary_loop_temp_diff")

# Check qualification
if app.qualify("building.ttl"):
    # Run analysis
    results = app.analyze("building.ttl", "timeseries.csv", config)
```

See [User Guide - Running Apps](../user-guide/applications/running-apps/) for detailed instructions.

---

## Creating Your Own App

Want to build custom analytics? Follow our step-by-step tutorial:

👉 [Developer Guide](../app-development/)

---

## Application Status Legend

- ✅ **Production Ready**: Tested on 100+ buildings
- 🧪 **Beta**: Under active development
- 📋 **Planned**: Coming soon
