################################################################################
## 控制器震动
################################################################################
##
## Ren'Py 没有提供桌面端手柄震动的公开 API。游戏使用的 SDL2 被静态链接在
## librenpython.dll 中，所以这里用 ctypes 直接调用 SDL_GameControllerRumble()。
##
## DualSense（PS5 手柄）通过蓝牙连接时，SDL 2.0.20 默认关闭震动，
## 必须在打开手柄之前设置 SDL_JOYSTICK_HIDAPI_PS5_RUMBLE=1。
## 这里在 init 阶段设置 hint，因此 Ren'Py 之后打开手柄时也会带上震动支持。

init -10 python:
    import ctypes

    # 各档位对应（低频马达, 高频马达）的振幅，范围 0-65535。
    controller_rumble_levels = {
        "off": (0, 0),
        "weak": (0x3000, 0x7000),
        "medium": (0x8000, 0xC000),
        "strong": (0xFFFF, 0xFFFF),
    }

    class _SDLRumble(object):

        def __init__(self):
            self.lib = None
            self.ready = False
            self.error = None
            self.opened = {}
            self.load()

        def load(self):
            # Ren'Py 自带 get_sdl_dll()，返回进程内正在使用的 SDL 库
            # （Windows 上是 librenpython.dll，Linux/macOS 同理）。
            try:
                dll = renpy.get_sdl_dll()
            except Exception:
                dll = None

            if dll is None:
                self.error = "SDL library not found"
                return

            self.lib = dll

            dll.SDL_Init.restype = ctypes.c_int
            dll.SDL_Init.argtypes = [ctypes.c_uint32]

            dll.SDL_SetHint.restype = ctypes.c_int
            dll.SDL_SetHint.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

            dll.SDL_NumJoysticks.restype = ctypes.c_int

            dll.SDL_IsGameController.restype = ctypes.c_int
            dll.SDL_IsGameController.argtypes = [ctypes.c_int]

            dll.SDL_JoystickGetDeviceInstanceID.restype = ctypes.c_int
            dll.SDL_JoystickGetDeviceInstanceID.argtypes = [ctypes.c_int]

            dll.SDL_GameControllerOpen.restype = ctypes.c_void_p
            dll.SDL_GameControllerOpen.argtypes = [ctypes.c_int]

            dll.SDL_GameControllerRumble.restype = ctypes.c_int
            dll.SDL_GameControllerRumble.argtypes = [
                ctypes.c_void_p, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint32,
            ]

            # 必须在打开手柄之前设置。PS4 / PS5 在蓝牙下的震动默认是关的。
            dll.SDL_SetHint(b"SDL_JOYSTICK_HIDAPI_PS5_RUMBLE", b"1")
            dll.SDL_SetHint(b"SDL_JOYSTICK_HIDAPI_PS4_RUMBLE", b"1")

        def ensure_ready(self):
            if self.lib is None:
                return False

            if not self.ready:
                # 手柄子系统可能已经由 Ren'Py 初始化；SDL_Init 是引用计数的。
                self.lib.SDL_Init(0x00000200 | 0x00002000)
                self.ready = True

            return True

        def refresh(self):
            """重新枚举手柄，打开新设备，忘掉已断开的设备。"""

            if not self.ensure_ready():
                return

            try:
                count = self.lib.SDL_NumJoysticks()
            except Exception:
                return

            present = set()

            for i in range(count):
                try:
                    if not self.lib.SDL_IsGameController(i):
                        continue

                    instance_id = self.lib.SDL_JoystickGetDeviceInstanceID(i)
                except Exception:
                    continue

                present.add(instance_id)

                if instance_id not in self.opened:
                    try:
                        handle = self.lib.SDL_GameControllerOpen(i)
                    except Exception:
                        handle = None

                    if handle:
                        self.opened[instance_id] = handle

            # 不调用 SDL_GameControllerClose：Ren'Py 自己也可能持有同一个
            # SDL_GameController，关闭会把它的输入一起关掉。断开的设备
            # SDL 会自己回收，这里只需要不再向它发送震动。
            for instance_id in list(self.opened):
                if instance_id not in present:
                    del self.opened[instance_id]

        def rumble(self, low, high, duration_ms):
            if low <= 0 and high <= 0:
                return

            self.refresh()

            for handle in self.opened.values():
                try:
                    self.lib.SDL_GameControllerRumble(handle, low, high, duration_ms)
                except Exception:
                    pass

    _sdl_rumble = _SDLRumble()

    def controller_rumble_level():
        return getattr(persistent, "controller_rumble", "off")

    def controller_rumble(duration=0.15, level=None):
        """按当前设置的强度震动。可在剧本里用 $ controller_rumble(0.3, "strong") 调用。"""

        if level is None:
            level = controller_rumble_level()

        low, high = controller_rumble_levels.get(level, (0, 0))

        if low or high:
            _sdl_rumble.rumble(low, high, max(1, int(duration * 1000)))

    def controller_rumble_preview(value):
        """OPTIONS 里切换强度时试震一下。"""

        low, high = controller_rumble_levels.get(value, (0, 0))

        if low or high:
            _sdl_rumble.rumble(low, high, 350)

    def controller_rumble_choice():
        """选择选项时给一个较轻的短震动。"""

        low, high = controller_rumble_levels.get(controller_rumble_level(), (0, 0))

        if low or high:
            _sdl_rumble.rumble(max(1, low // 2), max(1, high // 2), 70)
