################################################################################
## 初始化
################################################################################

init offset = -1

init python:
    window_scale_options = [
        ("自动", None), ("50%", 0.5), ("66%", 0.66), ("100%", 1.0),
        ("133%", 1.33), ("150%", 1.5), ("200%", 2.0),
        ("266%", 2.66), ("300%", 3.0),
    ]

    def set_window_scale(scale):
        if scale is None:
            renpy.reset_physical_size()
        else:
            renpy.set_physical_size((int(config.screen_width * scale),
                                     int(config.screen_height * scale)))

    def is_current_window_scale(scale):
        ps = renpy.game.preferences.physical_size
        if scale is None:
            return ps is None
        if ps is None:
            return False
        return abs(ps[0] / float(config.screen_width) - scale) < 0.02

    # Custom preferences used by the 9-tab OPTIONS screen.
    # 触屏设备默认使用大按钮的“触控”快捷菜单。
    _default_quick_menu_mode = "touch" if renpy.variant("touch") else "classic"

    _custom_defaults = {
        "quick_menu_mode": _default_quick_menu_mode,
        "side_menu_hidden": False,
        "choice_pos": "upper",
        "choice_cursor": "yes",
        "skip_speed": 0.5,
        "voice_skip_stop": True,
        "controller_rumble": "off",
        "ui_language": "zh",
        "font_choice": "sans",
        "window_color": "deep",
        "window_opacity": 100,
        "read_mark": "off",
        "per_char_delay": 0.0,
        "key_c_mode": "hold",
        "key_z_mode": "hold",
        "key_s": "quicksave",
        "key_l": "quickload",
        "key_up": "history",
        "mouse_right": "menu",
        "mouse_both": "none",
        "mouse_wheel": "none",
        "mouse_wheel_up": "history",
        "mouse_wheel_down": "none",
        "mouse_side": "none",
        "mouse_gesture": "off",
        "mouse_auto_move": "off",
        "touch_skip": "off",
        "touch_back": "off",
        "touch_forward": "off",
        "touch_rewind": "off",
    }
    for _k, _v in _custom_defaults.items():
        if getattr(persistent, _k) is None:
            setattr(persistent, _k, _v)

    # 旧版默认/已保存的选项位置是底部或中央；本版把默认改到上半。
    # 只迁移一次，之后玩家在 OPTIONS 里的选择会保留。
    if not getattr(persistent, "choice_pos_migrated_upper", False):
        persistent.choice_pos = "upper"
        persistent.choice_pos_migrated_upper = True

    class SaveNoteInputValue(VariableInputValue):
        """存档备注输入：回车先保存当前选中槽位（备注随存档写入）。"""

        def enter(self):
            renpy.store.save_note_editing = False
            slot = getattr(store, "file_slot_sel", 1)
            if slot:
                renpy.run(FileSave(slot, confirm=False))
            return None

    def prefs_font():
        if persistent.font_choice == "serif":
            return "fonts/NotoSerifCJKsc-Regular.otf"
        return "fonts/NotoSansCJKsc-Regular.otf"

    class PerCharDelayValue(BarValue):
        def __init__(self):
            pass

        def get_adjustment(self):
            cps = renpy.game.preferences.text_cps
            delay = 0.0 if cps <= 0 or cps >= 999 else min(0.2, 1.0 / cps)
            return ui.adjustment(range=0.2, value=delay, changed=self.changed)

        def changed(self, value):
            if value <= 0.005:
                renpy.game.preferences.text_cps = 0
            else:
                renpy.game.preferences.text_cps = max(1, int(round(1.0 / value)))
            renpy.restart_interaction()

    def apply_custom_prefs():
        try:
            config.skip_delay = max(0.01, 0.12 - 0.11 * float(persistent.skip_speed))
        except Exception:
            pass

    config.start_interact_callbacks.append(apply_custom_prefs)

    # 跳过对白时是否停止配音（OPTIONS → 基本设置 → 播放角色语音）。
    def _voice_skip_control():
        if renpy.config.skipping and persistent.voice_skip_stop:
            renpy.sound.stop(channel="voice")

    config.periodic_callbacks.append(_voice_skip_control)

    # Summer Pockets style confirmations for the in-game TITLE / EXIT buttons.
    # 日文实际值在 tl/japanese/manual.rpy 的 translate japanese python 中覆盖。
    layout.QUIT = _("内容尚未保存，是否退出游戏？")
    layout.MAIN_MENU = _("是否返回标题界面？")

    # Store the dialogue line at the save point, so the save screen can show
    # it above the note (Summer Pockets style).
    def _save_dialogue_json(d):
        d["dialogue"] = getattr(store, "_last_say_what", "") or ""

    config.save_json_callbacks.append(_save_dialogue_json)

    # Remember which voice file belongs to each history line, for LOG replay.
    def _history_store_voice(h):
        v = getattr(store, "_voice", None)
        h.voice = getattr(v, "play", None) if v is not None else None

    config.history_callbacks.append(_history_store_voice)

    # Q.LOAD: load the quick save with a confirmation, or say so when empty.
    class QuickLoadAction(Action):
        def __call__(self):
            if FileLoadable(1, page="quick"):
                renpy.run(Confirm(
                    _("是否读取快速存档？"),
                    FileLoad(1, page="quick", confirm=False),
                    confirm_selected=True))
            else:
                renpy.notify(_("没有快速存档"))

        def get_sensitive(self):
            return True


################################################################################
## 样式
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## 游戏内屏幕
################################################################################


## 对话屏幕 ########################################################################
##
## 对话屏幕用于向用户显示对话。它需要两个参数，who 和 what，分别是叙述角色的名字
## 和所叙述的文本。（如果没有名字，参数 who 可以是 None。）
##
## 此屏幕必须创建一个 id 为 what 的文本可视控件，因为 Ren'Py 使用它来管理文本显
## 示。它还可以创建 id 为 who 和 id 为 window 的可视控件来应用样式属性。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#say

screen say(who, what):

    $ _alpha = max(0.0, min(1.0, getattr(persistent, "window_opacity", 100) / 100.0))
    $ _tb = ("gui/textbox_light.png" if persistent.window_color == "light" else
             ("gui/textbox_black.png" if persistent.window_color == "black" else
              "gui/textbox_deep.png"))
    $ _font = prefs_font()

    window:
        id "window"
        background Transform(Image(_tb, xalign=0.5, yalign=1.0), alpha=_alpha)

        if who is not None:

            window:
                id "namebox"
                style "namebox"
                text who id "who" font _font

        text what id "what" font _font


    ## 如果有对话框头像，会将其显示在文本之上。请不要在手机界面下显示这个，因为
    ## 没有空间。
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0


## 通过 Character 对象使名称框可用于样式化。
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height

    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background None
    padding (0, 0)

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5
    outlines [(2, "#061416", 0, 1)]

style say_dialogue:
    properties gui.text_properties("dialogue")

    ## Summer-Pockets-style subtitle text, left edge aligned with the name.
    xpos gui.name_xpos
    xanchor 0.0
    xsize gui.namebox_width
    ypos gui.dialogue_ypos
    textalign 0.0
    layout "subtitle"
    outlines [(2, "#061416", 0, 1)]

    adjust_spacing False

## 输入屏幕 ########################################################################
##
## 此屏幕用于显示 renpy.input。prompt 参数用于传递文本提示。
##
## 此屏幕必须创建一个 id 为 input 的输入可视控件来接受各种输入参数。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xanchor gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width


## 选择屏幕 ########################################################################
##
## 此屏幕用于显示由 menu 语句生成的游戏内选项。参数 items 是一个对象列表，每个对
## 象都有字幕和动作字段。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        ypos (720 if persistent.choice_pos == "bottom" else (280 if persistent.choice_pos == "upper" else 405))

        for i in items:
            textbutton i.caption action [Function(controller_rumble_choice), i.action]


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 405
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")

style choice_button_text is default:
    properties gui.text_properties("choice_button")


## 快捷菜单屏幕 ######################################################################
##
## 快捷菜单显示于游戏内，以便于访问游戏外的菜单。

