# ==============================================================================
# 角色表情切换辅助 (Template-Owned)
# ==============================================================================

init python:

    def emote(
        sprite,
        expression,
        pose=None,
        outfit=None
    ):

        sprite.set(
            outfit=outfit,
            pose=pose,
            expression=expression
        )

        # 走 CharacterSprite.show()，使用 current_at / default_at 并应用 IMAGE_OFFSETS。
        sprite.show()
