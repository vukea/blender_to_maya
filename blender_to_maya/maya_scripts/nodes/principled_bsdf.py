import maya.cmds as cmds
from dispatcher import dispatch_node

# --- Define input types ---
INPUT_TYPES = {
    "baseColor": "color",
    "specularRoughness": "float",
    "metalness": "float",
    "opacity": "float",
    "subsurface": "float",
    "subsurfaceRadius": "color",
    "transmission": "float",
    "emissionColor": "color",
    "emission": "float",
    "normal": "vector",  # Normal input
}

DEFAULT_OUTPUT = "outColor"  # aiStandardSurface outputs color by default

# Map JSON slot names to Maya attributes
SLOT_MAP = {
    "Base Color": "baseColor",
    "Roughness": "specularRoughness",
    "Metallic": "metalness",
    "Alpha": "opacity",
    "Subsurface Weight": "subsurface",
    "Subsurface Radius": "subsurfaceRadius",
    "Transmission Weight": "transmission",
    "Emission Color": "emissionColor",
    "Emission Strength": "emission",
    "Normal": "normal",
    "Bump": "normal",
}

def create(name, node_data):
    """Create aiStandardSurface and recursively connect inputs"""
    if cmds.objExists(name):
        shader = name
        print(f"[bsdf] Reusing shader: {shader}")
    else:
        shader = cmds.shadingNode("aiStandardSurface", asShader=True, name=name)
        print(f"[bsdf] Created aiStandardSurface: {shader}")

    channels = node_data.get("channels", {})

    for slot_name, info in channels.items():
        maya_attr = SLOT_MAP.get(slot_name)
        if not maya_attr:
            continue

        expected_type = INPUT_TYPES.get(maya_attr, "float")

        # Handle default values
        if info["source_type"] == "default":
            value = info["value"]
            try:
                if maya_attr == "opacity":
                    # Set each RGB channel individually
                    if isinstance(value, list) and len(value) == 3:
                        cmds.setAttr(f"{shader}.opacityR", value[0])
                        cmds.setAttr(f"{shader}.opacityG", value[1])
                        cmds.setAttr(f"{shader}.opacityB", value[2])
                    else:
                        # Single float
                        cmds.setAttr(f"{shader}.opacityR", value)
                        cmds.setAttr(f"{shader}.opacityG", value)
                        cmds.setAttr(f"{shader}.opacityB", value)
                elif isinstance(value, list):
                    cmds.setAttr(f"{shader}.{maya_attr}", *value)
                else:
                    cmds.setAttr(f"{shader}.{maya_attr}", value)
                print(f"[bsdf] {shader}.{maya_attr} = {value}")
            except Exception as e:
                print(f"[bsdf] Could not set {maya_attr}: {e}")

        # Handle node inputs
        elif info["source_type"] == "node":
            child_name = f"{name}_{slot_name}"
            child_node = dispatch_node(info["node_type"], child_name, info)

            # Determine connection attribute
            if maya_attr == "normal":
                connect_attr = "outValue"  # aiBump2d and aiNormalMap output
                dest_attr = "normalCamera"
            elif expected_type == "color":
                connect_attr = "outColor"
                dest_attr = maya_attr
            else:
                # For float inputs like Roughness, try outFloat first, fallback to outColorR
                if cmds.objExists(f"{child_node}.outFloat"):
                    connect_attr = "outFloat"
                else:
                    connect_attr = "outColorR"
                dest_attr = maya_attr

            # Connect node
            try:
                cmds.connectAttr(f"{child_node}.{connect_attr}", f"{shader}.{dest_attr}", force=True)
                print(f"[bsdf] Connected {child_node}.{connect_attr} → {shader}.{dest_attr}")
            except Exception as e:
                print(f"[bsdf] Could not connect {child_node}.{connect_attr} → {shader}.{dest_attr}: {e}")

    return shader