screen quick_menu():

    ## 确保该菜单出现在其他屏幕之上，
    zorder 100

    $ _qm_mode = getattr(persistent, "quick_menu_mode", "classic")

    if quick_menu and _qm_mode != "hide":

        if _qm_mode == "touch":

            hbox:
                xalign 0.5
                yalign 1.0
                yoffset -18
                spacing 18

                textbutton "SAVE" action ShowMenu("save") style "quick_touch_button"
                textbutton "LOAD" action ShowMenu("load") style "quick_touch_button"
                textbutton "MENU" action ShowMenu("game_menu_home") style "quick_touch_button"
                textbutton "AUTO" action Preference("auto-forward", "toggle") style "quick_touch_button"
                textbutton "SKIP" action Skip() alternate Skip(fast=True, confirm=True) style "quick_touch_button"
                textbutton "HIDE" action HideInterface() style "quick_touch_button"

        else:

            hbox:
                xalign 0.5
                yalign 1.0
                yoffset -6
                spacing 2

                use quick_bar_button("gui/icon_qsave.png", "Q.SAVE", QuickSave(message=_("已快速保存")))
                use quick_bar_button("gui/icon_qload.png", "Q.LOAD", QuickLoadAction())
                use quick_bar_button("gui/icon_save.png", "SAVE", ShowMenu("save"))
                use quick_bar_button("gui/icon_load.png", "LOAD", ShowMenu("load"))
                use quick_bar_button("gui/icon_back.png", "BACK", Rollback())
                use quick_bar_button("gui/icon_next.png", "NEXT", RollForward())
                use quick_bar_button("gui/icon_auto.png", "AUTO", Preference("auto-forward", "toggle"))
                use quick_bar_button("gui/icon_rewind.png", "REWIND", Rollback())
                use quick_bar_button("gui/icon_skip.png", "SKIP", Skip(), Skip(fast=True, confirm=True))
                use quick_bar_button("gui/icon_title.png", "TITLE", MainMenu(confirm=True))
                use quick_bar_button("gui/icon_exit.png", "EXIT", Quit(confirm=True))
                use quick_bar_button("gui/icon_options.png", "OPTIONS", ShowMenu("preferences"))
                use quick_bar_button("gui/icon_record.png", "RECORD", ShowMenu("extras"))
                use quick_bar_button("gui/icon_manual.png", "MANUAL", ShowMenu("help"))
                use quick_bar_button("gui/icon_lock.png", "LOCK", ToggleField(persistent, "side_menu_hidden"))

            ## Summer Pockets style vertical menu at the lower right.
            ## LOCK hides this menu; the LOCK button in the bottom bar brings
            ## it back, matching the original game.
            if not getattr(persistent, "side_menu_hidden", False):

                vbox:
                    xalign 1.0
                    yalign 1.0
                    xoffset -14
                    yoffset -74
                    spacing 2

                    use quick_side_button("gui/icon_close.png", "CLOSE", HideInterface())
                    use quick_side_button("gui/icon_voice.png", "VOICE", VoiceReplay())
                    use quick_side_button("gui/icon_log.png", "LOG", ShowMenu("history"))
                    use quick_side_button("gui/icon_lock_open.png", "LOCK", ToggleField(persistent, "side_menu_hidden"))


screen quick_bar_button(icon, label, act, alt=None):

    button:
        style "quick_bar_button"
        action act
        alternate (alt or act)

        vbox:
            spacing 1

            add icon xalign 0.5 xysize (30, 30)
            text label style "quick_bar_label" xalign 0.5


screen quick_side_button(icon, label, act):

    button:
        style "quick_side_button"
        action act

        hbox:
            xalign 1.0
            yalign 0.5
            spacing 8

            add icon xysize (28, 28) yalign 0.5
            text label style "quick_side_label" xsize 105 textalign 0.0 yalign 0.5


screen custom_keys():

    if renpy.get_screen("say") and not renpy.get_screen("input"):

        if persistent.key_s == "quicksave":
            key "K_s" action QuickSave(message=_("已快速保存"))
        if persistent.key_l == "quickload":
            key "K_l" action QuickLoadAction()
        if persistent.key_up == "history":
            key "K_UP" action ShowMenu("history")

        key "K_c" action Skip()
        key "K_z" action Rollback()

        if persistent.mouse_right == "hide":
            key "mouseup_3" action HideInterface()

        if persistent.mouse_wheel == "hide":
            key "mouseup_2" action HideInterface()
        elif persistent.mouse_wheel == "menu":
            key "mouseup_2" action ShowMenu("preferences")

        if persistent.mouse_wheel_up == "history":
            key "mousedown_4" action ShowMenu("history")
        elif persistent.mouse_wheel_up == "back":
            key "mousedown_4" action Rollback()

        if persistent.mouse_wheel_down == "hide":
            key "mousedown_5" action HideInterface()
        elif persistent.mouse_wheel_down == "forward":
            key "mousedown_5" action RollForward()

        if persistent.mouse_side == "page":
            key "mouseup_4" action Rollback()
            key "mouseup_5" action RollForward()


## 此代码确保只要用户没有主动隐藏界面，就会在游戏中显示 quick_menu 屏幕。
init python:
    config.overlay_screens.append("quick_menu")
    config.overlay_screens.append("custom_keys")

default quick_menu = True

style quick_menu is vbox
style quick_button is default
style quick_button_text is button_text

style quick_menu:
    xalign 1.0
    yalign 1.0
    xoffset -40
    yoffset -24
    spacing 6
    background None
    padding (0, 0)

style quick_button:
    properties gui.button_properties("quick_button")
    background None
    padding (8, 4)

style quick_button_text:
    properties gui.text_properties("quick_button")
    font gui.text_font
    size 24
    color "#F4F1E8"
    hover_color "#F2C77E"
    selected_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style quick_bar_button:
    background None
    hover_background "#7FC8C022"
    padding (4, 3)
    xsize 104

style quick_bar_label:
    font gui.text_font
    size 13
    color "#F4F1E8"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style quick_side_button:
    background None
    hover_background "#7FC8C022"
    padding (6, 2)
    xsize 156

style quick_side_label:
    font gui.text_font
    size 18
    color "#F4F1E8"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style quick_touch_button:
    background None
    hover_background None
    padding (10, 6)

style quick_touch_button_text:
    font gui.text_font
    size 26
    color "#F4F1E8"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]


################################################################################
## 标题和游戏菜单屏幕
################################################################################

## 导航屏幕 ########################################################################
##
## 该屏幕包含在标题菜单和游戏菜单中，并提供导航到其他菜单，以及启动游戏。

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing gui.navigation_spacing

        if main_menu:

            textbutton _("开始游戏") action Start()

        else:

            textbutton _("历史") action ShowMenu("history")

            textbutton _("保存") action ShowMenu("save")

        textbutton _("读取游戏") action ShowMenu("load")

        textbutton _("鉴赏") action ShowMenu("extras")

        textbutton _("设置") action ShowMenu("preferences")

        if _in_replay:

            textbutton _("结束回放") action EndReplay(confirm=True)

        elif not main_menu:

            textbutton _("标题菜单") action MainMenu()

        textbutton _("关于") action ShowMenu("about")

        textbutton _("制作人员") action ShowMenu("credits")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

            ## “帮助”对移动设备来说并非必需或相关。
            textbutton _("帮助") action ShowMenu("help")

        if renpy.variant("pc"):

            ## 退出按钮在 iOS 上是被禁止使用的，在安卓和网页上也不是必要的。
            textbutton _("退出") action Quit(confirm=not main_menu)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text:
    properties gui.text_properties("navigation_button")


## 标题菜单屏幕 ######################################################################
##
## 用于在 Ren'Py 启动时显示标题菜单。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#main-menu

default main_menu_page = 0


