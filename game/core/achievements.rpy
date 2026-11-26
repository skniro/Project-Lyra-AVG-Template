# ==============================================================================
# 成就系统 + Steam 成就联动 (Template-Owned)
# ==============================================================================
# 项目在 game/project/00_project_config.rpy 中配置 PROJECT_ACHIEVEMENTS：
#   {
#       "id": "ach_prologue",
#       "steam": "ACH_PROLOGUE",     # 可选，默认同 id
#       "title": _("夏末的起点"),
#       "desc": _("完成序幕并踏入小镇。"),
#       "hidden": False,             # 未解锁时是否隐藏描述
#       "stat_max": None,            # 进度型成就目标值（如 7）
#       "icon": None,                # 支持 PNG / .svg / 内联 <svg>
#   }

init python:

    import datetime

    def _svg_trophy_badge(unlocked=True, size=64):
        fill = "#F2C77E" if unlocked else "#2A4A52"
        ring = "#7FC8C0" if unlocked else "#17343A"
        bg = "#091E22" if unlocked else "#061416"
        markup = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
            '<circle cx="32" cy="32" r="29" fill="{bg}" stroke="{ring}" stroke-width="3"/>'
            '<path d="M21 18h22v10c0 7-5 12-11 12s-11-5-11-12V18z" fill="{fill}"/>'
            '<path d="M21 21h-5c0 6 3 9 6 9v-3c-1.5 0-3-1.5-3-4h2v-2zm22 0h5c0 6-3 9-6 9v-3c1.5 0 3-1.5 3-4h-2v-2z" fill="{fill}"/>'
            '<rect x="29" y="39" width="6" height="7" fill="{fill}"/>'
            '<rect x="23" y="46" width="18" height="4" rx="2" fill="{fill}"/>'
            '</svg>'
        ).format(bg=bg, ring=ring, fill=fill)
        return svg_inline(markup, size=(size, size))

    def _find_achievement(ach_id):
        for item in PROJECT_ACHIEVEMENTS:
            if item.get("id") == ach_id:
                return item
        return None

    def is_achievement_unlocked(ach_id):
        try:
            return bool(achievement.has(ach_id))
        except Exception:
            return False

    def get_achievement_unlock_time(ach_id):
        times = getattr(persistent, "_ach_unlock_times", None)
        if isinstance(times, dict):
            return times.get(ach_id, "")
        return ""

    def grant_achievement(ach_id, show_toast=True):
        """解锁指定成就（自动同步到本地 persistent 与 Steam），并弹出 SPRB 风格提示。"""
        already = is_achievement_unlocked(ach_id)
        try:
            achievement.grant(ach_id)
            achievement.sync()
        except Exception:
            pass

        if not already:
            if not isinstance(getattr(persistent, "_ach_unlock_times", None), dict):
                persistent._ach_unlock_times = {}
            persistent._ach_unlock_times[ach_id] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            item = _find_achievement(ach_id)
            if item:
                steam_timeline_event(_("解锁成就"), item.get("title", ach_id), priority=1)
            if show_toast and PROJECT_SHOW_ACHIEVEMENT_TOAST and getattr(persistent, "achievement_toast", True):
                renpy.show_screen("achievement_toast", ach_id=ach_id)

    def progress_achievement(ach_id, completed):
        """上报进度型成就进度；达到 stat_max 时自动触发解锁与弹窗。"""
        was_unlocked = is_achievement_unlocked(ach_id)
        try:
            achievement.progress(ach_id, completed)
            achievement.sync()
        except Exception:
            pass
        if (not was_unlocked) and is_achievement_unlocked(ach_id):
            grant_achievement(ach_id, show_toast=True)

    def clear_all_local_achievements():
        """开发测试用：清除本地成就记录。"""
        try:
            achievement.clear_all()
            persistent._ach_unlock_times = {}
            achievement.sync()
        except Exception:
            pass

    def get_achievement_stats():
        total = len(PROJECT_ACHIEVEMENTS)
        unlocked = sum(1 for item in PROJECT_ACHIEVEMENTS if is_achievement_unlocked(item.get("id", "")))
        pct = int(round(100.0 * unlocked / max(1, total))) if total > 0 else 0
        return {"unlocked": unlocked, "total": total, "pct": pct}


screen achievement_toast(ach_id):

    zorder 250
    $ _item = _find_achievement(ach_id) or {"title": ach_id, "desc": "", "icon": None}

    frame at achievement_toast_anim:
        style "ach_toast_frame"
        xalign 1.0
        ypos 28
        xoffset -28

        hbox:
            spacing 16
            yalign 0.5

            if _item.get("icon"):
                add render_visual(_item["icon"], default_size=(54, 54)) yalign 0.5
            else:
                add _svg_trophy_badge(True, size=54) yalign 0.5

            vbox:
                spacing 4
                yalign 0.5

                text _("ACHIEVEMENT UNLOCKED") style "ach_toast_label"
                text _item.get("title", ach_id) style "ach_toast_title"
                if _item.get("desc"):
                    text _item["desc"] style "ach_toast_desc"

    timer 3.5 action Hide("achievement_toast")


transform achievement_toast_anim:
    on show:
        xoffset 420 alpha 0.0
        easeout 0.25 xoffset 0 alpha 1.0
    on hide:
        easein 0.25 xoffset 420 alpha 0.0


