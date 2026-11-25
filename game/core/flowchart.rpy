# ==============================================================================
# CHART 剧情分支流程图 (SVG 矢量连线 + 可交互节点) (Template-Owned)
# ==============================================================================
# 项目在 game/project/00_project_config.rpy 中配置 PROJECT_FLOWCHART：
#   {
#       "title": "CHART",
#       "subtitle": _("剧情分支流程图"),
#       "canvas_size": (1520, 740),
#       "nodes": [
#           {
#               "id": "n_start",
#               "title": _("0.0 序幕"),
#               "subtitle": _("海滨站台"),
#               "summary": _("梅雨季来到夕凪町的第一夜。"),
#               "pos": (80, 260),
#               "type": "story",        # story | choice | route | ending
#               "label": "ch1_sec001",  # 可选，点击可回放/跳转
#               "unlock_flag": None,    # 可选；留空自动检查 renpy.seen_label(label)
#           },
#       ],
#       "edges": [
#           ("n_start", "n_branch_a"),
#           ("n_start", "n_branch_b", "#F2C77E"),
#       ],
#   }

init python:

    def unlock_flowchart_node(node_id):
        if not isinstance(getattr(persistent, "_unlocked_chart_nodes", None), set):
            persistent._unlocked_chart_nodes = set()
        persistent._unlocked_chart_nodes.add(node_id)

    def is_flowchart_node_unlocked(node):
        nid = node.get("id", "")
        manual = getattr(persistent, "_unlocked_chart_nodes", None)
        if isinstance(manual, set) and nid in manual:
            return True
        flag = node.get("unlock_flag")
        if flag and getattr(persistent, flag, False):
            return True
        lbl = node.get("label")
        if lbl and renpy.has_label(lbl) and renpy.seen_label(lbl):
            return True
        return False

    def get_flowchart_stats():
        nodes = PROJECT_FLOWCHART.get("nodes", []) if isinstance(PROJECT_FLOWCHART, dict) else []
        total = len(nodes)
        unlocked = sum(1 for n in nodes if is_flowchart_node_unlocked(n))
        endings = [n for n in nodes if n.get("type") == "ending"]
        endings_ok = sum(1 for n in endings if is_flowchart_node_unlocked(n))
        pct = int(round(100.0 * unlocked / max(1, total))) if total > 0 else 0
        return {
            "unlocked": unlocked,
            "total": total,
            "endings_ok": endings_ok,
            "endings_total": len(endings),
            "pct": pct,
        }

    def svg_flowchart_edges(nodes, edges, canvas_w=1520, canvas_h=740):
        """使用 SVG 三次贝塞尔曲线绘制流程图节点连线。"""
        node_map = {n.get("id"): n for n in nodes}
        node_w = 240
        node_h = 84
        parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'.format(
                w=canvas_w, h=canvas_h
            ),
            '<defs>'
            '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
            '<path d="M 40 0 L 0 0 0 40" fill="none" stroke="#174A4E" stroke-opacity="0.28" stroke-width="1"/>'
            '</pattern>'
            '</defs>',
            '<rect x="0" y="0" width="{w}" height="{h}" fill="url(#grid)"/>'.format(w=canvas_w, h=canvas_h),
        ]

        for edge in edges:
            src_id = edge[0]
            dst_id = edge[1]
            custom_color = edge[2] if len(edge) > 2 else None
            src = node_map.get(src_id)
            dst = node_map.get(dst_id)
            if not src or not dst:
                continue

            sx, sy = src.get("pos", (0, 0))
            dx, dy = dst.get("pos", (0, 0))
            x1 = sx + node_w
            y1 = sy + node_h // 2
            x2 = dx
            y2 = dy + node_h // 2
            cx = max(40, abs(x2 - x1) * 0.5)

            both_ok = is_flowchart_node_unlocked(src) and is_flowchart_node_unlocked(dst)
            node_color = dst.get("color") or src.get("color")
            stroke = custom_color if (custom_color and both_ok) else (node_color if (node_color and both_ok) else ("#7FC8C0" if both_ok else "#254950"))
            opacity = "0.95" if both_ok else "0.55"
            width = "3" if both_ok else "2"
            dash = "" if both_ok else ' stroke-dasharray="6 5"'

            parts.append(
                '<path d="M {x1} {y1} C {c1x} {y1}, {c2x} {y2}, {x2} {y2}" '
                'fill="none" stroke="{st}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round"{dash}/>'.format(
                    x1=x1, y1=y1, c1x=x1 + cx, c2x=x2 - cx, x2=x2, y2=y2,
                    st=stroke, op=opacity, sw=width, dash=dash
                )
            )
            parts.append(
                '<circle cx="{x2}" cy="{y2}" r="4" fill="{st}" fill-opacity="{op}"/>'.format(
                    x2=x2, y2=y2, st=stroke, op=opacity
                )
            )

        parts.append('</svg>')
        return svg_inline("".join(parts), size=(canvas_w, canvas_h))