screen main_menu():

    ## 此语句可确保替换掉任何其他菜单屏幕。
    tag menu

    add gui.main_menu_background
    if PROJECT_SHOW_LOGO_IMAGE and PROJECT_LOGO_IMAGE:
        add render_visual(PROJECT_LOGO_IMAGE) xalign 0.5 yalign 0.06

    if PROJECT_SHOW_MAIN_MENU_TITLE_TEXT:
        if PROJECT_TITLE_EN:
            text PROJECT_TITLE_EN:
                xalign 0.5
                ypos 140
                font "fonts/NotoSerifCJKsc-Regular.otf"
                size 92
                color "#F4F1E8"
                outlines [(3, "#061416", 0, 0)]

        text PROJECT_TITLE:
            xalign 0.5
            ypos 365
            font "fonts/NotoSerifCJKsc-Regular.otf"
            size 38
            color "#7FC8C0"
            outlines [(2, "#061416", 0, 0)]

    use main_menu_navigation

    vbox:
        xalign 1.0
        yalign 1.0
        xoffset -30
        yoffset -16
        spacing 2

        text ("Ver. %s" % config.version):
            style "main_menu_version"
            xalign 1.0
        if PROJECT_BUILD_DATE:
            text PROJECT_BUILD_DATE:
                style "main_menu_version"
                xalign 1.0


screen main_menu_navigation():

    # Summer Pockets 式左右翻页：第一页 START/LOAD/OPTIONS/MANUAL/EXIT，
    # 第二页 EXTRAS/CREDITS。半透明菜单带 + 两侧空心三角箭头。

    frame:
        background "#06141659"
        xfill True
        ysize 96
        yalign 0.55

    hbox:
        style_prefix "mainmenu"
        xalign 0.5
        yalign 0.55
        spacing 40

        # 左侧箭头占位（第二页显示）
        frame:
            background None
            xsize 56
            ysize 72
            yalign 0.5

            if main_menu_page == 1:
                button:
                    action SetVariable("main_menu_page", 0)
                    xsize 56
                    ysize 72
                    background "gui/menu_arrow_left.png"
                    hover_background "gui/menu_arrow_left_hover.png"
                    padding (0, 0)

        frame:
            background None
            xsize 1120
            ysize 72
            yalign 0.5

            hbox:
                xalign 0.5
                yalign 0.5
                spacing 44

                if main_menu_page == 0:

                    textbutton _("START") action Start()
                    textbutton _("LOAD") action ShowMenu("load")
                    textbutton _("OPTIONS") action ShowMenu("preferences")
                    textbutton _("MANUAL") action ShowMenu("help")
                    textbutton _("EXIT") action Quit(confirm=False)

                else:

                    textbutton _("GALLERY") action ShowMenu("cg_gallery")
                    textbutton _("MUSIC") action ShowMenu("music_room")
                    textbutton _("CREDITS") action ShowMenu("credits")
                    for _mm_label, _mm_action in PROJECT_MAIN_MENU_EXTRA_ITEMS:
                        textbutton _mm_label action _mm_action

        # 右侧箭头占位（第一页显示）
        frame:
            background None
            xsize 56
            ysize 72
            yalign 0.5

            if main_menu_page == 0:
                button:
                    action SetVariable("main_menu_page", 1)
                    xsize 56
                    ysize 72
                    background "gui/menu_arrow_right.png"
                    hover_background "gui/menu_arrow_right_hover.png"
                    padding (0, 0)

    # 键盘左右键也可以翻页（鼠标箭头之外的备用操作）。
    key "K_LEFT" action SetVariable("main_menu_page", 0)
    key "K_RIGHT" action SetVariable("main_menu_page", 1)


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 420
    yfill True

    background "gui/overlay/main_menu.png"

style main_menu_vbox:
    xalign 1.0
    xoffset -30
    xmaximum 1200
    yalign 1.0
    yoffset -30

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")
    outlines [(2, "#061416", 0, 0)]

style main_menu_version:
    properties gui.text_properties("version")
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 22
    color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style mainmenu_button is button
style mainmenu_button_text is button_text

style mainmenu_button:
    background None
    padding (14, 8)
    yalign 0.5

style mainmenu_button_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 38
    color "#7FC8C0"
    hover_color "#F2C77E"
    selected_color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]
    xalign 0.5
    yalign 0.5


## 游戏菜单屏幕 ######################################################################
##
## 此屏幕列出了游戏菜单的基本共同结构。可使用屏幕标题调用，并显示背景、标题和导
## 航菜单。
##
## scroll 参数可以是 None，也可以是 viewport 或 vpgrid。此屏幕旨在与一个或多个子
## 屏幕同时使用，这些子屏幕将被嵌入（放置）在其中。

screen game_menu(title, scroll=None, yinitial=0.0, spacing=0):

    style_prefix "game_menu"

    if main_menu:
        add gui.main_menu_background
    else:
        add gui.game_menu_background

    frame:
        style "game_menu_outer_frame"

        hbox:

            ## 导航部分的预留空间。
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        vbox:
                            spacing spacing

                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial yinitial

                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        spacing spacing

                        transclude

                else:

                    transclude

    use navigation

    textbutton _("返回"):
        style "return_button"

        action Return()

    label title

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 45
    top_padding 180

    background "gui/overlay/game_menu.png"

style game_menu_navigation_frame:
    xsize 420
    yfill True

style game_menu_content_frame:
    left_margin 60
    right_margin 30
    top_margin 15

style game_menu_viewport:
    xsize 1380

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 15

style game_menu_label:
    xpos 75
    ysize 180

style game_menu_label_text:
    size 75
    color gui.accent_color
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -45


## 关于屏幕 ########################################################################
##
## 此屏幕提供有关游戏和 Ren'Py 的制作人员和版权信息。
##
## 此屏幕没有什么特别之处，因此它也可以作为一个例子来说明如何制作一个自定义屏
## 幕。

screen about():

    tag menu

    ## 此 use 语句将 game_menu 屏幕包含到了这个屏幕内。子级 vbox 将包含在
    ## game_menu 屏幕的 viewport 内。
    use game_menu(_("关于"), scroll="viewport"):

        style_prefix "about"

        vbox:

            label "[config.name!t]"
            text _("版本 [config.version!t]\n")

            ## gui.about 通常在 options.rpy 中设置。
            if gui.about:
                text "[gui.about!t]\n"

            text _("引擎：{a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only]\n\n[renpy.license!t]")


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size


## 读取和保存屏幕 #####################################################################
##
## 这些屏幕负责让用户保存游戏并能够再次读取。由于它们几乎完全一样，因此这两个屏
## 幕都是以第三个屏幕 file_slots 来实现的。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#save https://doc.renpy.cn/zh-
## CN/screen_special.html#load

default file_slot_sel = 1
default save_note_editing = False

screen save():

    tag menu
    use file_slots(_("SAVE"), "save")


screen load():

    tag menu
    use file_slots(_("LOAD"), "load")


