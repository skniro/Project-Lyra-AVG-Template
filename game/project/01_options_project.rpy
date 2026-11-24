# ==============================================================================
# 项目引擎与发布配置 (Project-Owned — 模板更新不会覆盖本文件)
# ==============================================================================
# 本文件在 game/options.rpy 之后执行（字母序 'o' < 'p'），用于覆盖项目标识、
# 存档目录、主菜单音乐与发布打包策略。

## 基础标识（每个新项目必须修改，尤其是 config.save_directory） ##################

define config.name = _("新视觉小说项目")
define build.name = "AVGProject"
define config.version = "0.1.0"
define config.save_directory = "AVGProject-0000000000"
define config.window_icon = "gui/window_icon.png"

define gui.about = _p("""
""")


## 音频与样本 ####################################################################

# define config.main_menu_music = "audio/bgm/main_menu.ogg"
# define config.sample_sound = "audio/se/sample.ogg"
# define config.sample_voice = "audio/voice/sample.ogg"


## 发布打包配置 ##################################################################
# 正式发布时建议设为 True，将图片/音频/字体/脚本打包为 .rpa 归档。

define PROJECT_BUILD_ARCHIVE = False
define PROJECT_BUILD_ARCHIVE_NAME = "archive"

# 如需额外排除项目内临时文件，可追加通配符：
# define PROJECT_EXTRA_BUILD_EXCLUDES = ["game/docs/**", "**.psd"]

# define build.itch_project = "yourname/your-game"
# define build.google_play_key = "..."
