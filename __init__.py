from .nodes import *

NODE_CLASS_MAPPINGS = {
    "TextEncodeQwenImageEditAdv": TextEncodeQwenImageEditAdv,
    "QwenImageEditScale": QwenImageEditScale,
    "QwenImageEditSimpleScale": QwenImageEditSimpleScale
}


__all__ = ['NODE_CLASS_MAPPINGS']