screen achievements():

    tag menu

    default ach_filter = "all"
    $ _stats = get_achievement_stats()
    $ _steam_on = is_steam_active()
    $ _items = [
        item for item in PROJECT_ACHIEVEMENTS
        if ach_filter == "all"
        or (ach_filter == "unlocked" and is_achievement_unlocked(item.get("id", "")))
        or (ach_filter == "locked" and not is_achievement_unlocked(item.get("id", "")))
    ]

    add "gui/extras_bg.png"

    text _("ACHIEVEMENT") style "extras_heading_text" xpos 64 ypos 22

    hbox:
        xalign 1.0
        xoffset -64
        ypos 26
        spacing 16

        if _steam_on:
            text _("Steam 已连接") style "extras_meta_text" yalign 0.5
        text (__("已解锁  %d / %d") % (_stats["unlocked"], _stats["total"])) style "extras_meta_text" yalign 0.5
        add svg_progress_ring(_stats["pct"], size=58) yalign 0.5

    hbox:
        xpos 64
        ypos 112
        spacing 16

        textbutton _("全部"):
            action SetScreenVariable("ach_filter", "all")
            style "options_segment"
            selected (ach_filter == "all")
        textbutton _("已解锁"):
            action SetScreenVariable("ach_filter", "unlocked")
            style "options_segment"
            selected (ach_filter == "unlocked")
        textbutton _("未解锁"):
            action SetScreenVariable("ach_filter", "locked")
            style "options_segment"
            selected (ach_filter == "locked")

    frame:
        style "extras_music_panel_frame"
        xalign 0.5
        ypos 192
        xsize 1680
        ysize 748

        for _ach_key index _ach_key in [str(ach_filter)]:
            fixed xfill True yfill True at template_tab_swap(dx=0, dy=8, dur=0.20):
                if _items:
                    viewport:
                        xfill True
                        yfill True
                        scrollbars "vertical"
                        mousewheel True
                        draggable True

                        vpgrid:
                            cols 2
                            spacing 20
                            xalign 0.5

                            for item in _items:
                                $ _aid = item.get("id", "")
                                $ _ok = is_achievement_unlocked(_aid)
                                $ _hidden = bool(item.get("hidden", False)) and (not _ok)
                                $ _smax = item.get("stat_max", None)
                                $ _prog = achievement.get_progress(_aid) if _smax else 0
                                $ _utime = get_achievement_unlock_time(_aid) if _ok else ""

                                frame:
                                    style ("ach_card_unlocked" if _ok else "ach_card_locked")
                                    xsize 760
                                    ysize 132

                                    hbox:
                                        spacing 18
                                        yalign 0.5

                                        if _ok and item.get("icon"):
                                            add render_visual(item["icon"], default_size=(72, 72)) yalign 0.5
                                        else:
                                            add _svg_trophy_badge(_ok, size=72) yalign 0.5

                                        vbox:
                                            xsize 600
                                            spacing 4
                                            yalign 0.5

                                            hbox:
                                                xfill True
                                                text (_("？？？") if _hidden else item.get("title", _aid)) style "ach_card_title"
                                                if _utime:
                                                    text _utime style "ach_card_time" xalign 1.0 yalign 0.5

                                            text (_("达成特定条件后解锁") if _hidden else item.get("desc", "")) style "ach_card_desc"

                                            if _smax and not _hidden:
                                                hbox:
                                                    spacing 10
                                                    yalign 0.5
                                                    bar value StaticValue(min(_prog, _smax), _smax) xsize 360 ysize 12 style "ach_progress_bar" yalign 0.5
                                                    text ("%d / %d" % (min(_prog, _smax), _smax)) style "ach_card_time" yalign 0.5
                else:
                    text _("暂无成就记录") style "extras_meta_text" xalign 0.5 yalign 0.5

    if _steam_on:
        textbutton _("Steam 成就面板") action Function(steam_open_overlay, "Achievements") style "extras_back_button" xpos 64 yalign 1.0 yoffset -44

    textbutton _("返回") action (ShowMenu("main_menu") if main_menu else ShowMenu("extras")) style "extras_back_button" xalign 1.0 yalign 1.0 xoffset -64 yoffset -44
    key "game_menu" action (ShowMenu("main_menu") if main_menu else ShowMenu("extras"))


style ach_toast_frame:
    background Frame("gui/extras_panel.png", 44, 44)
    padding (24, 16)
    xminimum 420
    xmaximum 560

style ach_toast_label:
    font gui.text_font
    size 14
    color "#F2C77E"

style ach_toast_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 24
    color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style ach_toast_desc:
    font gui.text_font
    size 18
    color "#B9CBD3"

style ach_card_unlocked:
    background "#113238E8"
    padding (20, 16)

style ach_card_locked:
    background "#081A1ECC"
    padding (20, 16)

style ach_card_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 25
    color "#F4F1E8"
    outlines [(2, "#061416", 0, 0)]

style ach_card_desc:
    font gui.text_font
    size 19
    color "#B9CBD3"

style ach_card_time:
    font gui.text_font
    size 16
    color "#7FC8C0"

style ach_progress_bar:
    left_bar Solid("#7FC8C0")
    right_bar Solid("#174A4E")
