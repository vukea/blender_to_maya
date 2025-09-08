import maya.cmds as cmds

INPUT_TYPES = {}  # file node has no inputs
DEFAULT_OUTPUT = "outColor"  # file node outputs color

class ImageTexture:
    NODE_TYPE = "file"

    @classmethod
    def create(cls, name, node_data, material_name=None):
        """Create a file texture node"""
        node = cmds.shadingNode(cls.NODE_TYPE, asTexture=True, isColorManaged=True, name=name)
        print(f"[image_texture] Created node: {node}")

        # Set file path
        file_path = node_data.get("file_path")
        if file_path:
            try:
                cmds.setAttr(f"{node}.fileTextureName", file_path, type="string")
                print(f"[image_texture] {node}.fileTextureName = {file_path}")
            except Exception as e:
                print(f"[image_texture] FAILED setting texture path: {e}")

        return node
