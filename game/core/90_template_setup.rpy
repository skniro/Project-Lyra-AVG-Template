# ==============================================================================
# AVGTemplate Core Setup (Template-Owned — 请勿在业务项目中直接修改)
# ==============================================================================
# 在所有项目配置与资源脚本加载后（init 1），将 PROJECT_* 配置同步到引擎子系统。

init 1 python hide:

    # 1. 角色语音通道注册（含系统音效通道）
    try:
        if not renpy.music.channel_defined("system"):
            renpy.music.register_channel("system", mixer="system", loop=False)
        for _entry in PROJECT_VOICE_CAST:
            _tag = _entry[0]
            if _tag and not renpy.music.channel_defined("voice_" + _tag):
                renpy.music.register_channel("voice_" + _tag, mixer=_tag, loop=False)
    except Exception:
        pass

    # 2. 角色站位避让配置
    if isinstance(PROJECT_CHARACTER_LAYOUT, dict):
        NPC_TAGS.update(PROJECT_CHARACTER_LAYOUT.get("npc_tags") or ())
        NPC_LARGE_TAGS.update(PROJECT_CHARACTER_LAYOUT.get("npc_large_tags") or ())
        if PROJECT_CHARACTER_LAYOUT.get("main_left_tag") is not None:
            store.MAIN_LEFT_TAG = PROJECT_CHARACTER_LAYOUT.get("main_left_tag")
        if PROJECT_CHARACTER_LAYOUT.get("main_right_tag") is not None:
            store.MAIN_RIGHT_TAG = PROJECT_CHARACTER_LAYOUT.get("main_right_tag")

    # 3. 同步角色立绘偏移、自动语音映射、CG/音乐清单
    if PROJECT_IMAGE_OFFSETS:
        IMAGE_OFFSETS.update(PROJECT_IMAGE_OFFSETS)

    if PROJECT_AUTO_VOICE_MAP:
        auto_voice_map.update(PROJECT_AUTO_VOICE_MAP)

    if PROJECT_CG_ENTRIES and not cg_entries:
        cg_entries.extend(PROJECT_CG_ENTRIES)

    if PROJECT_MUSIC_TRACKS and not music_tracks:
        music_tracks.extend(PROJECT_MUSIC_TRACKS)

    # 4. 注册成就（同步绑定 Steam 后端）
    for _ach in PROJECT_ACHIEVEMENTS:
        _aid = _ach.get("id")
        if not _aid:
            continue
        _ach_kwargs = {}
        if _ach.get("steam"):
            _ach_kwargs["steam"] = _ach["steam"]
        if _ach.get("stat_max"):
            _ach_kwargs["stat_max"] = _ach["stat_max"]
        if _ach.get("stat_modulo"):
            _ach_kwargs["stat_modulo"] = _ach["stat_modulo"]
        try:
            achievement.register(_aid, **_ach_kwargs)
        except Exception:
            pass
    try:
        achievement.sync()
    except Exception:
        pass

    # 5. 发布打包：额外的排除规则与资源归档
    for _pattern in PROJECT_EXTRA_BUILD_EXCLUDES:
        build.classify(_pattern, None)

    if PROJECT_BUILD_ARCHIVE:
        _archive_name = PROJECT_BUILD_ARCHIVE_NAME or "archive"
        for _pattern in PROJECT_BUILD_ARCHIVE_PATTERNS:
            build.classify(_pattern, _archive_name)
