# ==============================================================================
# 路线结束画面 (Template-Owned)
# ==============================================================================
# 6 秒后自动返回主界面，点击/回车可提前返回。

screen the_end():

    modal True
    zorder 200

    add Solid("#000000")

    text "The End":
        xalign 0.5
        yalign 0.5
        font "fonts/NotoSerifCJKsc-Regular.otf"
        size 96
        color "#F4F1E8"
        outlines [(3, "#000000", 0, 0)]

    key "dismiss" action Return()
    timer 6.0 action Return()
