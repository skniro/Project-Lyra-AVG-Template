# AVGTemplate 通用 Ren'Py 视觉小说模板使用指南

本模板将 **核心引擎/UI 层（Template-Owned）** 与 **项目配置/剧情/资源层（Project-Owned）** 彻底解耦，确保任何项目在开坑开发后，仍可以安全拉取模板上游更新，并直接用于多平台打包发布。

---

## 1. 目录职责划分

### 模板核心层（`template_owned` — 请勿在业务项目中直接修改）
以下文件由模板维护，执行 `sync_template.ps1` 时会按清单自动更新：
- `game/core/`：模板默认值（`00_template_defaults.rpy`）、配置装配（`90_template_setup.rpy`）、SVG 矢量绘图与富视觉渲染（`svg_support.rpy`）、通用内容页系统（`content_pages.rpy`）、多语言切换与开屏语言选择（`localization.rpy`）、分页 CG/音乐鉴赏（`extras.rpy`）、数据驱动制作人员页（`credits.rpy`）、手柄震动（`controller_rumble.rpy`）、自动语音（`voice_system.rpy`）、结束画面（`the_end.rpy`）。
- `game/api/`：立绘状态机与自动对齐/配角避让站位系统（`character_system.rpy`、`character_position.rpy`、`character_emote.rpy`）。
- `game/gui.rpy`、`game/options.rpy`、`game/screens.rpy`：基础样式、通用引擎默认项与发布排除规则、数据驱动 UI 界面。
- `game/fonts/`、`game/libs/`、`game/gui/` 基础控件图、`game/tl/None/`、`game/tl/japanese/{common,manual,screens,template_ui}.rpy`。
- `tools/{sync_template.ps1,prepare_release.ps1}`、`template.manifest.json`、`TEMPLATE_GUIDE.md`。

### 项目定制层（`project_owned` / `seed_only` — 各项目独立拥有，同步模板时绝不覆盖）
- `game/project/00_project_config.rpy`：作品标题（中/英/日）、语言列表、主菜单 LOGO/标题显示、说明书文案、制作人员分页、CG 清单、BGM 清单、角色配音列表、以及可选的 `gui.*` 颜色/背景覆盖。
- `game/project/01_options_project.rpy`：项目专属 `config.name`、`build.name`、`config.version`、`config.save_directory`、主菜单音乐、`PROJECT_BUILD_ARCHIVE`（发布 `.rpa` 打包开关）及额外排除规则。
- `game/project/characters.rpy`：角色 `Character(...)`、`auto_register_character(...)`、`CharacterSprite(...)` 与 `PROJECT_CHARACTER_LAYOUT`。
- `game/project/character_offsets.rpy`、`cg_declarations.rpy`、`voice_map.rpy`。
- `game/script.rpy`：游戏入口 `label start:`（如需自定义开屏逻辑，可定义 `label project_splashscreen:`）。
- `game/chapters/`、`game/images/`、`game/audio/`、`game/tl/*/project_strings.rpy`。
- `game/gui/{logo,window_icon,main_menu,game_menu,extras_bg}.png`、`android.json`、`project.json`、`android-icon_*.png`。

---

## 2. 从模板创建新项目

```powershell
cd "G:\new game\Project Lyra\renpy\AVGTemplate"
.\tools\init_project.ps1 `
    -TargetDir "..\MyNewGame" `
    -ProjectCode "MyNewGame" `
    -DisplayName "我的新游戏" `
    -EnglishTitle "MY NEW GAME" `
    -JapaneseTitle "新しいゲーム" `
    -PackageId "org.example.mynewgame"
```

脚本会自动复制模板、生成唯一 `config.save_directory`、写入基础配置与 `.template-lock.json`、并初始化干净的 Git 仓库。

---

## 3. 开发开始后同步模板更新

当 `AVGTemplate` 修复了 Bug 或新增了 UI/系统能力后，在业务项目根目录运行：

```powershell
# 先预览变更（不写入文件）
.\tools\sync_template.ps1 -DryRun

# 执行同步（从本地模板目录或远程 Git 仓库）
.\tools\sync_template.ps1
# 或指定远程 Git 仓库：
.\tools\sync_template.ps1 -Source "https://github.com/yourname/AVGTemplate.git" -Branch "main"
```

- 仅更新 `template_owned` 与 `tools_owned` 文件；
- 自动清理 `game/core/` 与 `game/api/` 中已被模板移除的旧文件；
- 自动清除过时 `.rpyc` / `.rpymc`；
- **绝不覆盖** `game/project/`、`game/script.rpy`、`game/chapters/`、`game/images/`、`game/audio/`、`game/tl/*/project_strings.rpy` 及项目图标/背景等 `seed_only` 文件。

---

## 4. 打包发布流程

1. 检查 `game/project/01_options_project.rpy`：确认 `config.version`、`config.save_directory`，正式版建议设置 `define PROJECT_BUILD_ARCHIVE = True`。
2. 如需在主菜单右下角显示发布日期，在 `game/project/00_project_config.rpy` 设置 `define PROJECT_BUILD_DATE = "2026-12-01"`。
3. 运行发布检查与打包脚本：

```powershell
# 编译 + 静态 Lint 检查
.\tools\prepare_release.ps1 -Clean

# 检查通过后直接生成 PC / Mac 发布包
.\tools\prepare_release.ps1 -Clean -Distribute -Packages @("pc","mac")
```

（若需接入 `Project AVG Assistant`，直接将整部作品导出到项目的 `game/chapters/` 目录，再在 `game/script.rpy` 中 `jump` 至对应入口 label 即可。）
