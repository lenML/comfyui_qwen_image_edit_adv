# Qwen Image Edit Adv - ComfyUI Nodes

这里提供了改进后的 **Qwen Image Edit** 相关自定义节点，主要目标是修复 ComfyUI 内置节点导致的**编辑结果偏移**问题，并提供更灵活的缩放和裁剪逻辑。

主要节点：

- **TextEncodeQwenImageEditAdv**: 仅负责编码图片和 prompt，不进行缩放
- **QwenImageEditScale**: 提供灵活可控的缩放和裁剪逻辑，满足 Qwen Image Edit 模型需求
- **QwenImageEditSimpleScale**: 自动选择最合适的分辨率进行缩放的简化版

<img width="946" height="683" alt="image" src="https://github.com/user-attachments/assets/4f57406b-5b11-4738-a833-2eaed4e54c0f" />

> 在对比测试中，可以看到本实现不会出现偏移问题，且无需多次抽卡生成。

---

## 背景

ComfyUI 内置的 `TextEncodeQwenImageEdit` 节点包含了强绑定的缩放逻辑，但该缩放方式与 Qwen Image Edit 模型官方要求并不完全一致，且难以调试。
因此，本仓库将 **缩放** 与 **编码** 分离开，并提供更合理的缩放策略，方便测试和调优。

你可以使用 [`./workflows/demo_compare.json`](./workflows/demo_compare.json) 工作流快速对比官方流程与本节点输出结果，并通过 comparer 查看一致性。

---

## 节点与参数说明

### 1. TextEncodeQwenImageEditAdv

<img width="675" height="378" alt="image" src="https://github.com/user-attachments/assets/69a05fe7-b213-43bf-bfee-47f88fda65d4" />

作用与内置的 `TextEncodeQwenImageEdit` 基本一致：

- 输入 `clip`、`prompt`，可选 `vae` 和 `image`
- 输出 **conditioning** 和 **latent**
- 不包含任何缩放逻辑，更透明可控

---

### 2. QwenImageEditScale

<img width="459" height="368" alt="image" src="https://github.com/user-attachments/assets/548bcec4-9533-4e25-aef4-e30ffd0a9542" />

提供高度可配置的缩放与裁剪逻辑。

参数说明：

- **upscale_method**: 缩放方法（`area`/`bicubic`/`bilinear`/`nearest-exact`/`lanczos`），一般无需修改
- **ratio_strategy**: 长宽比处理策略

  - `disabled`: 不处理比例
  - `closest`: 自动裁剪为最接近的官方允许比例
  - `W:H`: 固定裁剪到指定比例（如 `3:2`）

- **target_megapixels**:

  - 控制缩放后的总像素量
  - 默认 `1.0` → 接近 `1024x1024`
  - 可调节范围 `0.3M ~ 1.4M`，推荐值：`1`、`0.65`、`0.95`、`0.9`、`2`
  - 越大 → 模型自由度更高，越容易不严格遵循 prompt
  - 越小 → 一致性更强，不容易偏移

- **alignment**: 尺寸对齐的步长（默认 `32`，官方训练使用值），推荐值：`32`、`16`、`56`、`14`、`8`

返回结果：

- `IMAGE`: 缩放后的图像
- `width` / `height`: 实际输出分辨率
- `ratio`: 裁剪后的比例字符串（如 `3:2`）

---

### 3. QwenImageEditSimpleScale

<img width="473" height="244" alt="image" src="https://github.com/user-attachments/assets/b7f18ef8-1513-4899-a4bd-3392adf89980" />

`QwenImageEditScale` 的简化版：

- 自动根据输入尺寸选择最合适的缩放比例
- 保证分辨率落在 **Qwen Image Edit 可接受范围 (0.3M–1.4M pixels)**
- 仅需设置：

  - **max_side**: 最大边长（默认 `1024`）
  - **aligment**: 对齐步长（默认 `32`）

适用场景：

- 一般使用推荐 `QwenImageEditSimpleScale`（自动化处理）
- 需要手动调试时使用 `QwenImageEditScale`

---

## LoRA 推荐

结合以下 LoRA 使用，可以进一步提升一致性和低分辨率效果：

- [DiffSynth-Studio/Qwen-Image-Edit-Lowres-Fix](https://modelscope.cn/models/DiffSynth-Studio/Qwen-Image-Edit-Lowres-Fix/files)
- [QwenEdit Consistance Edit Lora](https://civitai.com/models/1939453/qwenedit-consistance-edit-lora) by xiaozhijason

---

## 后续计划

未来可能会继续扩展更多 Qwen Image Edit 相关功能：

- 仅限 **不依赖任何第三方库** 的实现
- 提供更多灵活可控的分辨率适配策略
- 优化与不同 VAE/CLIP 组合的兼容性
