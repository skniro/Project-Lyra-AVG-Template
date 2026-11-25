# ==============================================================================
# 项目总配置 (Project-Owned — 模板更新不会覆盖本文件)
# ==============================================================================
# 本文件在 gui.rpy (init -2) 之后、screens.rpy (init -1) 之前执行，
# 因此可以安全覆盖 PROJECT_* 元数据与 gui.* 主题变量。

init offset = -2

## 1. 作品标题与语言配置 #########################################################

define PROJECT_TITLE = _("新视觉小说项目")
define PROJECT_TITLE_EN = "AVG PROJECT"
define PROJECT_TITLE_JA = "新規ビジュアルノベル"

define PROJECT_ENABLE_LANGUAGE_SELECT = True
define PROJECT_LANGUAGES = [
    ("日本語", "japanese", "ja", True),
    ("English", "english", "en", False),
    (_("简体中文"), None, "zh", True),
]

define PROJECT_SHOW_LOGO_IMAGE = True
define PROJECT_LOGO_IMAGE = "gui/logo.png"
define PROJECT_SHOW_MAIN_MENU_TITLE_TEXT = True
# 可选：发布时填写构建日期（如 "2026-12-01"），留 None 则仅显示版本号
define PROJECT_BUILD_DATE = None


## 2. 说明书与制作人员 ###########################################################

define PROJECT_MANUAL_INTRO = _("这是一款边阅读故事边前进的视觉小说。\n按照途中玩家所作的选择，故事会变得不一样。")
define PROJECT_MANUAL_BRANCH_INFO = _("故事会在关键选项处产生分支，\n根据玩家的决定进入不同的剧情路线。")

define PROJECT_CREDITS_PAGES = [
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


## 3. 鉴赏清单与角色配音署名 #####################################################

# CG 条目格式：(id, title, path_or_filename, show_tag)
# 例：("CG01", _("初遇站台"), "cg_01_station.png", "cg_01_station")
define PROJECT_CG_ENTRIES = []

# 音乐条目格式：(title, audio_path)
# 例：("潮声停泊的小站", "audio/bgm/station.ogg")
define PROJECT_MUSIC_TRACKS = []
define PROJECT_MUSIC_SUBTITLE = _("BGM")

# 角色语音条格式：(tag, display_name, portrait_path_or_None, actor_credit)
# 例：("heroine", _("女主"), "gui/portrait_heroine.png", "VOICEVOX:春日部つむぎ")
define PROJECT_VOICE_CAST = []


## 4. 扩展内容页与 SVG 矢量插图（可选） #########################################
# 支持 .svg 文件路径、内联 "<svg ...>...</svg>" 字符串或 {"svg": ..., "size": (w, h)}。
#
# define PROJECT_MAIN_MENU_EXTRA_ITEMS = [
#     ("CODEX", ShowMenu("content_page", page_id="codex")),
# ]
# define PROJECT_EXTRA_CARDS = [
#     {
#         "title": "CODEX",
#         "sub": _("设定集"),
#         "action": ShowMenu("content_page", page_id="codex"),
#         "visual": "<svg ...>...</svg>",
#     },
# ]
# define PROJECT_CONTENT_PAGES = {
#     "codex": {
#         "title": "CODEX",
#         "subtitle": _("世界观与设定"),
#         "pages": [
#             {
#                 "left": [{"title": _("词条"), "body": _("内容"), "visual": "<svg ...>...</svg>", "visual_size": (480, 220)}],
#                 "right": [(_("补充"), _("正文"))],
#             }
#         ],
#     }
# }
# define PROJECT_MANUAL_EXTRA_PAGES = []


## 5. 主题/UI 覆盖（可选，无需修改 game/gui.rpy） #################################

# define gui.main_menu_background = "gui/main_menu.png"
# define gui.game_menu_background = "gui/game_menu.png"
# define gui.accent_color = '#7FC8C0'
