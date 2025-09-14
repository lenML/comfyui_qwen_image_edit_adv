import node_helpers
import comfy.utils
import math


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

    RETURN_TYPES = ("CONDITIONING",)
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
        return (conditioning,)


class QwenImageEditScale:
    UPSCALE_METHODS = ["area", "bicubic", "bilinear", "nearest-exact", "lanczos"]
    CROP_METHODS = ["disabled", "center"]

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "upscale_method": (s.UPSCALE_METHODS, {"default": "area"}),
                "crop": (s.CROP_METHODS, {"default": "disabled"}),
            },
            "optional": {
                "target_megapixels": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.1,
                        "max": 16.0,
                        "step": 0.1,
                        "round": 0.01,
                    },
                ),
                "alignment": ("INT", {"default": 32, "min": 8, "max": 128, "step": 8}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "width", "height")
    FUNCTION = "scale_and_align"

    CATEGORY = "QwenImageEditAdv/Scale"

    def scale_and_align(
        self, image, upscale_method, crop, target_megapixels=1.0, alignment=32
    ):
        # image tensor shape: [Batch, Height, Width, Channels]
        # comfy.utils.common_upscale expects: [Batch, Channels, Height, Width]
        samples = image.movedim(-1, 1)

        original_height = samples.shape[2]
        original_width = samples.shape[3]

        if original_height == 0 or original_width == 0:
            return (image, 0, 0)

        # 1. 计算保持宽高比的新尺寸
        target_total_pixels = target_megapixels * 1024 * 1024
        aspect_ratio = original_width / original_height

        # h * w = total_pixels
        # w = h * aspect_ratio
        # h * (h * aspect_ratio) = total_pixels => h^2 * aspect_ratio = total_pixels

        new_height = math.sqrt(target_total_pixels / aspect_ratio)
        new_width = new_height * aspect_ratio

        # 2. 将尺寸对齐到指定倍数
        # 注意: common_upscale 内部会处理crop，我们这里只需要提供最终的目标尺寸
        aligned_width = round(new_width / alignment) * alignment
        aligned_height = round(new_height / alignment) * alignment

        # 如果对齐后尺寸为0，则避免缩放
        if aligned_width == 0 or aligned_height == 0:
            # 返回原始图像和尺寸，避免错误
            return (image, original_width, original_height)

        # 3. 使用对齐后的尺寸和用户选择的方法进行缩放
        s = comfy.utils.common_upscale(
            samples, int(aligned_width), int(aligned_height), upscale_method, crop
        )

        # Convert back to [Batch, Height, Width, Channels]
        aligned_image = s.movedim(1, -1)

        return (aligned_image, int(aligned_width), int(aligned_height))
