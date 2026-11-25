# ==============================================================================
# 通用富内容页面系统（支持 SVG 矢量绘图 / 图文混排 / 自动分页） (Template-Owned)
# ==============================================================================
# 项目可在 game/project/00_project_config.rpy 中通过 PROJECT_CONTENT_PAGES 注册
# 任意内容页（如世界观设定集、用语辞典、路线图解、成就徽章页等），每条区块均支持：
#   - 传统元组：(title, body)
#   - 字典：{"title": ..., "body": ..., "icon": ..., "visual": "<svg ...>" or "path.svg/png", "visual_size": (w, h)}
# 页面支持单栏 ("sections") 或双栏 ("left" / "right") 布局。

screen content_section_block(sec, col_width=730):

    if isinstance(sec, dict):
        $ _title = sec.get("title", "")
        $ _body = sec.get("body", "")
        $ _icon = sec.get("icon", None)
        $ _visual = sec.get("visual", None)
        $ _vsize = sec.get("visual_size", (min(col_width, 640), 220))
    else:
        $ _title, _body = sec[0], sec[1]
        $ _icon = None
        $ _visual = None
        $ _vsize = None

    vbox:
        xsize col_width
        spacing 10

        if _title:
            hbox:
                spacing 10
                yalign 0.5

                if _icon:
                    add render_visual(_icon, default_size=(30, 30)) yalign 0.5
                text _title style "manual_section_title"

        if _visual:
            frame:
                background "#06141688"
                padding (14, 12)
                xmaximum col_width

                add render_visual(_visual, default_size=_vsize) xalign 0.5

        if _body:
            text _body style "manual_body" xmaximum col_width


screen content_page_body(page_spec):

    if isinstance(page_spec, dict) and ("left" in page_spec or "right" in page_spec):
        hbox:
            spacing 44

            vbox:
                xsize 730
                spacing 20
                for _sec in page_spec.get("left", []):
                    use content_section_block(_sec, 730)

            vbox:
                xsize 730
                spacing 20
                for _sec in page_spec.get("right", []):
                    use content_section_block(_sec, 730)

    elif isinstance(page_spec, dict):
        vbox:
            xsize 1520
            spacing 22
            for _sec in page_spec.get("sections", []):
                use content_section_block(_sec, 1520)

    else:
        vbox:
            xsize 1520
            spacing 22
            for _sec in page_spec:
                use content_section_block(_sec, 1520)


screen content_page(page_id):

    tag menu

    default cp_page = 0
    $ _spec = PROJECT_CONTENT_PAGES.get(page_id, {})
    $ _title_en = _spec.get("title", "INFO")
    $ _subtitle = _spec.get("subtitle", "")
    $ _pages = _spec.get("pages") or [[{"title": _("说明"), "body": _("暂无内容。")}]]
    $ _total = len(_pages)
    $ _idx = min(cp_page, _total - 1)

    add "gui/log_bg.png"
    add "gui/manual_banner.png" xalign 0.5 ypos 0

    text _title_en style "manual_title" xpos 130 ypos 18
    if _subtitle:
        text _subtitle style "manual_title_zh" xpos 360 ypos 30
    text ("PAGE %d" % (_idx + 1)) style "manual_page_no" xalign 1.0 xoffset -130 ypos 38

    frame:
        style "manual_panel_frame"
        xalign 0.5
        ypos 150
        xsize 1660
        ysize 800

        viewport:
            scrollbars "vertical"
            mousewheel True
            draggable True

            use content_page_body(_pages[_idx])

    if _total > 1:
        imagebutton:
            idle "gui/manual_prev.png"
            hover "gui/manual_prev_hover.png"
            action SetScreenVariable("cp_page", max(0, _idx - 1))
            background None
            idle_background None
            padding (0, 0)
            xpos 18
            ypos 550
            yanchor 0.5

        imagebutton:
            idle "gui/manual_next.png"
            hover "gui/manual_next_hover.png"
            action SetScreenVariable("cp_page", min(_total - 1, _idx + 1))
            background None
            idle_background None
            padding (0, 0)
            xalign 1.0
            xoffset -18
            ypos 550
            yanchor 0.5

    frame:
        style "manual_bottom_bar"
        xalign 0.5
        yalign 1.0
        yoffset -16

        hbox:
            xalign 0.5
            spacing 26

            for i in range(_total):
                textbutton str(i + 1):
                    action SetScreenVariable("cp_page", i)
                    style "manual_page_button"
                    selected (_idx == i)

            if _total > 1:
                text _("左右箭头翻页") style "manual_hint"
            textbutton _("关闭") action Return() style "log_close_button"

    key "game_menu" action Return()
