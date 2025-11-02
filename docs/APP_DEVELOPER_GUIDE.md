# App Developer Guide - HHW Brick Application

**Version**: 1.0.0  
**Last Updated**: October 22, 2025  
**Audience**: Developers who want to create custom analytics applications

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Framework Overview](#framework-overview)
3. [Quick Start](#quick-start)
4. [BaseApp API Reference](#baseapp-api-reference)
5. [SPARQL Query Patterns](#sparql-query-patterns)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Introduction

The HHW Brick Application framework allows you to create custom analytics applications that analyze Brick models of hot water systems. This guide will teach you how to:

- Create custom apps using the `BaseApp` class
- Query Brick models using SPARQL
- Process and export results
- Integrate with the CLI

### What is an App?

An **App** is a Python class that:
1. Inherits from `BaseApp`
2. Implements an `analyze()` method
3. Queries Brick models using SPARQL
4. Returns structured results

### Prerequisites

- Python 3.8+
- Basic understanding of Brick Schema
- Familiarity with SPARQL (helpful but not required)
- HHW Brick Application installed

---

## 🏗️ Framework Overview

### Architecture

```
User runs CLI → AppRunner → Your App → SPARQL Query → Brick Model
                                    ↓
                              Results → Export (CSV/JSON)
```

### Key Components

**BaseApp** - Base class for all apps
- Provides common functionality
- Handles Brick model loading
- Manages namespaces
- Provides helper methods

**AppRegistry** - Manages app registration
- Discovers available apps
- Provides app metadata
- Handles app instantiation

**AppRunner** - Executes apps
- Loads Brick models
- Runs apps
- Handles output

### App Lifecycle

```python
1. App is registered (via @register_app decorator or manual registration)
2. User runs app via CLI: hhw-brick apps run <app_name> <model.ttl>
3. AppRunner loads the Brick model
4. AppRunner instantiates your app
5. Your analyze() method is called
6. Results are returned and optionally exported
```

---

## 🚀 Quick Start

### Step 1: Create Your First App

Create a new file `my_first_app.py`:

```python
from hhw_brick.analytics.core.base_app import BaseApp, register_app
from rdflib import Namespace

@register_app(
    name="my_first_app",
    description="My first Brick analytics app",
    version="1.0.0"
)
class MyFirstApp(BaseApp):
    """A simple app that counts buildings in the model."""
    
    def analyze(self, graph, building_name=None, **kwargs):
        """
        Analyze the Brick model.
        
        Args:
            graph: rdflib.Graph - The loaded Brick model
            building_name: str - Optional building name filter
            **kwargs: Additional arguments
            
        Returns:
            dict: Analysis results
        """
        # Define SPARQL query
        query = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        
        SELECT ?building
        WHERE {
            ?building a brick:Building .
        }
        """
        
        # Execute query
        results = graph.query(query)
        
        # Process results
        buildings = [str(row.building) for row in results]
        
        # Return structured results
        return {
            'building_count': len(buildings),
            'buildings': buildings
        }
```

### Step 2: Run Your App

```bash
# Run via CLI
hhw-brick apps run my_first_app building_105.ttl

# Run with output file
hhw-brick apps run my_first_app building_105.ttl -o results.json
```

### Step 3: Use in Python

```python
from my_first_app import MyFirstApp
from rdflib import Graph

# Load Brick model
graph = Graph()
graph.parse("building_105.ttl", format="turtle")

# Create app instance
app = MyFirstApp()

# Run analysis
results = app.analyze(graph)

print(f"Found {results['building_count']} buildings")
```

---

## 📖 BaseApp API Reference

### Class: BaseApp

**Location**: `hhw_brick.analytics.core.base_app`

#### Constructor

```python
def __init__(self, config=None):
    """
    Initialize the app.
    
    Args:
        config (dict, optional): Configuration dictionary
    """
```

#### Methods

##### analyze()

**Abstract method - MUST be implemented by your app**

```python
def analyze(self, graph, building_name=None, **kwargs):
    """
    Analyze the Brick model.
    
    Args:
        graph (rdflib.Graph): The loaded Brick model
        building_name (str, optional): Building name filter
        **kwargs: Additional arguments
        
    Returns:
        dict: Analysis results
        
    Raises:
        NotImplementedError: If not implemented by subclass
    """
```

##### get_buildings()

```python
def get_buildings(self, graph):
    """
    Get all buildings in the model.
    
    Args:
        graph (rdflib.Graph): The Brick model
        
    Returns:
        list: List of building URIs
    """
```

##### get_points()

```python
def get_points(self, graph, point_class=None):
    """
    Get all points in the model.
    
    Args:
        graph (rdflib.Graph): The Brick model
        point_class (str, optional): Filter by point class
        
    Returns:
        list: List of point URIs
    """
```

##### get_equipment()

```python
def get_equipment(self, graph, equipment_class=None):
    """
    Get all equipment in the model.
    
    Args:
        graph (rdflib.Graph): The Brick model
        equipment_class (str, optional): Filter by equipment class
        
    Returns:
        list: List of equipment URIs
    """
```

#### Properties

##### brick (Namespace)

```python
@property
def brick(self):
    """Brick Schema namespace."""
    return Namespace("https://brickschema.org/schema/Brick#")
```

##### rdfs (Namespace)

```python
@property
def rdfs(self):
    """RDFS namespace."""
    return RDFS
```

##### rdf (Namespace)

```python
@property
def rdf(self):
    """RDF namespace."""
    return RDF
```

---

## 🔍 SPARQL Query Patterns

### Common Query Patterns for Brick Models

#### Pattern 1: Get All Points

```python
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?point ?pointType
WHERE {
    ?point a/rdfs:subClassOf* brick:Point .
    ?point a ?pointType .
}
"""
```

#### Pattern 2: Get Equipment with Points

```python
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?equipment ?point ?pointType
WHERE {
    ?equipment brick:hasPoint ?point .
    ?point a ?pointType .
}
"""
```

#### Pattern 3: Get System Topology

```python
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?system ?equipment
WHERE {
    ?system brick:hasPart ?equipment .
    ?equipment a/rdfs:subClassOf* brick:Equipment .
}
"""
```

#### Pattern 4: Get Relationships

```python
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?source ?target
WHERE {
    ?source brick:feeds ?target .
}
"""
```

#### Pattern 5: Filter by Building

```python
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX hhws: <https://example.org/hhws#>

SELECT ?point
WHERE {
    hhws:building105 brick:hasPart* ?point .
    ?point a/rdfs:subClassOf* brick:Point .
}
"""
```

---

## ✅ Best Practices

### 1. Return Structured Data

**Good:**
```python
def analyze(self, graph, **kwargs):
    return {
        'summary': {'total_points': 42, 'total_equipment': 5},
        'points': [...],
        'equipment': [...]
    }
```

**Bad:**
```python
def analyze(self, graph, **kwargs):
    return "Found 42 points and 5 equipment"  # Hard to process!
```

### 2. Handle Errors Gracefully

```python
def analyze(self, graph, **kwargs):
    try:
        results = graph.query(query)
        return self._process_results(results)
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }
```

### 3. Use Efficient Queries

**Good:**
```python
# Get everything in one query
query = """
SELECT ?equipment ?point ?pointType
WHERE {
    ?equipment brick:hasPoint ?point .
    ?point a ?pointType .
}
"""
```

**Bad:**
```python
# Multiple queries (slow!)
for equipment in get_equipment():
    for point in get_points_for_equipment(equipment):
        ...  # Inefficient!
```

### 4. Document Your App

```python
@register_app(
    name="my_app",
    description="Clear description of what this app does",
    version="1.0.0",
    author="Your Name",
    requires=["pandas", "matplotlib"]  # Optional dependencies
)
class MyApp(BaseApp):
    """
    Detailed docstring explaining:
    - What the app analyzes
    - What results it returns
    - Example usage
    """
    
    def analyze(self, graph, **kwargs):
        """
        Clear docstring for analyze method.
        
        Args:
            graph: The Brick model
            param1: What this parameter does
            
        Returns:
            dict with keys:
            - 'key1': Description
            - 'key2': Description
        """
```

### 5. Make Results Exportable

Return data that can be easily converted to CSV/JSON:

```python
# Pandas DataFrame (auto-converts to CSV)
import pandas as pd

def analyze(self, graph, **kwargs):
    data = [...]
    df = pd.DataFrame(data)
    return {
        'dataframe': df,
        'summary': {...}
    }
```

---

## 🎨 Common Patterns

### Pattern: Data Extraction App

```python
@register_app(name="data_extractor")
class DataExtractorApp(BaseApp):
    """Extract specific data from Brick model."""
    
    def analyze(self, graph, **kwargs):
        # Query
        results = self._query_data(graph)
        
        # Transform
        data = self._transform_results(results)
        
        # Export-ready format
        return {
            'data': data,
            'count': len(data)
        }
```

### Pattern: Analytics App

```python
@register_app(name="performance_analyzer")
class PerformanceAnalyzerApp(BaseApp):
    """Calculate performance metrics."""
    
    def analyze(self, graph, **kwargs):
        # Get data
        equipment = self._get_equipment(graph)
        points = self._get_points(graph)
        
        # Calculate metrics
        metrics = self._calculate_metrics(equipment, points)
        
        # Return analysis
        return {
            'metrics': metrics,
            'recommendations': self._generate_recommendations(metrics)
        }
```

### Pattern: Validation App

```python
@register_app(name="topology_validator")
class TopologyValidatorApp(BaseApp):
    """Validate system topology."""
    
    def analyze(self, graph, **kwargs):
        # Run checks
        checks = [
            self._check_required_equipment(graph),
            self._check_relationships(graph),
            self._check_completeness(graph)
        ]
        
        # Aggregate results
        return {
            'valid': all(c['passed'] for c in checks),
            'checks': checks
        }
```

---

## 🐛 Troubleshooting

### Issue: Query Returns No Results

**Problem**: Your SPARQL query returns empty results

**Solutions**:
1. Check namespace prefixes
2. Verify the data exists in the model
3. Test query in SPARQL editor
4. Check for typos in class names

### Issue: Import Errors

**Problem**: Cannot import BaseApp or other components

**Solutions**:
```bash
# Reinstall package
pip install -e .

# Check installation
python -c "from hhw_brick.analytics.core.base_app import BaseApp"
```

### Issue: App Not Discovered

**Problem**: Your app doesn't appear in `hhw-brick apps list`

**Solutions**:
1. Ensure you used `@register_app` decorator
2. Check app is in correct location
3. Verify no syntax errors in file

---

## 📚 Next Steps

1. **Read the Tutorials** - Step-by-step examples
   - `tutorials/01_hello_world_app.md`
   - `tutorials/02_point_extraction_app.md`
   - `tutorials/03_equipment_analysis_app.md`

2. **Study Demo Apps** - Real working examples
   - `analytics/apps/available_points.py`
   - `analytics/apps/equipment_analysis.py`

3. **Review Examples** - Additional code samples
   - `examples/custom_apps/`

4. **Check API Reference** - Complete API documentation
   - `docs/API_REFERENCE.md`

---

## 🤝 Contributing

Want to contribute your app to the project?

1. Create your app following these guidelines
2. Add tests
3. Document thoroughly
4. Submit a pull request

---

**Questions?** Open an issue on GitHub or check the documentation.

**Happy coding!** 🚀

