# ==============================================================================
# 项目角色与立绘注册 (Project-Owned — 模板更新不会覆盖本文件)
# ==============================================================================
# 立绘文件命名规范：images/characters/<tag>/<outfit>_<pose>_<expression>.png
#
# 示例：
# define heroine = Character(_("女主"), color="#7FC8C0")
#
# init python:
#     auto_register_character("heroine")
#
# define heroine_sprite = CharacterSprite(
#     "heroine",
#     "images/characters/heroine",
#     default_at=[right_halfbody]
# )
#
# 如需启用配角自动避让站位：
# define PROJECT_CHARACTER_LAYOUT = {
#     "npc_tags": {"npc1"},
#     "npc_large_tags": set(),
#     "main_left_tag": "protagonist",
#     "main_right_tag": "heroine",
# }

init python:
    pass
