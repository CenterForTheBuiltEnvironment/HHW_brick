#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brick Model Visualization Script

This script visualizes Brick TTL files as graph diagrams, showing:
- Entities (Buildings, Systems, Equipment, Points) as colored nodes
- Relationships (brick:hasPart, brick:feeds, etc.) as labeled edges
- Type hierarchy (using Brick and REC ontologies)

Features:
- Automatic color coding by entity type (Point, Equipment, System, Location)
- Type inference using Brick ontology
- Selective file visualization (by system type or building number)
- High-quality PNG output

Author: HHWS Brick Application
Date: 2025-10-29
"""

from pathlib import Path
import rdflib
from graphviz import Digraph
from collections import defaultdict
import warnings

# Suppress RDF parsing warnings
warnings.filterwarnings("ignore", category=UserWarning, module="rdflib")

# ============== Configuration ==============
INPUT_DIR = Path("Brick_Models_Output")  # Relative path
OUTPUT_DIR = Path("Brick_Visualizations")  # Relative path
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Namespaces
BRICK = rdflib.Namespace("https://brickschema.org/schema/Brick#")
REF   = rdflib.Namespace("https://brickschema.org/schema/Brick/ref#")
QUDT  = rdflib.Namespace("http://qudt.org/vocab/unit/")
OWL   = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
REC   = rdflib.Namespace("https://w3id.org/rec#")
RDF   = rdflib.RDF
RDFS  = rdflib.RDFS

# Colors per top-level Brick class
COLOR_BY_CLASS = {
    str(REC.Space):       "LightCoral",  # REC Space (Building is subclass of Space)
    str(BRICK.Point):     "Gold",
    str(BRICK.Equipment): "#32BF84",
    str(BRICK.System):    "#BFD7FF",  # light blue for systems
}

# ============== File Type Classification ==============
def classify_file_type(filename: str) -> str:
    """Extract system type from filename."""
    if "condensing" in filename and "non-condensing" not in filename:
        return "condensing"
    elif "non-condensing" in filename:
        return "non-condensing"
    elif "district_hw" in filename:
        return "district_hw"
    elif "district_steam" in filename:
        return "district_steam"
    elif "boiler" in filename:
        return "boiler"
    else:
        return "other"

def select_representative_files(input_dir: Path, max_per_type: int = 1) -> dict:
    """
    Select representative files for each system type.
    Prioritize files that contain pumps.
    Returns dict: {type_name: [file_paths]}
    """
    type_files = defaultdict(list)

    for file in input_dir.glob("*.ttl"):
        file_type = classify_file_type(file.name)

        # Check if file contains pump
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                has_pump = 'pump' in content.lower()
        except:
            has_pump = False

        # Store files with priority (pump files first)
        type_files[file_type].append((file, has_pump))

    # Select files for each type, prioritizing those with pumps
    selected = {}
    for type_name, files in type_files.items():
        if files:
            # Sort by has_pump (True first), then by filename
            sorted_files = sorted(files, key=lambda x: (not x[1], x[0].name))
            # Take only the file paths (not the has_pump flag)
            selected[type_name] = [f[0] for f in sorted_files[:max_per_type]]

    return selected

# ============== Helpers ==============
def iri(value) -> str:
    """Return the full IRI string."""
    return str(value)

def local(value) -> str:
    """Return the local name after '#' if present; otherwise the full string."""
    s = str(value)
    return s.split("#")[-1] if "#" in s else s

def is_brick_predicate(p) -> bool:
    """Keep Brick# predicates, REC predicates and owl:sameAs; exclude ref#."""
    ps = iri(p)
    # Include Brick predicates, REC predicates and owl:sameAs
    return (ps.startswith(str(BRICK)) and not ps.startswith(str(REF))) or ps.startswith(str(REC)) or ps == str(OWL.sameAs)

def is_ref_type(t) -> bool:
    """Check if a type IRI is under Brick/ref#."""
    return iri(t).startswith(str(REF))

def is_unit_node(u) -> bool:
    """Check if a node is a QUDT unit (should be filtered out)."""
    return iri(u).startswith(str(QUDT))

# ============== Build subclass map ==============
def build_subclass_map(g):
    """Build subclass map for ancestor lookup."""
    subclass_map = {}
    for s, _, o in g.triples((None, RDFS.subClassOf, None)):
        if isinstance(s, rdflib.term.Identifier) and isinstance(o, rdflib.term.Identifier):
            subclass_map.setdefault(s, set()).add(o)
    return subclass_map

# Cache ancestors lookup
from functools import lru_cache

def make_ancestors_func(subclass_map):
    """Create an ancestors lookup function with cache."""
    @lru_cache(maxsize=None)
    def ancestors(cls: rdflib.term.Identifier):
        """Return all superclasses reachable via rdfs:subClassOf edges."""
        seen = set()
        stack = [cls]
        while stack:
            c = stack.pop()
            for p in subclass_map.get(c, ()):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        return seen
    return ancestors