screen file_slots(title, mode):

    on "show" action SetVariable("save_note_editing", False)

    $ sel = file_slot_sel

    $ cur_page = FileCurrentPage()
    $ accent = "#D99A3D" if mode == "save" else "#2E7478"
    $ accent_text = "#091E22" if mode == "save" else "#F4F1E8"

    add "gui/extras_bg.png"

    hbox:
        xalign 0.5
        ypos 30
        spacing 18

        frame:
            background Solid(accent)
            xsize 300
            ysize 210
            padding (24, 16)

            vbox:
                spacing 4
                text ("No. %d" % sel) style "save_no_text" color accent_text
                text FileTime(sel, format="%Y年%m月%d日", empty="—") style "save_date_text" color accent_text
                text FileTime(sel, format="%H:%M:%S", empty="") style "save_date_text" color accent_text

        frame:
            style "save_info_panel"
            xsize 1282
            ysize 210

            vbox:
                spacing 6
                text title style "save_title_text"

                $ sel_dialogue = FileJson(sel, "dialogue", empty=(_last_say_what if mode == "save" else ""), missing="")
                if sel_dialogue:
                    text ("「%s」" % sel_dialogue) style "save_dialogue_text"
                else:
                    text _("（暂无对白记录）") style "save_dialogue_text_dim"

                text FileSaveName(sel, empty=_("空存档位")) style "save_name_text"

                if mode == "save":
                    hbox:
                        spacing 10
                        yalign 0.5
                        text _("备注") style "save_note_label"

                        frame:
                            background "#FFFFFF"
                            padding (10, 2)
                            xsize 520
                            ysize 34
                            yalign 0.5

                            if save_note_editing:
                                input value SaveNoteInputValue("save_name") style "save_note_input" length 40
                            else:
                                button:
                                    action SetVariable("save_note_editing", True)
                                    background None
                                    hover_background "#D9E6EA"
                                    xfill True
                                    yfill True

                                    text (save_name if save_name else _("点击输入备注")):
                                        style "save_note_input"

                        text _("点击备注框即可添加备注") style "save_note_hint"
                else:
                    text FileTime(sel, format="%Y-%m-%d  %H:%M", empty="") style "save_note_hint"

    grid 5 4:
        xalign 0.5
        ypos 265
        xsize 1600
        ysize 734
        spacing 10

        for i in range(20):
            $ slot = i + 1

            if mode == "save":
                $ slot_prompt = _("是否覆盖？") if FileLoadable(slot) else _("是否保存？")
                $ slot_action = Confirm(slot_prompt, FileSave(slot, confirm=False), confirm_selected=True)
            else:
                $ slot_action = Confirm(_("是否读取？"), FileLoad(slot, confirm=False), confirm_selected=True)

            button:
                style "save_slot_button"
                action slot_action
                hovered SetVariable("file_slot_sel", slot)
                selected (sel == slot)

                if FileLoadable(slot):
                    add FileScreenshot(slot) xysize (300, 164)
                else:
                    text ("+" if mode == "save" else "") style "save_slot_plus" xalign 0.5 yalign 0.5

    button:
        action FilePagePrevious(max=15)
        style "save_side_button"
        xpos 14
        ypos 632
        yanchor 0.5

        vbox:
            spacing 0

            for ch in title:
                text ch style "save_side_text"
            text "◀" style "save_side_arrow"

    button:
        action FilePageNext(max=15)
        style "save_side_button"
        xalign 1.0
        xoffset -14
        ypos 632
        yanchor 0.5

        vbox:
            spacing 0

            for ch in title:
                text ch style "save_side_text"
            text "▶" style "save_side_arrow"

    hbox:
        xpos 160
        yalign 1.0
        yoffset -16
        spacing 28

        textbutton _("删除"):
            action FileDelete(sel, confirm=True)
            style "save_bottom_button"

        textbutton _("跳至最近一次的存档"):
            action FileLoad(1, page="auto")
            style "save_bottom_button"

    textbutton _("关闭"):
        action Return()
        style "save_bottom_button"
        xalign 1.0
        xoffset -160
        yalign 1.0
        yoffset -16

    hbox:
        xalign 0.5
        yalign 1.0
        yoffset -16
        spacing 8

        for page in range(1, 16):
            textbutton str(page):
                action FilePage(page)
                style "save_page_button"
                selected (str(cur_page) == str(page))


style save_no_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 38

style save_date_text:
    font gui.text_font
    size 22

style save_info_panel:
    background "#F4F1E8EE"
    padding (24, 14)

style save_title_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 30
    color "#091E22"

style save_dialogue_text:
    font gui.text_font
    size 20
    color "#174A4E"

style save_dialogue_text_dim:
    font gui.text_font
    size 18
    color "#7A9599"

style save_name_text:
    font gui.text_font
    size 24
    color "#174A4E"

style save_note_label:
    font gui.text_font
    size 20
    color "#174A4E"
    yalign 0.5

style save_note_input:
    font gui.text_font
    size 22
    color "#091E22"
    yalign 0.5

style save_note_hint:
    font gui.text_font
    size 18
    color "#5B7A7E"
    yalign 0.5

style save_slot_button:
    background "gui/button/save_slot_idle.png"
    hover_background "gui/button/save_slot_hover.png"
    selected_background "gui/button/save_slot_selected.png"
    selected_hover_background "gui/button/save_slot_selected.png"
    xsize 312
    ysize 176
    padding (6, 6)

style save_slot_plus:
    font gui.text_font
    size 40
    color "#7FC8C088"

style save_page_button:
    background None
    hover_background None
    padding (6, 2)

style save_page_button_text:
    font gui.text_font
    size 20
    color "#B9CBD3"
    hover_color "#F2C77E"
    selected_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style save_bottom_button:
    background None
    hover_background None
    padding (10, 4)

style save_bottom_button_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 22
    color "#7FC8C0"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style save_side_button:
    background None
    hover_background "#7FC8C022"
    padding (6, 10)

style save_side_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 40
    color "#7FC8C0"
    outlines [(2, "#061416", 0, 0)]
    xalign 0.5

style save_side_arrow:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 26
    color "#D99A3D"
    xalign 0.5


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 75
    ypadding 5
    xalign 0.5

style page_label_text:
    textalign 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.text_properties("slot_button")


## 游戏菜单首页 ######################################################################
##
## 触屏快捷菜单的“菜单”按钮打开这里。单独做一个首页，是因为保存、设置等
## 屏幕都是全屏独立布局，没有公共导航栏。

screen game_menu_home():

    tag menu

    add "gui/extras_bg.png"

    text _("MENU") style "options_heading" xpos 64 ypos 22

    frame:
        style "options_panel"
        xalign 0.5
        ypos 150
        xsize 780

        vbox:
            xalign 0.5
            yalign 0.5
            spacing 16

            textbutton _("保存") action ShowMenu("save") style "menu_home_button"
            textbutton _("读取游戏") action ShowMenu("load") style "menu_home_button"
            textbutton _("设置") action ShowMenu("preferences") style "menu_home_button"
            textbutton _("鉴赏") action ShowMenu("extras") style "menu_home_button"
            textbutton _("标题菜单") action MainMenu(confirm=True) style "menu_home_button"
            textbutton _("退出游戏") action Quit(confirm=True) style "menu_home_button"
            textbutton _("返回游戏") action Return() style "menu_home_button"

    key "game_menu" action Return()


## 设置屏幕 ########################################################################
##
## 设置屏幕允许用户配置游戏，使其更适合自己。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#preferences

default prefs_tab = "basic"

screen preferences():

    tag menu

    add "gui/extras_bg.png"

    text _("OPTIONS") style "options_heading" xpos 120 ypos 22

    hbox:
        xpos 420
        ypos 40
        spacing 12

        textbutton _("基本设置") action SetVariable("prefs_tab", "basic") style "options_tab" selected (prefs_tab == "basic")
        text "|" style "options_tab_sep"
        textbutton _("文字1") action SetVariable("prefs_tab", "text1") style "options_tab" selected (prefs_tab == "text1")
        text "|" style "options_tab_sep"
        textbutton _("文字2") action SetVariable("prefs_tab", "text2") style "options_tab" selected (prefs_tab == "text2")
        text "|" style "options_tab_sep"
        textbutton _("音量") action SetVariable("prefs_tab", "audio") style "options_tab" selected (prefs_tab == "audio")
        text "|" style "options_tab_sep"
        textbutton _("语音") action SetVariable("prefs_tab", "voice") style "options_tab" selected (prefs_tab == "voice")
        text "|" style "options_tab_sep"
        textbutton _("键盘") action SetVariable("prefs_tab", "keyboard") style "options_tab" selected (prefs_tab == "keyboard")
        text "|" style "options_tab_sep"
        textbutton _("鼠标") action SetVariable("prefs_tab", "mouse") style "options_tab" selected (prefs_tab == "mouse")
        text "|" style "options_tab_sep"
        textbutton _("触控") action SetVariable("prefs_tab", "touch") style "options_tab" selected (prefs_tab == "touch")
        text "|" style "options_tab_sep"
        textbutton _("系统") action SetVariable("prefs_tab", "system") style "options_tab" selected (prefs_tab == "system")

    frame:
        style "options_panel"
        xalign 0.5
        ypos 145
        xsize 1680
        ysize 780

        if prefs_tab == "basic":
            use prefs_basic
        elif prefs_tab == "text1":
            use prefs_text1
        elif prefs_tab == "text2":
            use prefs_text2
        elif prefs_tab == "audio":
            use prefs_audio
        elif prefs_tab == "voice":
            use prefs_voice
        elif prefs_tab == "keyboard":
            use prefs_keyboard
        elif prefs_tab == "mouse":
            use prefs_mouse
        elif prefs_tab == "touch":
            use prefs_touch
        else:
            use prefs_system

    textbutton _("恢复默认设置") action Preference("reset") style "options_footer_button" xpos 120 yalign 1.0 yoffset -36
    textbutton _("关闭") action Return() style "options_footer_button" xalign 1.0 yalign 1.0 xoffset -120 yoffset -36

    key "game_menu" action Return()


