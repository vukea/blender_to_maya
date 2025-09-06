import maya.cmds as cmds
from .base_node import BaseNode

class NormalMapNode(BaseNode):
    def create(self):
        file_path = self.data.get("file_path")
        if not file_path:
            print(f"Warning: No file path for normal map {self.name}")
            return None

        if not cmds.objExists(self.name):
            self.node = cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=self.name)
            cmds.setAttr(f"{self.node}.fileTextureName", file_path, type="string")
            # Set as raw
            cmds.setAttr(f"{self.node}.colorSpace", "Raw", type="string")

        # Create bump2d node
        bump_node = f"{self.name}_bump"
        if not cmds.objExists(bump_node):
            bump = cmds.shadingNode('aiNormalMap', asShader=True, name=bump_node)
            cmds.connectAttr(f"{self.node}.outColor", f"{bump}.input")
        return bump_node

    def connect(self, target_attr):
        if self.node:
            try:
                cmds.connectAttr(f"{self.node}.outValue", target_attr, force=True)
            except Exception as e:
                print(f"Warning: Could not connect {self.node} to {target_attr}: {e}")
