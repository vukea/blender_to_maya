import bpy

class DeleteFloatingNodes:
    @staticmethod
    def delete_unused_nodes():
        """Delete unconnected nodes and useless normal/bump nodes."""
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            # Collect nodes to remove
            to_remove = []

            for n in nodes:
                inputs = list(n.inputs)
                outputs = list(n.outputs)

                # --- 1. Standard unused nodes ---
                if not any(s.is_linked for s in inputs + outputs) and n.type != 'OUTPUT_MATERIAL':
                    to_remove.append(n)
                    continue

                # --- 2. Normal/Bump nodes with no color input connected ---
                if n.type in {'NORMAL_MAP', 'BUMP'}:
                    # Check if output is connected to a Principled BSDF Normal input
                    connected_to_normal = False
                    for out_socket in outputs:
                        for link in out_socket.links:
                            if link.to_socket.name == 'Normal' and link.to_node.type == 'BSDF_PRINCIPLED':
                                connected_to_normal = True
                                break
                    # If connected to Normal but input is empty, mark for removal
                    if connected_to_normal:
                        # NORMAL_MAP nodes: check "Color" input
                        if n.type == 'NORMAL_MAP' and not n.inputs['Color'].is_linked:
                            to_remove.append(n)
                        # BUMP nodes: check "Height" input
                        elif n.type == 'BUMP' and not n.inputs['Height'].is_linked:
                            to_remove.append(n)

            # Remove collected nodes
            for node in to_remove:
                nodes.remove(node)

        print("Unused nodes and dead normal/bump nodes deleted.")

    @staticmethod
    def delete_unused_materials():
        """Delete materials not assigned to any object."""
        unused_mats = [m for m in bpy.data.materials if m.users == 0]
        for mat in unused_mats:
            bpy.data.materials.remove(mat)
        print("Unused materials deleted.")

    @classmethod
    def clean_all(cls):
        cls.delete_unused_nodes()
        cls.delete_unused_materials()
        print("Material cleaning complete.")


# --- Usage ---
if __name__ == "__main__":
    DeleteFloatingNodes.clean_all()
