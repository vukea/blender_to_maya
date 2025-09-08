import bpy

# -----------------------------
# Recursive upstream search
# -----------------------------
def find_linked_image_nodes(socket, visited=None):
    """Recursively find all Image Texture nodes connected upstream from a socket."""
    if visited is None:
        visited = set()

    image_nodes = []
    for link in socket.links:
        from_node = link.from_node
        if from_node in visited:
            continue
        visited.add(from_node)

        if from_node.type == 'TEX_IMAGE':
            image_nodes.append(from_node)

        # Search deeper through node inputs
        for input_socket in from_node.inputs:
            image_nodes.extend(find_linked_image_nodes(input_socket, visited))

    return image_nodes


# -----------------------------
# Core function
# -----------------------------
def enforce_image_colorspaces():
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue

        nt = mat.node_tree
        for node in nt.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                for input_name, socket in node.inputs.items():
                    if not socket:
                        continue

                    image_nodes = find_linked_image_nodes(socket)

                    for img_node in image_nodes:
                        if not img_node.image:
                            continue

                        # Rule 1: Base Color chain -> sRGB
                        if input_name == "Base Color":
                            if img_node.image.colorspace_settings.name != "sRGB":
                                print(f"[{mat.name}] {img_node.image.name} → sRGB")
                                img_node.image.colorspace_settings.name = "sRGB"

                        # Rule 2: All other inputs -> Non-Color
                        else:
                            if img_node.image.colorspace_settings.name != "Non-Color":
                                print(f"[{mat.name}] {img_node.image.name} → Non-Color")
                                img_node.image.colorspace_settings.name = "Non-Color"


# -----------------------------
# Run it once
# -----------------------------
enforce_image_colorspaces()
