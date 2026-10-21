# 建筑超写实渲染 Skill

面向 Codex 的建筑、桥梁和景观 AI 后期技能：读取原始主图与渲染通道，逐图识别几何、陆水关系和材质分区，建立跨视角物体/材质台账，再写有针对性的超写实提示词。

## 关键行为

- 保留原图镜头、模型位置、体量、构件、开口、道路、岸线及支承落点；岸上物体不能被水面处理淹没。
- 同一建筑的立面、窗格、材质尺度和方向跨视角复用，不给每张图随机生成一套立面。
- 区分 D5 的 AI_Albedo、AI_Normal、AI_Material 与单独 MaterialID；不猜测未公开的通道编码。
- 先实际读图再写词。配对脚本只是元数据检查，不声称自动识别了建筑。
- 仅写提示词时不生成；执行生成时逐张检查形体、材质身份与接触关系。

## 安装

这是公开仓库，可直接克隆或下载，无需 GitHub 登录、访问令牌或 GitHub CLI。

### 方式一：让 Codex 安装

在 Codex 中发送：

```text
使用 $skill-installer 安装：
https://github.com/Jinyi5077/archviz-photoreal-skill/tree/main/skills/archviz-photoreal
```

### 方式二：Windows 使用 Git

已安装 Git 时，在准备存放仓库的目录运行：

```powershell
git clone https://github.com/Jinyi5077/archviz-photoreal-skill.git
cd archviz-photoreal-skill
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

### 方式三：Windows 下载 ZIP

没有 Git 也可以安装：

1. [下载 main 分支 ZIP](https://github.com/Jinyi5077/archviz-photoreal-skill/archive/refs/heads/main.zip) 并解压。
2. 在解压后的 `archviz-photoreal-skill-main` 目录打开 PowerShell。
3. 运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

Windows 安装脚本会将技能复制到 `$CODEX_HOME/skills/archviz-photoreal`；未设置 CODEX_HOME 时使用 `~/.codex/skills/archviz-photoreal`。目标目录已存在时会停止，不覆盖已有版本。仓库更新后可先用 `git pull --ff-only` 更新克隆目录；已安装的技能不会自动同步。

macOS/Linux：克隆或解压后，将 `skills/archviz-photoreal` 整个目录复制到 `${CODEX_HOME:-$HOME/.codex}/skills/` 下；已有同名目录时先检查，不直接覆盖。

## 使用

安装后在下一轮消息可调用：

```text
使用 $archviz-photoreal 读取这个目录的主图和 AI 后期通道，
先建立几何约束与跨视角材质台账，再为每张图编写提示词。
此阶段只编写提示词，确认后再生成。
```

同一机位的输入放在同一目录，例如：

```text
场景 2.png
场景 2_AI_Albedo.png
场景 2_AI_Normal.png
场景 2_AI_Material.png
```

主图也可以使用“图片.png”等其他名称。告诉 Codex 主图范围、输出目录、需要保留的结构和材质要求；补充已确认的场地事实，例如某个桥墩位于干燥河岸上。技能会将这些事实记录到当前项目，避免误套到其他项目。

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
