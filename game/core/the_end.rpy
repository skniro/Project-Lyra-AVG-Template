# ==============================================================================
# 路线结束画面 (Template-Owned)
# ==============================================================================
# 6 秒后自动返回主界面，点击/回车可提前返回。
# 支持可选参数：ending_title（结局副标）、accent（主题色）、theme（"dark" | "warm"）。

screen the_end(ending_title=None, accent="#7FC8C0", theme="dark"):

    modal True
    zorder 200

    $ _is_warm = (theme == "warm")
    $ _bg_color = "#F4EFE4" if _is_warm else "#061416"
    $ _fg_color = "#2D2622" if _is_warm else "#F4F1E8"
    $ _sub_color = "#6E6158" if _is_warm else "#9FB6C0"

    add Solid(_bg_color)

    vbox:
        xalign 0.5
        yalign 0.48
        spacing 24

        text "The End":
            xalign 0.5
            font "fonts/NotoSerifCJKsc-Regular.otf"
            size 96
            color _fg_color

        add svg_divider(width=580, height=18, primary=("#5C4A3E" if _is_warm else accent), secondary=accent) xalign 0.5

        if ending_title:
            text ending_title:
                xalign 0.5
                font "fonts/NotoSerifCJKsc-Regular.otf"
                size 26
                color accent

        text _("点击任意处或等待片刻返回标题画面"):
            xalign 0.5
            font gui.text_font
            size 17
            color _sub_color

    key "dismiss" action Return()
    timer 6.0 action Return()
