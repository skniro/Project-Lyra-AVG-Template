# ==============================================================================
# 鉴赏界面：CG 画廊 / 音乐室 (Template-Owned)
# ==============================================================================
# 数据由 game/project/00_project_config.rpy 中的 PROJECT_CG_ENTRIES / PROJECT_MUSIC_TRACKS 提供。

init python:

    cg_entries = []
    music_tracks = []

    def _cg_persistent_key(cid):
        if cid.startswith("CG") and len(cid) > 2:
            return "cg_" + cid[2:]
        return "cg_" + cid

    def is_cg_unlocked(cid):
        return bool(getattr(persistent, _cg_persistent_key(cid), False))

    def unlock_cg(cid):
        setattr(persistent, _cg_persistent_key(cid), True)

    def _resolve_cg_path(filename):
        norm = filename.replace("\\", "/")
        if "/" in norm:
            return norm
        return "images/CG/" + norm

    def unlock_seen_cgs():
        """当指定 tag 的 CG 正在屏幕显示时自动解锁。"""
        for cid, title, filename, tag in cg_entries:
            if renpy.showing(tag):
                unlock_cg(cid)

    def _track_matches(playing, path):
        if not playing or not path:
            return False
        p_play = playing.replace("\\", "/")
        p_track = path.replace("\\", "/")
        return p_play == p_track or p_play.rsplit("/", 1)[-1] == p_track.rsplit("/", 1)[-1]

    def mark_music(index):
        setattr(persistent, "music_%02d" % (index + 1), True)

    def play_music_index(index):
        """点击曲目：立即播放并标记为已收听。"""
        title, path = music_tracks[index]
        renpy.music.play(path, channel="music", loop=True)
        mark_music(index)

    def unlock_heard_music():
        """在剧情播放 BGM 时同步记录到音乐鉴赏解锁状态。"""
        playing = renpy.music.get_playing("music")
        if not playing:
            return
        for index, (title, path) in enumerate(music_tracks):
            if _track_matches(playing, path):
                mark_music(index)

    config.start_interact_callbacks.append(unlock_seen_cgs)
    config.start_interact_callbacks.append(unlock_heard_music)


## 鉴赏入口 #####################################################################

screen extras():
    tag menu

    $ unlocked = sum(1 for cid, title, filename, tag in cg_entries if is_cg_unlocked(cid))

    add "gui/extras_bg.png"
    text _("EXTRAS") style "extras_heading_text" xpos 64 ypos 22
    text _("旅途中收集到的画面与旋律") style "extras_meta_text" xalign 1.0 xoffset -64 ypos 40

    hbox:
        xalign 0.5
        yalign 0.53
        spacing 64

        button:
            style "extras_card_button"
            action ShowMenu("cg_gallery")
            vbox:
                xalign 0.5
                yalign 0.5
                spacing 8
                text _("GALLERY") style "extras_card_title"
                text (__("CG 鉴赏  %d / %d") % (unlocked, len(cg_entries))) style "extras_card_sub"
                text _("点击进入") style "extras_hint_text"

        button:
            style "extras_card_button"
            action ShowMenu("music_room")
            vbox:
                xalign 0.5
                yalign 0.5
                spacing 8
                text _("MUSIC") style "extras_card_title"
                text (__("音乐鉴赏  %d 首") % len(music_tracks)) style "extras_card_sub"
                text _("点击进入") style "extras_hint_text"

    textbutton _("返回") action Return() style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -64 yoffset -36
    key "game_menu" action Return()


## CG 鉴赏（支持自动分页） ######################################################