screen pref_row(label):

    hbox:
        spacing 32
        yalign 0.5

        frame:
            style "options_label_chip"
            text label style "options_label_text"

        frame:
            style "options_control_frame"
            transclude


screen pref_field_row(label, field, choices, test=None):

    use pref_row(label):
        hbox:
            spacing 14

            for choice_text, value, enabled in choices:
                if enabled:
                    textbutton choice_text:
                        action ([SetField(persistent, field, value)] + ([Function(test, value)] if test else []))
                        style "options_segment"
                        selected (getattr(persistent, field) == value)
                else:
                    textbutton choice_text:
                        action NullAction()
                        style "options_segment_disabled"


screen pref_action_row(label, options):

    use pref_row(label):
        hbox:
            spacing 14

            for choice_text, act in options:
                textbutton choice_text:
                    action act
                    style "options_segment"


screen pref_slider_row(label, value):

    use pref_row(label):
        bar value value style "options_slider"


screen prefs_basic():

    vbox:
        spacing 12

        use pref_field_row(_("快捷菜单"), "quick_menu_mode", [
            (_("不显示"), "hide", True),
            (_("触控"), "touch", True),
            (_("传统风格"), "classic", True),
        ])

        use pref_row(_("快进")):
            hbox:
                spacing 14

                textbutton _("仅限已读内容"):
                    action Preference("skip", "seen")
                    style "options_segment"
                    selected (not preferences.skip_unseen)

                textbutton _("全部"):
                    action Preference("skip", "all")
                    style "options_segment"
                    selected preferences.skip_unseen

        use pref_slider_row(_("快进/快退速度"), FieldValue(persistent, "skip_speed", range=1.0, step=0.1))

        use pref_field_row(_("选项位置"), "choice_pos", [
            (_("上部"), "upper", True),
            (_("中央"), "center", True),
            (_("下部"), "bottom", True),
        ])

        use pref_field_row(_("播放角色语音"), "voice_skip_stop", [
            (_("跳过对白时停止配音"), True, True),
            (_("不停止"), False, True),
        ])

        use pref_field_row(_("光标初期位置"), "choice_cursor", [
            (_("位于“是”"), "yes", True),
            (_("位于“否”"), "no", True),
        ])

        use pref_field_row(_("控制器震动功能"), "controller_rumble", [
            (_("无效"), "off", True),
            (_("弱"), "weak", True),
            (_("中"), "medium", True),
            (_("强"), "strong", True),
        ], test=controller_rumble_preview)


screen prefs_text1():

    vbox:
        spacing 12

        use pref_row(_("语言")):
            hbox:
                spacing 14

                for _lang_label, _renpy_code, _ui_code, _enabled in PROJECT_LANGUAGES:
                    if _enabled:
                        textbutton _lang_label:
                            action [SetField(persistent, "ui_language", _ui_code), SetField(persistent, "language_chosen", True), Language(_renpy_code)]
                            style "options_segment"
                            selected (preferences.language == _renpy_code)
                    else:
                        textbutton _lang_label:
                            action NullAction()
                            style "options_segment_disabled"

        use pref_field_row(_("字体"), "font_choice", [
            (_("黑体"), "sans", True),
            (_("圆黑体"), "round", True),
            (_("宋体"), "serif", True),
        ])

        use pref_field_row(_("窗口颜色"), "window_color", [
            (_("浅蓝色"), "light", True),
            (_("深蓝色"), "deep", True),
            (_("黑色"), "black", True),
        ])

        use pref_slider_row(_("窗口透明度"), FieldValue(persistent, "window_opacity", range=100, step=5))

        use pref_field_row(_("已读内容颜色标记"), "read_mark", [
            (_("关"), "off", True),
            (_("仅对选项有效"), "choices", True),
            (_("开"), "on", True),
        ])

        frame:
            style "options_preview_frame"
            text _("此文本反映了文字速度等设置的结果。") style "options_preview_text"


screen prefs_text2():

    vbox:
        spacing 20

        use pref_slider_row(_("文字速度"), Preference("text speed"))
        use pref_slider_row(_("按字数翻页"), PerCharDelayValue())
        use pref_slider_row(_("固定等待时间"), Preference("auto-forward time"))

        frame:
            style "options_preview_frame"
            text _("文字预览。") style "options_preview_text"


screen prefs_audio():

    vbox:
        spacing 16

        use pref_slider_row(_("整体音量"), Preference("main volume"))
        use pref_slider_row(_("语音"), Preference("voice volume"))
        use pref_slider_row(_("音乐"), Preference("music volume"))
        use pref_slider_row(_("效果音"), Preference("sound volume"))
        use pref_slider_row(_("系统音"), Preference("mixer system volume"))


screen pref_voice_cast_row(name, portrait, actor):

    hbox:
        spacing 32
        yalign 0.5

        frame:
            style "options_label_chip"
            hbox:
                spacing 14
                if portrait and renpy.loadable(portrait):
                    add portrait xysize (56, 56) yalign 0.5
                text name style "options_label_text"

        frame:
            style "options_control_frame"
            text actor style "options_preview_text"


screen prefs_voice():

    vbox:
        spacing 16

        text _("语音音量可在「音量」标签页调整。") style "options_preview_text"

        if PROJECT_VOICE_CAST:
            viewport:
                ysize 580
                scrollbars "vertical"
                mousewheel True
                draggable True

                vbox:
                    spacing 12
                    for _tag, _vname, _vportrait, _vactor in PROJECT_VOICE_CAST:
                        use pref_voice_cast_row(_vname, _vportrait, _vactor)
        else:
            text _("暂无已注册的角色语音，接入配音资源后将在此显示。") style "options_preview_text"


screen prefs_keyboard():

    vbox:
        spacing 12

        use pref_field_row(_("C键（快进）"), "key_c_mode", [
            (_("长按中持续"), "hold", True),
            (_("开始/结束"), "toggle", True),
        ])

        use pref_field_row(_("Z键（快退）"), "key_z_mode", [
            (_("长按中持续"), "hold", True),
            (_("开始/结束"), "toggle", True),
        ])

        use pref_field_row(_("S键"), "key_s", [
            (_("无效"), "none", True),
            (_("快速保存"), "quicksave", True),
        ])

        use pref_field_row(_("L键"), "key_l", [
            (_("无效"), "none", True),
            (_("快速读取"), "quickload", True),
            (_("切换语言"), "language", False),
        ])

        use pref_field_row(_("上方向键"), "key_up", [
            (_("无效"), "none", True),
            (_("剧情回顾"), "history", True),
        ])


