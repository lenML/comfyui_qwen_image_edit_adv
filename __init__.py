from .nodes_edit import TextEncodeQwenImageEditAdv
from .nodes_scale import QwenImageEditScale, QwenImageEditSimpleScale
from .nodes_plus import TextEncodeQwenImageEditPlusAdv, TextEncodeQwenImageEditInfAdv

NODE_CLASS_MAPPINGS = {
    "TextEncodeQwenImageEditAdv": TextEncodeQwenImageEditAdv,
    "QwenImageEditScale": QwenImageEditScale,
    "QwenImageEditSimpleScale": QwenImageEditSimpleScale,
    "TextEncodeQwenImageEditPlusAdv": TextEncodeQwenImageEditPlusAdv,
    "TextEncodeQwenImageEditInfAdv": TextEncodeQwenImageEditInfAdv
}


__all__ = ['NODE_CLASS_MAPPINGS']
