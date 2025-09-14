# Qwen Image Edit Adv - ComfyUI Nodes

这里提供了以下自定义节点：

- TextEncodeQwenImageEditAdv: 仅编码图片和 prompt 不进行缩放
- QwenImageEditScale: 缩放图片以符合 Qwen Image Edit 模型需要

## 背景

使用 comfyui 内置的 qwen image edit 节点编辑图片的时候，总是会导致输出编辑结果偏移
根据我的调查，主要问题出现在 `TextEncodeQwenImageEdit` 这个节点导致的，其中包含了对于图片的缩放逻辑，而其缩放规则不符合要求，且不透明难以调试。

所以我开发了这个自定义节点，将缩放和编码分离开，方便测试，同时修改了缩放逻辑以符合 qwen image edit 官方要求。

对比测试可以使用 `./workflows/qwen-image-edit-adv.json` 工作流，其中包含了官方流程和本节点的使用示例，以及最终对于两个输出的 comparer 。

## 后续

后续可能会增加更多和 qwen image edit 有关的功能，但是，将仅限于不引入任何第三方依赖的前提下进行开发
