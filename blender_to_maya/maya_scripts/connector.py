# connector.py
import importlib
import maya.cmds as cmds
from dispatcher import dispatch_node

def connect_material_nodes(materials):
    """
    Go through all materials and connect any node-based inputs.
    This will recursively create node inputs if needed and connect them.
    """
    for mat_name, mat_data in materials.items():
        shader_type = mat_data.get("shader")
        shader_node = mat_name  # assume shader exists with same name
        channels = mat_data.get("channels", {})

        for slot, info in channels.items():
            if info.get("source_type") == "node":
                # Build a name for the input node
                input_node_name = f"{mat_name}_{slot}"

                # Create the node (this may duplicate if already exists)
                input_node = dispatch_node(info.get("node_type"), input_node_name, info)

                # Determine which output attribute to connect
                out_attr = "outColor" if info.get("node_type") == "Image Texture" else "outValue"

                # Connect to the appropriate shader attribute
                if cmds.objExists(shader_node) and cmds.objExists(input_node):
                    try:
                        cmds.connectAttr(f"{input_node}.{out_attr}", f"{shader_node}.{slot}", force=True)
                        print(f" → Connected {input_node}.{out_attr} → {shader_node}.{slot}")
                    except Exception as e:
                        print(f" ⚠️ Could not connect {input_node} to {shader_node}: {e}")
