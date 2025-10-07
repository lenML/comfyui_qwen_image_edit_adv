import node_helpers
import comfy.utils
import math
import torch

class QwenImageEditScaleBase:
    """基础缩放逻辑，供子类复用"""

    UPSCALE_METHODS = ["area", "bicubic", "bilinear", "nearest-exact", "lanczos"]
    CROP_METHODS = ["disabled", "center"]

    ALLOWED_ASPECT_RATIOS = [
        (1, 1),
        (2, 3),
        (3, 2),
        (3, 4),
        (4, 3),
        (9, 16),
        (16, 9),
        (1, 3),
        (3, 1),
    ]

    CROP_STRATEGIES = ["disabled", "closest", "fixed"]  # 新增配置

    @classmethod
    def ratio_choices(cls):
        """生成 'W:H' 格式的字符串列表"""
        return [f"{w}:{h}" for w, h in cls.ALLOWED_ASPECT_RATIOS]

    @classmethod
    def parse_ratio(cls, ratio_str):
        """从 'W:H' 解析成 (w, h)"""
        if isinstance(ratio_str, str) and ":" in ratio_str:
            w, h = ratio_str.split(":")
            return int(w), int(h)
        return None

    def find_closest_ratio(self, w, h, allowed_ratios):
        aspect_ratio = w / h
        best_ratio = None
        best_diff = float("inf")
        for rw, rh in allowed_ratios:
            r = rw / rh
            diff = abs(r - aspect_ratio)
            if diff < best_diff:
                best_diff = diff
                best_ratio = (rw, rh)
        return best_ratio

    def center_crop_to_ratio(self, image, target_ratio):
        # image shape: [B, C, H, W]
        b, c, h, w = image.shape
        target_w, target_h = target_ratio
        target_aspect = target_w / target_h
        current_aspect = w / h

        if current_aspect > target_aspect:
            # 裁宽
            new_w = int(h * target_aspect)
            offset = (w - new_w) // 2
            cropped = image[:, :, :, offset : offset + new_w]
        else:
            # 裁高
            new_h = int(w / target_aspect)
            offset = (h - new_h) // 2
            cropped = image[:, :, offset : offset + new_h, :]
        return cropped

    def apply_crop_strategy(self, samples, crop_strategy, fixed_ratio=None):
        """根据策略裁剪：disabled / closest / fixed"""
        h, w = samples.shape[2], samples.shape[3]

        if crop_strategy == "disabled":
            return samples
        elif crop_strategy == "closest":
            target_ratio = self.find_closest_ratio(w, h, self.ALLOWED_ASPECT_RATIOS)
            return self.center_crop_to_ratio(samples, target_ratio)
        elif crop_strategy == "fixed" and fixed_ratio is not None:
            ratio_tuple = self.parse_ratio(fixed_ratio)
            if ratio_tuple:
                return self.center_crop_to_ratio(samples, ratio_tuple)
        return samples

    def upscale_and_align(
        self,
        samples,
        new_width,
        new_height,
        upscale_method,
        crop,
        target_total_pixels,
        alignment,
    ):
        aligned_width = int(new_width) // alignment * alignment
        aligned_height = int(new_height) // alignment * alignment

        while aligned_width * aligned_height > target_total_pixels:
            aligned_width -= alignment
            aligned_height -= alignment

        if aligned_width <= 0 or aligned_height <= 0:
            return samples, 0, 0

        s = comfy.utils.common_upscale(
            samples, aligned_width, aligned_height, upscale_method, crop
        )
        return s, aligned_width, aligned_height


