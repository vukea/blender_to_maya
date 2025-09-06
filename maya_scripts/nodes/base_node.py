"""
base_node.py
Abstract base class for node builders.
"""

class BaseNode:
    def _unique_name(self, base, material_name=None):
        return "{}_{}".format(material_name, base) if material_name else base

    def build(self, node_json, desired_attribute=None, material_name=None):
        raise NotImplementedError