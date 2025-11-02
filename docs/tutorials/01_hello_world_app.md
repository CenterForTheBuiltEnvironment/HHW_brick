# Tutorial 1: Hello World App

**Duration**: 15 minutes  
**Difficulty**: Beginner  
**Goal**: Create your first Brick analytics app

---

## What You'll Build

A simple app that:
- Counts buildings in a Brick model
- Lists all building names
- Exports results to JSON

---

## Prerequisites

- HHWS Brick Application installed
- A Brick model file (e.g., `building_105.ttl`)
- Basic Python knowledge

---

## Step 1: Create App File

Create a new file called `hello_world_app.py`:

```python
"""
Hello World App - Tutorial 1
A simple app that counts and lists buildings.
"""

from hhw_brick.analytics.core.base_app import BaseApp, register_app
from rdflib import Namespace

# Register your app
@register_app(
    name="hello_world",
    description="Counts and lists all buildings in the model",
    version="1.0.0"
)
class HelloWorldApp(BaseApp):
    """My first Brick analytics app!"""
    
    def analyze(self, graph, building_name=None, **kwargs):
        """
        Count and list all buildings.
        
        Args:
            graph: The Brick model (rdflib.Graph)
            building_name: Optional filter (not used in this example)
            
        Returns:
            dict: Contains building count and list
        """
        # Step 1: Define SPARQL query
        query = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?building ?label
        WHERE {
            ?building a brick:Building .
            OPTIONAL { ?building rdfs:label ?label }
        }
        """
        
        # Step 2: Execute query
        results = graph.query(query)
        
        # Step 3: Process results
        buildings = []
        for row in results:
            building_uri = str(row.building)
            building_label = str(row.label) if row.label else building_uri
            
            buildings.append({
                'uri': building_uri,
                'name': building_label
            })
        
        # Step 4: Return structured results
        return {
            'building_count': len(buildings),
            'buildings': buildings,
            'summary': f"Found {len(buildings)} building(s) in the model"
        }
```

---

## Step 2: Test Your App

### Option A: Run via CLI

```bash
# List all apps (should show your new app)
hhws-brick apps list

# Run your app
hhws-brick apps run hello_world building_105.ttl

# Run with JSON output
hhws-brick apps run hello_world building_105.ttl -o results.json
```

### Option B: Run in Python

Create a test script `test_hello_world.py`:

```python
from hello_world_app import HelloWorldApp
from rdflib import Graph

# Load Brick model
print("Loading Brick model...")
graph = Graph()
graph.parse("building_105.ttl", format="turtle")
print(f"Loaded {len(graph)} triples")

# Create and run app
print("\nRunning Hello World app...")
app = HelloWorldApp()
results = app.analyze(graph)

# Display results
print(f"\n{results['summary']}")
print(f"\nBuildings:")
for building in results['buildings']:
    print(f"  - {building['name']}")
```

Run it:

```bash
python test_hello_world.py
```

---

## Expected Output

```
Loading Brick model...
Loaded 1,234 triples

Running Hello World app...

Found 1 building(s) in the model

Buildings:
  - building105
```

---

## Step 3: Understand the Code

### The @register_app Decorator

```python
@register_app(
    name="hello_world",           # CLI command name
    description="...",             # Shows in help
    version="1.0.0"               # Your app version
)
```

This makes your app discoverable by the framework.

### The analyze() Method

This is the **core method** that does the work:

```python
def analyze(self, graph, building_name=None, **kwargs):
    # Your analysis code here
    return {...}  # Must return a dict
```

**Parameters:**
- `graph`: The loaded Brick model (rdflib.Graph object)
- `building_name`: Optional building filter
- `**kwargs`: Additional parameters

**Returns:**
- Must return a dictionary
- Can contain any structure
- Will be converted to JSON/CSV automatically

### The SPARQL Query

```python
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?building ?label
WHERE {
    ?building a brick:Building .
    OPTIONAL { ?building rdfs:label ?label }
}
"""
```

