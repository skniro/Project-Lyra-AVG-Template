# ==============================================================================
# SVG 矢量绘图与富内容视觉渲染系统 (Template-Owned)
# ==============================================================================
# 支持两类 SVG 输入：
#   1. 工程内 .svg 文件路径（如 "images/ui/badge.svg"）
#   2. 内联 <svg ...>...</svg> 字符串（适合程序化生成徽章、分隔线、图表、进度环等）
#
# 同时提供 render_visual(spec, default_size=None) 供内容页面（Manual/Credits/Extras/
# 自定义内容页）统一渲染 PNG/WebP/SVG 文件与内联 SVG。

init -8 python:

    import io
    import hashlib

    class InlineSVGImage(renpy.display.im.ImageBase):
        """将内联 SVG 字符串直接通过 Ren'Py SDL_image 管线光栅化为指定尺寸纹理。"""

        obsolete = False

        def __init__(self, svg_markup, size=None, **properties):
            if isinstance(svg_markup, str):
                data = svg_markup.encode("utf-8")
            else:
                data = bytes(svg_markup)

            norm_size = tuple(int(v) for v in size) if size else None
            digest = hashlib.sha1(data).hexdigest()[:16]
            super(InlineSVGImage, self).__init__(digest, norm_size, **properties)
            self.data = data
            self.target_size = norm_size
            self.is_svg = True
            self.pixel_perfect = True
            self.const_size = (norm_size is not None)

        def get_hash(self):
            return hashlib.sha1(self.data + repr(self.target_size).encode("ascii")).hexdigest()

        def load(self):
            f = io.BytesIO(self.data)
            if self.target_size:
                return renpy.display.pgrender.load_image(f, "inline.svg", size=self.target_size)
            return renpy.display.pgrender.load_image(f, "inline.svg")

        def predict_files(self):
            return []


    class SizedSVGFile(renpy.display.im.ImageBase):
        """将工程内 .svg 文件光栅化为精确目标像素尺寸，保持矢量边缘锐利。"""

        obsolete = False

        def __init__(self, filename, size=None, **properties):
            norm_size = tuple(int(v) for v in size) if size else None
            super(SizedSVGFile, self).__init__(filename, norm_size, **properties)
            self.filename = filename
            self.target_size = norm_size
            self.is_svg = True
            self.pixel_perfect = True
            self.const_size = (norm_size is not None)

        def get_hash(self):
            return renpy.loader.get_hash(self.filename)

        def load(self):
            with renpy.loader.load(self.filename, directory="images") as f:
                if self.target_size:
                    return renpy.display.pgrender.load_image(f, self.filename, size=self.target_size)
                return renpy.display.pgrender.load_image(f, self.filename)

        def predict_files(self):
            return [self.filename]


    def svg_inline(svg_markup, size=None):
        """将内联 SVG XML 字符串转为 Ren'Py Displayable。"""
        return InlineSVGImage(svg_markup, size=size)


    def svg_file(path, size=None, dpi=96):
        """加载工程内 .svg 文件。若传入 size=(w, h) 则按目标分辨率矢量光栅化。"""
        if size is not None:
            return SizedSVGFile(path, size=size)
        return Image(path, dpi=dpi)


    def is_inline_svg(value):
        return isinstance(value, str) and value.lstrip().startswith("<svg")


    def render_visual(spec, default_size=None):
        """统一解析图片路径、.svg 文件、内联 <svg> 字符串或配置字典。"""
        if spec is None:
            return None

        if isinstance(spec, dict):
            size = spec.get("size", default_size)
            if "svg" in spec and spec["svg"]:
                return svg_inline(spec["svg"], size=size)
            if "file" in spec and spec["file"]:
                path = spec["file"]
                if path.lower().endswith(".svg"):
                    return svg_file(path, size=size, dpi=spec.get("dpi", 96))
                disp = Image(path)
                return Transform(disp, xysize=size) if size else disp
            return None

        if isinstance(spec, str):
            if is_inline_svg(spec):
                return svg_inline(spec, size=default_size)
            if spec.lower().endswith(".svg"):
                return svg_file(spec, size=default_size)
            disp = Image(spec)
            return Transform(disp, xysize=default_size) if default_size else disp

        return spec


    def svg_progress_ring(percent, size=84, accent="#7FC8C0", track="#174A4E", text_color="#F4F1E8"):
        """生成矢量环形完成度图标（SVG）。"""
        import math
        pct = max(0, min(100, int(round(percent))))
        r = 34
        circ = 2.0 * math.pi * r
        dash = circ * (pct / 100.0)
        gap = max(0.0, circ - dash)
        markup = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">'
            '<circle cx="48" cy="48" r="34" fill="#061416" fill-opacity="0.72" '
            'stroke="{track}" stroke-width="8"/>'
            '<circle cx="48" cy="48" r="34" fill="none" stroke="{accent}" stroke-width="8" '
            'stroke-linecap="round" stroke-dasharray="{dash:.2f} {gap:.2f}" '
            'transform="rotate(-90 48 48)"/>'
            '<text x="48" y="54" text-anchor="middle" font-family="sans-serif" '
            'font-size="20" font-weight="bold" fill="{text_color}">{pct}%</text>'
            '</svg>'
        ).format(track=track, accent=accent, dash=dash, gap=gap, text_color=text_color, pct=pct)
        return svg_inline(markup, size=(size, size))


    def svg_divider(width=640, height=16, primary="#7FC8C0", secondary="#F2C77E"):
        """生成双色渐隐矢量分隔线（SVG）。"""
        mid = width // 2
        y1 = height // 2 - 2
        y2 = height // 2 + 2
        markup = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            '<defs>'
            '<linearGradient id="g1" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0%" stop-color="{p}" stop-opacity="0"/>'
            '<stop offset="20%" stop-color="{p}" stop-opacity="0.95"/>'
            '<stop offset="80%" stop-color="{p}" stop-opacity="0.95"/>'
            '<stop offset="100%" stop-color="{p}" stop-opacity="0"/>'
            '</linearGradient>'
            '<linearGradient id="g2" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0%" stop-color="{s}" stop-opacity="0"/>'
            '<stop offset="25%" stop-color="{s}" stop-opacity="0.9"/>'
            '<stop offset="75%" stop-color="{s}" stop-opacity="0.9"/>'
            '<stop offset="100%" stop-color="{s}" stop-opacity="0"/>'
            '</linearGradient>'
            '</defs>'
            '<rect x="0" y="{y1}" width="{w}" height="2" fill="url(#g1)"/>'
            '<rect x="0" y="{y2}" width="{w}" height="1.5" fill="url(#g2)"/>'
            '<polygon points="{mid},{t} {mr},{cy} {mid},{b} {ml},{cy}" fill="{s}"/>'
            '</svg>'
        ).format(
            w=width, h=height, p=primary, s=secondary,
            y1=y1, y2=y2, mid=mid, ml=mid - 6, mr=mid + 6,
            t=max(0, height // 2 - 6), b=min(height, height // 2 + 6), cy=height // 2
        )
        return svg_inline(markup, size=(width, height))
