[cn](./README.md) | [en](./README_en.md)

# Qwen Image Edit Adv - ComfyUI Nodes

This repository provides improved custom nodes for **Qwen Image Edit**.

**Main Goals:**

1.  **Fix Offset Issues**: Resolves the image shift/offset problem caused by the forced internal scaling of the built-in ComfyUI nodes.
2.  **Multi-Image Context**: Adds support for multiple reference images, going beyond simple single-image editing.
3.  **Flexible Scaling**: Provides professional scaling tools tailored to the model's training distribution (1024px, 32-pixel alignment).

---

## Node List

This plugin consists of two categories of nodes: **Encoding Nodes** and **Scaling Nodes**.

### 1. Encoding Nodes

These nodes are solely responsible for encoding Prompts and Image Latents. They **contain no scaling logic**, ensuring the process is transparent and controllable. All encoding nodes inherit from the same base class and output `CONDITIONING` and `LATENT`.

#### 🛠️ TextEncodeQwenImageEditAdv (Standard)

- **Input**: Single image (`image`).
- **Use Case**: Standard single-image editing tasks.
- **Function**: Similar to the native built-in node, but with scaling removed and internal logic fixed.

#### 🛠️ TextEncodeQwenImageEditPlusAdv (Three-Image Support)

- **Input**: Explicit inputs for three images (`image1`, `image2`, `image3`).
- **Use Case**: Scenarios requiring fixed multi-image references.
- **Function**: You can connect different image sources independently. The model interprets them sequentially as "Picture 1", "Picture 2", etc., and processes them combined with the Prompt.

#### 🛠️ TextEncodeQwenImageEditInfAdv (Infinite/Batch Support)

- **Input**: An image batch (`images`).
- **Use Case**: Dynamic multi-image scenarios, lists of images, or when using more than 3 reference images.
- **Function**: Deconstructs the input Image Batch (e.g., images merged via a Batch Images node) into a sequence of reference images.
- **Note**: This is **NOT** "Batch Generation" (generating multiple images at once). It is "Multi-Image Context", where the entire batch is treated as multiple reference materials for a single task.

---

### 2. Scaling Nodes

Since the Qwen Image Edit model is extremely sensitive to resolution (training data is concentrated around 1024x1024), it is highly recommended to preprocess images using the following nodes before entering the encoding nodes.

#### 📐 QwenImageEditSimpleScale (Recommended)

<img width="473" height="244" alt="image" src="https://github.com/user-attachments/assets/b7f18ef8-1513-4899-a4bd-3392adf89980" />

A simplified scaling node suitable for most scenarios.

- **Resolution**: Default `1024`. The model is best optimized for this resolution.
- **Logic**: Automatically calculates the scaling factor so that the total pixel count is close to 1M (1024x1024) while ensuring width and height meet the Alignment requirements.

#### 📐 QwenImageEditScale (Advanced)

<img width="459" height="368" alt="image" src="https://github.com/user-attachments/assets/548bcec4-9533-4e25-aef4-e30ffd0a9542" />

Provides highly configurable scaling and cropping logic, suitable for debugging.

- **ratio_strategy**:
  - `closest`: Automatically crops to the closest aspect ratio allowed by the official implementation (Recommended).
  - `disabled`: No cropping, scaling only.
  - `W:H`: Forces cropping to a specific ratio.
- **target_megapixels**: Controls total pixel count (Default `1.0`). Higher values give the model more freedom but may lead to artifacts; lower values increase consistency.
- **alignment**: Size alignment step (Default `32`).

---

## Why use these nodes?

### 1. Avoiding Offsets

The built-in `TextEncodeQwenImageEdit` node in ComfyUI includes hard-coded scaling logic that forces a resize of the input image, causing the generated Latent to shift in position relative to the original image. This plugin decouples **Scaling** from **Encoding**, allowing you to precisely control the dimensions of the image entering the model.

### 2. Multi-Image Editing Logic

Qwen-VL has multi-modal understanding capabilities. Using the `PlusAdv` and `InfAdv` nodes, the underlying Prompt is constructed as:

```
Picture 1: <vision_tokens...>
Picture 2: <vision_tokens...>
User: <prompt>
```

This enables complex editing tasks, such as "Generate a new image based on the composition of Picture 1 and the color scheme of Picture 2".

---

## Example Workflows

### Comparison Test

You can use the [`./workflows/demo_compare.json`](./workflows/demo_compare.json) workflow to quickly compare the output of the official process versus these nodes.

### Recommended Parameters

- **Resolution**: 1024
- **Alignment**: 32
- **CFG**: A lower CFG (e.g., 1.0 - 2.5) is recommended for better instruction following.

---

## LoRA Recommendations

Using the following LoRAs can further improve consistency and performance at lower resolutions:

- [DiffSynth-Studio/Qwen-Image-Edit-Lowres-Fix](https://modelscope.cn/models/DiffSynth-Studio/Qwen-Image-Edit-Lowres-Fix/files)
- [QwenEdit Consistance Edit Lora](https://civitai.com/models/1939453/qwenedit-consistance-edit-lora) by xiaozhijason