screen prefs_mouse():

    vbox:
        spacing 4

        use pref_field_row(_("右键"), "mouse_right", [
            (_("隐藏窗口"), "hide", True),
            (_("系统菜单"), "menu", True),
        ])

        use pref_field_row(_("左键+右键"), "mouse_both", [
            (_("无效"), "none", True),
            (_("切换语言"), "language", False),
        ])

        use pref_field_row(_("鼠标滚轮"), "mouse_wheel", [
            (_("无效"), "none", True),
            (_("隐藏窗口"), "hide", True),
            (_("系统菜单"), "menu", True),
        ])

        use pref_field_row(_("鼠标滚轮向上"), "mouse_wheel_up", [
            (_("无效"), "none", True),
            (_("剧情回顾"), "history", True),
            (_("后退一项"), "back", True),
        ])

        use pref_field_row(_("鼠标滚轮向下"), "mouse_wheel_down", [
            (_("无效"), "none", True),
            (_("隐藏窗口"), "hide", True),
            (_("前进一项"), "forward", True),
        ])

        use pref_field_row(_("返回/前进键"), "mouse_side", [
            (_("无效"), "none", True),
            (_("跳转及切换页面"), "page", True),
        ])

        use pref_field_row(_("手势操作"), "mouse_gesture", [
            (_("无效"), "off", True),
            (_("有效"), "on", True),
        ])

        use pref_action_row(_("指针自动移动"), [
            (_("无效"), Preference("automatic move", "disable")),
            (_("对话框和选项"), Preference("automatic move", "enable")),
        ])


screen prefs_touch():

    vbox:
        spacing 12

        use pref_field_row(_("快进"), "touch_skip", [
            (_("无效"), "off", True),
            (_("有效"), "on", True),
        ])

        use pref_field_row(_("快退"), "touch_back", [
            (_("无效"), "off", True),
            (_("有效"), "on", True),
        ])

        use pref_field_row(_("跳转（前进）"), "touch_forward", [
            (_("无效"), "off", True),
            (_("有效"), "on", True),
        ])

        use pref_field_row(_("跳转（后退）"), "touch_rewind", [
            (_("无效"), "off", True),
            (_("有效"), "on", True),
        ])

        frame:
            style "options_preview_frame"
            text _("触控手势仅在触屏设备上生效。") style "options_preview_text"


screen prefs_system():

    vbox:
        spacing 30

        use pref_action_row(_("显示模式"), [
            (_("窗口模式"), Preference("display", "window")),
            (_("全屏模式"), Preference("display", "fullscreen")),
        ])

        use pref_row(_("窗口大小")):
            hbox:
                spacing 6
                for scale_label, scale in window_scale_options:
                    textbutton _(scale_label):
                        action Function(set_window_scale, scale)
                        style "options_scale"
                        selected is_current_window_scale(scale)


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text


## Summer-Pockets-style OPTIONS screen.

style options_heading:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 58
    color "#F4F1E8"
    outlines [(3, "#061416", 0, 0)]

style options_tab:
    background None
    hover_background None
    padding (4, 2)

style options_tab_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 26
    color "#9FB6C0"
    hover_color "#F2C77E"
    selected_color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style options_tab_sep:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 26
    color "#7FC8C066"
    yalign 0.5

style options_panel:
    background Frame("gui/extras_panel.png", 44, 44)
    padding (48, 34)

style options_version:
    font gui.text_font
    size 19
    color "#B9CBD3"
    outlines [(2, "#061416", 0, 0)]

style options_footer_button:
    background None
    hover_background None
    padding (8, 4)

style options_footer_button_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 25
    color "#7FC8C0"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style options_label_chip:
    background Frame("gui/pref_chip.png", 24, 24)
    xsize 380
    ysize 72
    padding (24, 14)

style options_label_text:
    font gui.text_font
    size 28
    color "#F4F1E8"
    yalign 0.5
    outlines [(2, "#061416", 0, 0)]

style options_control_frame:
    background None
    padding (0, 0)
    yalign 0.5
    xsize 1120

style options_segment is button:
    background Frame("gui/pref_segment_idle.png", 20, 20)
    hover_background Frame("gui/pref_segment_hover.png", 20, 20)
    selected_background Frame("gui/pref_segment_selected.png", 20, 20)
    padding (18, 8)
    xminimum 220

style options_segment_text is button_text:
    font gui.text_font
    size 25
    color "#D7E6E6"
    hover_color "#F2C77E"
    selected_color "#091E22"
    outlines [(2, "#061416", 0, 0)]
    selected_outlines [(1, "#7FC8C0", 0, 0)]
    xalign 0.5
    yalign 0.5
    textalign 0.5

style options_segment_disabled is button:
    background Frame("gui/pref_segment_idle.png", 20, 20)
    padding (18, 8)
    xminimum 220

style options_segment_disabled_text is button_text:
    font gui.text_font
    size 25
    color "#7A8C93"
    outlines [(2, "#061416", 0, 0)]
    xalign 0.5
    yalign 0.5
    textalign 0.5

style menu_home_button is options_segment:
    xsize 520
    padding (20, 14)

style menu_home_button_text is options_segment_text:
    size 30
    xalign 0.5
    textalign 0.5

style options_scale is button:
    background Frame("gui/pref_segment_idle.png", 16, 16)
    hover_background Frame("gui/pref_segment_hover.png", 16, 16)
    selected_background Frame("gui/pref_segment_selected.png", 16, 16)
    padding (10, 6)
    xminimum 92

style options_scale_text is button_text:
    font gui.text_font
    size 19
    color "#D7E6E6"
    hover_color "#F2C77E"
    selected_color "#091E22"
    outlines [(2, "#061416", 0, 0)]
    selected_outlines [(1, "#7FC8C0", 0, 0)]
    xalign 0.5
    yalign 0.5
    textalign 0.5

style options_check_button is check_button:
    foreground Transform("gui/pref_check_[prefix_]foreground.png", yoffset=4)
    background None
    hover_background None
    padding (34, 2, 8, 6)

style options_check_button_text is check_button_text:
    font gui.text_font
    size 25
    color "#D7E6E6"
    hover_color "#F2C77E"
    selected_color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style options_slider is bar:
    xsize 1000
    ysize 22
    yalign 0.5
    thumb_offset 14
    left_bar Solid("#7FC8C0")
    right_bar Solid("#174A4E")
    thumb "gui/pref_thumb.png"

style options_preview_frame:
    background "#0B2428AA"
    xsize 1532
    ysize 92
    padding (24, 12)

style options_preview_text:
    font gui.text_font
    size 24
    color "#F4F1E8"
    yalign 0.5
    outlines [(2, "#061416", 0, 0)]


style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 3

style pref_label_text:
    yalign 1.0

style pref_vbox:
    xsize 338

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.text_properties("radio_button")

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.text_properties("check_button")

style slider_slider:
    xsize 525

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 15

style slider_button_text:
    properties gui.text_properties("slider_button")

style slider_vbox:
    xsize 675


## 历史屏幕 ########################################################################
##
## 这是一个向用户显示对话历史的屏幕。虽然此屏幕没有什么特别之处，但它必须访问储
## 存在 _history_list 中的对话历史记录。
##
## https://doc.renpy.cn/zh-CN/history.html

screen history():

    tag menu

    ## 避免预缓存此屏幕，因为它可能非常大。
    predict False

    add "gui/log_bg.png"

    text "LOG" style "log_title" xpos 160 ypos 26
    text _("回顾已读对白") style "log_subtitle" xpos 268 ypos 42

    frame:
        style "log_list_frame"
        xalign 0.5
        ypos 110
        xsize 1600
        ysize 846

        viewport:
            xsize 1600
            ysize 830
            mousewheel True
            draggable True
            scrollbars "vertical"
            yinitial 1.0

            vbox:
                spacing 14

                for i, h in enumerate(_history_list):
                    $ is_last = (i == len(_history_list) - 1)
                    $ who_color = (h.who_args.get("color", "#F2C77E") if h.who_args else "#F2C77E")
                    $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)

                    frame:
                        style ("log_entry_active" if is_last else "log_entry")
                        xsize 1556

                        hbox:
                            spacing 18
                            yalign 0.5

                            if getattr(h, "voice", None):
                                button:
                                    style "log_voice_button"
                                    action Play("voice", h.voice)
                                    add "gui/icon_voice.png" xysize (38, 38)
                            else:
                                null width 38

                            vbox:
                                xsize 1380
                                spacing 6
                                yalign 0.5

                                if h.who:
                                    text h.who style "log_who" color who_color
                                text what style "log_text" substitute False

                if not _history_list:
                    text _("尚无对话历史记录。") style "log_empty" xalign 0.5

    frame:
        style "log_bottom_bar"
        xalign 0.5
        yalign 1.0
        yoffset -16

        hbox:
            xalign 0.5
            spacing 30
            text _("滚轮 / 拖动查看历史，点击扬声器重播语音") style "log_hint"
            textbutton _("关闭") action Return() style "log_close_button"

    key "game_menu" action Return()


