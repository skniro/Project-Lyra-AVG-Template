# ==============================================================================
# 自动语音映射系统 (Template-Owned)
# ==============================================================================
# 项目侧请在 game/project/voice_map.rpy 中填充 auto_voice_map 或 PROJECT_AUTO_VOICE_MAP。

init python:

    auto_voice_map = {}

    def _template_auto_voice(tlid):
        return auto_voice_map.get(tlid)

    config.auto_voice = _template_auto_voice
