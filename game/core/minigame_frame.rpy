# ==============================================================================
# 可选彩蛋小游戏统一浮层框架 (Template-Owned)
# ==============================================================================
# 体现「零压力纯爱、绝不卡关」理念：
#   - 顶部 76px 统一横栏：色标 + 标题 + 玩法提示 + 进度小圆点 + 右上角「一键跳过 · SKIP」
#   - 中央 (120..1800, 100..996) 开放给各线独立小游戏画布

screen minigame_shell(title, hint="", accent="#6BA8C9", progress=0, total=0, skip_action=None, skip_note=None):

    default show_skip_tip = False

    frame:
        style "minigame_topbar_frame"
        xpos 0
        ypos 0
        xfill True
        ysize 76

        hbox:
            xfill True
            yalign 0.5

            hbox:
                spacing 16
                yalign 0.5

                frame:
                    background Solid(accent)
                    xsize 6
                    ysize 40
                    yalign 0.5

                text title style "minigame_title_text" yalign 0.5
                if hint:
                    text hint style "minigame_hint_text" yalign 0.5

            if total > 0:
                hbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 12

                    for _idx in range(total):
                        $ _lit = (_idx < progress)
                        frame:
                            background Solid(accent if _lit else "#C8BFB4")
                            xsize 14
                            ysize 14
                            yalign 0.5

            if skip_action is not None:
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 14

                    if show_skip_tip:
                        text (skip_note or _("跳过不影响任何好感与 True End")) style "minigame_skip_tip" yalign 0.5

                    textbutton _("一键跳过 · SKIP"):
                        action skip_action
                        hovered SetScreenVariable("show_skip_tip", True)
                        unhovered SetScreenVariable("show_skip_tip", False)
                        style "minigame_skip_button"


style minigame_topbar_frame:
    background "#FAF7F0E0"
    padding (36, 12)

style minigame_title_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 26
    color "#2D2622"

style minigame_hint_text:
    font gui.text_font
    size 19
    color "#6E6158"

style minigame_skip_tip:
    font gui.text_font
    size 16
    color "#B87A3D"

style minigame_skip_button:
    background "#FBF0E2"
    hover_background "#F5DEC0"
    padding (20, 8)

style minigame_skip_button_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 20
    color "#2D2622"
    hover_color "#8C521A"
