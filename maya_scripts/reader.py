import json
import os
from dispatcher import dispatch_node

def read_material(material_name, material_data):
    """Read a single material and pass it to dispatcher"""
    shader_type = material_data.get("shader")
    print(f"\n=== Reading material: {material_name} ({shader_type}) ===")
    return dispatch_node(shader_type, material_data)

if __name__ == "__main__":
    # Your JSON path
    json_path = r"C:\Users\Mpho\Desktop\blender_to_maya\to_maya\test_scene.json"

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, "r") as f:
        materials = json.load(f)

    for mat_name, mat_data in materials.items():
        read_material(mat_name, mat_data)
