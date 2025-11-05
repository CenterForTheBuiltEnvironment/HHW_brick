# Application Development Tutorial - Overview

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
- **YAML**: Basic configuration file syntax (we'll teach SPARQL!)

### No Experience Needed With

- ❌ Brick Schema (we'll teach you!)
- ❌ SPARQL (covered in Step 3)
- ❌ RDF/Semantic Web (explained as we go)
- ❌ Advanced visualization (templates provided)

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

### Reading the Steps

Each step follows this structure:

1. **Goal**: What you'll accomplish
2. **Code**: Copy-paste ready code snippets
3. **Explanation**: Understanding what the code does
4. **Test**: Verify your implementation works
5. **Checkpoint**: Ensure you're ready for the next step

### Code Blocks

**📋 Copy this** - Code ready to paste:
```python
# This code is ready to use
def example():
    return "Hello World"
```

**💡 Explanation** - Understanding code:
```python
# This explains the logic
# Variables: x (input), y (output)
y = x * 2  # Double the input
```

**⚠️ Common mistakes**:
```python
# ❌ Wrong
config = load_config

# ✅ Correct
config = load_config()  # Don't forget ()
```

### Tips Throughout

- 💡 **Tip**: Helpful suggestions
- ⚠️ **Warning**: Common pitfalls
- 📚 **Resource**: External learning materials
- ✅ **Best Practice**: Recommended approaches
- ❌ **Avoid**: What not to do

---

## Getting Help

### During the Tutorial

**Issue**: Code doesn't work  
**Solution**:
1. Check the **Common Issues** section in each step
2. Compare your code with example applications in `hhw_brick/applications/`
3. Run the test scripts provided in each step

**Issue**: Concept unclear  
**Solution**:
1. Review the **Understanding** sections
2. Check linked resources
3. Look at working examples: `primary_loop_temp_diff` or `secondary_loop_temp_diff`

### After the Tutorial

- **Brick Schema**: https://docs.brickschema.org/
- **SPARQL**: https://www.w3.org/TR/sparql11-query/
- **GitHub Issues**: https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues

---

## Example Applications

Study these working applications for reference:

### 📁 secondary_loop_temp_diff

**Location**: `hhw_brick/applications/secondary_loop_temp_diff/`

**What it does**: Analyzes temperature differential in secondary hot water loops

**Complexity**: ⭐⭐ Medium

**Learn from it**:
- Simple SPARQL query
- Basic statistical analysis
- Standard visualization patterns

### 📁 primary_loop_temp_diff

**Location**: `hhw_brick/applications/primary_loop_temp_diff/`

**What it does**: Analyzes temperature differential in primary loops with boilers

**Complexity**: ⭐⭐ Medium

**Learn from it**:
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

👉 **Begin with [Step 1: Create Application Structure](./step-01-structure.md)**

---

## Questions Before Starting?

**Q: Do I need to know Brick Schema?**  
A: No! We'll teach you the essentials as you build.

**Q: How much Python experience do I need?**  
A: Basic knowledge (variables, functions, loops). If you can follow Python tutorials, you're ready.

**Q: Can I skip visualization steps?**  
A: You need at least basic visualization. Steps 6-7 can be simplified.

**Q: How long until I have a working app?**  
A: Following Path 1 (Quick Start), about 1.5 hours.

**Q: Can I build my own app idea while following tutorial?**  
A: Yes! Follow the steps but adapt them to your needs. The structure works for any analysis.

---

**🚀 Let's build your first HHW Brick application!**

👉 [Start Tutorial - Step 1](./step-01-structure.md)
