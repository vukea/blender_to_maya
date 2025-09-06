import maya.cmds as cmds
from .base_node import BaseNode

class PrincipledBSDFNode(BaseNode):
    def create(self):
        if not cmds.objExists(self.name):
            self.node = cmds.shadingNode('aiStandardSurface', asShader=True, name=self.name)
        else:
            self.node = self.name
        return self.node

    def set_default(self, attr_name, value):
        if self.node:
            try:
                cmds.setAttr(f"{self.node}.{attr_name}", value, type='double3' if isinstance(value, (list, tuple)) else None)
            except Exception as e:
                print(f"Warning: Could not set {attr_name} on {self.node}: {e}")

    def connect(self, target_attr):
        if self.node:
            try:
                cmds.connectAttr(f"{self.node}.outColor", target_attr, force=True)
            except Exception as e:
                print(f"Warning: Could not connect {self.node} to {target_attr}: {e}")
