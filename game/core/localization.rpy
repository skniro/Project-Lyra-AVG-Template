# ==============================================================================
# 多语言支持：首次启动语言选择 + 运行中切换辅助 (Template-Owned)
# ==============================================================================
# 语言模型：
#   preferences.language = None        -> 中文原版（游戏源码）
#   preferences.language = "japanese"  -> game/tl/japanese/
#   其他启用语言                       -> 对应 game/tl/<lang>/

init python:

    def set_ui_language(lang):
        """切换语言并同步 persistent 字段。lang 为 ui_lang 代码（如 'zh' / 'ja' / 'en'）。"""
        persistent.ui_language = lang
        persistent.language_chosen = True
        target = None
        for _label, _renpy_code, _ui_code, _enabled in PROJECT_LANGUAGES:
            if _ui_code == lang:
                target = _renpy_code
                break
        renpy.change_language(target)

    def current_ui_language():
        cur = preferences.language
        for _label, _renpy_code, _ui_code, _enabled in PROJECT_LANGUAGES:
            if cur == _renpy_code:
                return _ui_code
        return "zh"


label splashscreen:
    if PROJECT_ENABLE_LANGUAGE_SELECT and not persistent.language_chosen:
        call screen language_select
        $ persistent.language_chosen = True
        $ set_ui_language(_return)
    if renpy.has_label("project_splashscreen"):
        $ renpy.call("project_splashscreen")
    return


screen language_select():

    modal True
    zorder 300

    add gui.main_menu_background
    if PROJECT_SHOW_LOGO_IMAGE and PROJECT_LOGO_IMAGE:
        add PROJECT_LOGO_IMAGE xalign 0.5 yalign 0.06

    frame:
        background "#061416B8"
        padding (64, 44)
        xalign 0.5
        yalign 0.56

        vbox:
            xalign 0.5
            spacing 24

            if PROJECT_TITLE_JA:
                text PROJECT_TITLE_JA:
                    xalign 0.5
                    font "fonts/NotoSerifCJKsc-Regular.otf"
                    size 56
                    color "#F4F1E8"
                    outlines [(3, "#061416", 0, 0)]

            text PROJECT_TITLE:
                xalign 0.5
                font "fonts/NotoSerifCJKsc-Regular.otf"
                size 32
                color "#B9CBD3"

            null height 12

            text "言語を選択 / 请选择语言":
                xalign 0.5
                font gui.text_font
                size 28
                color "#F2C77E"

            hbox:
                xalign 0.5
                spacing 72

                for _lang_label, _renpy_code, _ui_code, _enabled in PROJECT_LANGUAGES:
                    if _enabled:
                        textbutton _lang_label:
                            action Return(_ui_code)
                            style "mainmenu_button"

            text "後から OPTIONS で変更できます。 / 之后可在 OPTIONS 中更改。":
                xalign 0.5
                font gui.text_font
                size 20
                color "#9FB6C0"

    # 必须选择后才能进入标题菜单。
    key "game_menu" action NullAction()


# 日文断行规则（Ren'Py 的 style 属性 language）。
translate japanese style default:
    language "japanese-normal"
