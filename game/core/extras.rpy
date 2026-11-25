# ==============================================================================
# 鉴赏中心：CG 画廊(支持差分) / 音乐室(支持播控) / MEMORIES / CHART / ACHIEVEMENT
# (Template-Owned)
# ==============================================================================

init python:

    import random

    cg_entries = []
    music_tracks = []
    _music_current_index = -1
    _music_paused = False
    _music_play_mode = "list"   # "list" | "single" | "shuffle"

    def _cg_fields(entry):
        if isinstance(entry, dict):
            cid = entry.get("id", "")
            title = entry.get("title", cid)
            variants = entry.get("variants") or ([entry["file"]] if entry.get("file") else [])
            tag = entry.get("tag", cid)
            return cid, title, variants, tag
        cid, title, filename, tag = entry
        variants = list(filename) if isinstance(filename, (list, tuple)) else [filename]
        return cid, title, variants, tag

    def _cg_persistent_key(cid):
        if cid.startswith("CG") and len(cid) > 2:
            return "cg_" + cid[2:]
        return "cg_" + cid

    def is_cg_unlocked(cid):
        return bool(getattr(persistent, _cg_persistent_key(cid), False))

    def unlock_cg(cid):
        setattr(persistent, _cg_persistent_key(cid), True)

    def unlock_all_extras():
        """开发/测试辅助：一键解锁全部 CG、音乐、回想与流程图节点。"""
        for entry in cg_entries:
            cid, _title, _vars, _tag = _cg_fields(entry)
            unlock_cg(cid)
        for index in range(len(music_tracks)):
            mark_music(index)
        unlock_all_memories()
        if isinstance(PROJECT_FLOWCHART, dict):
            for n in PROJECT_FLOWCHART.get("nodes", []):
                unlock_flowchart_node(n.get("id", ""))

    def _resolve_cg_path(filename):
        if is_inline_svg(filename):
            return filename
        norm = filename.replace("\\", "/")
        if "/" in norm:
            return norm
        return "images/CG/" + norm

    def _cg_is_loadable(path):
        if is_inline_svg(path):
            return True
        return renpy.loadable(path)

    def unlock_seen_cgs():
        """当指定 tag 的 CG 正在屏幕显示时自动解锁。"""
        for entry in cg_entries:
            cid, _title, _vars, tag = _cg_fields(entry)
            if tag and renpy.showing(tag):
                unlock_cg(cid)

    def _track_fields(entry):
        if isinstance(entry, dict):
            return entry.get("title", ""), entry.get("path", ""), entry.get("artist", "")
        if len(entry) >= 3:
            return entry[0], entry[1], entry[2]
        return entry[0], entry[1], ""

    def _track_matches(playing, path):
        if not playing or not path:
            return False
        p_play = playing.replace("\\", "/")
        p_track = path.replace("\\", "/")
        return p_play == p_track or p_play.rsplit("/", 1)[-1] == p_track.rsplit("/", 1)[-1]

    def mark_music(index):
        setattr(persistent, "music_%02d" % (index + 1), True)

    def play_music_index(index):
        """点击或切歌：立即播放并标记为已收听。"""
        global _music_current_index, _music_paused
        if not music_tracks:
            return
        index = index % len(music_tracks)
        title, path, artist = _track_fields(music_tracks[index])
        loop_single = (_music_play_mode == "single")
        renpy.music.set_pause(False, channel="music")
        renpy.music.play(path, channel="music", loop=loop_single)
        _music_current_index = index
        _music_paused = False
        mark_music(index)

    def toggle_music_pause():
        global _music_paused
        if not renpy.music.get_playing("music"):
            if music_tracks:
                idx = _music_current_index if 0 <= _music_current_index < len(music_tracks) else 0
                play_music_index(idx)
            return
        _music_paused = not _music_paused
        renpy.music.set_pause(_music_paused, channel="music")

    def stop_music_room():
        global _music_paused
        _music_paused = False
        renpy.music.set_pause(False, channel="music")
        renpy.music.stop(channel="music")

    def play_next_music(step=1):
        if not music_tracks:
            return
        if _music_play_mode == "shuffle" and len(music_tracks) > 1:
            choices = [i for i in range(len(music_tracks)) if i != _music_current_index]
            play_music_index(random.choice(choices))
            return
        base = _music_current_index if _music_current_index >= 0 else (0 if step > 0 else 1)
        play_music_index((base + step) % len(music_tracks))

    def cycle_music_mode():
        global _music_play_mode
        order = ("list", "single", "shuffle")
        _music_play_mode = order[(order.index(_music_play_mode) + 1) % len(order)]
        # 若正在播放且切换为单曲循环或列表模式，刷新当前曲目 loop 状态。
        playing = renpy.music.get_playing("music")
        if playing and 0 <= _music_current_index < len(music_tracks):
            _t, path, _a = _track_fields(music_tracks[_music_current_index])
            if _track_matches(playing, path):
                renpy.music.queue(path, channel="music", loop=(_music_play_mode == "single"))

    def _music_mode_label():
        if _music_play_mode == "single":
            return _("单曲循环")
        if _music_play_mode == "shuffle":
            return _("随机播放")
        return _("顺序循环")

    def _music_auto_advance_tick():
        if _music_play_mode == "single" or _music_paused or not music_tracks:
            return
        if _music_current_index >= 0 and not renpy.music.get_playing("music"):
            play_next_music(1)

    def unlock_heard_music():
        """在剧情播放 BGM 时同步记录到音乐鉴赏解锁状态。"""
        playing = renpy.music.get_playing("music")
        if not playing:
            return
        for index, entry in enumerate(music_tracks):
            _t, path, _a = _track_fields(entry)
            if _track_matches(playing, path):
                mark_music(index)

    def get_game_completion_stats():
        """汇总 CG、BGM、回想、流程图与成就总体收集统计。"""
        cg_unlocked = sum(1 for e in cg_entries if is_cg_unlocked(_cg_fields(e)[0]))
        cg_total = len(cg_entries)
        music_heard = sum(1 for i in range(len(music_tracks)) if getattr(persistent, "music_%02d" % (i + 1), False))
        music_total = len(music_tracks)
        mem = get_memory_stats()
        fc = get_flowchart_stats()
        ach = get_achievement_stats()

        total_items = cg_total + music_total + mem["total"] + fc["total"] + ach["total"]
        done_items = cg_unlocked + music_heard + mem["unlocked"] + fc["unlocked"] + ach["unlocked"]
        overall_pct = int(round(100.0 * done_items / max(1, total_items))) if total_items > 0 else 0
        cg_pct = int(round(100.0 * cg_unlocked / max(1, cg_total))) if cg_total > 0 else 0
        music_pct = int(round(100.0 * music_heard / max(1, music_total))) if music_total > 0 else 0
        return {
            "cg_unlocked": cg_unlocked,
            "cg_total": cg_total,
            "cg_pct": cg_pct,
            "music_heard": music_heard,
            "music_total": music_total,
            "music_pct": music_pct,
            "mem_unlocked": mem["unlocked"],
            "mem_total": mem["total"],
            "chart_unlocked": fc["unlocked"],
            "chart_total": fc["total"],
            "ach_unlocked": ach["unlocked"],
            "ach_total": ach["total"],
            "overall_pct": overall_pct,
        }

    config.start_interact_callbacks.append(unlock_seen_cgs)
    config.start_interact_callbacks.append(unlock_heard_music)