class QwenImageEditScale(QwenImageEditScaleBase):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "upscale_method": (s.UPSCALE_METHODS, {"default": "area"}),
                "ratio_strategy": (
                    ["disabled", "closest"] + s.ratio_choices(),
                    {"default": "closest"},
                ),
            },
            "optional": {
                "target_megapixels": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.01,
                        "max": 16.0,
                        "step": 0.01,
                        "round": 0.01,
                    },
                ),
                "alignment": ("INT", {"default": 32, "min": 8, "max": 128, "step": 8}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("IMAGE", "width", "height", "ratio")
    FUNCTION = "scale_and_align"
    CATEGORY = "QwenImageEditAdv/Scale"

    def scale_and_align(
        self,
        image,
        upscale_method,
        ratio_strategy="closest",
        target_megapixels=1.0,
        alignment=32,
    ):
        samples = image.movedim(-1, 1)
        h, w = samples.shape[2], samples.shape[3]
        if h == 0 or w == 0:
            return (image, 0, 0, "invalid")

        # clamp total pixels in safe range [0.3M, 1.4M]
        target_total_pixels = int(target_megapixels * 1024 * 1024)
        target_total_pixels = max(300_000, min(target_total_pixels, 1_400_000))

        # decide ratio
        if ratio_strategy == "disabled":
            rw, rh = w, h
        elif ratio_strategy == "closest":
            rw, rh = self.find_closest_ratio(w, h, self.ALLOWED_ASPECT_RATIOS)
            samples = self.center_crop_to_ratio(samples, (rw, rh))
        else:
            rw, rh = self.parse_ratio(ratio_strategy)
            samples = self.center_crop_to_ratio(samples, (rw, rh))

        aspect_ratio = rw / rh

        # 计算缩放因子
        scale_factor = math.sqrt(target_total_pixels / (w * h))
        new_width = w * scale_factor
        new_height = h * scale_factor

        # 对齐
        aligned_width = round(new_width / alignment) * alignment
        aligned_height = round(new_height / alignment) * alignment

        if aligned_width <= 0 or aligned_height <= 0:
            return (image, 0, 0, f"{rw}:{rh}")

        s = comfy.utils.common_upscale(
            samples, aligned_width, aligned_height, upscale_method, "center"
        )
        aligned_image = s.movedim(1, -1)
        return (aligned_image, aligned_width, aligned_height, f"{rw}:{rh}")


# 生成允许的分辨率
def generate_allowed_resolutions(
    min_pixels=256**2, max_pixels=1328**2, step=32, ratios=None
):
    allowed = []
    if ratios is None:
        ratios = [
            (1, 1),
            (2, 3),
            (3, 2),
            (3, 4),
            (4, 3),
            (9, 16),
            (16, 9),
            (1, 3),
            (3, 1),
            (4, 5),
            (5, 4),
            (2, 1),
            (1, 2),
        ]
    for rw, rh in ratios:
        max_w = int((max_pixels * rw / rh) ** 0.5)
        w = step
        while w <= max_w:
            h = int(w * rh / rw)
            h = (h // step) * step
            total_pixels = w * h
            if total_pixels < min_pixels:
                w += step
                continue
            if total_pixels > max_pixels:
                break
            allowed.append((w, h))
            w += step
    return allowed


class QwenImageEditSimpleScale:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "resolution": (
                    "INT",
                    {"default": 1024, "min": 512, "max": 4096, "step": 8},
                ),
                "alignment": (
                    "INT",
                    {"default": 32, "min": 8, "max": 256, "step": 2},
                ),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "width", "height")
    CATEGORY = "QwenImageEditAdv/Scale"

    FUNCTION = "scale"
    DESCRIPTION = "Resizes image to the closest Qwen-Image-Edit compatible resolution (1M pixels), with configurable max side length and step alignment."

    def scale(self, image, resolution=1024, alignment=32):
        h, w = image.shape[1:3]

        res = resolution**2
        input_size = h * w
        scale_factor = math.sqrt(res / input_size)

        nh = h * scale_factor
        nw = w * scale_factor
        nh = round(nh / alignment) * alignment
        nw = round(nw / alignment) * alignment

        image = comfy.utils.common_upscale(
            image.movedim(-1, 1), nw, nh, "lanczos", "center"
        ).movedim(1, -1)
        return (image, nw, nh)
