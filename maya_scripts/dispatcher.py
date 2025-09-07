from nodes import principled_bsdf, image_texture, mix_shader

# Map Blender shader names → our modules
NODE_MAP = {
    "Principled BSDF": principled_bsdf,
    "Image Texture": image_texture,
    "Mix Shader": mix_shader,
}

def dispatch_node(shader_type, node_data):
    """Route shader creation to the correct module"""
    module = NODE_MAP.get(shader_type)
    if not module:
        print(f"[!] Unsupported node type: {shader_type}")
        return None
    return module.create(node_data)
