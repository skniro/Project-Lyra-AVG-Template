# ==============================================================================
# MEMORIES 场景回想 / 回放系统 (Template-Owned)
# ==============================================================================
# 项目在 game/project/00_project_config.rpy 中配置 PROJECT_MEMORIES：
#   {
#       "id": "mem_ch1_01",
#       "group": _("第一章"),
#       "title": _("海滨站台的声声风铃"),
#       "desc": _("初到夕凪町的雨夜。"),
#       "label": "ch1_sec001",
#       "thumb": "images/backgrounds/station.png",  # 支持 PNG / .svg / 内联 <svg>
#       "unlock_flag": None,                        # 可选；留空时自动检测 renpy.seen_label(label)
#   }

init python:

    def unlock_memory(mem_id):
        """手动解锁指定回想节点。"""
        if not isinstance(getattr(persistent, "_unlocked_memories", None), set):
            persistent._unlocked_memories = set()
        persistent._unlocked_memories.add(mem_id)

    def unlock_all_memories():
        for item in PROJECT_MEMORIES:
            unlock_memory(item.get("id", ""))

    def is_memory_unlocked(item):
        mid = item.get("id", "")
        manual = getattr(persistent, "_unlocked_memories", None)
        if isinstance(manual, set) and mid in manual:
            return True
        flag = item.get("unlock_flag")
        if flag and getattr(persistent, flag, False):
            return True
        lbl = item.get("label")
        if lbl and renpy.has_label(lbl) and renpy.seen_label(lbl):
            return True
        return False

    def get_memory_groups():
        groups = []
        for item in PROJECT_MEMORIES:
            g = item.get("group") or _("全部")
            if g not in groups:
                groups.append(g)
        return groups

    def get_memory_stats():
        total = len(PROJECT_MEMORIES)
        unlocked = sum(1 for item in PROJECT_MEMORIES if is_memory_unlocked(item))
        pct = int(round(100.0 * unlocked / max(1, total))) if total > 0 else 0
        return {"unlocked": unlocked, "total": total, "pct": pct}


screen memories():

    tag menu

    default mem_group = None
    default mem_page = 0

    $ _groups = get_memory_groups()
    $ _filtered = [
        item for item in PROJECT_MEMORIES
        if (mem_group is None) or ((item.get("group") or _("全部")) == mem_group)
    ]
    $ _per_page = 8
    $ _total_pages = max(1, (len(_filtered) + _per_page - 1) // _per_page)
    $ _cur_page = min(mem_page, _total_pages - 1)
    $ _page_items = _filtered[_cur_page * _per_page : (_cur_page + 1) * _per_page]
    $ _stats = get_memory_stats()

    add "gui/extras_bg.png"
    text _("MEMORIES") style "extras_heading_text" xpos 64 ypos 22

    hbox:
        xalign 1.0
        xoffset -64
        ypos 26
        spacing 16

        text (__("已收录  %d / %d") % (_stats["unlocked"], _stats["total"])) style "extras_meta_text" yalign 0.5
        add svg_progress_ring(_stats["pct"], size=58) yalign 0.5

    if _groups:
        hbox:
            xpos 64
            ypos 108
            spacing 14

            textbutton _("全部"):
                action [SetScreenVariable("mem_group", None), SetScreenVariable("mem_page", 0)]
                style "options_segment"
                selected (mem_group is None)

            for _g in _groups:
                textbutton _g:
                    action [SetScreenVariable("mem_group", _g), SetScreenVariable("mem_page", 0)]
                    style "options_segment"
                    selected (mem_group == _g)

    if _page_items:
        grid 4 2:
            xalign 0.5
            ypos 205
            spacing 24

            for item in _page_items:
                $ _ok = is_memory_unlocked(item)
                $ _lbl = item.get("label")
                $ _thumb = item.get("thumb")

                vbox:
                    xsize 370
                    ysize 315
                    spacing 8

                    if _ok and _lbl and renpy.has_label(_lbl):
                        button:
                            style "mem_card_button"
                            action Replay(_lbl)

                            vbox:
                                spacing 8
                                if _thumb and (is_inline_svg(_thumb) or renpy.loadable(_thumb)):
                                    add render_visual(_thumb, default_size=(346, 194)) xysize (346, 194)
                                else:
                                    frame:
                                        style "extras_locked_frame"
                                        xsize 346
                                        ysize 194
                                        text "REPLAY" xalign 0.5 yalign 0.5 color "#7FC8C0" size 26

                                text item.get("title", "") style "mem_card_title"
                                if item.get("desc"):
                                    text item["desc"] style "mem_card_desc"
                    else:
                        frame:
                            style "mem_card_locked"
                            vbox:
                                spacing 8
                                frame:
                                    style "extras_locked_frame"
                                    xsize 346
                                    ysize 194
                                    text _("未解锁") xalign 0.5 yalign 0.5 color "#7FC8C0" size 22
                                text _("？？？") style "mem_card_title"

            for _ in range(_per_page - len(_page_items)):
                frame:
                    style "mem_card_locked"
                    frame:
                        style "extras_locked_frame"
                        xsize 346
                        ysize 194
                        text "—" xalign 0.5 yalign 0.5 color "#7FC8C066" size 30
    else:
        frame:
            style "extras_music_panel_frame"
            xalign 0.5
            ypos 205
            xsize 1680
            ysize 688
            text _("暂无已收录的场景回想") style "extras_meta_text" xalign 0.5 yalign 0.5

    if _total_pages > 1:
        hbox:
            xalign 0.5
            yalign 1.0
            yoffset -44
            spacing 16

            textbutton "‹":
                action SetScreenVariable("mem_page", max(0, _cur_page - 1))
                style "extras_back_button"
                sensitive (_cur_page > 0)

            for p in range(_total_pages):
                textbutton str(p + 1):
                    action SetScreenVariable("mem_page", p)
                    style "manual_page_button"
                    selected (_cur_page == p)

            textbutton "›":
                action SetScreenVariable("mem_page", min(_total_pages - 1, _cur_page + 1))
                style "extras_back_button"
                sensitive (_cur_page < _total_pages - 1)

    text _("点击已解锁场景即可进入独立回想") style "extras_hint_text" xpos 64 yalign 1.0 yoffset -44
    textbutton _("返回") action (ShowMenu("main_menu") if main_menu else ShowMenu("extras")) style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -64 yoffset -44
    key "game_menu" action (ShowMenu("main_menu") if main_menu else ShowMenu("extras"))


style mem_card_button:
    background "#0D272CE0"
    hover_background "#174A4EEE"
    xsize 370
    ysize 305
    padding (12, 12)

style mem_card_locked:
    background "#07181BCC"
    xsize 370
    ysize 305
    padding (12, 12)

style mem_card_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 20
    color "#F4F1E8"

style mem_card_desc:
    font gui.text_font
    size 15
    color "#9FB6C0"
