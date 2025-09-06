import maya.cmds as cmds
from .base_node import BaseNode

class ImageTextureNode(BaseNode):
    def create(self):
        file_path = self.data.get("file_path")
        if not file_path:
            print(f"Warning: No file path for image texture {self.name}")
            return None

        if not cmds.objExists(self.name):
            self.node = cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=self.name)
            cmds.setAttr(f"{self.node}.fileTextureName", file_path, type="string")
        else:
            self.node = self.name

        # Create a place2dTexture node
        p2d = f"{self.name}_place2d"
        if not cmds.objExists(p2d):
            place2d = cmds.shadingNode('place2dTexture', asUtility=True, name=p2d)
            cmds.connectAttr(f"{place2d}.outUV", f"{self.node}.uvCoord")
            cmds.connectAttr(f"{place2d}.outUvFilterSize", f"{self.node}.uvFilterSize")
        return self.node

    def connect(self, target_attr):
        if self.node:
            try:
                cmds.connectAttr(f"{self.node}.outColor", target_attr, force=True)
            except Exception as e:
                print(f"Warning: Could not connect {self.node} to {target_attr}: {e}")
