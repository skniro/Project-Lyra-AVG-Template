# ==============================================================================
# SPRB 风格地图选点 / 日程行动系统 (Template-Owned)
# ==============================================================================
# 支持使用 PNG 或 SVG 矢量地图背景，配合角色头像/SVG 标记与地点提示卡片。
# 在剧本中使用方式：
#   $ chosen_loc = renpy.call_screen("location_map", map_id="town", day_text="8月1日", time_text="午后")
#   if chosen_loc == "station":
#       jump sec_station
# 或在地点条目中直接配置 "label": "sec_station" 实现点击即跳转（Call / Jump）。

init python:

    def _default_svg_map_bg():
        markup = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">'
            '<defs>'
            '<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%" stop-color="#0B232B"/><stop offset="100%" stop-color="#133B46"/>'
            '</linearGradient>'
            '</defs>'
            '<rect width="1920" height="1080" fill="url(#sea)"/>'
            '<path d="M180,680 Q460,360 960,420 T1680,340 L1760,820 Q1220,920 720,840 T180,680 Z" '
            'fill="#1B474B" stroke="#7FC8C0" stroke-opacity="0.55" stroke-width="4"/>'
            '<path d="M120,600 Q960,520 1800,580" fill="none" stroke="#F2C77E" stroke-opacity="0.5" stroke-width="3" stroke-dasharray="12 8"/>'
            '</svg>'
        )
        return svg_inline(markup, size=(1920, 1080))

    def _map_pin_visible(pin):
        cond = pin.get("condition")
        if callable(cond):
            return bool(cond())
        if isinstance(cond, str) and cond:
            return bool(getattr(persistent, cond, False) or getattr(store, cond, False))
        return True


screen location_map(map_id="default", day_text="", time_text=""):

    modal True
    default hovered_pin = None

    $ _m = PROJECT_MAPS.get(map_id, {}) if isinstance(PROJECT_MAPS, dict) else {}
    $ _bg = _m.get("background")
    $ _pins = [p for p in _m.get("locations", []) if _map_pin_visible(p)]

    if _bg:
        add render_visual(_bg, default_size=(1920, 1080))
    else:
        add _default_svg_map_bg()

    # 顶部日期 / 时段牌（SPRB 左上角日期条风格）
    if day_text or time_text or _m.get("title"):
        frame:
            background "#061416D8"
            padding (28, 16)
            xpos 48
            ypos 36

            hbox:
                spacing 18
                yalign 0.5

                if day_text:
                    text day_text style "map_day_text" yalign 0.5
                if time_text:
                    text time_text style "map_time_text" yalign 0.5
                if _m.get("title"):
                    text _m["title"] style "map_subtitle_text" yalign 0.5

    # 地图标记点
    for pin in _pins:
        $ _px, _py = pin.get("pos", (960, 540))
        $ _act = (Jump(pin["label"]) if pin.get("label") else Return(pin.get("id")))

        button:
            style "map_pin_button"
            xpos _px
            ypos _py
            anchor (0.5, 0.5)
            hovered SetScreenVariable("hovered_pin", pin)
            unhovered SetScreenVariable("hovered_pin", None)
            action _act

            hbox:
                spacing 10
                yalign 0.5

                if pin.get("char_icon"):
                    add render_visual(pin["char_icon"], default_size=(46, 46)) yalign 0.5

                vbox:
                    yalign 0.5
                    spacing 2
                    text pin.get("name", "") style "map_pin_title"
                    if pin.get("char_name"):
                        text pin["char_name"] style "map_pin_char"

    # 右下角/左下角悬停地点说明卡
    if hovered_pin:
        frame:
            style "manual_bottom_bar"
            xpos 48
            yalign 1.0
            yoffset -44
            xsize 900
            padding (28, 18)

            vbox:
                spacing 6
                hbox:
                    spacing 14
                    text hovered_pin.get("name", "") style "manual_section_title"
                    if hovered_pin.get("char_name"):
                        text ("· " + hovered_pin["char_name"]) style "map_time_text"
                if hovered_pin.get("desc"):
                    text hovered_pin["desc"] style "manual_body"

    textbutton _("系统菜单") action ShowMenu("preferences") style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -48 yoffset -44
    key "game_menu" action ShowMenu("preferences")


style map_day_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 34
    color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style map_time_text:
    font gui.text_font
    size 22
    color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style map_subtitle_text:
    font gui.text_font
    size 20
    color "#7FC8C0"

style map_pin_button:
    background "#091E22E8"
    hover_background "#174A4EFF"
    padding (16, 10)

style map_pin_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 22
    color "#F4F1E8"

style map_pin_char:
    font gui.text_font
    size 16
    color "#F2C77E"