## 鉴赏入口（SPRB RECORD Hub） #################################################

screen extras():
    tag menu

    $ _stats = get_game_completion_stats()
    $ _has_extra_cards = bool(PROJECT_EXTRA_CARDS)

    add "gui/extras_bg.png"
    text _("EXTRAS") style "extras_heading_text" xpos 64 ypos 22

    hbox:
        xalign 1.0
        xoffset -64
        ypos 26
        spacing 16

        if is_steam_active():
            text _("Steam 已连接") style "extras_meta_text" yalign 0.5
        text _("旅途中收集到的画面、旋律与记忆") style "extras_meta_text" yalign 0.5
        add svg_progress_ring(_stats["overall_pct"], size=58) yalign 0.5

    vbox:
        xalign 0.5
        yalign 0.52
        spacing 30

        hbox:
            xalign 0.5
            spacing 56

            button:
                style "extras_card_button"
                action ShowMenu("cg_gallery")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 10
                    text _("GALLERY") style "extras_card_title"
                    text (__("CG 鉴赏  %d / %d") % (_stats["cg_unlocked"], _stats["cg_total"])) style "extras_card_sub"
                    text _("点击进入") style "extras_hint_text"

            button:
                style "extras_card_button"
                action ShowMenu("music_room")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 10
                    text _("MUSIC") style "extras_card_title"
                    text (__("音乐鉴赏  %d 首") % _stats["music_total"]) style "extras_card_sub"
                    text _("点击进入") style "extras_hint_text"

        hbox:
            xalign 0.5
            spacing 32

            button:
                style "extras_subcard_button"
                action ShowMenu("memories")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 6
                    text _("MEMORIES") style "extras_subcard_title" xalign 0.5
                    text (__("场景回想  %d / %d") % (_stats["mem_unlocked"], _stats["mem_total"])) style "extras_card_sub"

            button:
                style "extras_subcard_button"
                action ShowMenu("flowchart")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 6
                    text _("CHART") style "extras_subcard_title" xalign 0.5
                    text (__("剧情流程  %d / %d") % (_stats["chart_unlocked"], _stats["chart_total"])) style "extras_card_sub"

            button:
                style "extras_subcard_button"
                action ShowMenu("achievements")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 6
                    text _("ACHIEVEMENT") style "extras_subcard_title" xalign 0.5
                    text (__("成就记录  %d / %d") % (_stats["ach_unlocked"], _stats["ach_total"])) style "extras_card_sub"

        if _has_extra_cards:
            hbox:
                xalign 0.5
                spacing 32

                for _card in PROJECT_EXTRA_CARDS:
                    button:
                        style "extras_subcard_button"
                        action _card["action"]
                        hbox:
                            xalign 0.5
                            yalign 0.5
                            spacing 18

                            if _card.get("visual"):
                                add render_visual(_card["visual"], default_size=(58, 58)) yalign 0.5

                            vbox:
                                yalign 0.5
                                spacing 6
                                text _card.get("title", "") style "extras_subcard_title"
                                if _card.get("sub"):
                                    text _card["sub"] style "extras_card_sub"

    textbutton _("返回") action Return() style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -64 yoffset -44
    key "game_menu" action Return()


