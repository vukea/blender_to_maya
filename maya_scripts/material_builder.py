import maya.cmds as cmds
from nodes import NODE_REGISTRY

class MaterialBuilder:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.shader_node = None
        self.sg_node = None

    def build(self):
        # Check shading group
        if not cmds.objExists(f"{self.name}_SG"):
            self.sg_node = cmds.sets(name=f"{self.name}_SG", renderable=True, noSurfaceShader=True, empty=True)
        else:
            self.sg_node = f"{self.name}_SG"

        # Create PrincipledBSDF
        self.shader_node = NODE_REGISTRY["PrincipledBSDF"](self.name + "_shader", {}).create()
        cmds.connectAttr(f"{self.shader_node}.outColor", f"{self.sg_node}.surfaceShader", force=True)

        # Iterate channels
        for channel_name, channel_data in self.data.items():
            source_type = channel_data.get("source_type")
            value = channel_data.get("value")
            if source_type == "default" and value is not None:
                try:
                    cmds.setAttr(f"{self.shader_node}.{channel_name}", *value if isinstance(value, (list, tuple)) else value, type="double3" if isinstance(value, (list, tuple)) else None)
                except Exception as e:
                    print(f"Warning: Could not set {channel_name}: {e}")
            elif source_type == "node":
                node_type = channel_data.get("node_type")
                node_class = NODE_REGISTRY.get(node_type)
                if node_class:
                    node_instance = node_class(f"{self.name}_{channel_name}", channel_data)
                    created_node = node_instance.create()
                    if created_node:
                        node_instance.connect(f"{self.shader_node}.{channel_name}")
                else:
                    print(f"Warning: Unsupported node type {node_type}")
