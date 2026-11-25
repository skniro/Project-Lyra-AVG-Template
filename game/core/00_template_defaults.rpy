# ==============================================================================
# AVGTemplate Core Defaults (Template-Owned — 请勿在业务项目中直接修改)
# ==============================================================================
# 本文件在 init -10 阶段设置回退默认值，避免与 game/project/ 中的 define 冲突。
# 具体项目请在 game/project/00_project_config.rpy 与 01_options_project.rpy 中覆盖。

init -10 python:

    PROJECT_TITLE = _("新视觉小说项目")
    PROJECT_TITLE_EN = "AVG PROJECT"
    PROJECT_TITLE_JA = "新規ビジュアルノベル"

    PROJECT_ENABLE_LANGUAGE_SELECT = True
    PROJECT_LANGUAGES = [
        ("日本語", "japanese", "ja", True),
        ("English", "english", "en", False),
        (_("简体中文"), None, "zh", True),
    ]

    PROJECT_SHOW_LOGO_IMAGE = True
    PROJECT_LOGO_IMAGE = "gui/logo.png"
    PROJECT_SHOW_MAIN_MENU_TITLE_TEXT = True
    PROJECT_BUILD_DATE = None

    PROJECT_MANUAL_INTRO = _("这是一款边阅读故事边前进的视觉小说。\n按照途中玩家所作的选择，故事会变得变得不一样。")
    PROJECT_MANUAL_BRANCH_INFO = _("故事会在关键选项处产生分支，\n根据玩家的决定进入不同的剧情路线。")
    PROJECT_MANUAL_EXTRA_PAGES = []

    PROJECT_MUSIC_SUBTITLE = _("BGM")

    PROJECT_CREDITS_PAGES = [
        [
            (_("作品名称"), _("新视觉小说项目")),
            (_("企划・剧本・程序"), _("待补充")),
        ],
        [
            (_("角色配音与音频署名"), _("暂无配音与音频署名信息，接入音频素材后在此补充。")),
        ],
        [
            (_("引擎"), _("Ren'Py [renpy.version_only]")),
            (_("模板"), _("AVGTemplate")),
        ],
    ]

    PROJECT_CG_ENTRIES = []
    PROJECT_MUSIC_TRACKS = []
    PROJECT_VOICE_CAST = []
    PROJECT_AUTO_VOICE_MAP = {}
    PROJECT_IMAGE_OFFSETS = {}

    # SPRB 风格扩展系统数据（由项目侧在 game/project/00_project_config.rpy 配置）
    PROJECT_MEMORIES = []
    PROJECT_ACHIEVEMENTS = []
    PROJECT_SHOW_ACHIEVEMENT_TOAST = True
    PROJECT_FLOWCHART = {
        "title": "CHART",
        "subtitle": _("剧情分支流程图"),
        "canvas_size": (1520, 740),
        "nodes": [],
        "edges": [],
    }
    PROJECT_MAPS = {}

    # 扩展导航与内容页面
    PROJECT_MAIN_MENU_EXTRA_ITEMS = []
    PROJECT_EXTRA_CARDS = []
    PROJECT_CONTENT_PAGES = {}

    PROJECT_CHARACTER_LAYOUT = {
        "npc_tags": set(),
        "npc_large_tags": set(),
        "main_left_tag": None,
        "main_right_tag": None,
    }

    PROJECT_BUILD_ARCHIVE = False
    PROJECT_BUILD_ARCHIVE_NAME = "archive"
    PROJECT_BUILD_ARCHIVE_PATTERNS = [
        "game/images/**",
        "game/audio/**",
        "game/fonts/**",
        "game/chapters/**",
        "game/core/**",
        "game/api/**",
        "game/project/**",
    ]
    PROJECT_EXTRA_BUILD_EXCLUDES = []
