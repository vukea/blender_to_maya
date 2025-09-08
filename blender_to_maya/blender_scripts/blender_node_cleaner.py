import bpy

class MaterialNodeCleaner:
    """
    Soft-deletes unwanted nodes, emulating Ctrl+X, reconnecting upstream to downstream
    regardless of exact socket type (like Blender does). Keeps Texture Coordinate node.
    """
    def __init__(self):
        self.allowed_nodes = {
            "BSDF_PRINCIPLED",
            "MIX_SHADER",
            "MIX_RGB",
            "TEX_IMAGE",
            "HUE_SAT",
            "INVERT",
            "RGB",
            "TEX_NOISE",
            "TEX_CHECKER",
            "VALTORGB",
            "VALUE",
            "MAPPING",
            "NORMAL_MAP",
            "BUMP",
            "OUTPUT_MATERIAL",
            "TEX_COORD"  # Texture Coordinate node
        }

    def soft_delete_node(self, node):
        tree = node.id_data
        # Collect first upstream connection
        first_input_source = None
        for input_sock in node.inputs:
            if input_sock.is_linked:
                first_input_source = input_sock.links[0].from_socket
                break

        if first_input_source:
            # Connect this source to all output links
            for output_sock in node.outputs:
                for link in list(output_sock.links):
                    tree.links.new(first_input_source, link.to_socket)

        # Remove node
        tree.nodes.remove(node)

    def clean_materials(self):
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            nodes = list(mat.node_tree.nodes)
            for node in nodes:
                if node.type not in self.allowed_nodes and node.type != "MIX":
                    self.soft_delete_node(node)

        print("Node cleanup complete!")


# Usage
if __name__ == "__main__":
    node_cleaner = MaterialNodeCleaner()
    node_cleaner.clean_materials()
