"""
nodes/__init__.py
Registry for supported nodes.
"""
from .image_texture import ImageTextureNode
from .principled_bsdf import PrincipledBSDFNode

registry = {
    "Image Texture": ImageTextureNode,
    "Principled BSDF": PrincipledBSDFNode,
}