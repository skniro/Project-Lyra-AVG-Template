# ==============================================================================
# Steam 集成与章节状态跟踪 (Template-Owned)
# ==============================================================================
# 安全封装 Ren'Py 内置 00steam.rpy / 00achievement.rpy 接口：
#   - 绑定 config.steam_appid 后，发布到 Steam 时自动接管 Steam 成就与时间线
#   - 非 Steam 环境（本地开发 / Android / 独立版）自动静默降级，不产生报错

default _current_chapter_title = ""

init -6 python:

    def is_steam_active():
        try:
            return getattr(achievement, "steam", None) is not None
        except Exception:
            return False

    def steam_persona_name():
        if not is_steam_active():
            return None
        try:
            return achievement.steam.get_persona_name()
        except Exception:
            return None

    def steam_open_overlay(dialog="Achievements"):
        """打开 Steam 悬浮窗（Achievements / Friends / Community / Settings 等）。"""
        if not is_steam_active():
            renpy.notify(_("当前未连接到 Steam 客户端"))
            return False
        try:
            achievement.steam.activate_overlay(dialog)
            return True
        except Exception:
            return False

    def steam_timeline_event(title, description="", icon="steam_achievement", priority=0):
        """向 Steam Timeline 记录关键剧情节点事件。"""
        if not is_steam_active():
            return
        try:
            achievement.steam.add_timeline_event(icon, title, description, priority=priority)
        except Exception:
            pass

    def set_story_chapter(chapter_title, timeline_desc=None):
        """剧本中切换章节时调用：更新存档槽章节名并同步 Steam Timeline 状态。"""
        store._current_chapter_title = chapter_title or ""
        if is_steam_active():
            try:
                desc = timeline_desc if timeline_desc is not None else chapter_title
                if desc:
                    achievement.steam.set_timeline_state_description(desc)
            except Exception:
                pass