## 此代码决定了允许在历史记录屏幕上显示哪些标签。

define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    textalign gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    textalign gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## LOG 屏幕样式（Summer Pockets 风格） ##############################################

style log_list_frame:
    background None
    padding (0, 0)

style log_entry:
    background Frame("gui/log_entry.png", 30, 30)
    padding (26, 18)

style log_entry_active is log_entry:
    background Frame("gui/log_entry_active.png", 30, 30)

style log_voice_button:
    background None
    hover_background "#7FC8C022"
    padding (6, 6)
    yalign 0.5

style log_who:
    font gui.interface_text_font
    size 24
    color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style log_text:
    font gui.text_font
    size 26
    color "#F4F1E8"
    line_spacing 4
    outlines [(2, "#061416", 0, 0)]

style log_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 40
    color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style log_subtitle:
    font gui.text_font
    size 18
    color "#7FC8C0"

style log_empty:
    font gui.text_font
    size 28
    color "#B9CBD3"
    xalign 0.5
    yalign 0.5

style log_bottom_bar:
    background "#091E22CC"
    xsize 1600
    padding (24, 10)

style log_hint:
    font gui.text_font
    size 18
    color "#7FC8C0"
    yalign 0.5

style log_close_button is save_bottom_button


## MANUAL 屏幕样式（Summer Pockets 风格） ###########################################

style manual_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 38
    color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style manual_title_zh:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 26
    color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style manual_page_no:
    font gui.text_font
    size 24
    color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style manual_panel_frame:
    background Frame("gui/manual_panel.png", 40, 40)
    padding (48, 36)

style manual_section_title:
    font gui.interface_text_font
    size 24
    color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style manual_body:
    font gui.text_font
    size 21
    color "#F4F1E8"
    line_spacing 4

style manual_arrow:
    background None
    hover_background "#7FC8C022"
    padding (12, 12)

style manual_arrow_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 56
    color "#7FC8C0"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style manual_bottom_bar:
    background "#091E22CC"
    xsize 1660
    padding (24, 10)

style manual_page_button:
    background None
    hover_background None
    padding (10, 4)

style manual_page_button_text:
    font gui.text_font
    size 22
    color "#7FC8C0"
    hover_color "#F2C77E"
    selected_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style manual_hint:
    font gui.text_font
    size 18
    color "#7FC8C0"
    yalign 0.5


## 帮助屏幕 ########################################################################
##
## 提供有关键盘和鼠标映射信息的屏幕。它使用其它屏幕（keyboard_help、mouse_help
## 和 gamepad_help）来显示实际的帮助内容。

screen help():

    tag menu

    default manual_page = 0
    $ _extra_pages = PROJECT_MANUAL_EXTRA_PAGES if PROJECT_MANUAL_EXTRA_PAGES else []
    $ manual_pages = 3 + len(_extra_pages)
    $ _mp = min(manual_page, manual_pages - 1)

    add "gui/log_bg.png"
    add "gui/manual_banner.png" xalign 0.5 ypos 0

    text "MANUAL" style "manual_title" xpos 130 ypos 18
    text _("游戏说明") style "manual_title_zh" xpos 360 ypos 30
    text ("PAGE %d" % (_mp + 1)) style "manual_page_no" xalign 1.0 xoffset -130 ypos 38

    frame:
        style "manual_panel_frame"
        xalign 0.5
        ypos 150
        xsize 1660
        ysize 800

        if _mp == 0:
            use manual_page_1
        elif _mp == 1:
            use manual_page_2
        elif _mp == 2:
            use manual_page_3
        else:
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True

                use content_page_body(_extra_pages[_mp - 3])

    imagebutton:
        idle "gui/manual_prev.png"
        hover "gui/manual_prev_hover.png"
        action SetScreenVariable("manual_page", max(0, _mp - 1))
        background None
        idle_background None
        padding (0, 0)
        xpos 18
        ypos 550
        yanchor 0.5

    imagebutton:
        idle "gui/manual_next.png"
        hover "gui/manual_next_hover.png"
        action SetScreenVariable("manual_page", min(manual_pages - 1, _mp + 1))
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

            for i in range(manual_pages):
                textbutton str(i + 1):
                    action SetScreenVariable("manual_page", i)
                    style "manual_page_button"
                    selected (_mp == i)

            text _("左右箭头翻页") style "manual_hint"
            textbutton _("关闭") action Return() style "log_close_button"

    key "game_menu" action Return()


screen manual_section(title, body, icon=None, visual=None, visual_size=None):

    vbox:
        spacing 6

        hbox:
            spacing 10
            yalign 0.5

            if icon:
                add render_visual(icon, default_size=(30, 30)) yalign 0.5
            text title style "manual_section_title"

        if visual:
            add render_visual(visual, default_size=visual_size)

        text body style "manual_body"


screen manual_page_1():

    hbox:
        spacing 44

        vbox:
            xsize 760
            spacing 20

            text PROJECT_MANUAL_INTRO style "manual_body"

            use manual_section(_("选项"), _("画面上出现选项时，用鼠标左键点击选择。\n选项位置可在 OPTIONS 的基本设置中调整。"))

            use manual_section(_("分支"), PROJECT_MANUAL_BRANCH_INFO)

        vbox:
            xsize 760
            spacing 20

            use manual_section(_("快捷菜单"), _("文本窗口右侧显示 CLOSE / VOICE / LOG / LOCK。\n可在 OPTIONS 的基本设置中选择快捷菜单的显示方式。"))

            use manual_section(_("CLOSE"), _("暂时隐藏文本和界面，点击画面即可恢复。"), "gui/icon_close.png")
            use manual_section(_("VOICE"), _("重播该句角色语音；没有语音的句子不可用。"), "gui/icon_voice.png")
            use manual_section(_("LOG"), _("打开历史记录，可滚动查看并重播语音。"), "gui/icon_log.png")
            use manual_section(_("LOCK"), _("收起右侧菜单；点击底部 LOCK 可恢复显示。"), "gui/icon_lock_open.png")


screen manual_page_2():

    hbox:
        spacing 44

        vbox:
            xsize 760
            spacing 20

            use manual_section(_("Q.SAVE / Q.LOAD"), _("快速保存 / 快速读取。\nQ.LOAD 会先确认「是否读取快速存档？」。"), "gui/icon_qsave.png")
            use manual_section(_("SAVE / LOAD"), _("打开存档 / 读档画面。\n5×4 槽位，鼠标悬停即选中，点击后确认保存、覆盖或读取。"), "gui/icon_save.png")

        vbox:
            xsize 760
            spacing 20

            use manual_section(_("BACK / NEXT / REWIND"), _("回退、前进与快速回退。"), "gui/icon_back.png")
            use manual_section(_("AUTO / SKIP"), _("自动播放 / 快进。\nSKIP 可在 OPTIONS 中选择仅跳过已读或全部跳过。"), "gui/icon_auto.png")
            use manual_section(_("TITLE / EXIT"), _("返回标题界面 / 退出游戏，均会先弹出确认。"), "gui/icon_title.png")
            use manual_section(_("OPTIONS / RECORD"), _("打开设置 / 鉴赏（CG 与音乐）。"), "gui/icon_options.png")
            use manual_section(_("MANUAL / LOCK"), _("打开本说明 / 收起右侧菜单。"), "gui/icon_manual.png")


