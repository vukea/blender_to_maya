"""
material_translator.py
Orchestrates reading Blender-exported JSON and building materials in Maya.
"""

import os
import json
import sys

try:
    import maya.cmds as cmds
except ImportError:
    raise RuntimeError("This script must be run inside Maya (maya.cmds not available).")

from material_builder import MaterialBuilder

DEFAULT_JSON_PATH = r"C:\Users\Mpho\Desktop\blender_to_maya\to_maya\test_scene.json"


def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError("JSON file not found: {}".format(path))
    with open(path, "r") as f:
        return json.load(f)


def main(json_path=None):
    json_path = json_path or DEFAULT_JSON_PATH
    print("Material translator starting. Loading JSON:", json_path)

    try:
        data = load_json(json_path)
    except Exception as e:
        print("Failed to load JSON:", e)
        return

    builder = MaterialBuilder()
    materials_built = []

    for mat_name, mat_data in data.items():
        try:
            print("\n--- Building material: '{}' ---".format(mat_name))
            builder.build_material(mat_name, mat_data)
            materials_built.append(mat_name)
            print("SUCCESS:", mat_name)
        except Exception as e:
            print("ERROR: Failed to build '{}': {}".format(mat_name, e))

    print("\nFinished. Materials built:", materials_built)
    return materials_built


if __name__ == "__main__":
    arg_path = sys.argv[-1] if len(sys.argv) > 1 else None
    main(arg_path)