## CG 鉴赏（支持自动分页、差分与 SVG 插画） ####################################

screen cg_gallery():
    tag menu

    default cg_page = 0
    $ _per_page = 12
    $ _total_pages = max(1, (len(cg_entries) + _per_page - 1) // _per_page)
    $ _cur_page = min(cg_page, _total_pages - 1)
    $ _page_items = cg_entries[_cur_page * _per_page : (_cur_page + 1) * _per_page]

    $ _stats = get_game_completion_stats()

    add "gui/extras_bg.png"
    text _("GALLERY") style "extras_heading_text" xpos 64 ypos 22
    text (__("完成度  %d%%") % _stats["cg_pct"]) style "extras_meta_text" xalign 1.0 xoffset -64 ypos 40

    grid 4 3:
        xalign 0.5
        ypos 160
        spacing 20

        for entry in _page_items:
            $ cid, title, variants, tag = _cg_fields(entry)
            $ resolved_list = [_resolve_cg_path(v) for v in variants]
            $ first_path = resolved_list[0] if resolved_list else ""
            vbox:
                xsize 340
                ysize 226
                spacing 6
                $ is_unlocked = is_cg_unlocked(cid)
                if is_unlocked and first_path and _cg_is_loadable(first_path):
                    button:
                        style "extras_thumb_button"
                        action Show("cg_view", variants=resolved_list, title=title)
                        add render_visual(first_path, default_size=(340, 191)) xysize (340, 191)
                else:
                    frame:
                        style "extras_locked_frame"
                        text (_("待生成") if is_unlocked else _("未解锁")):
                            xalign 0.5
                            yalign 0.5
                            color "#7FC8C0"
                            size 22
                text (_("%s (%d张)") % (_(title), len(resolved_list)) if len(resolved_list) > 1 else _(title)) style "extras_thumb_title"

        for i in range(_per_page - len(_page_items)):
            vbox:
                xsize 340
                ysize 226
                spacing 6
                frame:
                    style "extras_locked_frame"
                    text "—":
                        xalign 0.5
                        yalign 0.5
                        color "#7FC8C066"
                        size 30
                null height 24

    if _total_pages > 1:
        hbox:
            xalign 0.5
            yalign 1.0
            yoffset -44
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

    text _("点击缩略图全屏查看") style "extras_hint_text" xpos 64 yalign 1.0 yoffset -44
    textbutton _("返回") action (ShowMenu("main_menu") if main_menu else ShowMenu("extras")) style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -64 yoffset -44
    key "game_menu" action (ShowMenu("main_menu") if main_menu else ShowMenu("extras"))


## 音乐鉴赏（支持播控条、循环模式、作者署名与滚动列表） ###########################

screen music_room():
    tag menu

    $ playing = renpy.music.get_playing("music")
    $ _cur_entry = next((e for e in music_tracks if _track_matches(playing, _track_fields(e)[1])), None)
    $ _cur_title, _cur_path, _cur_artist = _track_fields(_cur_entry) if _cur_entry else ("", "", "")
    $ _stats = get_game_completion_stats()

    timer 0.4 repeat True action Function(_music_auto_advance_tick)

    add "gui/extras_bg.png"
    text _("MUSIC") style "extras_heading_text" xpos 64 ypos 22
    text (__("完成度  %d%%") % _stats["music_pct"]) style "extras_meta_text" xalign 1.0 xoffset -64 ypos 40

    frame:
        style "extras_now_frame"
        xalign 0.5
        ypos 124
        xsize 1680
        ysize 92

        hbox:
            xfill True
            yalign 0.5

            hbox:
                spacing 16
                yalign 0.5

                add "gui/icon_music.png" yalign 0.5
                text (_cur_title if _cur_title else _("未播放")) style "extras_now_title"
                if _cur_artist:
                    text ("- " + _cur_artist) style "extras_now_sub"
                else:
                    text PROJECT_MUSIC_SUBTITLE style "extras_now_sub"

            hbox:
                xalign 1.0
                yalign 0.5
                spacing 14

                textbutton "⏮" action Function(play_next_music, -1) style "extras_ctrl_button"
                textbutton ("▶" if _music_paused or not playing else "⏸") action Function(toggle_music_pause) style "extras_ctrl_button"
                textbutton "⏹" action Function(stop_music_room) style "extras_ctrl_button"
                textbutton "⏭" action Function(play_next_music, 1) style "extras_ctrl_button"
                textbutton _music_mode_label() action Function(cycle_music_mode) style "extras_mode_button"

    frame:
        style "extras_music_panel_frame"
        xalign 0.5
        ypos 232
        xsize 1680
        ysize 688

        if music_tracks:
            $ _mid = (len(music_tracks) + 1) // 2
            viewport:
                xfill True
                yfill True
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
            text _("暂无已收录的音乐") style "extras_meta_text" xalign 0.5 yalign 0.5

    text _("点击曲目立即播放，可切换顺序 / 单曲 / 随机模式") style "extras_hint_text" xpos 64 yalign 1.0 yoffset -44

    hbox:
        xalign 1.0
        yalign 1.0
        xoffset -64
        yoffset -44
        spacing 28

        textbutton _("停止播放") action Function(stop_music_room) style "extras_back_button"
        textbutton _("返回") action (ShowMenu("main_menu") if main_menu else ShowMenu("extras")) style "extras_back_button"

    key "game_menu" action (ShowMenu("main_menu") if main_menu else ShowMenu("extras"))


screen music_row(i):

    $ title, path, artist = _track_fields(music_tracks[i])
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
            if artist:
                text artist:
                    style "extras_music_artist"
            if is_playing:
                add "gui/icon_music.png" xysize (22, 22) yalign 0.5


## CG 全屏查看（支持多差分切换） ################################################

screen cg_view(variants, title=""):
    modal True
    zorder 200

    default var_idx = 0
    default show_hud = True

    $ _vlist = variants if isinstance(variants, (list, tuple)) else [variants]
    $ _idx = min(var_idx, max(0, len(_vlist) - 1))
    $ _img = _vlist[_idx] if _vlist else ""

    add Solid("#000000")
    if _img:
        add render_visual(_img, default_size=(1920, 1080)) xalign 0.5 yalign 0.5 xysize (1920, 1080)

    button:
        xfill True
        yfill True
        background None
        hover_background None
        action (SetScreenVariable("var_idx", _idx + 1) if _idx + 1 < len(_vlist) else Hide("cg_view"))

    if show_hud:
        $ _hint_text = (
            (_("%s  [%d / %d]  ·  点击切换差分 / 右键退出") % (title, _idx + 1, len(_vlist)))
            if len(_vlist) > 1
            else _("点击任意处返回")
        )
        text _hint_text:
            xalign 0.5
            yalign 0.96
            size 20
            color "#B9CBD3"
            outlines [(2, "#000000", 0, 0)]

    if len(_vlist) > 1:
        key "K_LEFT" action SetScreenVariable("var_idx", (_idx - 1) % len(_vlist))
        key "K_RIGHT" action SetScreenVariable("var_idx", (_idx + 1) % len(_vlist))
    key "K_h" action ToggleScreenVariable("show_hud")
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
    ysize 260
    padding (40, 26)

style extras_subcard_button:
    background Frame("gui/extras_panel.png", 44, 44)
    hover_background Frame("gui/extras_panel_hover.png", 44, 44)
    xsize 390
    ysize 168
    padding (28, 20)

style extras_subcard_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 34
    color "#7FC8C0"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]

style extras_card_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 52
    color "#7FC8C0"
    hover_color "#F2C77E"
    outlines [(2, "#061416", 0, 0)]
    xalign 0.5

style extras_card_sub:
    font gui.text_font
    size 23
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

style extras_ctrl_button:
    background "#0B2428CC"
    hover_background "#174A4EEE"
    padding (12, 6)

style extras_ctrl_button_text:
    font gui.text_font
    size 22
    color "#F4F1E8"
    hover_color "#F2C77E"

style extras_mode_button:
    background "#0B2428CC"
    hover_background "#174A4EEE"
    padding (16, 6)

style extras_mode_button_text:
    font gui.text_font
    size 20
    color "#7FC8C0"
    hover_color "#F2C77E"

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

style extras_music_panel_frame:
    background Frame("gui/extras_panel.png", 44, 44)
    padding (48, 30)

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

style extras_music_artist:
    font gui.text_font
    size 17
    color "#9FB6C0"
    yalign 0.5
