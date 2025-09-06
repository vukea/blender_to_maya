from .principled_bsdf import PrincipledBSDFNode
from .image_texture import ImageTextureNode
from .normal_map import NormalMapNode

NODE_REGISTRY = {
    "PrincipledBSDF": PrincipledBSDFNode,
    "ImageTexture": ImageTextureNode,
    "NormalMap": NormalMapNode,
}
