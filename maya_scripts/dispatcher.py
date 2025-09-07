import importlib

# Map node types to their module names
NODE_MAP = {
    "Principled BSDF": "nodes.principled_bsdf",
    "Image Texture": "nodes.image_texture",
    "Mix Shader": "nodes.mix_shader",
}

def dispatch_node(node_type, node_data):
    """Load the correct node module and run its create() method."""
    module_name = NODE_MAP.get(node_type)
    if not module_name:
        print(f"[Dispatcher] No module mapped for node type: {node_type}")
        return None

    module = importlib.import_module(module_name)
    importlib.reload(module)  # ensure latest changes are picked up
    return module.create(node_data)