screen manual_page_3():

    hbox:
        spacing 44

        vbox:
            xsize 760
            spacing 20

            use manual_section(_("存档画面"), _("鼠标悬停在槽位上即选中，顶部显示编号、日期、\n保存位置对白和备注。\n点击槽位会询问是否保存 / 覆盖 / 读取。"))
            use manual_section(_("翻页"), _("点击左右两列竖排的 SAVE / LOAD 与箭头，\n可切换到上一页 / 下一页（1–15 页）。"))

        vbox:
            xsize 760
            spacing 20

            use manual_section(_("OPTIONS"), _("共 9 个标签：\n基本设置 / 文字1 / 文字2 / 音量 / 语音 /\n键盘 / 鼠标 / 触控 / 系统。"))
            use manual_section(_("文字速度"), _("默认逐字显示，每秒约 30 个字；\n可在文字相关设置中调整速度。"))
            use manual_section(_("触控模式"), _("触控快捷条为：\nSAVE / LOAD / AUTO / SKIP / OPTIONS / HIDE。"))


screen keyboard_help():

    hbox:
        label _("回车")
        text _("推进对话并激活界面。")

    hbox:
        label _("空格")
        text _("在没有选择的情况下推进对话。")

    hbox:
        label _("方向键")
        text _("导航界面。")

    hbox:
        label _("Esc")
        text _("访问游戏菜单。")

    hbox:
        label _("键盘")
        text _("按住时快进对话。")

    hbox:
        label _("Tab")
        text _("切换对话快进。")

    hbox:
        label _("上一页")
        text _("回退至先前的对话。")

    hbox:
        label _("下一页")
        text _("向前至后来的对话。")

    hbox:
        label "H"
        text _("隐藏用户界面。")

    hbox:
        label "S"
        text _("截图。")

    hbox:
        label "V"
        text _("切换辅助{a=https://doc.renpy.cn/zh-CN/self_voicing.html}机器朗读{/a}。")

    hbox:
        label "Shift+A"
        text _("打开无障碍菜单。")


screen mouse_help():

    hbox:
        label _("左键点击")
        text _("推进对话并激活界面。")

    hbox:
        label _("中键点击")
        text _("隐藏用户界面。")

    hbox:
        label _("右键点击")
        text _("访问游戏菜单。")

    hbox:
        label _("鼠标滚轮上")
        text _("回退至先前的对话。")

    hbox:
        label _("鼠标滚轮下")
        text _("向前至后来的对话。")


screen gamepad_help():

    hbox:
        label _("右扳机键\nA/底键")
        text _("推进对话并激活界面。")

    hbox:
        label _("左扳机键\n左肩键")
        text _("回退至先前的对话。")

    hbox:
        label _("右肩键")
        text _("向前至后来的对话。")

    hbox:
        label _("十字键，摇杆")
        text _("导航界面。")

    hbox:
        label _("开始，向导，B/右键")
        text _("访问游戏菜单。")

    hbox:
        label _("Y/顶键")
        text _("隐藏用户界面。")

    textbutton _("校准") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 12

style help_button_text:
    properties gui.text_properties("help_button")

style help_label:
    xsize 375
    right_padding 30

style help_label_text:
    size gui.text_size
    xalign 1.0
    textalign 1.0



################################################################################
## 其他屏幕
################################################################################


## 确认屏幕 ########################################################################
##
## 当 Ren'Py 需要询问用户有关确定或取消的问题时，会调用确认屏幕。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## 显示此屏幕时，确保其他屏幕无法输入。
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 60

                textbutton _("是") action yes_action
                textbutton _("否") action no_action

    ## 右键点击退出并答复 no（取消）。
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame("gui/confirm_frame.png", gui.confirm_frame_borders, tile=gui.frame_tile)
    padding (70, 55, 70, 55)
    xsize 1000
    ysize 330
    xalign .5
    yalign .5

style confirm_prompt_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 42
    color "#174A4E"
    textalign 0.5
    layout "subtitle"

style confirm_button:
    background Frame("gui/confirm_choice_idle.png", 44, 44)
    hover_background Frame("gui/confirm_choice_hover.png", 44, 44)
    xsize 300
    ysize 90
    padding (0, 0)

style confirm_button_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 34
    color "#174A4E"
    hover_color "#091E22"
    xalign 0.5
    yalign 0.5
    textalign 0.5


## 快进指示屏幕 ######################################################################
##
## skip_indicator 屏幕用于指示快进正在进行中。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 9

            text _("正在快进")

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## 此变换用于一个接一个地闪烁箭头。
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## 我们必须使用包含“▸”（黑色右旋小三角）字形的字体。
    font "DejaVuSans.ttf"


## 通知屏幕 ########################################################################
##
## 通知屏幕用于向用户显示消息。（例如，当游戏快速保存或进行截屏时。）
##
## https://doc.renpy.cn/zh-CN/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL 模式屏幕 ####################################################################
##
## 此屏幕用于 NVL 模式的对话和菜单。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## 在 vpgrid 或 vbox 中显示对话框。
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## 显示菜单，如果给定的话。如果 config.narrator_menu 设置为 True，则菜单
        ## 可能显示不正确。
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


## 此语句控制一次可以显示的 NVL 模式条目的最大数量。
define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    textalign gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    textalign gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    textalign gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.text_properties("nvl_button")


## 对话气泡屏幕 ######################################################################
##
## 对话气泡屏幕用于以对话气泡的形式向玩家显示对话。对话气泡屏幕的参数与 say 屏幕
## 相同，必须创建一个 id 为 what 的可视控件，并且可以创建 id 为 namebox、who 和
## window 的可视控件。
##
## https://doc.renpy.cn/zh-CN/bubble.html#bubble-screen

screen bubble(who, what):
    style_prefix "bubble"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "bubble_namebox"

                text who:
                    id "who"

        text what:
            id "what"

        default ctc = None
        showif ctc:
            add ctc

style bubble_window is empty
style bubble_namebox is empty
style bubble_who is default
style bubble_what is default

style bubble_window:
    xpadding 30
    top_padding 5
    bottom_padding 5

style bubble_namebox:
    xalign 0.5

style bubble_who:
    xalign 0.5
    textalign 0.5
    color "#000"

style bubble_what:
    align (0.5, 0.5)
    text_align 0.5
    layout "subtitle"
    color "#000"

define bubble.frame = Frame("gui/bubble.png", 55, 55, 55, 95)
define bubble.thoughtframe = Frame("gui/thoughtbubble.png", 55, 55, 55, 55)

define bubble.properties = {
    "bottom_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "bottom_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "top_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "top_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "thought" : {
        "window_background" : bubble.thoughtframe,
    }
}

define bubble.expand_area = {
    "bottom_left" : (0, 0, 0, 22),
    "bottom_right" : (0, 0, 0, 22),
    "top_left" : (0, 22, 0, 0),
    "top_right" : (0, 22, 0, 0),
    "thought" : (0, 0, 0, 0),
}



################################################################################
## 移动设备界面
################################################################################

style pref_vbox:
    variant "medium"
    xsize 675

## 触屏设备也使用上面的自定义快捷菜单，由 OPTIONS → 基本设置 →
## 快捷菜单（不显示 / 触控 / 传统风格）控制。这里不要再定义
## variant "touch" 的 quick_menu，否则会覆盖玩家的选择。

style window:
    variant "small"
    background "gui/phone/textbox.png"

style radio_button:
    variant "small"
    foreground "gui/phone/button/radio_[prefix_]foreground.png"

style check_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 510

style game_menu_content_frame:
    variant "small"
    top_margin 0

style game_menu_viewport:
    variant "small"
    xsize 1305

style pref_vbox:
    variant "small"
    xsize 600

style bar:
    variant "small"
    ysize gui.bar_size
    left_bar Frame("gui/phone/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/phone/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    variant "small"
    xsize gui.bar_size
    top_bar Frame("gui/phone/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/phone/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    variant "small"
    ysize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    variant "small"
    xsize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    variant "small"
    ysize gui.slider_size
    base_bar Frame("gui/phone/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/horizontal_[prefix_]thumb.png"

style vslider:
    variant "small"
    xsize gui.slider_size
    base_bar Frame("gui/phone/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/vertical_[prefix_]thumb.png"

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 900
