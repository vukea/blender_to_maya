import sys
import os
import json
import importlib

# --- Path setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # maya_scripts
NODES_DIR = os.path.join(BASE_DIR, "nodes")

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
if NODES_DIR not in sys.path:
    sys.path.append(NODES_DIR)

# Import dispatcher (no circular import now)
import dispatcher
importlib.reload(dispatcher)
from dispatcher import dispatch_node


def read_material(material_name, material_data):
    """Read a single material entry from JSON and create its node(s)."""
    shader_type = material_data.get("shader")
    print(f"\n=== Reading material: {material_name} ({shader_type}) ===")
    return dispatch_node(shader_type, material_data)


def read_scene(json_path):
    """Load a JSON scene file and process all materials."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON not found: {json_path}")

    with open(json_path, "r") as f:
        materials = json.load(f)

    for mat_name, mat_data in materials.items():
        read_material(mat_name, mat_data)
