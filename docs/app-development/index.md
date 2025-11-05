
Learn to create HHW Brick analytics applications through hands-on, step-by-step tutorials.

## Tutorial Structure

This tutorial is divided into logical steps, each focusing on one aspect of application development.

### 📚 Tutorial Steps

| Step | Topic | Time | Difficulty |
|------|-------|------|------------|
| [Step 1](./step-01-structure.md) | Create Application Structure | 10 min | ⭐ Easy |
| [Step 2](./step-02-load-config.md) | Write load_config Function | 15 min | ⭐ Easy |
| [Step 3](./step-03-sparql-qualify.md) | SPARQL Query & qualify Function | 30 min | ⭐⭐ Medium |
| [Step 4](./step-04-analyze-part1.md) | analyze Function - Data Loading | 20 min | ⭐⭐ Medium |
| [Step 5](./step-05-analyze-part2.md) | analyze Function - Analysis Logic | 25 min | ⭐⭐ Medium |
| [Step 6](./step-06-visualization-matplotlib.md) | Matplotlib Visualization | 20 min | ⭐⭐ Medium |
| [Step 7](./step-07-visualization-plotly.md) | Plotly HTML Visualization | 30 min | ⭐⭐⭐ Advanced |
| [Step 8](./step-08-testing.md) | Testing Your Application | 20 min | ⭐⭐ Medium |
| [Step 9](./step-09-deployment.md) | Deployment & Integration | 15 min | ⭐ Easy |

**Total Time**: ~3 hours

---

## What You'll Build

By the end of this tutorial, you'll have built a complete analytics application that:

✅ **Qualifies** buildings based on required sensors  
✅ **Analyzes** time-series data from Brick models  
✅ **Generates** statistical reports  
✅ **Creates** visualizations (PNG and interactive HTML)  
✅ **Integrates** with the HHW Brick framework  

---

## Prerequisites

### Required Knowledge

- **Python Basics**: Variables, functions, file I/O
- **Command Line**: Navigate directories, run Python scripts
- **YAML**: Basic configuration file syntax

**Note**: No prior experience with Brick Schema or SPARQL needed - we'll teach you!

### Software Requirements

```bash
# Python 3.8 or higher
python --version

# HHW Brick package installed
pip install -e /path/to/HHW_brick

# Or install dependencies
pip install pandas numpy matplotlib seaborn plotly rdflib brickschema pyyaml
```

---

## Tutorial Learning Path

### 🎯 Path 1: Quick Start (Minimum Viable App)

Build a working app as fast as possible:

1. [Step 1](./step-01-structure.md) - Structure
2. [Step 2](./step-02-load-config.md) - Config loading
3. [Step 3](./step-03-sparql-qualify.md) - Qualification
4. [Step 4](./step-04-analyze-part1.md) - Basic analysis
5. [Step 8](./step-08-testing.md) - Test it

**Time**: ~1.5 hours  
**Result**: Working application with basic functionality

### 🎓 Path 2: Complete Tutorial (Recommended)

Follow all steps for full understanding:

1-9 in order

**Time**: ~3 hours  
**Result**: Production-ready application with all features

### 🚀 Path 3: Advanced (Custom Applications)

After completing the tutorial:

- Modify existing applications
- Create complex SPARQL queries
- Implement custom analytics
- Add advanced visualizations

---

## Application Example

Here's what you'll build - a temperature differential analysis app:

**Input**:
- Brick model (.ttl file) with temperature sensors
- Time-series data (.csv file) with sensor readings

**Process**:
1. Check if building has supply and return temperature sensors
2. Load and map sensor data
3. Calculate temperature differential
4. Compute statistics (mean, std, range, etc.)
5. Generate visualizations

**Output**:
- CSV files with statistics and processed data
- PNG plots (timeseries, histograms, heatmaps)
- Interactive HTML dashboards

**See it in action**: `hhw_brick/applications/secondary_loop_temp_diff/`

---

## How to Use This Tutorial

Each step follows this structure:

1. **Goal**: What you'll accomplish
2. **Code**: Copy-paste ready code snippets
3. **Explanation**: Understanding what the code does
4. **Test**: Verify your implementation works
5. **Checkpoint**: Ensure you're ready for the next step

**Icons Used**:

- 💡 **Tip**: Helpful suggestions
- ⚠️ **Warning**: Common pitfalls
- 📚 **Resource**: External learning materials
- ✅ **Best Practice**: Recommended approaches

---

## Getting Help

**If code doesn't work**:

1. Check the **Common Issues** section in each step
2. Compare with example applications in `hhw_brick/applications/`
3. Run the test scripts provided

**Resources**:

- [Brick Schema Docs](https://docs.brickschema.org/)
- [SPARQL Tutorial](https://www.w3.org/TR/sparql11-query/)
- [GitHub Issues](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues)

---

## Example Applications

Study these working applications in `hhw_brick/applications/` for reference:

**secondary_loop_temp_diff** (⭐⭐ Medium):
- Simple SPARQL query
- Basic statistical analysis  
- Standard visualization patterns

**primary_loop_temp_diff** (⭐⭐ Medium):
- Filtered SPARQL queries
- Anomaly detection
- Multiple visualization types

---

## Tips for Success

### ✅ Do's

1. **Read the explanations**: Don't just copy code, understand it
2. **Run tests frequently**: Catch errors early
3. **Start simple**: Get basics working before adding features
4. **Study examples**: Look at existing applications
5. **Use version control**: Git commit after each step

### ❌ Don'ts

1. **Don't skip steps**: Each builds on the previous
2. **Don't ignore errors**: Fix them before proceeding
3. **Don't customize prematurely**: Finish tutorial first, then customize
4. **Don't skip testing**: Tests ensure your code works
5. **Don't forget documentation**: Update README as you go

---

## After Completing the Tutorial

### Next Steps

1. **Customize**: Modify your app for specific use cases
2. **Create new apps**: Build applications for different analyses
3. **Contribute**: Share your applications with the community
4. **Advanced topics**: Explore complex SPARQL, custom analytics

### Share Your Work

- Submit pull requests to add your app to HHW Brick
- Write blog posts about your application
- Help others in GitHub Issues

---

## Ready to Start?

**🚀 Let's build your first HHW Brick application!**

👉 **Begin with [Step 1: Create Application Structure](./step-01-structure.md)**