**Breakdown:**
- `PREFIX`: Define namespaces
- `SELECT`: Variables to return
- `WHERE`: Pattern to match
- `OPTIONAL`: Make label optional (building might not have one)

---

## Step 4: Enhance Your App

### Add Error Handling

```python
def analyze(self, graph, building_name=None, **kwargs):
    try:
        query = "..."
        results = graph.query(query)
        # ... process results
        return {...}
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }
```

### Add Filtering

```python
def analyze(self, graph, building_name=None, **kwargs):
    # Filter by building name if provided
    if building_name:
        query = f"""
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX hhws: <https://example.org/hhws#>
        
        SELECT ?building
        WHERE {{
            ?building a brick:Building .
            FILTER(CONTAINS(STR(?building), "{building_name}"))
        }}
        """
    else:
        query = "..."  # Original query
```

### Add Logging

```python
def analyze(self, graph, building_name=None, **kwargs):
    print(f"Analyzing {len(graph)} triples...")
    
    query = "..."
    results = graph.query(query)
    
    print(f"Found {len(list(results))} buildings")
    
    return {...}
```

---

## Step 5: Export Results

### To JSON

```bash
hhws-brick apps run hello_world building_105.ttl -o results.json
```

Creates `results.json`:

```json
{
  "building_count": 1,
  "buildings": [
    {
      "uri": "https://example.org/hhws#building105",
      "name": "building105"
    }
  ],
  "summary": "Found 1 building(s) in the model"
}
```

### To CSV (with pandas)

Modify your app to return a DataFrame:

```python
import pandas as pd

def analyze(self, graph, **kwargs):
    # ... query and process ...
    
    # Create DataFrame
    df = pd.DataFrame(buildings)
    
    return {
        'dataframe': df,  # Auto-converts to CSV
        'summary': {...}
    }
```

---

## Common Issues

### Issue 1: No Results

**Problem**: Query returns empty results

**Solution**: Check that the Brick model actually contains buildings:

```python
# Debug: print all classes
for s, p, o in graph.triples((None, RDF.type, None)):
    print(f"{s} is a {o}")
```

### Issue 2: Import Error

**Problem**: Cannot import BaseApp

**Solution**:
```bash
pip install -e .
```

### Issue 3: App Not Listed

**Problem**: `hhws-brick apps list` doesn't show your app

**Solution**: Ensure @register_app decorator is used and file is in correct location.

---

## 🎉 Congratulations!

You've created your first Brick analytics app!

### What You Learned

✅ How to create an app class  
✅ How to use the @register_app decorator  
✅ How to write SPARQL queries  
✅ How to process and return results  
✅ How to run apps via CLI

### Next Steps

- **Tutorial 2**: Point Extraction App (extract all points from a building)
- **Tutorial 3**: Equipment Analysis App (analyze equipment relationships)
- **Tutorial 4**: Custom Analytics App (calculate performance metrics)

---

## Full Code

```python
"""Hello World App - Complete Code"""

from hhw_brick.analytics.core.base_app import BaseApp, register_app

@register_app(
    name="hello_world",
    description="Counts and lists all buildings in the model",
    version="1.0.0"
)
class HelloWorldApp(BaseApp):
    """My first Brick analytics app!"""
    
    def analyze(self, graph, building_name=None, **kwargs):
        """Count and list all buildings."""
        
        query = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?building ?label
        WHERE {
            ?building a brick:Building .
            OPTIONAL { ?building rdfs:label ?label }
        }
        """
        
        results = graph.query(query)
        
        buildings = []
        for row in results:
            buildings.append({
                'uri': str(row.building),
                'name': str(row.label) if row.label else str(row.building)
            })
        
        return {
            'building_count': len(buildings),
            'buildings': buildings,
            'summary': f"Found {len(buildings)} building(s) in the model"
        }
```

**Happy coding!** 🚀