TOP_CLASSES = {rdflib.URIRef(k) for k in COLOR_BY_CLASS.keys()}

def classify_node(u: rdflib.term.Identifier, g, ancestors_func) -> str:
    """
    Decide fill color for a node:
    - Consider rdf:type with Brick# or REC# prefix (ignore ref#)
    - If an instance of a subclass of Point/Equipment/System/Location, use mapped color
    - Priority when multiple types exist: Point > Equipment > System > Location
    - Fallback: light gray
    """
    # Collect Brick and REC types
    types = [t for t in g.objects(u, RDF.type)
             if (iri(t).startswith(str(BRICK)) or iri(t).startswith(str(REC)))
             and not is_ref_type(t)]
    if not types:
        return "#EEEEEE"  # default gray

    # Priority order (Point has highest priority)
    priority = [
        (rdflib.URIRef(str(BRICK.Point)), COLOR_BY_CLASS[str(BRICK.Point)]),
        (rdflib.URIRef(str(BRICK.Equipment)), COLOR_BY_CLASS[str(BRICK.Equipment)]),
        (rdflib.URIRef(str(BRICK.System)), COLOR_BY_CLASS[str(BRICK.System)]),
        (rdflib.URIRef(str(REC.Space)), COLOR_BY_CLASS[str(REC.Space)]),
    ]

    # Check each type and its ancestors
    for t in types:
        # Get all ancestors of this type
        type_ancestors = ancestors_func(t)
        type_ancestors.add(t)  # Include the type itself

        # Check against priority order
        for top_class, color in priority:
            if top_class in type_ancestors:
                return color

    # Fallback: light gray
    return "#EEEEEE"

# ============== Main Visualization Function ==============
def visualize_brick_model(ttl_path: Path, output_name: str):
    """
    Visualize a single Brick TTL file.

    Args:
        ttl_path: Path to the TTL file
        output_name: Base name for output files (without extension)
    """
    print(f"\n📊 Visualizing: {ttl_path.name}")

    # Load user's TTL file first (to identify user nodes)
    user_graph = rdflib.Graph()
    try:
        user_graph.parse(str(ttl_path), format="turtle")
    except Exception as e:
        print(f"  ❌ Error parsing {ttl_path.name}: {e}")
        return

    # Collect all subjects and objects from user's file (these are user's nodes)
    user_nodes = set()
    for s, p, o in user_graph:
        if isinstance(s, rdflib.term.URIRef):
            user_nodes.add(s)
        if isinstance(o, rdflib.term.URIRef):
            user_nodes.add(o)

    print(f"  ✓ Found {len(user_nodes)} nodes in user file")

    # Now load Brick ontology for type inference (but we'll only draw user nodes)
    try:
        from brickschema import Graph as BrickGraph
        g = BrickGraph(load_brick=True)
        g.parse(str(ttl_path), format="turtle")
        # Load REC ontology for Space/Building classification
        rec_loaded = False
        try:
            # Try loading REC full ontology
            g.parse("https://w3id.org/rec", format="turtle")
            rec_loaded = True
            print(f"  ✓ Loaded Brick and REC ontologies")
        except Exception as e:
            # If REC loading fails, manually add the critical subclass relationship
            print(f"  ⚠ REC load failed ({e}), adding manual Space/Building relationship")
            g.add((REC.Building, RDFS.subClassOf, REC.Space))
            rec_loaded = True
    except ImportError:
        print(f"  ⚠ Using user graph without Brick ontology")
        g = user_graph

    # Build subclass map
    subclass_map = build_subclass_map(g)
    ancestors_func = make_ancestors_func(subclass_map)

    # Collect all predicates we will draw (automatic: any Brick# predicate)
    brick_predicates = {p for _, p, _ in g if is_brick_predicate(p)}

    # Create Graphviz canvas with optimized settings
    dot = Digraph(comment=f'Brick Model: {ttl_path.stem}')
    dot.attr(rankdir='LR')
    dot.graph_attr.update(dict(
        dpi='300',           # Reduced DPI for faster rendering
        size='16,12',        # Smaller canvas
        ratio='auto',        # Auto ratio
        splines="true",
        overlap="scale",     # Allow overlap scaling for better fit
        concentrate="true",
        ranksep="0.8",       # Reduced spacing
        nodesep="0.5",
        bgcolor="white",
    ))
    # Use default ellipse shape - more elegant
    dot.node_attr.update(dict(
        shape="ellipse",
        style="filled",
        color="#333333",
        fontname="Helvetica",
        fontsize="12",       # Slightly larger font
        penwidth="1.5",
    ))
    dot.edge_attr.update(dict(
        fontname="Helvetica",
        fontsize="10",       # Slightly larger edge labels
        color="#666666",
        arrowsize="0.7",
    ))

    added_nodes = set()

    def add_node(u):
        """Add a node once with color decided by its Brick type. Skip unit nodes and non-user nodes."""
        # Only add nodes that are in the user's original file
        if u not in user_nodes:
            return False
        if u in added_nodes or is_unit_node(u):
            return False

        # Get the node's color
        fill = classify_node(u, g, ancestors_func)

        # Get the node's types for label (Brick and REC types)
        types = [t for t in g.objects(u, RDF.type)
                if (iri(t).startswith(str(BRICK)) or iri(t).startswith(str(REC)))
                and not is_ref_type(t)]

        # Create label with node name and type
        node_name = local(u)
        if types:
            # Use the first (most specific) type
            type_iri = iri(types[0])
            type_name = local(types[0])
            # Add appropriate prefix
            if type_iri.startswith(str(BRICK)):
                label = f"{node_name}\n(brick:{type_name})"
            elif type_iri.startswith(str(REC)):
                label = f"{node_name}\n(rec:{type_name})"
            else:
                label = f"{node_name}\n({type_name})"
        else:
            label = node_name

        dot.node(local(u), label=label, fillcolor=fill)
        added_nodes.add(u)
        return True

    # Draw edges for all Brick predicates from user's file only
    for s, p, o in user_graph:
        # Only process Brick predicates
        if not is_brick_predicate(p):
            continue
        # Skip if either subject or object is a unit node
        if is_unit_node(s) or is_unit_node(o):
            continue
        # Only draw if both nodes are in user's file
        if s in user_nodes and o in user_nodes:
            s_added = add_node(s)
            o_added = add_node(o)
            if s_added or s in added_nodes:
                if o_added or o in added_nodes:
                    # Add prefix to edge label
                    p_str = iri(p)
                    if p_str.startswith(str(BRICK)):
                        edge_label = f"brick:{local(p)}"
                    elif p_str.startswith(str(REC)):
                        edge_label = f"rec:{local(p)}"
                    elif p_str.startswith(str(OWL)):
                        edge_label = f"owl:{local(p)}"
                    else:
                        edge_label = local(p)
                    dot.edge(local(s), local(o), label=edge_label)

    # Export high-quality PNG
    png_path = OUTPUT_DIR / f"{output_name}.png"

    try:
        dot.render(str(OUTPUT_DIR / output_name), view=False, format='png', cleanup=True)
        print(f"  ✅ Generated: {png_path.name}")
    except Exception as e:
        print(f"  ❌ Error rendering: {e}")

