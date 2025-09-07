import maya.cmds as cmds
from dispatcher import dispatch_node

# Map Blender inputs → Arnold aiStandardSurface attributes
INPUTS = {
    "Base Color": "baseColor",
    "Roughness": "specularRoughness",
    "Metallic": "metalness",
    "Alpha": "opacity",
    "Subsurface Weight": "subsurface",
    "Subsurface Radius": "subsurfaceRadius",
    "Transmission Weight": "transmission",
    "Emission Color": "emissionColor",
    "Emission Strength": "emissionStrength",
    # Normal map will be handled later
}

def create(data):
    """Create an aiStandardSurface node and set attributes"""
    node = cmds.shadingNode("aiStandardSurface", asShader=True)
    print(f" → Created {node} (Principled BSDF)")

    channels = data.get("channels", {})
    for slot, maya_attr in INPUTS.items():
        if slot not in channels:
            continue

        slot_data = channels[slot]
        source_type = slot_data.get("source_type")

        # Default slot values → setAttr
        if source_type == "default":
            value = slot_data.get("value")

            if isinstance(value, list):  # e.g. colors (RGB)
                cmds.setAttr(f"{node}.{maya_attr}", *value, type="double3")
            else:  # scalar values
                cmds.setAttr(f"{node}.{maya_attr}", value)

            print(f"    {maya_attr} = {value}")

        # Node slot → recursive dispatch
        elif source_type == "node":
            sub_type = slot_data.get("node_type")
            print(f"    {slot} is a node → dispatching {sub_type}")
            sub_node = dispatch_node(sub_type, slot_data)
            # connections will be handled later

    return node
