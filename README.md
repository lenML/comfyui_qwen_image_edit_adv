# Qwen Image Edit Adv - ComfyUI Nodes

[cn](./README.md) | [en](./README_en.md)

这里提供了改进后的 **Qwen Image Edit** 相关自定义节点。

主要目标：

1. **解决偏移问题**：修复 ComfyUI 内置节点因强制缩放导致的编辑结果偏移。
2. **多图上下文支持**：新增支持多张参考图像的输入（Multi-Image Context），不仅仅局限于单张图片编辑。
3. **灵活缩放**：提供符合模型训练分布（1024px, 32 对齐）的专业缩放工具。

---

## 节点列表

本插件包含两类节点：**编码节点 (Encoding)** 和 **缩放节点 (Scaling)**。

### 1. 编码节点 (Encoding Nodes)

这些节点仅负责编码 Prompt 和图像 Latent，**不包含任何缩放逻辑**，确保流程透明可控。所有编码节点均继承自同一基类，输出 `CONDITIONING` 和 `LATENT`。

#### 🛠️ TextEncodeQwenImageEditAdv (标准版)

- **输入**：单张图片 (`image`)
- **适用场景**：标准的单图编辑任务。
- **功能**：与原版内置节点类似，但移除了缩放，且修复了逻辑。

#### 🛠️ TextEncodeQwenImageEditPlusAdv (三图版)

- **输入**：显式的三个图片输入口 (`image1`, `image2`, `image3`)
- **适用场景**：需要固定多图参考的场景。
- **功能**：你可以将不同的图片源分别接入，模型会按顺序理解为 "Picture 1", "Picture 2"... 并结合 Prompt 进行处理。

#### 🛠️ TextEncodeQwenImageEditInfAdv (无限版/Batch 版)

- **输入**：一个图片批次 (`images`)
- **适用场景**：动态多图、图片列表或大于 3 张图片的场景。
- **功能**：将输入的 Image Batch（例如通过 Batch Images 节点合并的一组图片）拆解为多张参考图序列。
- **注意**：这不是“批量生成”，而是“多图上下文”。输入的 Batch 会被视为同一任务中的多张参考素材。

---

### 2. 缩放节点 (Scaling Nodes)

由于 Qwen Image Edit 模型对分辨率极其敏感（训练数据集中在 1024x1024 附近），建议在进入编码节点前使用以下节点对图像进行预处理。

#### 📐 QwenImageEditSimpleScale (推荐)

<img width="473" height="244" alt="image" src="https://github.com/user-attachments/assets/b7f18ef8-1513-4899-a4bd-3392adf89980" />

简化版缩放节点，大多数情况下使用此节点即可。

- **Resolution**：默认 `1024`。模型对此分辨率优化最好。
- **Logic**：自动计算缩放比例，使总像素量接近 1M (1024x1024)，并保证长宽符合 Alignment 要求。

#### 📐 QwenImageEditScale (高级)

<img width="459" height="368" alt="image" src="https://github.com/user-attachments/assets/548bcec4-9533-4e25-aef4-e30ffd0a9542" />

提供高度可配置的缩放与裁剪逻辑，适合调试。

- **ratio_strategy**:
  - `closest`: 自动裁剪为最接近的官方允许比例（推荐）。
  - `disabled`: 不裁剪，仅缩放。
  - `W:H`: 强制裁剪到指定比例。
- **target_megapixels**: 控制总像素量（推荐 1.0）。数值越大模型自由度越高但易崩坏，数值越小一致性越强。
- **alignment**: 尺寸对齐步长（推荐 32）。

---

## 为什么需要这些节点？

### 1. 避免偏移

ComfyUI 内置的 `TextEncodeQwenImageEdit` 包含强绑定的缩放，导致输入图片被强制 Resize，从而使生成的 Latent 与原图产生位置偏移。本插件将**缩放**与**编码**解耦，你可以精确控制进入模型的图像尺寸。

### 2. 多图编辑逻辑

Qwen-VL 具有多模态理解能力。通过 `PlusAdv` 和 `InfAdv` 节点，底层 Prompt 会被构建为：

```
Picture 1: <vision_tokens...>
Picture 2: <vision_tokens...>
User: <prompt>
```

这使得你可以进行更复杂的编辑任务，例如“基于图 1 的构图和图 2 的颜色生成新图像”。

---

## 示例工作流

### 对比测试

你可以使用 [`./workflows/demo_compare.json`](./workflows/demo_compare.json) 快速对比官方流程与本节点输出结果。

### 推荐参数

- **Resolution**: 1024
- **Alignment**: 32
- **CFG**: 推荐较低的 CFG (e.g., 1.0 - 2.5) 以获得更好的指令遵循能力。

---

## LoRA 推荐

结合以下 LoRA 使用，可以进一步提升一致性和低分辨率效果：

- [DiffSynth-Studio/Qwen-Image-Edit-Lowres-Fix](https://modelscope.cn/models/DiffSynth-Studio/Qwen-Image-Edit-Lowres-Fix/files)
- [QwenEdit Consistance Edit Lora](https://civitai.com/models/1939453/qwenedit-consistance-edit-lora) by xiaozhijason
