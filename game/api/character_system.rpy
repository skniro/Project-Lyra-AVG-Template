init python:

    import os

    # 可在新项目注册角色时按需配置：
    # NPC_TAGS: 需要自动避让主角立绘的配角 tag 集合
    # NPC_LARGE_TAGS: 使用较大缩放比例的配角 tag 集合
    # MAIN_LEFT_TAG / MAIN_RIGHT_TAG: 左右主位角色 tag（用于自动避让判断）
    NPC_TAGS = set()
    NPC_LARGE_TAGS = set()
    MAIN_LEFT_TAG = None
    MAIN_RIGHT_TAG = None
    IMAGE_OFFSETS = {}

    def _pick_npc_at(tag):
        """配角选位：两边都有人站中间，只有一边有人站另一边，没人站左边。"""
        if tag in NPC_LARGE_TAGS:
            left, right, center = npc_left_big, npc_right_big, npc_center_low_big
        else:
            left, right, center = npc_left, npc_right, npc_center_low

        left_shown = bool(MAIN_LEFT_TAG and renpy.showing(MAIN_LEFT_TAG))
        right_shown = bool(MAIN_RIGHT_TAG and renpy.showing(MAIN_RIGHT_TAG))

        if left_shown and right_shown:
            return [center]
        if right_shown:
            return [left]
        if left_shown:
            return [right]
        return [left]

    class CharacterSprite:

        def __init__(
            self,
            tag,
            image_dir,
            default_outfit="normal",
            default_pose="stand",
            default_expression="normal",
            default_at=None
        ):

            self.tag = tag
            self.image_dir = image_dir

            self.outfit = default_outfit
            self.pose = default_pose
            self.expression = default_expression

            # 第一次被 emote()/show() 时使用的位置；避免没有初始 show 时
            # 掉到屏幕左上角的默认 transform。
            self.default_at = default_at or []
            self.current_at = []

        # ======================
        # 设置状态
        # ======================

        def set(
            self,
            outfit=None,
            pose=None,
            expression=None
        ):

            if outfit:
                self.outfit = outfit

            if pose:
                self.pose = pose

            if expression:
                self.expression = expression

        # ======================
        # 获取 image 名称
        # ======================

        def image_name(self):

            return (
                f"{self.tag} "
                f"{self.outfit} "
                f"{self.pose} "
                f"{self.expression}"
            )

        # ======================
        # 显示角色
        # ======================

        def show(
            self,
            at_list=None,
            layer="master",
            zorder=0
        ):

            image_name = self.image_name()
  
            # 检查图片是否存在
            if not renpy.has_image(image_name):

                raise Exception(
                    f"[CharacterSystem] 未找到角色图片: "
                    f"{image_name}"
                )
        
            kwargs = {
                "name": image_name,
                "tag": self.tag,
                "layer": layer,
                "zorder": zorder,
            }

            # 配角首次 show / 显式 npc_center 时，按左右空位自动选位。
            if self.tag in NPC_TAGS:
                if at_list and any(t is npc_center for t in at_list):
                    at_list = _pick_npc_at(self.tag)
                elif (not at_list and not self.current_at and self.default_at
                      and any(t is npc_center for t in self.default_at)):
                    at_list = _pick_npc_at(self.tag)

            # 位置优先级：本次传入 > 上次记住的位置 > 角色默认位置。
            if at_list:
                kwargs["at_list"] = at_list
                self.current_at = at_list
            elif self.current_at:
                kwargs["at_list"] = self.current_at
            elif self.default_at:
                kwargs["at_list"] = self.default_at
                self.current_at = self.default_at

            # 根据 IMAGE_OFFSETS 把角色内容中心/脚底对齐到同一基准。
            ox, oy = IMAGE_OFFSETS.get(image_name, (0, 0))
            if ox or oy:
                at = list(kwargs.get("at_list", []))
                at.append(Transform(xoffset=ox, yoffset=oy))
                kwargs["at_list"] = at

            renpy.show(**kwargs)

        # ======================
        # 隐藏角色
        # ======================

        def hide(self):

            renpy.hide(self.tag)

    # ==========================================
    # 自动注册角色图片
    # ==========================================

    def auto_register_character(character_name):

        prefix = f"images/characters/{character_name}/"

        for fn in renpy.list_files():

            if not fn.startswith(prefix):
                continue

            if not fn.lower().endswith(".png"):
                continue

            file = fn.split("/")[-1]

            filename = file[:-4]

            parts = filename.split("_")

            if len(parts) != 3:
                print(
                    f"[CharacterSystem] 文件名格式错误: {file}"
                )
                continue

            outfit, pose, expression = parts

            image_name = (
                f"{character_name} "
                f"{outfit} "
                f"{pose} "
                f"{expression}"
            )

            renpy.image(
                image_name,
                fn
            )

            print(
                f"[CharacterSystem] 注册图片: {image_name}"
            )
            