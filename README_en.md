[cn](./README.md) | [en](./README_en.md)

# Qwen Image Edit Adv - ComfyUI Nodes

This repository provides improved **Qwen Image Edit** custom nodes.
The main goal is to fix the **editing offset issue** caused by ComfyUI’s built-in node, and to provide more flexible scaling and cropping logic.

Main nodes:

- **TextEncodeQwenImageEditAdv**: Handles image + prompt encoding only, without scaling
- **QwenImageEditScale**: Provides configurable scaling and cropping logic tailored for Qwen Image Edit models
- **QwenImageEditSimpleScale**: Simplified version that automatically chooses the most suitable resolution

<img width="946" height="683" alt="image" src="https://github.com/user-attachments/assets/4f57406b-5b11-4738-a833-2eaed4e54c0f" />

> In comparative testing, this implementation eliminates offset issues and does not require multiple re-rolls for stable results.

---

## Background

ComfyUI’s built-in `TextEncodeQwenImageEdit` node contains hard-coded scaling logic.
However, this scaling approach is not fully aligned with the official Qwen Image Edit requirements and is difficult to debug.

This repository **separates scaling from encoding**, and provides more reasonable scaling strategies for easier testing and fine-tuning.

You can use [`./workflows/demo_compare.json`](./workflows/demo_compare.json) to quickly compare the official workflow with the custom nodes, and inspect consistency via the comparer.

---

## Nodes & Parameters

### 1. TextEncodeQwenImageEditAdv

<img width="675" height="378" alt="image" src="https://github.com/user-attachments/assets/69a05fe7-b213-43bf-bfee-47f88fda65d4" />

Works almost the same as the built-in `TextEncodeQwenImageEdit`:

- Inputs: `clip`, `prompt`, optional `vae` and `image`
- Outputs: **conditioning** and **latent**
- No scaling logic included → fully transparent and controllable

---

### 2. QwenImageEditScale

<img width="459" height="368" alt="image" src="https://github.com/user-attachments/assets/548bcec4-9533-4e25-aef4-e30ffd0a9542" />

Provides highly configurable scaling and cropping logic.

**Parameters:**

- **upscale_method**: Resizing method (`area` / `bicubic` / `bilinear` / `nearest-exact` / `lanczos`) — usually fine to leave default

- **ratio_strategy**: Aspect ratio handling strategy

  - `disabled`: No ratio adjustment
  - `closest`: Auto-crop to the closest officially supported ratio
  - `W:H`: Force crop to a specific ratio (e.g. `3:2`)

- **target_megapixels**:

  - Controls total pixels after scaling
  - Default `1.0` → roughly `1024x1024`
  - Valid range: `0.3M ~ 1.4M`
  - Recommended values: `1`, `0.65`, `0.95`, `0.9`, `2`
  - Larger → more freedom, but less faithful to the prompt
  - Smaller → stronger consistency, less offset

- **alignment**: Step size for dimension alignment (default `32`, official training value).
  Recommended values: `32`, `16`, `56`, `14`, `8`

**Outputs:**

- `IMAGE`: Resized image
- `width` / `height`: Actual output resolution
- `ratio`: Cropped aspect ratio string (e.g. `3:2`)

---

### 3. QwenImageEditSimpleScale

<img width="473" height="244" alt="image" src="https://github.com/user-attachments/assets/b7f18ef8-1513-4899-a4bd-3392adf89980" />

A simplified version of `QwenImageEditScale`:

- Automatically selects the most suitable scaling ratio based on input size
- Ensures resolution falls within **Qwen Image Edit’s acceptable range (\~1M pixels)**
- Only requires two settings:

  - **resolution**: Target resolution (default `1024`) → in practice, almost only `1024` works properly due to model training
  - **alignment**: Alignment step (default `32`) → rarely needs to be changed, but you can experiment with `32`, `56`, `16`, `8`

**Use cases:**

- For general use → **QwenImageEditSimpleScale** is recommended
- For manual fine-tuning → use **QwenImageEditScale**
- You can also use any other resize node outside this package, but it requires more manual adjustment

---

## Recommended LoRAs

Combining the following LoRAs can further improve consistency and low-resolution performance:

- [DiffSynth-Studio/Qwen-Image-Edit-Lowres-Fix](https://modelscope.cn/models/DiffSynth-Studio/Qwen-Image-Edit-Lowres-Fix/files)
- [QwenEdit Consistence Edit Lora](https://civitai.com/models/1939453/qwenedit-consistance-edit-lora) by xiaozhijason
