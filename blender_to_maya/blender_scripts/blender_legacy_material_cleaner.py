import bpy

class LegacyMaterialCleaner:
    def __init__(self):
        self.shader_map = {
            'BSDF_GLASS': self.copy_glass_to_principled,
            'EMISSION': self.copy_emission_to_principled,
            'BSDF_DIFFUSE': self.copy_diffuse_to_principled
        }

    def clean_scene_materials(self):
        for mat in bpy.data.materials:
            if mat.node_tree:
                self.clean_material(mat)

    def clean_material(self, mat):
        nodes = mat.node_tree.nodes
        for node in list(nodes):
            if node.type in self.shader_map:
                self.replace_node(mat, node)

    def replace_node(self, mat, node):
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = node.location

        # Copy shader-specific properties
        self.shader_map[node.type](node, principled)

        # Reconnect outgoing links
        for output in node.outputs:
            for link in output.links:
                links.new(principled.outputs[0], link.to_socket)

        nodes.remove(node)

    # --- Copy functions ---
    def copy_glass_to_principled(self, old_node, new_node):
        if 'Transmission Weight' in new_node.inputs:
            new_node.inputs['Transmission Weight'].default_value = 1.0
        if 'Base Color' in new_node.inputs and 'Color' in old_node.inputs:
            new_node.inputs['Base Color'].default_value = old_node.inputs['Color'].default_value
        if 'Roughness' in new_node.inputs and 'Roughness' in old_node.inputs:
            new_node.inputs['Roughness'].default_value = old_node.inputs['Roughness'].default_value
        if 'IOR' in new_node.inputs and 'IOR' in old_node.inputs:
            new_node.inputs['IOR'].default_value = old_node.inputs['IOR'].default_value

    def copy_emission_to_principled(self, old_node, new_node):
        # Set color to both Emission Color and Base Color
        if 'Emission Color' in new_node.inputs and 'Color' in old_node.inputs:
            new_node.inputs['Emission Color'].default_value = old_node.inputs['Color'].default_value
        if 'Base Color' in new_node.inputs and 'Color' in old_node.inputs:
            new_node.inputs['Base Color'].default_value = old_node.inputs['Color'].default_value
        # Set emission strength
        if 'Emission Strength' in new_node.inputs and 'Strength' in old_node.inputs:
            new_node.inputs['Emission Strength'].default_value = old_node.inputs['Strength'].default_value

    def copy_diffuse_to_principled(self, old_node, new_node):
        if 'Base Color' in new_node.inputs and 'Color' in old_node.inputs:
            new_node.inputs['Base Color'].default_value = old_node.inputs['Color'].default_value
        if 'Roughness' in new_node.inputs and 'Roughness' in old_node.inputs:
            new_node.inputs['Roughness'].default_value = old_node.inputs['Roughness'].default_value

# --- Run ---
if __name__ == "__main__":
    legacy_mat_cleaner = LegacyMaterialCleaner()
    legacy_mat_cleaner.clean_scene_materials()

