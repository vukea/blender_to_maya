# dispatcher.py
import sys
import os
import importlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NODES_DIR = os.path.join(BASE_DIR, "nodes")

if NODES_DIR not in sys.path:
    sys.path.append(NODES_DIR)


def dispatch_node(node_type, node_name, node_data):
    """
    Dynamically import a node module and call its create() function.
    Supports both module-level create() and class-level create().
    """
    try:
        module_name = node_type.lower().replace(" ", "_")  # e.g. "Principled BSDF" → "principled_bsdf"
        module = importlib.import_module(module_name)
        importlib.reload(module)

        # Prefer module-level create()
        if hasattr(module, "create"):
            return module.create(node_name, node_data)

        # Fallback: class-level create()
        class_name = "".join(word.title() for word in node_type.split())  # "Image Texture" → "ImageTexture"
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            return cls.create(node_name, node_data)

        raise AttributeError(f"No valid create() found in module '{module_name}'")

    except Exception as e:
        print(f"[dispatcher] ERROR dispatching '{node_type}' as '{node_name}': {e}")
        return None
