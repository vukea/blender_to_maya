"""
image_texture.py
Builds file + place2dTexture nodes for Image Texture.
"""
import maya.cmds as cmds
import os
from .base_node import BaseNode


class ImageTextureNode(BaseNode):
    def build(self, node_json, desired_attribute=None, material_name=None):
        file_path = node_json.get("file_path")
        if not file_path:
            print("ImageTextureNode: no file_path in JSON.")
            return None

        file_path = os.path.normpath(file_path)

        place2d = cmds.shadingNode("place2dTexture", asUtility=True, name=self._unique_name("place2d", material_name))
        file_node = cmds.shadingNode("file", asTexture=True, name=self._unique_name("fileTex", material_name))

        # connect common attrs
        for attr in ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV",
                     "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV", "noiseUV"]:
            try:
                cmds.connectAttr(place2d + "." + attr, file_node + "." + attr, f=True)
            except:
                pass
        cmds.connectAttr(place2d + ".outUV", file_node + ".uvCoord", f=True)

        cmds.setAttr(file_node + ".fileTextureName", file_path, type="string")

        # decide output plug
        if desired_attribute and "color" in desired_attribute.lower():
            return file_node + ".outColor"
        else:
            return file_node + ".outColorR"