import maya.cmds as cmds
from dispatcher import dispatch_node

def create(data):
    """Create an aiMixShader node and its sub-shaders"""
    node = cmds.shadingNode("aiMixShader", asShader=True)
    print(f" → Created {node} (Mix Shader)")

    fac = data.get("fac", {}).get("value")
    if fac is not None:
        cmds.setAttr(f"{node}.mix", fac)
        print(f"    mix = {fac}")

    # Create sub-shaders recursively
    for idx, sub_shader in enumerate(data.get("shaders", [])):
        if not sub_shader:
            continue
        shader_type = sub_shader.get("shader")
        print(f"    Sub-shader {idx}: {shader_type}")
        sub_node = dispatch_node(shader_type, sub_shader)
        # connections will be handled later

    return node
