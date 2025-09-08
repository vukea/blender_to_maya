import maya.cmds as cmds
from dispatcher import dispatch_node

INPUT_TYPES = {
    "colorA": "color",
    "colorB": "color",
    "factor": "float",
}

DEFAULT_OUTPUT = "outColor"

# Operation enum for colorComposite
OPERATION_ENUM = {
    "ADD": 0,
    "SUBTRACT": 1,
    "MIX": 2,
    "MULTIPLY": 3,
    "SCREEN": 4,
    "OVERLAY": 5,
    "DIFFERENCE": 6,
    "DODGE": 7,
    "BURN": 8,
}

def create(name, node_data):
    node = cmds.shadingNode("colorComposite", asUtility=True, name=name)
    print(f"[mix_color] Created node: {node}")

    # Force operation to MIX (enum 2)
    try:
        cmds.setAttr(f"{node}.operation", OPERATION_ENUM["MIX"])
        print(f"[mix_color] {node}.operation = MIX (2)")
    except Exception as e:
        print(f"[mix_color] Could not set operation: {e}")

    # Factor
    fac = node_data.get("fac", 0.5)
    try:
        cmds.setAttr(f"{node}.factor", fac)
        print(f"[mix_color] {node}.factor = {fac}")
    except Exception as e:
        print(f"[mix_color] Could not set factor: {e}")

    # Recursive handling for A
    A = node_data.get("A")
    if A:
        if A.get("source_type") == "node":
            A_node = dispatch_node(A["node_type"], f"{name}_A", A)
            try:
                cmds.connectAttr(f"{A_node}.outColor", f"{node}.colorA", force=True)
                print(f"[mix_color] Connected {A_node}.outColor → {node}.colorA")
            except Exception as e:
                print(f"[mix_color] Could not connect colorA: {e}")
        else:
            try:
                cmds.setAttr(f"{node}.colorA", *A["value"])
                print(f"[mix_color] {node}.colorA = {A['value']}")
            except Exception as e:
                print(f"[mix_color] Could not set colorA: {e}")

    # Recursive handling for B
    B = node_data.get("B")
    if B:
        if B.get("source_type") == "node":
            B_node = dispatch_node(B["node_type"], f"{name}_B", B)
            try:
                cmds.connectAttr(f"{B_node}.outColor", f"{node}.colorB", force=True)
                print(f"[mix_color] Connected {B_node}.outColor → {node}.colorB")
            except Exception as e:
                print(f"[mix_color] Could not connect colorB: {e}")
        else:
            try:
                cmds.setAttr(f"{node}.colorB", *B["value"])
                print(f"[mix_color] {node}.colorB = {B['value']}")
            except Exception as e:
                print(f"[mix_color] Could not set colorB: {e}")

    return node
