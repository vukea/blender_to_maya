import maya.cmds as cmds
import maya.mel as mel

class LegacyToArnoldConverter:
    def __init__(self):
        self.legacy_shaders = ['lambert', 'blinn', 'phong', 'phongE', 'surfaceShader']
        self.default_materials = ['lambert1', 'particleCloud1', 'shaderGlow1', 'layerShader1']

    def convert_scene(self):
        materials = cmds.ls(mat=True)
        for mat in materials:
            if mat in self.default_materials:
                continue
            if cmds.nodeType(mat) in self.legacy_shaders:
                self.convert_material(mat)

        # Delete unused nodes using Maya's built-in command
        self.delete_unused_nodes()

    def convert_material(self, old_mat):
        print(f"Converting: {old_mat}")

        old_name = old_mat
        new_mat = cmds.shadingNode('aiStandardSurface', asShader=True, name=f"{old_name}_temp")

        shading_groups = cmds.listConnections(old_mat, type='shadingEngine') or []
        for sg in shading_groups:
            cmds.connectAttr(f"{new_mat}.outColor", f"{sg}.surfaceShader", force=True)

        if cmds.attributeQuery('color', node=old_mat, exists=True):
            color = cmds.getAttr(f"{old_mat}.color")[0]
            cmds.setAttr(f"{new_mat}.baseColor", *color, type="double3")

        if cmds.attributeQuery('incandescence', node=old_mat, exists=True):
            emission = cmds.getAttr(f"{old_mat}.incandescence")[0]
            cmds.setAttr(f"{new_mat}.emissionColor", *emission, type="double3")
            if emission != (0,0,0):
                cmds.setAttr(f"{new_mat}.emission", 1.0)

        if cmds.nodeType(old_mat) in ['blinn', 'phong', 'phongE']:
            if cmds.attributeQuery('specularColor', node=old_mat, exists=True):
                spec = cmds.getAttr(f"{old_mat}.specularColor")[0]
                cmds.setAttr(f"{new_mat}.specularColor", *spec, type="double3")
            if cmds.attributeQuery('eccentricity', node=old_mat, exists=True):
                rough = 1.0 - cmds.getAttr(f"{old_mat}.eccentricity")
                cmds.setAttr(f"{new_mat}.specularRoughness", rough)

        # Delete old shader
        cmds.delete(old_mat)

        # Rename new shader to the old shader's name
        new_mat = cmds.rename(new_mat, old_name)

        print(f"Converted {old_mat} -> {new_mat}")

    def delete_unused_nodes(self):
        print("Deleting unused nodes...")
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
        print("Unused nodes deleted.")


# Usage
if __name__ == "__main__":
    converter = LegacyToArnoldConverter()
    converter.convert_scene()
