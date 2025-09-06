"""
principled_bsdf.py
Stub class for Principled BSDF (handled at material level).
"""
from .base_node import BaseNode

class PrincipledBSDFNode(BaseNode):
    def build(self, node_json, desired_attribute=None, material_name=None):
        print("PrincipledBSDFNode is handled by MaterialBuilder. Skipping explicit node build.")
        return None