screen flowchart():

    tag menu

    default chart_selected_id = None

    $ _fc = PROJECT_FLOWCHART if isinstance(PROJECT_FLOWCHART, dict) else {}
    $ _title = _fc.get("title", "CHART")
    $ _subtitle = _fc.get("subtitle", _("剧情分支流程图"))
    $ _csize = _fc.get("canvas_size", (1520, 740))
    $ _nodes = _fc.get("nodes", [])
    $ _edges = _fc.get("edges", [])
    $ _stats = get_flowchart_stats()
    $ _sel_node = next((n for n in _nodes if n.get("id") == chart_selected_id), None)

    add "gui/log_bg.png"
    add "gui/manual_banner.png" xalign 0.5 ypos 0

    text _title style "manual_title" xpos 130 ypos 18
    text _subtitle style "manual_title_zh" xpos 360 ypos 30

    hbox:
        xalign 1.0
        xoffset -130
        ypos 20
        spacing 18

        text (__("节点 %d / %d  ·  结局 %d / %d") % (
            _stats["unlocked"], _stats["total"], _stats["endings_ok"], _stats["endings_total"]
        )) style "extras_meta_text" yalign 0.5
        add svg_progress_ring(_stats["pct"], size=54) yalign 0.5

    frame:
        style "manual_panel_frame"
        xalign 0.5
        ypos 142
        xsize 1660
        ysize 720
        padding (28, 24)

        if _nodes:
            viewport:
                xfill True
                yfill True
                scrollbars "both"
                mousewheel True
                draggable True

                fixed:
                    xsize _csize[0]
                    ysize _csize[1]

                    add svg_flowchart_edges(_nodes, _edges, _csize[0], _csize[1])

                    for node in _nodes:
                        $ _nid = node.get("id", "")
                        $ _nx, _ny = node.get("pos", (0, 0))
                        $ _ok = is_flowchart_node_unlocked(node)
                        $ _ntype = node.get("type", "story")
                        $ _style = (
                            "chart_node_ending" if (_ok and _ntype == "ending")
                            else ("chart_node_choice" if (_ok and _ntype == "choice")
                            else ("chart_node_unlocked" if _ok else "chart_node_locked"))
                        )

                        button:
                            style _style
                            xpos _nx
                            ypos _ny
                            action SetScreenVariable("chart_selected_id", _nid)
                            selected (chart_selected_id == _nid)

                            vbox:
                                spacing 2
                                yalign 0.5

                                text (node.get("title", _nid) if _ok else _("？？？")) style "chart_node_title"
                                if _ok and node.get("subtitle"):
                                    text node["subtitle"] style "chart_node_sub"
                                elif not _ok:
                                    text _("未探索分支") style "chart_node_sub"
        else:
            text _("当前项目尚未配置剧情流程图节点（请在 game/project/00_project_config.rpy 中配置 PROJECT_FLOWCHART）。") style "extras_meta_text" xalign 0.5 yalign 0.5

    frame:
        style "manual_bottom_bar"
        xalign 0.5
        yalign 1.0
        yoffset -44
        xsize 1660

        hbox:
            xfill True
            yalign 0.5

            if _sel_node:
                $ _sok = is_flowchart_node_unlocked(_sel_node)
                $ _slbl = _sel_node.get("label")
                hbox:
                    spacing 18
                    yalign 0.5

                    text (_sel_node.get("title", "") if _sok else _("？？？")) style "manual_section_title" yalign 0.5
                    text (_sel_node.get("summary", "") if _sok else _("尚未抵达该剧情节点。")) style "manual_hint" yalign 0.5

                    if _sok and _slbl and renpy.has_label(_slbl):
                        textbutton _("回放该节点") action Replay(_slbl) style "save_bottom_button" yalign 0.5
            else:
                text _("拖动或滚轮浏览流程图，点击已解锁节点可查看摘要或回放") style "manual_hint" yalign 0.5

            textbutton _("关闭") action (ShowMenu("main_menu") if main_menu else ShowMenu("extras")) style "log_close_button" xalign 1.0 yalign 0.5

    key "game_menu" action (ShowMenu("main_menu") if main_menu else ShowMenu("extras"))


style chart_node_unlocked:
    background "#113238F0"
    hover_background "#1A4D56FF"
    selected_background "#1F5E68FF"
    xsize 240
    ysize 84
    padding (16, 10)

style chart_node_choice is chart_node_unlocked:
    background "#1A3742F0"

style chart_node_ending is chart_node_unlocked:
    background "#3B2D16F0"
    hover_background "#543F1EFF"

style chart_node_locked:
    background "#08191CE0"
    xsize 240
    ysize 84
    padding (16, 10)

style chart_node_title:
    font "fonts/NotoSerifCJKsc-Regular.otf"
    size 20
    color "#F4F1E8"

style chart_node_sub:
    font gui.text_font
    size 15
    color "#7FC8C0"
