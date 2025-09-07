import maya.cmds as cmds

def create(material_name, node_data):
    """
    Create or update a Principled BSDF (aiStandardSurface) shader in Maya.
    - If material_name exists: reuse it.
    - Else: create a new aiStandardSurface with that name.
    """

    # Check if shader exists
    if cmds.objExists(material_name):
        shader = material_name
        print(f" → Reusing existing {shader} (Principled BSDF)")
    else:
        shader = cmds.shadingNode("aiStandardSurface", asShader=True, name=material_name)
        print(f" → Created new {shader} (Principled BSDF)")

    channels = node_data.get("channels", {})

    for slot, info in channels.items():
        if info.get("source_type") == "default":
            val = info.get("value")

            if slot == "Base Color":
                cmds.setAttr(f"{shader}.baseColor", *val, type="double3")
                print(f"    baseColor = {val}")

            elif slot == "Roughness":
                cmds.setAttr(f"{shader}.specularRoughness", val)
                print(f"    specularRoughness = {val}")

            elif slot == "Metallic":
                cmds.setAttr(f"{shader}.metalness", val)
                print(f"    metalness = {val}")

            elif slot == "Alpha":
                cmds.setAttr(f"{shader}.opacity", val, val, val, type="double3")
                print(f"    opacity = {val}")

            elif slot == "Subsurface Weight":
                cmds.setAttr(f"{shader}.subsurface", val)
                print(f"    subsurface = {val}")

            elif slot == "Subsurface Radius":
                r, g, b = val
                cmds.setAttr(f"{shader}.subsurfaceRadiusR", r)
                cmds.setAttr(f"{shader}.subsurfaceRadiusG", g)
                cmds.setAttr(f"{shader}.subsurfaceRadiusB", b)
                print(f"    subsurfaceRadius = {val}")

            elif slot == "Transmission Weight":
                cmds.setAttr(f"{shader}.transmission", val)
                print(f"    transmission = {val}")

            elif slot == "Emission Color":
                cmds.setAttr(f"{shader}.emissionColor", *val, type="double3")
                print(f"    emissionColor = {val}")

            elif slot == "Emission Strength":
                cmds.setAttr(f"{shader}.emission", val)
                print(f"    emission = {val}")

    return shader
