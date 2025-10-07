import torch
import node_helpers

class BaseTextEncodeQwenImageEditAdv:
    """
    这是一个用于 Qwen-VL 高级编码节点的基类，不应直接作为节点使用。
    它封装了处理一个图像列表、生成 conditioning 和 batched latent 的核心逻辑。
    子类需要实现自己的 `encode` 方法，并调用本类的 `process_encode` 方法。
    """
    RETURN_TYPES = ("CONDITIONING", "LATENT",)
    CATEGORY = "QwenImageEditAdv/conditioning"

    def process_encode(self, clip, prompt, vae, image_list):
        """
        核心处理函数，接收一个准备好的图像张量列表。
        :param clip: CLIP 模型
        :param prompt: 文本提示
        :param vae: VAE 模型
        :param image_list: 一个列表，其中每个元素都是一个 shape 为 [1, C, H, W] 的图像张量
        :return: (conditioning, latent_dict)
        """
        ref_latents = []
        images_for_vl = []

        llama_template = "<|im_start|>system\nDescribe the key features of the input image (color, shape, size, texture, objects, background), then explain how the user's text instruction should alter or modify the image. Generate a new image that meets the user's requirements while maintaining consistency with the original input where appropriate.<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n"
        image_prompt_segment = ""

        # 遍历由子类准备好的图像列表
        for i, image_tensor in enumerate(image_list):
            images_for_vl.append(image_tensor[:, :, :, :3])

            if vae is not None:
                latent = vae.encode(image_tensor[:, :, :, :3])
                ref_latents.append(latent)

            image_prompt_segment += "Picture {}: <|vision_start|><|image_pad|><|vision_end|>".format(i + 1)
        
        full_prompt = image_prompt_segment + prompt
        tokens = clip.tokenize(full_prompt, images=images_for_vl, llama_template=llama_template)
        conditioning = clip.encode_from_tokens_scheduled(tokens)

        batched_latent_output = None
        if len(ref_latents) > 0:
            conditioning = node_helpers.conditioning_set_values(conditioning, {"reference_latents": ref_latents}, append=True)
            batched_latent_output = torch.cat(ref_latents, dim=0)

        return (conditioning, {"samples": batched_latent_output})
      
class TextEncodeQwenImageEditPlusAdv(BaseTextEncodeQwenImageEditAdv):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            },
            "optional": {
                "vae": ("VAE",),
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
            },
        }

    FUNCTION = "encode"

    def encode(self, clip, prompt, vae=None, image1=None, image2=None, image3=None):
        # 这里假设取到的image都是 [1, C, H, W] 的张量
        image_list = []
        for img in [image1, image2, image3]:
            if img is not None:
                image_list.append(img)

        return self.process_encode(clip, prompt, vae, image_list)
      
class TextEncodeQwenImageEditInfAdv(BaseTextEncodeQwenImageEditAdv):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            },
            "optional": {
                "vae": ("VAE",),
                "images": ("IMAGE",),
            },
        }

    FUNCTION = "encode"

    def encode(self, clip, prompt, vae=None, images=None):
        image_list = []
        if images is not None:
            # 将 shape 为 [B, C, H, W] 的张量拆分为 B 个 shape 为 [1, C, H, W] 的张量列表
            for i in range(images.shape[0]):
                image_list.append(images[i:i+1, :, :, :])

        return self.process_encode(clip, prompt, vae, image_list)