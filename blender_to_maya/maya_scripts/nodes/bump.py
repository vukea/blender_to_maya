import maya.cmds as cmds
from dispatcher import dispatch_node

INPUT_TYPES = {
    "height": "float",   # corrected
    "strength": "float",
}

DEFAULT_OUTPUT = "outValue"

def create(name, node_data):
    node = cmds.shadingNode("aiBump2d", asUtility=True, name=name)
    print(f"[bump] Created node: {node}")

    # Set bumpHeight (strength)
    strength = node_data.get("strength", 1.0)
    try:
        cmds.setAttr(f"{node}.bumpHeight", strength)
        print(f"[bump] {node}.bumpHeight = {strength}")
    except Exception as e:
        print(f"[bump] Could not set bumpHeight: {e}")

    # Handle child input (image texture)
    input_data = node_data.get("input")
    if input_data and input_data.get("source_type") == "node":
        child_name = f"{name}_input"
        child_node = dispatch_node(input_data["node_type"], child_name, input_data)
        # Connect outColorR → bumpMap
        try:
            cmds.connectAttr(f"{child_node}.outColorR", f"{node}.bumpMap", force=True)
            print(f"[bump] Connected {child_node}.outColorR → {node}.bumpMap")
        except Exception as e:
            print(f"[bump] Could not connect {child_node}.outColorR → {node}.bumpMap: {e}")

    return node
