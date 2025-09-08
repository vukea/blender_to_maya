import maya.cmds as cmds
from dispatcher import dispatch_node

INPUT_TYPES = {
    "floatA": "float",
    "floatB": "float",
    "factor": "float",
}

DEFAULT_OUTPUT = "outFloat"

# Force operation to MIX
DEFAULT_OPERATION = 2  # 2 = Mix

def create(name, node_data):
    """Create Mix Float node and recursively connect A/B if they are nodes"""
    if cmds.objExists(name):
        node = name
        print(f"[mix_float] Reusing node: {node}")
    else:
        node = cmds.shadingNode("floatComposite", asUtility=True, name=name)
        print(f"[mix_float] Created node: {node}")

        # Force operation to Mix
        try:
            cmds.setAttr(f"{node}.operation", DEFAULT_OPERATION)
            print(f"[mix_float] {node}.operation = Mix ({DEFAULT_OPERATION})")
        except Exception as e:
            print(f"[mix_float] Could not set operation: {e}")

    # Map JSON slots to Maya attributes
    SLOT_MAP = {"A": "floatA", "B": "floatB", "fac": "factor"}

    for slot_name in ["A", "B", "fac"]:
        info = node_data.get(slot_name)
        if not info:
            continue

        node_attr = SLOT_MAP[slot_name]

        if info["source_type"] == "default":
            value = info["value"]
            try:
                cmds.setAttr(f"{node}.{node_attr}", value)
                print(f"[mix_float] {node}.{node_attr} = {value}")
            except Exception as e:
                print(f"[mix_float] Could not set {node_attr}: {e}")

        elif info["source_type"] == "node":
            # Recursively create input node
            child_name = f"{name}_{slot_name}"
            child_node = dispatch_node(info["node_type"], child_name, info)

            # Connect output → Mix Float input
            # Use outColorR for floats from textures or nodes
            connect_attr = "outColorR"
            try:
                cmds.connectAttr(f"{child_node}.{connect_attr}", f"{node}.{node_attr}", force=True)
                print(f"[mix_float] Connected {child_node}.{connect_attr} → {node}.{node_attr}")
            except Exception as e:
                print(f"[mix_float] Could not connect {child_node}.{connect_attr} → {node}.{node_attr}: {e}")

    return node
