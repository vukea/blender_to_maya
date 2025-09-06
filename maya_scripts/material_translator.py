# maya_scripts/material_translator.py

import os
import json
import importlib

import maya.cmds as cmds

# --- Import material builder ---
import material_builder
importlib.reload(material_builder)  # force reload during dev


def load_json(json_path):
    """Load and return material data from a JSON file."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, "r") as f:
        data = json.load(f)
    return data


def main(json_path):
    """Main entry point: reads JSON and builds materials in Maya."""
    try:
        materials = load_json(json_path)
    except Exception as e:
        print(f"[Translator] ❌ Failed to load JSON: {e}")
        return

    print(f"[Translator] ✅ Loaded materials JSON: {json_path}")

    for mat_name, mat_data in materials.items():
        try:
            print(f"\n[Translator] 🔧 Building material: {mat_name}")
            material_builder.build_material(mat_name, mat_data)
        except Exception as e:
            print(f"[Translator] ❌ Error building {mat_name}: {e}")


# --- Allow direct execution inside Maya Script Editor ---
if __name__ == "__main__":
    # Change this to your JSON path
    test_json = r"C:\Users\Mpho\Desktop\blender_to_maya\to_maya\test_scene.json"

    if os.path.exists(test_json):
        main(test_json)
    else:
        print(f"[Translator] ⚠ Test JSON path not found: {test_json}")