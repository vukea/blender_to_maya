import maya.cmds as cmds
from dispatcher import dispatch_node

INPUT_TYPES = {
    "normal": "color",
    "strength": "float",
}

DEFAULT_OUTPUT = "outValue"

def create(name, node_data):
    node = cmds.shadingNode("aiNormalMap", asUtility=True, name=name)
    print(f"[normal_map] Created node: {node}")

    # Set strength
    strength = node_data.get("strength", 1.0)
    try:
        cmds.setAttr(f"{node}.strength", strength)
        print(f"[normal_map] {node}.strength = {strength}")
    except Exception as e:
        print(f"[normal_map] Could not set strength: {e}")

    # Handle child input (image texture)
    input_data = node_data.get("input")
    if input_data and input_data.get("source_type") == "node":
        child_name = f"{name}_input"
        child_node = dispatch_node(input_data["node_type"], child_name, input_data)
        # Decide which attribute to connect
        try:
            cmds.connectAttr(f"{child_node}.outColor", f"{node}.normal", force=True)
            print(f"[normal_map] Connected {child_node}.outColor → {node}.normal")
        except Exception as e:
            print(f"[normal_map] Could not connect {child_node}.outColor → {node}.normal: {e}")

    return node
