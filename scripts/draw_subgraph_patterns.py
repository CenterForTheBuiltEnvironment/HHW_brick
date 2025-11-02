#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Draw Subgraph Patterns for Hot Water Systems
Black & White format with dashed lines for optional elements

This script generates conceptual pattern diagrams showing:
- Pattern 1: Boiler System (with primary and secondary loops)
- Pattern 2: District System (no boiler, single loop)

Features:
- Curved lines (splines='curved')
- Ellipse nodes (shape='ellipse')
- Black & white color scheme (white background nodes)
- Dashed lines for optional elements

Author: Generated for HHWS Brick Application
Date: 2025-10-29
"""

from graphviz import Digraph
from pathlib import Path


# ============== Configuration ==============
OUTPUT_DIR = Path(__file__).parent / "Subgraph_Patterns"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============== Pattern Drawing Functions ==============

def draw_pattern_1_boiler_system():
    """
    Draw Pattern 1: Boiler System with Dual Loops

    Structure:
    - rec:Building (required)
      ├── rec:isLocationOf → brick:Hot_Water_System (required)
      └── rec:isLocationOf → brick:Weather_Station (optional, dashed)

    - brick:Hot_Water_System (required)
      ├── brick:hasPart → brick:Primary_Loop (required)
      └── brick:hasPart → brick:Secondary_Loop (required)

    - brick:Primary_Loop (required)
      ├── brick:hasPart → brick:Boiler (required)
      └── brick:hasPart → brick:Pump (required)

    - brick:Secondary_Loop (required)
      └── brick:hasPart → brick:Pump (required)

    - brick:Primary_Loop → brick:feeds → brick:Secondary_Loop (required)
    """

    dot = Digraph(comment='Pattern 1: Boiler System', format='png')

    # Graph settings - curved lines, clean layout
    dot.attr(rankdir='TB')
    dot.graph_attr.update({
        'dpi': '300',
        'bgcolor': 'white',
        'rankdir': 'TB',
        'ranksep': '1.5',
        'nodesep': '1.2',
        'splines': 'curved',  # Curved lines
        'label': 'Pattern 1: Boiler System',
        'labelloc': 't',
        'fontsize': '24',
        'fontname': 'Helvetica-Bold',
    })

    # Node style - ellipse nodes, white background
    dot.node_attr.update({
        'shape': 'ellipse',  # Ellipse nodes
        'style': 'filled',
        'fillcolor': 'white',  # All nodes white background
        'color': 'black',
        'fontname': 'Helvetica',
        'fontsize': '14',
        'penwidth': '2.0',
        'margin': '0.2,0.1',
    })

    # Edge style - curved black lines
    dot.edge_attr.update({
        'fontname': 'Helvetica',
        'fontsize': '12',
        'color': 'black',
        'arrowsize': '1.0',
        'penwidth': '1.5',
    })

    # ============== Nodes ==============

    # Building (required) - thick border
    dot.node('Building', 'Building\\n(rec:Building)',
             fillcolor='white', penwidth='3.0')

    # Hot Water System (required) - thick border
    dot.node('HWS', 'Hot_Water_System\\n(brick:Hot_Water_System)',
             fillcolor='white', penwidth='3.0')

    # Weather Station (optional - dashed border)
    dot.node('Weather', 'Weather_Station\\n(brick:Weather_Station)',
             fillcolor='white', penwidth='2.0', style='filled,dashed')

    # Primary Loop (required) - thick border
    dot.node('PrimLoop', 'Primary_Loop\\n(brick:Hot_Water_Loop)',
             fillcolor='white', penwidth='3.0')

    # Secondary Loop (required) - thick border
    dot.node('SecLoop', 'Secondary_Loop\\n(brick:Hot_Water_Loop)',
             fillcolor='white', penwidth='3.0')

    # Boiler in Primary Loop (required) - medium border
    dot.node('Boiler', 'Boiler\\n(brick:Boiler)',
             fillcolor='white', penwidth='2.5')

    # Pump in Primary Loop (required) - medium border
    dot.node('PrimPump', 'Pump\\n(brick:Pump)',
             fillcolor='white', penwidth='2.5')

    # Pump in Secondary Loop (required) - medium border
    dot.node('SecPump', 'Pump\\n(brick:Pump)',
             fillcolor='white', penwidth='2.5')

    # ============== Edges ==============

    # Building connections
    dot.edge('Building', 'HWS', label='rec:isLocationOf',
             penwidth='2.5', color='black')

    # Building to Weather Station (optional - dashed)
    dot.edge('Building', 'Weather', label='rec:isLocationOf\\n(optional)',
             style='dashed', penwidth='2.0', color='black')

    # HWS to Loops
    dot.edge('HWS', 'PrimLoop', label='brick:hasPart',
             penwidth='2.5', color='black')
    dot.edge('HWS', 'SecLoop', label='brick:hasPart',
             penwidth='2.5', color='black')

    # Primary Loop components
    dot.edge('PrimLoop', 'Boiler', label='brick:hasPart',
             penwidth='2.0', color='black')
    dot.edge('PrimLoop', 'PrimPump', label='brick:hasPart',
             penwidth='2.0', color='black')

    # Boiler feeds Pump
    dot.edge('Boiler', 'PrimPump', label='brick:feeds',
             penwidth='2.0', color='black')

    # Secondary Loop components
    dot.edge('SecLoop', 'SecPump', label='brick:hasPart',
             penwidth='2.0', color='black')

    # Loop-to-Loop connection
    dot.edge('PrimLoop', 'SecLoop', label='brick:feeds',
             penwidth='2.5', color='black', style='bold')

    # ============== Render ==============
    output_path = OUTPUT_DIR / 'pattern_1_boiler_system'
    dot.render(str(output_path), cleanup=True)
    print(f"✅ Generated: {output_path}.png")

    return str(output_path) + '.png'


def draw_pattern_2_district_system():
    """
    Draw Pattern 2: District System (No Boiler)

    Structure:
    - rec:Building (required)
      ├── rec:isLocationOf → brick:Hot_Water_System (required)
      └── rec:isLocationOf → brick:Weather_Station (optional, dashed)

    - brick:Hot_Water_System (required)
      └── brick:hasPart → brick:Hot_Water_Loop (Secondary Loop only) (required)

    - brick:Hot_Water_Loop (Secondary Loop) (required)
      └── brick:hasPart → brick:Pump (required)

    Note: NO Boiler (district heating from central plant)
    Note: Only ONE loop (Secondary), no Primary loop
    """

    dot = Digraph(comment='Pattern 2: District System', format='png')

    # Graph settings - curved lines, clean layout
    dot.attr(rankdir='TB')
    dot.graph_attr.update({
        'dpi': '300',
        'bgcolor': 'white',
        'rankdir': 'TB',
        'ranksep': '1.5',
        'nodesep': '1.2',
        'splines': 'curved',  # Curved lines
        'label': 'Pattern 2: District System',
        'labelloc': 't',
        'fontsize': '24',
        'fontname': 'Helvetica-Bold',
    })

    # Node style - ellipse nodes, white background
    dot.node_attr.update({
        'shape': 'ellipse',  # Ellipse nodes
        'style': 'filled',
        'fillcolor': 'white',  # All nodes white background
        'color': 'black',
        'fontname': 'Helvetica',
        'fontsize': '14',
        'penwidth': '2.0',
        'margin': '0.2,0.1',
    })

    # Edge style - curved black lines
    dot.edge_attr.update({
        'fontname': 'Helvetica',
        'fontsize': '12',
        'color': 'black',
        'arrowsize': '1.0',
        'penwidth': '1.5',
    })

    # ============== Nodes ==============

    # Building (required) - thick border
    dot.node('Building', 'Building\\n(rec:Building)',
             fillcolor='white', penwidth='3.0')

    # Hot Water System (required) - thick border
    dot.node('HWS', 'Hot_Water_System\\n(brick:Hot_Water_System)',
             fillcolor='white', penwidth='3.0')

    # Weather Station (optional - dashed border)
    dot.node('Weather', 'Weather_Station\\n(brick:Weather_Station)',
             fillcolor='white', penwidth='2.0', style='filled,dashed')

    # Secondary Loop (required) - thick border (only one loop in district system)
    dot.node('SecLoop', 'Secondary_Loop\\n(brick:Hot_Water_Loop)',
             fillcolor='white', penwidth='3.0')

    # Pump in Secondary Loop (required) - medium border
    dot.node('SecPump', 'Pump\\n(brick:Pump)',
             fillcolor='white', penwidth='2.5')

    # ============== Edges ==============

    # Building connections
    dot.edge('Building', 'HWS', label='rec:isLocationOf',
             penwidth='2.5', color='black')

    # Building to Weather Station (optional - dashed)
    dot.edge('Building', 'Weather', label='rec:isLocationOf\\n(optional)',
             style='dashed', penwidth='2.0', color='black')

    # HWS to Secondary Loop (only one loop)
    dot.edge('HWS', 'SecLoop', label='brick:hasPart',
             penwidth='2.5', color='black')

    # Secondary Loop to Pump
    dot.edge('SecLoop', 'SecPump', label='brick:hasPart',
             penwidth='2.0', color='black')

    # ============== Render ==============
    output_path = OUTPUT_DIR / 'pattern_2_district_system'
    dot.render(str(output_path), cleanup=True)
    print(f"✅ Generated: {output_path}.png")

    return str(output_path) + '.png'


def draw_legend():
    """
    Draw a legend explaining the visual notation
    """

    dot = Digraph(comment='Legend', format='png')

    # Graph settings
    dot.graph_attr.update({
        'label': 'Legend',
        'bgcolor': 'white',
        'rankdir': 'TB',
        'splines': 'curved',
        'label': 'Legend: Pattern Diagram Notation',
        'labelloc': 't',
        'fontsize': '20',
        'fontname': 'Helvetica-Bold',
    })

    # Node style - ellipse nodes, white background
    dot.node_attr.update({
        'shape': 'ellipse',
        'style': 'filled',
        'fillcolor': 'white',
        'fontname': 'Helvetica',
        'fontsize': '12',
    })

    # Legend items
    dot.node('req_node', 'Required Entity',
             fillcolor='white', penwidth='3.0', color='black')

    dot.node('opt_node', 'Optional Entity',
             fillcolor='white', penwidth='2.0', color='black',
             style='filled,dashed')

    dot.node('eq_node', 'Equipment/Component',
             fillcolor='white', penwidth='2.5', color='black')

    # Edge legend (using invisible nodes for alignment)
    with dot.subgraph(name='cluster_edges') as c:
        c.attr(label='Edge Types', fontsize='14', fontname='Helvetica-Bold')
        c.node('e1', '', style='invis', width='0')
        c.node('e2', '', style='invis', width='0')
        c.node('e3', '', style='invis', width='0')
        c.node('e4', '', style='invis', width='0')

        c.edge('e1', 'e2', label='Required Relationship',
               penwidth='2.5', color='black')
        c.edge('e3', 'e4', label='Optional Relationship',
               style='dashed', penwidth='2.0', color='black')

    # Render
    output_path = OUTPUT_DIR / 'pattern_legend'
    dot.render(str(output_path), cleanup=True)
    print(f"✅ Generated: {output_path}.png")

    return str(output_path) + '.png'


# ============== Main Execution ==============

def main():
    """Generate all subgraph pattern diagrams"""

    print("=" * 80)
    print("Generating Subgraph Pattern Diagrams (Black & White, Curved Lines)")
    print("=" * 80)
    print(f"\nOutput Directory: {OUTPUT_DIR}\n")

    # Generate Pattern 1: Boiler System
    print("Drawing Pattern 1: Boiler System...")
    pattern1_file = draw_pattern_1_boiler_system()

    # Generate Pattern 2: District System
    print("\nDrawing Pattern 2: District System...")
    pattern2_file = draw_pattern_2_district_system()

    # Generate Legend
    print("\nDrawing Legend...")
    legend_file = draw_legend()

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Generated 3 pattern diagrams:")
    print(f"  1. Pattern 1 - Boiler System: {Path(pattern1_file).name}")
    print(f"  2. Pattern 2 - District System: {Path(pattern2_file).name}")
    print(f"  3. Legend: {Path(legend_file).name}")
    print(f"\nAll files saved to: {OUTPUT_DIR}")
    print(f"\nDesign features:")
    print(f"  • Curved lines (splines='curved')")
    print(f"  • Ellipse nodes (shape='ellipse')")
    print(f"  • Black & white color scheme")
    print(f"  • White background for all nodes")
    print(f"  • Dashed lines for optional elements")
    print("=" * 80)


if __name__ == "__main__":
    main()
