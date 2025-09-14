# Qwen Image Edit Adv - ComfyUI Nodes

这里提供了以下自定义节点：

- TextEncodeQwenImageEditAdv: 仅编码图片和 prompt 不进行缩放
- QwenImageEditScale: 缩放图片以符合 Qwen Image Edit 模型需要

<img width="957" height="773" alt="image" src="https://github.com/user-attachments/assets/c0872af7-2f41-4c88-b822-932c9628d558" />

> 使用对比节点可以看出没有任何的偏移出现，且不需要抽卡多次生成

## 背景

使用 comfyui 内置的 qwen image edit 节点编辑图片的时候，总是会导致输出编辑结果偏移
根据我的调查，主要问题出现在 `TextEncodeQwenImageEdit` 这个节点导致的，其中包含了对于图片的缩放逻辑，而其缩放规则不符合要求，且不透明难以调试。

所以我开发了这个自定义节点，将缩放和编码分离开，方便测试，同时修改了缩放逻辑以符合 qwen image edit 官方要求。

对比测试可以使用 `./workflows/qwen-image-edit-adv.json` 工作流，其中包含了官方流程和本节点的使用示例，以及最终对于两个输出的 comparer 。

## 参数和配置

### TextEncodeQwenImageEditAdv
<img width="521" height="308" alt="image" src="https://github.com/user-attachments/assets/16366f89-4ec1-424f-ac07-d63405ae5319" />

TextEncodeQwenImageEditAdv 节点的用法和 TextEncodeQwenImageEdit 完全相同

### QwenImageEditScale
<img width="347" height="252" alt="image" src="https://github.com/user-attachments/assets/cc4dbc78-e1ed-45e4-9c98-1b2026d87bae" />

QwenImageEditScale 节点中包含多个可配置的值，几乎不需要改动，除非特殊情况

对于每个值的含义：
- upscale_method: 缩放方法，由于调整图像会进行一定缩放，所以可以选择缩放方法，但是一般情况前后调整非常小，所以默认即可
- crop: 即是否裁剪图片，默认即可
- target_megapixels:
  - 调整图片的目标值，1表示调整到 qwen image edit 模型需要的像素（1024*1024 px）大小，默认即可
  - 但是也有一定概率仍然导致一致性有问题，此时可以调大或者调小或者调大
  - 调大的作用：提供更多模型可发挥空间，更具创意但是容易不遵循 prompt 生成
  - 调小的作用：将输入严格限制到模型可控制范围，比如设置为 0.9 几乎百分之百不会导致偏移（默认1仍然有一定概率可能偏移，和输入图片的分辨率有关）
- alignment: 需要对齐到什么分辨率尺寸，此处建议默认 32，此值为 qwen 官方使用值，具体为什么是这个值，和模型训练数据有关

## 后续

后续可能会增加更多和 qwen image edit 有关的功能，但是，将仅限于不引入任何第三方依赖的前提下进行开发
