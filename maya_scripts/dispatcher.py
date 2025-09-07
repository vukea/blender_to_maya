import importlib

NODE_MAP = {
    "Principled BSDF": "principled_bsdf",
    "Image Texture": "image_texture",
    # add more nodes as needed
}

def dispatch_node(shader_type, material_name, node_data):
    if shader_type in NODE_MAP:
        module_name = NODE_MAP[shader_type]
        module = importlib.import_module(module_name)
        importlib.reload(module)
        return module.create(material_name, node_data)
    else:
        print(f"⚠️ Unknown shader type: {shader_type}")
        return None
