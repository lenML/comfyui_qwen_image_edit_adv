import node_helpers
import comfy.utils
import math
import torch


class TextEncodeQwenImageEditAdv:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            },
            "optional": {
                "vae": ("VAE",),
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = (
        "CONDITIONING",
        "LATENT",
    )
    FUNCTION = "encode"

    CATEGORY = "QwenImageEditAdv/conditioning"

    def encode(self, clip, prompt, vae=None, image=None):
        ref_latent = None
        if image is None:
            images = []
        else:
            images = [image[:, :, :, :3]]
            if vae is not None:
                ref_latent = vae.encode(image[:, :, :, :3])

        tokens = clip.tokenize(prompt, images=images)
        conditioning = clip.encode_from_tokens_scheduled(tokens)
        if ref_latent is not None:
            conditioning = node_helpers.conditioning_set_values(
                conditioning, {"reference_latents": [ref_latent]}, append=True
            )
        return (conditioning, {"samples": ref_latent})