screen cg_gallery():
    tag menu

    default cg_page = 0
    $ _per_page = 12
    $ _total_pages = max(1, (len(cg_entries) + _per_page - 1) // _per_page)
    $ _cur_page = min(cg_page, _total_pages - 1)
    $ _page_items = cg_entries[_cur_page * _per_page : (_cur_page + 1) * _per_page]

    $ unlocked = sum(1 for cid, title, filename, tag in cg_entries if is_cg_unlocked(cid))
    $ pct = int(round(100.0 * unlocked / max(1, len(cg_entries))))

    add "gui/extras_bg.png"
    text _("GALLERY") style "extras_heading_text" xpos 64 ypos 22
    text (__("完成度  %d%%") % pct) style "extras_meta_text" xalign 1.0 xoffset -64 ypos 40

    grid 4 3:
        xalign 0.5
        ypos 165
        spacing 20

        for cid, title, filename, tag in _page_items:
            vbox:
                spacing 6
                $ is_unlocked = is_cg_unlocked(cid)
                $ path = _resolve_cg_path(filename)
                if is_unlocked and renpy.loadable(path):
                    button:
                        style "extras_thumb_button"
                        action Show("cg_view", image=path)
                        add path xysize (340, 191)
                else:
                    frame:
                        style "extras_locked_frame"
                        text (_("待生成") if is_unlocked else _("未解锁")):
                            xalign 0.5
                            yalign 0.5
                            color "#7FC8C0"
                            size 22
                text _(title) style "extras_thumb_title"

        for i in range(_per_page - len(_page_items)):
            frame:
                style "extras_locked_frame"
                text "—":
                    xalign 0.5
                    yalign 0.5
                    color "#7FC8C066"
                    size 30

    if _total_pages > 1:
        hbox:
            xalign 0.5
            yalign 1.0
            yoffset -36
            spacing 16

            textbutton "‹":
                action SetScreenVariable("cg_page", max(0, _cur_page - 1))
                style "extras_back_button"
                sensitive (_cur_page > 0)

            for p in range(_total_pages):
                textbutton str(p + 1):
                    action SetScreenVariable("cg_page", p)
                    style "manual_page_button"
                    selected (_cur_page == p)

            textbutton "›":
                action SetScreenVariable("cg_page", min(_total_pages - 1, _cur_page + 1))
                style "extras_back_button"
                sensitive (_cur_page < _total_pages - 1)

    text _("点击缩略图全屏查看") style "extras_hint_text" xpos 64 yalign 1.0 yoffset -46
    textbutton _("返回") action (ShowMenu("main_menu") if main_menu else ShowMenu("extras")) style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -64 yoffset -36
    key "game_menu" action (ShowMenu("main_menu") if main_menu else ShowMenu("extras"))


## 音乐鉴赏（支持滚动列表） #####################################################

screen music_room():
    tag menu

    $ playing = renpy.music.get_playing("music")
    $ current = next((t for t, p in music_tracks if _track_matches(playing, p)), None)
    $ heard = sum(1 for i in range(len(music_tracks))
                  if getattr(persistent, "music_%02d" % (i + 1), False))
    $ pct = int(round(100.0 * heard / max(1, len(music_tracks))))

    add "gui/extras_bg.png"
    text _("MUSIC") style "extras_heading_text" xpos 64 ypos 22
    text (__("完成度  %d%%") % pct) style "extras_meta_text" xalign 1.0 xoffset -64 ypos 40

    frame:
        style "extras_now_frame"
        xalign 0.5
        ypos 128
        xsize 1680
        ysize 86

        hbox:
            spacing 16
            yalign 0.5

            add "gui/icon_music.png" yalign 0.5
            text (current if current else _("未播放")) style "extras_now_title"
            text PROJECT_MUSIC_SUBTITLE style "extras_now_sub"

    add "gui/extras_panel.png" xalign 0.5 ypos 235

    if music_tracks:
        $ _mid = (len(music_tracks) + 1) // 2
        viewport:
            xalign 0.5
            ypos 264
            xsize 1560
            ysize 640
            scrollbars "vertical"
            mousewheel True
            draggable True

            hbox:
                xalign 0.5
                spacing 56

                vbox:
                    spacing 2
                    for i in range(0, _mid):
                        use music_row(i)

                vbox:
                    spacing 2
                    for i in range(_mid, len(music_tracks)):
                        use music_row(i)
    else:
        text _("暂无已收录的音乐") style "extras_meta_text" xalign 0.5 ypos 420

    text _("点击曲目立即播放，自动循环") style "extras_hint_text" xpos 64 yalign 1.0 yoffset -46
    textbutton _("停止播放") action Stop("music") style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -220 yoffset -36
    textbutton _("返回") action (ShowMenu("main_menu") if main_menu else ShowMenu("extras")) style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -64 yoffset -36
    key "game_menu" action (ShowMenu("main_menu") if main_menu else ShowMenu("extras"))


screen music_row(i):

    $ title, path = music_tracks[i]
    $ is_playing = _track_matches(renpy.music.get_playing("music"), path)

    button:
        style "extras_music_row"
        action Function(play_music_index, i)

        hbox:
            spacing 14
            yalign 0.5

            text ("%02d" % (i + 1)):
                style "extras_music_num"
                color ("#F2C77E" if is_playing else "#7A8C93")
            text title:
                style "extras_music_title"
                color ("#F2C77E" if is_playing else "#F4F1E8")
            if is_playing:
                add "gui/icon_music.png" xysize (22, 22) yalign 0.5


## CG 全屏查看 #################################################################

screen cg_view(image):
    modal True
    zorder 200

    add Solid("#000000")
    add image xalign 0.5 yalign 0.5 xysize (1920, 1080)

    text _("点击任意处返回"):
        xalign 0.5
        yalign 0.98
        size 20
        color "#B9CBD3"
        outlines [(2, "#000000", 0, 0)]

    button:
        xfill True
        yfill True
        background None
        hover_background None
        action Hide("cg_view")

    key "game_menu" action Hide("cg_view")


## 样式 #########################################################################

style extras_heading_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 58
    color "#F4F1E8"
    outlines [(3, "#061416", 0, 0)]

style extras_meta_text:
    font gui.text_font
    size 24
    color "#D7E6E6"
    outlines [(2, "#061416", 0, 0)]

style extras_hint_text:
    font gui.text_font
    size 19
    color "#B9CBD3"
    outlines [(2, "#061416", 0, 0)]

style extras_card_button:
    background Frame("gui/extras_panel.png", 44, 44)
    hover_background Frame("gui/extras_panel_hover.png", 44, 44)
    xsize 560
    ysize 300
    padding (40, 30)

style extras_card_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 54
    color "#7FC8C0"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]
    xalign 0.5

style extras_card_sub:
    font gui.text_font
    size 24
    color "#F4F1E8"
    xalign 0.5

style extras_back_button:
    background None
    hover_background None
    padding (10, 6)

style extras_back_button_text:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 26
    color "#7FC8C0"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style extras_thumb_button:
    background None
    hover_background None
    padding (0, 0)

style extras_locked_frame:
    background "#0B2428DD"
    xsize 340
    ysize 191
    padding (0, 0)

style extras_thumb_title:
    font gui.text_font
    size 17
    color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]
    xalign 0.5

style extras_now_frame:
    background Frame("gui/extras_panel.png", 44, 44)
    padding (28, 10)

style extras_now_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 30
    color "#F4F1E8"
    yalign 0.5

style extras_now_sub:
    font gui.text_font
    size 20
    color "#B9CBD3"
    yalign 0.5

style extras_music_row:
    xsize 720
    background None
    hover_background "#7FC8C022"
    padding (14, 8)

style extras_music_num:
    font gui.text_font
    size 19
    yalign 0.5
    min_width 34

style extras_music_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 24
    yalign 0.5
