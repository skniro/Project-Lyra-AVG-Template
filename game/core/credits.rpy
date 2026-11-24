# ==============================================================================
# 制作人员 / 版权与素材署名 (Template-Owned)
# ==============================================================================
# 数据驱动分页：内容由 game/project/00_project_config.rpy 中的 PROJECT_CREDITS_PAGES 提供。

screen credits():

    tag menu

    default credits_page = 0
    $ _pages = PROJECT_CREDITS_PAGES if PROJECT_CREDITS_PAGES else [[(_("说明"), _("暂无制作人员信息。"))]]
    $ credits_pages = len(_pages)
    $ _cur_idx = min(credits_page, credits_pages - 1)
    $ _cur_sections = _pages[_cur_idx]

    add "gui/log_bg.png"
    add "gui/manual_banner.png" xalign 0.5 ypos 0

    text "CREDITS" style "manual_title" xpos 60 ypos 18
    text _("制作人员") style "manual_title_zh" xpos 290 ypos 30
    text ("PAGE %d" % (_cur_idx + 1)) style "manual_page_no" xalign 1.0 xoffset -60 ypos 38

    frame:
        style "manual_panel_frame"
        xalign 0.5
        ypos 150
        xsize 1720
        ysize 800

        viewport:
            scrollbars "vertical"
            mousewheel True
            draggable True

            vbox:
                spacing 22

                for _sec_title, _sec_body in _cur_sections:
                    use manual_section(_sec_title, _sec_body)

    imagebutton:
        idle "gui/manual_prev.png"
        hover "gui/manual_prev_hover.png"
        action SetScreenVariable("credits_page", max(0, _cur_idx - 1))
        background None
        idle_background None
        padding (0, 0)
        xpos 24
        yalign 0.5

    imagebutton:
        idle "gui/manual_next.png"
        hover "gui/manual_next_hover.png"
        action SetScreenVariable("credits_page", min(credits_pages - 1, _cur_idx + 1))
        background None
        idle_background None
        padding (0, 0)
        xalign 1.0
        xoffset -24
        yalign 0.5

    frame:
        style "manual_bottom_bar"
        xalign 0.5
        yalign 1.0
        yoffset -16

        hbox:
            xalign 0.5
            spacing 26

            for i in range(credits_pages):
                textbutton str(i + 1):
                    action SetScreenVariable("credits_page", i)
                    style "manual_page_button"
                    selected (_cur_idx == i)

            text _("左右箭头翻页") style "manual_hint"
            textbutton _("关闭") action Return() style "log_close_button"

    key "game_menu" action Return()