# ============== Main Execution ==============
if __name__ == "__main__":
    print("="*80)
    print("Brick Model Visualization - Special Cases + Representative Files")
    print("="*80)

    # Define specific buildings to visualize (special cases)
    special_buildings = [
        127,  # Complete Dual-loop (condensing, has supp/retp)
        315,  # Partial Dual-loop + Special pump config (pmp_spd, pmp1_vfd, pmp2_vfd)
        235,  # District Heating (no boiler)
        125,  # Partial Dual-loop (condensing, only retp)
        304,  # Complete Dual-loop (non-condensing)
    ]

    # Select representative files for each type (original 5)
    print(f"\n📁 Scanning directory: {INPUT_DIR}")
    selected_files = select_representative_files(INPUT_DIR, max_per_type=1)

    print(f"\n📋 Found {len(selected_files)} system types:")
    for type_name, files in selected_files.items():
        print(f"  - {type_name}: {len(files)} file(s)")

    # Find special building files
    print(f"\n🔍 Looking for special case buildings: {special_buildings}")
    special_files = []
    for building_num in special_buildings:
        pattern = f"building_{building_num}_*.ttl"
        matching = list(INPUT_DIR.glob(pattern))
        if matching:
            special_files.append((building_num, matching[0]))
            print(f"  ✓ Found: {matching[0].name}")
        else:
            print(f"  ✗ Not found: building_{building_num}_*.ttl")

    # Visualize representative files from each type
    print(f"\n🎨 Generating visualizations for representative files...")
    count = 0
    for type_name, files in selected_files.items():
        for file_path in files:
            count += 1
            output_name = f"brick_{type_name}_{file_path.stem}"
            visualize_brick_model(file_path, output_name)

    # Visualize special case buildings
    print(f"\n🎨 Generating visualizations for special case buildings...")
    for building_num, file_path in special_files:
        count += 1
        output_name = f"brick_special_case_{building_num}_{file_path.stem}"
        visualize_brick_model(file_path, output_name)

    print("\n" + "="*80)
    print(f"✅ Visualization complete! Generated {count} visualizations.")
    print(f"📂 Output directory: {OUTPUT_DIR}")
    print("="*80)

