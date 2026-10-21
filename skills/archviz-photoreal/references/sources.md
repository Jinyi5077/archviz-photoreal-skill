# 研究来源

查阅日期：2026-10-21。以下为官方一手资料，保留链接以便核对能力更新；本技能没有复制其完整提示词或手册。

1. [Adobe：Writing effective text prompts](https://helpx.adobe.com/firefly/web/work-with-images/generate-images/writing-effective-text-prompts.html)
   - 采用明确主体、可观察细节和光照描述的方法；本技能据此编写建筑材质与摄影模块。没有照搬 Firefly 特定的词数或界面设置作为所有工具的规则。
2. [Adobe：Match image composition to reference image](https://helpx.adobe.com/firefly/web/work-with-images/generate-images/match-image-composition-to-reference-image.html)
   - 结构/构图参考用于约束布局、轮廓和深度关系。该资料不证明任何生成工具可以像素级锁定几何。
3. [Adobe：Reference images for styling](https://helpx.adobe.com/firefly/web/work-with-images/generate-images/reference-images-for-styling.html)
   - 外观参考用于视觉风格与质感统一；应与当前原图的结构约束分开。
4. [D5：How to render channel maps? Which channel maps are supported?](https://docs.d5render.com/user-guide/render/how-to-render-channel-maps-which-channel-maps-are-supported)
   - 官方单列 MaterialID 与 AI 后期三通道 AI_Albedo、AI_Normal、AI_Material，并另有天空、深度、透明等通道。本技能不推断未公开的 AI_Material 编码。
5. [D5：Material](https://docs.d5render.com/user-guide/material)
   - 材质包含基础色、法线等属性；UV 的缩放、偏移、旋转与通道对齐会影响表面表现。本技能把尺度/方向纳入材质一致性记录，不把一张二维效果图视作真正共享三维 UV。

**工作流设计与来源区分**：稳定物体 ID、几何约束清单、跨视角材质台账、岸上/水中接触核对及逐图验收，是本技能为用户要求设计的工作流。它们不是上述厂商宣称的自动能力。当前二维图像工具是否支持遮罩、几何条件输入、输出分辨率或多视角一致性，需要在执行时核对，不从本文件推断。
