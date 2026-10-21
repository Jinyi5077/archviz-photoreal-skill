# 建筑超写实渲染 Skill

面向 Codex 的建筑、桥梁和景观 AI 后期技能：读取原始主图与渲染通道，逐图识别几何、陆水关系和材质分区，建立跨视角物体/材质台账，再写有针对性的超写实提示词。

## 关键行为

- 保留原图镜头、模型位置、体量、构件、开口、道路、岸线及支承落点；岸上物体不能被水面处理淹没。
- 同一建筑的立面、窗格、材质尺度和方向跨视角复用，不给每张图随机生成一套立面。
- 区分 D5 的 AI_Albedo、AI_Normal、AI_Material 与单独 MaterialID；不猜测未公开的通道编码。
- 先实际读图再写词。配对脚本只是元数据检查，不声称自动识别了建筑。
- 仅写提示词时不生成；执行生成时逐张检查形体、材质身份与接触关系。

## 安装

本仓库为私有仓库时，需要 GitHub 访问权限。Windows 使用已登录的 GitHub CLI：

```powershell
gh repo clone Jinyi5077/archviz-photoreal-skill
cd archviz-photoreal-skill
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

安装到 `$CODEX_HOME/skills/archviz-photoreal`；未设置 CODEX_HOME 时使用 `~/.codex/skills/archviz-photoreal`。不覆盖已有技能。安装后在下一轮消息可使用：

```text
使用 $archviz-photoreal 读取这个目录的主图和 AI 后期通道，
先建立几何约束与跨视角材质台账，再为每张图编写提示词。
此阶段只编写提示词，确认后再生成。
```

也可让 Codex 的 skill-installer 安装 `Jinyi5077/archviz-photoreal-skill` 中的 `skills/archviz-photoreal` 路径。私有仓库需安装器可用的 GitHub 认证；无需把 token 粘贴到对话。

macOS/Linux：先用 `gh repo clone` 克隆，再将 `skills/archviz-photoreal` 整个目录复制到 `${CODEX_HOME:-$HOME/.codex}/skills/` 下；已有同名目录时先人工检查，不直接覆盖。

## 文件清点工具（可选）

仅标准库，需要 Python 3.9 或更高版本：

```powershell
python .\skills\archviz-photoreal\scripts\inventory_render_set.py 'D:\renders' --out '.\render-inventory.json'
```

支持按同名后缀配对，计算 SHA256，核对 PNG/JPEG 尺寸。其他图像类型会登记并标记尺寸待核对。默认仅扫描指定目录一层；`--include '图片'` 可按主图文件名（不含扩展名）选择，参数可重复。输出文件已存在时拒绝覆盖。退出码 0 表示清点完成且未发现配对问题，2 表示重复/缺失主图/尺寸问题或指定视图不存在，1 表示运行失败；缺少可选 AI 通道只记录，不要求重导出。

## 依赖与边界

技能需要 Codex 或兼容代理具备本地文件读取和图像查看能力。实际生成还需可用的图像编辑工具；不内置 API 密钥、不指定收费服务或模型。读取本地图片后在外部生成工具中处理，遵循用户已授权的范围。

二维生成式编辑不能保证像素级几何不变或真正共享三维 UV。本技能提供具体约束、跨视角台账和验收流程；严格工程一致性应采用源场景统一材质并重渲等可验证流程。

仓库只包含技能、脚本与文档，不包含用户模型、图片、通道、项目清单或本机路径。联网研究依据见 [sources.md](skills/archviz-photoreal/references/sources.md)。

## 本地验证

```powershell
python -m unittest discover -s tests -v
```

另使用 Codex skill-creator 自带的 `quick_validate.py` 检查 `skills/archviz-photoreal` 的元数据和结构。验证不会调用图像生成服务。
