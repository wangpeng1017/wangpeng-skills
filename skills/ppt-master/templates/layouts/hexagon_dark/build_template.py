"""
v19 慧新全智风格 PPT 构建脚本
基于慧新全智模板 (Hexagon Theme) 重建 人形机器人 MOM 行业方案
策略：复制模板 PPT 结构，仅替换 slides 目录内容，100% 继承视觉资产
"""
from __future__ import annotations
import os
import shutil
import zipfile
import json
import re
from xml.sax.saxutils import escape

# ============ 路径配置 ============
BASE_DIR = "/Users/wangpeng/Downloads/yushu/projects/humanoid_case"
WORK_DIR = f"{BASE_DIR}/template_analysis"
BUILD_DIR = f"{WORK_DIR}/v19_build"
OUTPUT_PPTX = f"{BASE_DIR}/人形机器人MOM行业方案_v20_huixin.pptx"

# ============ 慧新全智配色 (主题色 + 深色背景适配) ============
COLOR = {
    "dark_bg": "003D4A",       # 深墨青背景（与模板首页一致）
    "primary": "0097BA",        # 主青色 accent1
    "light_cyan": "85CDDB",     # 浅青 accent2
    "lime": "A5D867",           # 黄绿 accent3
    "deep_cyan": "005072",      # 深青蓝 accent4 (用于深底强调/表头/页底金句)
    "green": "509E2F",          # accent5
    "orange": "ED8B00",         # accent6 (警示)
    "white": "FFFFFF",
    # 内容页深色背景适配 ↓
    "text_gray": "C8D3D7",     # 卡片内描述文字（在深背景上 浅灰）
    "light_gray": "D1D3D3",
    "card_bg_light": "0F3D4A",  # 卡片底（半暗深青蓝 · 比 layout 背景稍亮）
    "card_bg_glass": "1B5566",  # 卡片"亮色"层（再亮一档 用于行交替）
    "card_border": "1B5566",
}

# ============ 通用样式片段 ============
def xml_header():
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

def sld_open():
    return ('<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>')

def sld_close():
    return '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'

# Slide 尺寸 (EMU) 12192000 x 6858000
SLIDE_W = 12192000
SLIDE_H = 6858000

# ============ 形状生成器 ============
_sp_id_counter = [10]

def new_id():
    _sp_id_counter[0] += 1
    return _sp_id_counter[0]

def reset_id():
    _sp_id_counter[0] = 10

def rect_solid(x, y, w, h, fill_color, name="Rect"):
    """实色矩形"""
    sid = new_id()
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill_color}"/></a:solidFill>'
            f'<a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')

def rect_rounded(x, y, w, h, fill_color, border_color=None, radius_pct=10, name="RRect"):
    """圆角矩形"""
    sid = new_id()
    border = ''
    if border_color:
        border = f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{border_color}"/></a:solidFill></a:ln>'
    else:
        border = '<a:ln><a:noFill/></a:ln>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill_color}"/></a:solidFill>{border}</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')

def textbox(x, y, w, h, runs, anchor="t", align="l", auto_fit=False):
    """通用文本框
    runs: [(text, size_pt, color_hex, bold, font_latin, font_ea, italic), ...]
    runs 也可以包含特殊指令 ('<br>',)
    """
    sid = new_id()
    body_pr_anchor = anchor  # t/ctr/b
    autofit_xml = '<a:spAutoFit/>' if auto_fit else ''
    body_pr = f'<a:bodyPr wrap="square" anchor="{body_pr_anchor}">{autofit_xml}</a:bodyPr>'
    # 构造段落
    paragraphs_xml = []
    cur_runs_xml = []
    align_attr = {"l":"l", "c":"ctr", "r":"r"}.get(align, "l")
    for r in runs:
        if r == ('<br>',) or r == '<br>':
            paragraphs_xml.append(f'<a:p><a:pPr algn="{align_attr}"/>' + ''.join(cur_runs_xml) + '</a:p>')
            cur_runs_xml = []
            continue
        text, size_pt, color_hex, bold, font_latin, font_ea, italic = (r + (None,)*7)[:7]
        size_attr = f' sz="{int(size_pt*100)}"' if size_pt else ''
        bold_attr = f' b="{"1" if bold else "0"}"' if bold is not None else ''
        italic_attr = f' i="{"1" if italic else "0"}"' if italic is not None else ''
        color_xml = f'<a:solidFill><a:srgbClr val="{color_hex}"/></a:solidFill>' if color_hex else ''
        latin_xml = f'<a:latin typeface="{font_latin}"/>' if font_latin else '<a:latin typeface="Arial"/>'
        ea_xml = f'<a:ea typeface="{font_ea}"/>' if font_ea else '<a:ea typeface="微软雅黑"/>'
        rpr = f'<a:rPr lang="zh-CN" altLang="en-US"{size_attr}{bold_attr}{italic_attr}>{color_xml}{latin_xml}{ea_xml}</a:rPr>'
        # 转义文字
        safe_text = escape(text)
        cur_runs_xml.append(f'<a:r>{rpr}<a:t>{safe_text}</a:t></a:r>')
    if cur_runs_xml:
        paragraphs_xml.append(f'<a:p><a:pPr algn="{align_attr}"/>' + ''.join(cur_runs_xml) + '</a:p>')
    para_xml = ''.join(paragraphs_xml) if paragraphs_xml else '<a:p/>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="TextBox"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            f'<p:txBody>{body_pr}<a:lstStyle/>{para_xml}</p:txBody></p:sp>')

def vertical_bar(x, y, h, color, w=80000):
    """左侧装饰窄条"""
    return rect_solid(x, y, w, h, color, name="VBar")

def horizontal_line(x, y, w, color, thickness=12700):
    """水平细线"""
    return rect_solid(x, y, w, thickness, color, name="HLine")

# ============ 页面渲染：通用顶栏（按模板 slide5 复刻：深色背景 + 细白字 + 竖线） ============
def render_topbar(chapter_label, section_label):
    """模板内容页顶栏：透明背景（让 layout1 深色背景显现）+ 左侧白字章节 + 白色竖线 + 右侧小节名"""
    parts = []
    # 左侧章节标题（白色细字，模板位置 x=285750 y=129659）
    parts.append(textbox(
        285750, 129659, 3300000, 461665,
        [(chapter_label, 16, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    # 中部白色竖线（模板位置 x=3496427 y=184503 cy=379992）
    parts.append(rect_solid(3496427, 184503, 12700, 379992, COLOR["white"], name="HeaderSep"))
    # 右侧小节标题（白色字）
    parts.append(textbox(
        3575877, 191214, 8500000, 400110,
        [(section_label, 16, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    return parts


def page_header(title, subtitle):
    """统一内容页页头：白色主标题（顶部）+ 副标题最上沿与 layout 倒梯形上边缘对齐（额外上移 6px）"""
    parts = []
    # 主标题（白色 32pt · 整体上移）
    parts.append(textbox(
        285750, 80000, 11600000, 540000,
        [(title, 32, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    # 副标题（白色字 · 比倒梯形上沿 746259 上移 6px ≈ 60000 EMU）
    parts.append(textbox(
        1050000, 686000, 10800000, 300000,
        [(subtitle, 17, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="t", align="l"
    ))
    return parts

def render_footer(page_no, total=30):
    """底部页脚"""
    return [textbox(
        10800000, 6550000, 1200000, 200000,
        [(f"PAGE {page_no:02d} / {total}", 9, COLOR["text_gray"], False, "Arial", "微软雅黑")],
        anchor="ctr", align="r"
    )]

# ============ 5 类页型生成函数 ============

def render_cover(content):
    """封面: 复用模板cover.xml 文字结构 (深青背景由layout5自动提供)"""
    reset_id()
    parts = []
    # 主标题区
    # 上方英文小标题
    parts.append(textbox(
        877932, 800000, 10436135, 280000,
        [("INDUSTRY SOLUTION · HUMANOID ROBOT MANUFACTURING", 12, COLOR["lime"], True, "Arial", "Arial")],
        anchor="ctr", align="l"
    ))
    parts.append(textbox(
        877932, 1080000, 10436135, 240000,
        [("HUMANOID ROBOTICS · MANUFACTURING OPERATIONS MANAGEMENT", 11, COLOR["white"], False, "Arial", "Arial")],
        anchor="ctr", align="l"
    ))
    # 中部主标题（白色大字）
    parts.append(textbox(
        877932, 2200000, 10436135, 800000,
        [("面向规模化量产的", 36, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    parts.append(textbox(
        877932, 2950000, 10436135, 1100000,
        [("人形机器人 MOM 行业解决方案", 48, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    # 副标题装饰横条
    parts.append(rect_solid(877932, 4400000, 8742303, 60000, COLOR["primary"]))
    parts.append(textbox(
        877932, 4500000, 10436135, 320000,
        [("生产执行 · 仓储协同 · 质量追溯 · 设备运营 · 一体化平台", 16, COLOR["lime"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    parts.append(textbox(
        877932, 4860000, 10436135, 260000,
        [("Integrated MOM Platform for Mass-Production Humanoid Robotics", 11, COLOR["light_cyan"], False, "Arial", "Arial")],
        anchor="ctr", align="l"
    ))
    # 底部三个亮点标签
    labels = [
        ("行业方案", "INDUSTRY SOLUTION"),
        ("五大业务系统", "FIVE BUSINESS SYSTEMS"),
        ("全链路追溯", "END-TO-END TRACEABILITY"),
    ]
    x0 = 877932
    label_w = 2900000
    gap = 200000
    for i, (cn, en) in enumerate(labels):
        bx = x0 + i * (label_w + gap)
        # 左侧青色竖线
        parts.append(rect_solid(bx, 5550000, 50000, 380000, COLOR["primary"]))
        parts.append(textbox(
            bx + 130000, 5520000, label_w - 130000, 220000,
            [(cn, 13, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"
        ))
        parts.append(textbox(
            bx + 130000, 5760000, label_w - 130000, 200000,
            [(en, 9, COLOR["lime"], False, "Arial", "Arial")],
            anchor="ctr", align="l"
        ))
    # 底部页脚
    parts.append(textbox(
        877932, 6440000, 4200000, 220000,
        [("慧新全智工业互联科技(青岛)有限公司", 10, COLOR["light_cyan"], False, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    # 页码已按王老师要求移除
    return sld_open() + ''.join(parts) + sld_close()


def render_toc(content):
    """目录页: 5 大章节"""
    reset_id()
    parts = []
    # 顶部装饰条 - 青色细线
    parts.append(rect_solid(0, 0, SLIDE_W, 60000, COLOR["primary"]))
    # 大字"目录"
    parts.append(textbox(
        680000, 580000, 4000000, 900000,
        [("目录", 64, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    # 副标题
    parts.append(textbox(
        680000, 1550000, 9000000, 280000,
        [("全篇 44 页 · 5 大章节 · 行业方案完整叙事", 14, COLOR["lime"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    parts.append(textbox(
        680000, 1820000, 9000000, 240000,
        [("TABLE OF CONTENTS", 11, COLOR["light_cyan"], False, "Arial", "Arial")],
        anchor="ctr", align="l"
    ))
    # 5 大章节卡片
    chapters = [
        ("01", "行业介绍", "INDUSTRY CONTEXT", "市场容量 · 客户分布 · 业务特征 · 制造复杂性"),
        ("02", "行业痛点", "INDUSTRY PAIN POINTS", "6 大业务域痛点 + 3 个真实业务场景"),
        ("03", "整体解决方案", "OVERALL SOLUTION", "研产供销服平台 · 业务流程 · 系统架构 · 数据主线"),
        ("04", "落地场景方案", "SCENARIO IMPLEMENTATION", "底座 · 研发 · MES 4 场景 · WMS · QMS · EAM · 系统截图"),
        ("05", "价值收益", "VALUE & ROADMAP", "价值收益 · 能力沉淀 · 推进路径"),
    ]
    card_w = 2150000
    card_h = 3400000
    gap = 100000
    total_w = 5 * card_w + 4 * gap
    x0 = (SLIDE_W - total_w) // 2
    y0 = 2400000
    for i, (num, cn, en, desc) in enumerate(chapters):
        cx = x0 + i * (card_w + gap)
        # 卡片顶部青色细条
        parts.append(rect_solid(cx, y0, card_w, 50000, COLOR["primary"]))
        # 卡片主体（深青色渐变效果用纯色替代）
        sid = new_id()
        parts.append(f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="TocCard{i}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                     f'<p:spPr><a:xfrm><a:off x="{cx}" y="{y0+50000}"/><a:ext cx="{card_w}" cy="{card_h}"/></a:xfrm>'
                     f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                     f'<a:solidFill><a:srgbClr val="{COLOR["deep_cyan"]}"><a:alpha val="60000"/></a:srgbClr></a:solidFill>'
                     f'<a:ln><a:noFill/></a:ln></p:spPr>'
                     f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')
        # 大编号（青色）
        parts.append(textbox(
            cx + 130000, y0 + 280000, card_w - 260000, 900000,
            [(num, 56, COLOR["lime"], True, "Arial", "Arial")],
            anchor="ctr", align="l"
        ))
        # 中文标题
        parts.append(textbox(
            cx + 130000, y0 + 1320000, card_w - 260000, 400000,
            [(cn, 22, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"
        ))
        # 英文小标题
        parts.append(textbox(
            cx + 130000, y0 + 1740000, card_w - 260000, 240000,
            [(en, 9, COLOR["light_cyan"], True, "Arial", "Arial")],
            anchor="ctr", align="l"
        ))
        # 描述
        parts.append(textbox(
            cx + 130000, y0 + 2200000, card_w - 260000, 1100000,
            [(desc, 11, COLOR["white"], False, "Arial", "微软雅黑")],
            anchor="t", align="l"
        ))
    # 页码已按王老师要求移除
    return sld_open() + ''.join(parts) + sld_close()


def render_chapter(chapter_num, cn_title, en_title, desc, page_no):
    """章节过渡页：模板chapter.xml 的样式"""
    reset_id()
    parts = []
    # 顶部装饰条
    parts.append(rect_solid(0, 0, SLIDE_W, 60000, COLOR["primary"]))
    # 中部黑色圆角横条 - 主标题
    # 使用 chapter.xml 完全相同的位置：x=3668773 y=2714290 cx=5069908 cy=400110
    # 但加入更长的横条让标题显示更突出
    bar_x = 1800000
    bar_y = 2700000
    bar_w = 8500000
    bar_h = 800000
    sid = new_id()
    parts.append(
        f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="ChapBar"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{bar_x}" y="{bar_y}"/><a:ext cx="{bar_w}" cy="{bar_h}"/></a:xfrm>'
        f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 25000"/></a:avLst></a:prstGeom>'
        f'<a:gradFill flip="none" rotWithShape="1">'
        f'<a:gsLst>'
        f'<a:gs pos="0"><a:srgbClr val="0083A6"><a:shade val="30000"/><a:satMod val="115000"/></a:srgbClr></a:gs>'
        f'<a:gs pos="50000"><a:srgbClr val="0083A6"><a:shade val="67500"/><a:satMod val="115000"/></a:srgbClr></a:gs>'
        f'<a:gs pos="100000"><a:srgbClr val="0083A6"><a:shade val="100000"/><a:satMod val="115000"/></a:srgbClr></a:gs>'
        f'</a:gsLst><a:lin ang="8100000" scaled="1"/><a:tileRect/></a:gradFill>'
        f'<a:ln><a:noFill/></a:ln></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
    )
    # 标题文字（模板用青色编号 + 顿号 + 白色标题）
    parts.append(textbox(
        bar_x, bar_y, bar_w, bar_h,
        [(f"{chapter_num}", 30, COLOR["lime"], True, "Arial", "Arial"),
         ("、", 30, COLOR["white"], True, "Arial", "微软雅黑"),
         (cn_title, 30, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"
    ))
    # 横条下方黄绿色描述
    parts.append(textbox(
        bar_x, bar_y + bar_h + 200000, bar_w, 320000,
        [(desc, 14, COLOR["lime"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"
    ))
    # 英文章节标识
    parts.append(textbox(
        bar_x, bar_y + bar_h + 580000, bar_w, 260000,
        [(en_title, 11, COLOR["light_cyan"], False, "Arial", "Arial")],
        anchor="ctr", align="c"
    ))
    # 页码已按王老师要求移除
    return sld_open() + ''.join(parts) + sld_close()


def render_content(chapter_label, section_label, page_no, body_renderer):
    """内容页：深色 layout1 背景 + body 自行处理主标题/副标题/内容（无顶栏 · 无页码）"""
    reset_id()
    parts = []
    # 仅渲染主体（body 内部含 page_header）；不加顶栏、不加页码
    parts.extend(body_renderer())
    return sld_open() + ''.join(parts) + sld_close()


def render_closing(content):
    """封底页：THANK YOU + Visit + 公司"""
    reset_id()
    parts = []
    # THANK YOU 大字
    parts.append(textbox(
        680000, 2400000, 9000000, 1300000,
        [("THANK YOU", 80, COLOR["white"], True, "Arial", "Arial")],
        anchor="ctr", align="l"
    ))
    # 副标语（保留 v18 的精华）
    parts.append(textbox(
        680000, 3700000, 9000000, 360000,
        [("让每一台人形机器人 · 都拥有自己的", 18, COLOR["lime"], True, "Arial", "微软雅黑"),
         ("制造档案", 18, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    parts.append(textbox(
        680000, 4100000, 9000000, 260000,
        [("GIVE EVERY HUMANOID ROBOT ITS OWN MANUFACTURING DNA", 11, COLOR["light_cyan"], False, "Arial", "Arial")],
        anchor="ctr", align="l"
    ))
    # Visit + 公司信息
    parts.append(textbox(
        680000, 5400000, 4200000, 280000,
        [("Visit", 16, COLOR["primary"], True, "Arial", "Arial")],
        anchor="ctr", align="l"
    ))
    parts.append(textbox(
        680000, 5700000, 6000000, 260000,
        [("慧新全智工业互联科技(青岛)有限公司", 13, COLOR["white"], False, "Arial", "微软雅黑")],
        anchor="ctr", align="l"
    ))
    parts.append(textbox(
        680000, 6000000, 6000000, 240000,
        [("http://iiglocal.com/", 12, COLOR["lime"], False, "Arial", "Arial")],
        anchor="ctr", align="l"
    ))
    # 页码已按王老师要求移除
    return sld_open() + ''.join(parts) + sld_close()


# ============ 内容页主体生成器 ============

def body_p4_evolution():
    """P4: 从样机研发→走向规模化交付 (3 列卡片)"""
    parts = []
    parts.extend(page_header("从样机研发 · 走向规模化交付",
                             "技术展示 → 小批试制 → 规模化量产 · 制造运营成为下一阶段核心竞争力"))
    # 3 列卡片
    stages = [
        ("Stage 01", "样机研发期", "PROTOTYPE R&D",
         ["概念验证 · 单台手工装配", "BOM 频繁变更 · 工艺尚未固化", "关注：技术可行性 · 性能突破"],
         "制造管理重点：研发协同 · 配置基线"),
        ("Stage 02", "小批试制期", "PILOT PRODUCTION",
         ["数十至数百台 · 半自动化产线", "试制问题反哺研发", "关注：可制造性 · 质量一致性"],
         "制造管理重点：工艺定型 · 质量追溯"),
        ("Stage 03", "规模化量产期", "MASS PRODUCTION",
         ["千台/万台级 · 多基地协同", "供应链 + 测试 + 售后压力凸显", "关注：成本 · 交付 · 可追溯"],
         "制造管理重点：一体化平台 · 数据驱动"),
    ]
    card_w = 3680000
    card_h = 3700000
    gap = 200000
    x0 = (SLIDE_W - 3*card_w - 2*gap) // 2
    y0 = 1500000
    for i, (sk, cn, en, bullets, key) in enumerate(stages):
        cx = x0 + i*(card_w + gap)
        # 卡片背景（最后一个用 lime 强调）
        if i == 2:
            parts.append(rect_solid(cx, y0, card_w, 80000, COLOR["lime"]))
            parts.append(rect_solid(cx, y0+80000, card_w, card_h-80000, COLOR["card_bg_light"]))
        else:
            parts.append(rect_solid(cx, y0, card_w, 80000, COLOR["primary"]))
            parts.append(rect_solid(cx, y0+80000, card_w, card_h-80000, COLOR["card_bg_light"]))
        # Stage 编号
        parts.append(textbox(cx+200000, y0+200000, card_w-400000, 260000,
            [(sk, 11, COLOR["text_gray"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        # CN标题
        parts.append(textbox(cx+200000, y0+500000, card_w-400000, 520000,
            [(cn, 26, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        # EN副标
        parts.append(textbox(cx+200000, y0+1080000, card_w-400000, 260000,
            [(en, 10, COLOR["primary"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        # 分割线
        parts.append(rect_solid(cx+200000, y0+1380000, card_w-400000, 12700, COLOR["light_gray"]))
        # 要点
        for j, b in enumerate(bullets):
            parts.append(textbox(cx+200000, y0+1480000+j*420000, card_w-400000, 380000,
                [("● ", 11, COLOR["primary"], True, "Arial", "Arial"),
                 (b, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
                anchor="ctr", align="l"))
        # 重点底带
        parts.append(rect_solid(cx+200000, y0+card_h-440000, card_w-400000, 360000, COLOR["deep_cyan"]))
        parts.append(textbox(cx+200000, y0+card_h-440000, card_w-400000, 360000,
            [(key, 10, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
    # 底部强调横条
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("进入规模化量产期 · 比拼的不再是单台样机的性能 · 而是整套制造运营体系的成熟度",
          14, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p5_customer():
    """P5: 客户与场景分布"""
    parts = []
    parts.extend(page_header("客户与场景分布 · 多业态需求并存", "科研教育 · 工业应用 · 消费商业 · 特种场景 · 每类客户的制造要求各不相同"))
    # 4 列
    segs = [
        ("科研教育", "EDUCATION", "高校 / 研究所", ["小批 ≤ 50 台", "频繁变更", "教学/科研用途"]),
        ("工业应用", "INDUSTRIAL", "汽车 / 3C / 物流", ["数百至数千台", "稳定批次", "工艺协同复杂"]),
        ("消费商业", "CONSUMER", "服务机器人 / 商用", ["千台/万台级", "成本敏感", "迭代频繁"]),
        ("特种场景", "SPECIAL", "电力 / 安防 / 医疗", ["定制化高", "认证严格", "全程追溯"]),
    ]
    card_w = 2750000
    gap = 180000
    x0 = (SLIDE_W - 4*card_w - 3*gap) // 2
    y0 = 1450000
    card_h = 3550000
    for i, (cn, en, segment, bullets) in enumerate(segs):
        cx = x0 + i*(card_w + gap)
        # 顶色条
        bar_color = COLOR["primary"] if i % 2 == 0 else COLOR["lime"]
        parts.append(rect_solid(cx, y0, card_w, 100000, bar_color))
        parts.append(rect_solid(cx, y0+100000, card_w, card_h-100000, COLOR["card_bg_light"]))
        parts.append(textbox(cx+200000, y0+300000, card_w-400000, 540000,
            [(cn, 24, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+870000, card_w-400000, 260000,
            [(en, 10, COLOR["primary"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+200000, y0+1180000, card_w-400000, 12700, COLOR["light_gray"]))
        parts.append(textbox(cx+200000, y0+1260000, card_w-400000, 320000,
            [(segment, 12, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        for j, b in enumerate(bullets):
            parts.append(textbox(cx+200000, y0+1660000+j*440000, card_w-400000, 400000,
                [("● ", 11, bar_color, True, "Arial", "Arial"),
                 (b, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
                anchor="ctr", align="l"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("客户分布多元 · 量产能力是穿越多场景的共同底座", 14, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p6_features():
    """P6: 业务特征 · 四个并存"""
    parts = []
    parts.extend(page_header("机器人制造的业务特征 · 四个并存", "MTO 定制与 MTS 标品 · 研发与生产 · 装配与测试 · 生产与售后"))
    pairs = [
        ("MTO 定制", "vs", "MTS 标品", "定制订单与标品并存 · 工单类型多样"),
        ("研发", "vs", "生产", "研发频繁变更 · 生产要求稳定 · 协同张力"),
        ("装配", "vs", "测试", "装配工序多 · 测试环节长 · 工艺切换频繁"),
        ("生产", "vs", "售后", "前端不断量产 · 后端持续返修 · 数据要互通"),
    ]
    card_w = 5600000
    card_h = 1900000
    gap_x = 200000
    gap_y = 200000
    y0 = 1450000
    for i, (a, vs, b, desc) in enumerate(pairs):
        col = i % 2
        row = i // 2
        cx = 280000 + col*(card_w + gap_x)
        cy = y0 + row*(card_h + gap_y)
        # 卡片
        parts.append(rect_solid(cx, cy, card_w, 80000, COLOR["primary"]))
        parts.append(rect_solid(cx, cy+80000, card_w, card_h-80000, COLOR["card_bg_light"]))
        # A 块
        parts.append(rect_solid(cx+200000, cy+260000, 2300000, 800000, COLOR["deep_cyan"]))
        parts.append(textbox(cx+200000, cy+260000, 2300000, 800000,
            [(a, 22, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
        # VS
        parts.append(textbox(cx+2500000, cy+260000, 600000, 800000,
            [(vs, 18, COLOR["primary"], True, "Arial", "Arial")],
            anchor="ctr", align="c"))
        # B 块
        parts.append(rect_solid(cx+3100000, cy+260000, 2300000, 800000, COLOR["lime"]))
        parts.append(textbox(cx+3100000, cy+260000, 2300000, 800000,
            [(b, 22, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
        # 描述
        parts.append(textbox(cx+200000, cy+1180000, card_w-400000, 600000,
            [(desc, 13, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("「四个并存」是机器人制造的天然属性 · 也是 MOM 体系必须直面的设计起点",
          14, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p7_complexity():
    """P7: 制造复杂性 · 六重门"""
    parts = []
    parts.extend(page_header("制造的六重复杂性", "复杂 BOM / 精密装配 / 软硬联调 / 质量一致性 / 小批多变 / 全程追溯"))
    items = [
        ("01", "复杂 BOM", "Complex BOM", "千级零部件 + 多层级结构 + 软硬件混合"),
        ("02", "精密装配", "Precision Assembly", "关节/电机/传感器精度堆叠 · 工艺敏感"),
        ("03", "软硬联调", "Hw-Sw Integration", "电气调试 + 控制标定 + AI 模型部署"),
        ("04", "质量一致性", "Quality Consistency", "批次间一致性差 · 影响整机性能"),
        ("05", "小批多变", "High-Mix Low-Vol", "订单切换频繁 · 工艺切换成本高"),
        ("06", "全程追溯", "Full Traceability", "整机 SN → 部件 → 物料批次 全链路"),
    ]
    card_w = 3680000
    card_h = 1800000
    gap_x = 200000
    gap_y = 180000
    y0 = 1450000
    for i, (num, cn, en, desc) in enumerate(items):
        col = i % 3
        row = i // 3
        cx = (SLIDE_W - 3*card_w - 2*gap_x) // 2 + col*(card_w + gap_x)
        cy = y0 + row*(card_h + gap_y)
        # 左边色块编号
        parts.append(rect_solid(cx, cy, 600000, card_h, COLOR["deep_cyan"]))
        parts.append(textbox(cx, cy, 600000, card_h,
            [(num, 38, COLOR["lime"], True, "Arial", "Arial")],
            anchor="ctr", align="c"))
        # 右侧白底
        parts.append(rect_solid(cx+600000, cy, card_w-600000, card_h, COLOR["card_bg_light"]))
        parts.append(textbox(cx+780000, cy+200000, card_w-960000, 420000,
            [(cn, 22, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+780000, cy+660000, card_w-960000, 260000,
            [(en, 10, COLOR["primary"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+780000, cy+970000, card_w-960000, 12700, COLOR["light_gray"]))
        parts.append(textbox(cx+780000, cy+1060000, card_w-960000, 700000,
            [(desc, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("六重复杂性叠加 · 单点工具无法解决 · 必须靠一体化平台串联", 14, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p9_painpoints():
    """P9 痛点总览 - 深色卡片化表格（按王老师参考样式：行间留白、全深色行卡片）"""
    parts = []
    parts.extend(page_header("6 大业务域 · 全链路痛点全景", "研发协同 / 生产执行 / 仓储物流 / 质量管理 / 设备管理 / 售后追溯"))
    # 表头
    headers = ["痛点域 · DOMAIN", "典型问题 · TYPICAL ISSUE", "业务后果 · BUSINESS IMPACT"]
    col_w = [2400000, 5400000, 3800000]
    x0 = 280000
    y0 = 1375000
    # 表头深色块
    cx = x0
    for i, h in enumerate(headers):
        parts.append(rect_solid(cx, y0, col_w[i], 380000, COLOR["deep_cyan"]))
        parts.append(textbox(cx+150000, y0, col_w[i]-150000, 380000,
            [(h, 12, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        cx += col_w[i]
    # 行数据 - 全深色卡片化
    rows = [
        ("研发制造协同", "BOM / 工艺 / 图纸变更传递不及时", "现场错装 · 返工 · 等待"),
        ("生产执行", "工单、报工、齐套、上线数据不透明", "停线 · WIP 不清 · 进度失真"),
        ("仓储物流", "核心件与批次件混存 · 线边余料难管", "错发 · 呆滞 · 账实不一致"),
        ("质量管理", "IQC/IPQC/FQC · MRB · 计量数据离线", "异常闭环慢 · 质量证据链断"),
        ("设备管理", "点检保养、维修、备件与 OEE 分散", "故障响应慢 · 成本难归集"),
        ("售后追溯", "整机 SN 反查部件与批次困难", "客诉响应慢 · 影响范围难锁定"),
    ]
    row_h = 480000
    row_gap = 80000  # 行间留白（让每行像独立卡片）
    header_h = 380000
    header_gap = 120000
    for ri, row in enumerate(rows):
        ry = y0 + header_h + header_gap + ri*(row_h + row_gap)
        # 整行深色卡片底（统一用 card_bg_light）
        parts.append(rect_solid(x0, ry, sum(col_w), row_h, COLOR["card_bg_light"]))
        # 第一列左侧黄绿色窄条（图标位代替）
        parts.append(rect_solid(x0, ry, 60000, row_h, COLOR["lime"]))
        cx = x0
        for i, cell in enumerate(row):
            if i == 0:
                parts.append(textbox(cx+220000, ry, col_w[i]-220000, row_h,
                    [(cell, 14, COLOR["white"], True, "Arial", "微软雅黑")],
                    anchor="ctr", align="l"))
            elif i == 1:
                parts.append(textbox(cx+150000, ry, col_w[i]-150000, row_h,
                    [(cell, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
                    anchor="ctr", align="l"))
            else:
                parts.append(textbox(cx+150000, ry, col_w[i]-150000, row_h,
                    [(cell, 11, COLOR["orange"], True, "Arial", "微软雅黑")],
                    anchor="ctr", align="l"))
            cx += col_w[i]
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("痛点不是孤立的 · 是横跨研发、生产、仓储、质量、设备、售后的一条系统性断链",
          13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def _render_three_col_card(cx, y0, card_w, card_h, accent, icon_file, en_label, cn_label, bullets, value_style=False):
    """通用三栏卡片渲染（新设计：大图标+大字+大数字）"""
    parts = []
    # 顶部色条（加高到 160K）
    parts.append(rect_solid(cx, y0, card_w, 160000, accent))
    # 卡片主体
    parts.append(rect_solid(cx, y0+160000, card_w, card_h-160000, COLOR["card_bg_light"]))
    # 顶部大图标（白色 80×80pt）居中
    icon_size = 720000
    parts.append(picture_xml(
        cx + card_w//2 - icon_size//2,
        y0 + 260000,
        icon_size, icon_size,
        media_file=icon_file
    ))
    # EN 标签（13pt，居中）
    parts.append(textbox(cx+240000, y0+1020000, card_w-480000, 280000,
        [(en_label, 13, accent, True, "Arial", "Arial")],
        anchor="ctr", align="c"))
    # CN 大标题（28pt，居中）
    parts.append(textbox(cx+240000, y0+1320000, card_w-480000, 480000,
        [(cn_label, 28, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    # 分割线（在大标题下方）
    parts.append(rect_solid(cx+card_w//2 - 200000, y0+1860000, 400000, 20000, accent))
    # 要点列表
    y_bullet = y0 + 1980000
    if value_style:
        # 价值/影响样式：每个要点拆"大数字 + 小描述"
        item_h = 440000
        for j, b in enumerate(bullets[:5]):
            ry = y_bullet + j*item_h
            # 拆分"数字 · 描述"（用 ":" 或 "·" 分隔）
            if "：" in b or ":" in b or "·" in b:
                sep = "：" if "：" in b else (":" if ":" in b else "·")
                num_part, desc_part = b.split(sep, 1)
                num_part = num_part.strip()
                desc_part = desc_part.strip()
            else:
                num_part = b
                desc_part = ""
            parts.append(textbox(cx+240000, ry, card_w-480000, item_h,
                [(num_part, 18, accent, True, "Arial", "Arial"),
                 ("  " + desc_part if desc_part else "", 13, COLOR["white"], False, "Arial", "微软雅黑")],
                anchor="ctr", align="l"))
    else:
        # 普通样式：● + 14pt 要点
        item_h = 440000
        for j, b in enumerate(bullets[:5]):
            ry = y_bullet + j*item_h
            parts.append(textbox(cx+240000, ry, card_w-480000, item_h,
                [("● ", 14, accent, True, "Arial", "Arial"),
                 (b, 14, COLOR["white"], False, "Arial", "微软雅黑")],
                anchor="ctr", align="l"))
    return parts


def body_psv(scenario_title, scenario_sub, pains, solutions, values, summary):
    """通用 痛点-方案-价值 三栏（新版：大图标+大字+大数字）"""
    parts = []
    parts.extend(page_header(scenario_title, scenario_sub))
    card_w = 3680000
    card_h = 4180000
    gap_x = 200000
    x0 = (SLIDE_W - 3*card_w - 2*gap_x) // 2
    y0 = 1450000
    # 三栏
    cols = [
        (COLOR["orange"], "icon_alert.png",  "PAIN POINT",  "业务痛点", pains,     False),
        (COLOR["primary"], "icon_check.png", "SOLUTION",    "解决方案", solutions, False),
        (COLOR["lime"],    "icon_chart.png", "VALUE",       "价值收益", values,    True),
    ]
    for i, (accent, icon, en, cn, bullets, vstyle) in enumerate(cols):
        cx = x0 + i*(card_w + gap_x)
        parts.extend(_render_three_col_card(cx, y0, card_w, card_h, accent, icon, en, cn, bullets, value_style=vstyle))
    # 底部金句（加大字号）
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [(summary, 15, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_pain_only(scenario_title, scenario_sub, current_state, pains, impacts, warning):
    """纯痛点三栏（新版：大图标+大字+影响数字突出）"""
    parts = []
    parts.extend(page_header(scenario_title, scenario_sub))
    card_w = 3680000
    card_h = 4180000
    gap_x = 200000
    x0 = (SLIDE_W - 3*card_w - 2*gap_x) // 2
    y0 = 1450000
    # 三栏（全负向）
    cols = [
        ("85CDDB",           "icon_eye.png",   "PRESENT STATE",   "现状描述", current_state, False),
        (COLOR["orange"],    "icon_alert.png", "PAIN POINTS",     "痛点表现", pains,         False),
        ("E74C3C",           "icon_loss.png",  "BUSINESS IMPACT", "业务影响", impacts,       True),
    ]
    for i, (accent, icon, en, cn, bullets, vstyle) in enumerate(cols):
        cx = x0 + i*(card_w + gap_x)
        parts.extend(_render_three_col_card(cx, y0, card_w, card_h, accent, icon, en, cn, bullets, value_style=vstyle))
    # 底部警示金句（橙色底）加大字号
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["orange"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("⚠  ", 15, COLOR["white"], True, "Arial", "微软雅黑"),
         (warning, 15, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p10_psv():
    """P11 场景 1 · 生产追溯断链 · 纯痛点"""
    return body_pain_only(
        "场景 1 · 生产追溯断链",
        "整机交付后客诉响应数日 · 影响范围无法快速锁定",
        # 现状描述：现在是怎么做的
        ["整机 SN/部件 SN/物料批次 分散多系统 Excel 维护",
         "返修换件靠纸单记录 · 旧档案靠人工归档",
         "批次码生成靠车间打印机 · 无系统受控",
         "客诉处理：跨 MES/WMS/QMS/SRM 手工拉数",
         "供应商批次异常：人工拉 ERP 历史排查"],
        # 痛点表现
        ["四层 SN 追溯断链 · 关联关系易丢",
         "返修后旧档案未失效 · 新档案未生成",
         "批次码生成/变更 无受控记录",
         "客诉根因定位耗时 数日级",
         "供应商异常影响面无法快速锁定"],
        # 业务影响（大数字：描述 格式）
        ["3-7 天：客诉响应周期",
         "10 倍+：召回成本超实际异常",
         "下滑：客户满意度受损",
         "难举证：供应商质量索赔",
         "指数级：规模越大损失越大"],
        "如果不解决 · 量产规模化时 · 一次批次异常可能让整条生产线停摆"
    )

def body_p11_psv():
    """P12 场景 2 · 齐套与上线失控 · 纯痛点"""
    return body_pain_only(
        "场景 2 · 齐套与上线失控",
        "派工后才发现缺料 · 整线工位停摆",
        ["BOM 需求与库存 ERP/WMS 异步",
         "线边仓 班组长用 Excel 记录",
         "派工齐套 靠人工巡线检查",
         "替代料 各车间各自处理",
         "缺料处理 走 OA 审批等待"],
        ["BOM 与库存数据 时延数小时",
         "线边仓账实分离 错发错领",
         "齐套漏检 派工后才发现缺料",
         "替代料无规则 导致批量返工",
         "呆滞物料 库龄无预警 越积越多"],
        ["15-20%：停线等待占工时",
         "30%+：线边呆滞库存占比",
         "返工：替代料误用",
         "≤70%：工单按时齐套率",
         "低于设计：产能利用率"],
        "齐套问题不解决 · 排产计划永远只是「美好的计划」 · 现场永远在救火"
    )

def body_p12_psv():
    """P13 场景 3 · 质量与设备闭环不足 · 纯痛点"""
    return body_pain_only(
        "场景 3 · 质量与设备闭环不足",
        "质量异常无系统闭环 · OEE 数据沉淀缺失",
        ["IQC/IPQC/FQC 单据 纸单/Excel",
         "MRB 评审 走线下会议确认",
         "设备点检 班组长抄表月底汇总",
         "设备维修 凭经验无知识库",
         "备件采购 安全库存拍脑袋"],
        ["检验数据 滞后 1-3 天 · 异常发现慢",
         "MRB 评审 无留痕 · 责任难追溯",
         "OEE 算不出 · 设备瓶颈靠主观",
         "维修经验 流失 · 老师傅离职即损失",
         "备件 呆滞与短缺 并存"],
        ["数天-数周：质量异常处理周期",
         "跨系统：客诉根因定位困难",
         "难量化：设备故障停机时间",
         "20%+：备件成本占设备成本",
         "无沉淀：维修知识"],
        "质量与设备数据不闭环 · 「制造档案」永远缺一半 · 客户决策无依据"
    )

def _shape_geom(prst, x, y, w, h, fill_color, name="Shape", ln_color=None):
    """通用 prstGeom 形状（用于自制图标）"""
    sid = new_id()
    if ln_color:
        ln_xml = f'<a:ln w="6350"><a:solidFill><a:srgbClr val="{ln_color}"/></a:solidFill></a:ln>'
    else:
        ln_xml = '<a:ln><a:noFill/></a:ln>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill_color}"/></a:solidFill>{ln_xml}</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')


def make_icon(icon_type, cx, cy, size):
    """根据 icon_type 生成图标 XML（cx,cy 为图标中心点）"""
    x = cx - size // 2
    y = cy - size // 2
    parts = []
    W = COLOR["white"]
    L = COLOR["lime"]
    P = COLOR["primary"]
    DC = COLOR["deep_cyan"]

    if icon_type == "document":
        # 文档：白色圆角矩形 + 3 条横线（订单/需求）
        parts.append(_shape_geom("roundRect", x+size*15//100, y+size*5//100, size*70//100, size*90//100, W))
        for i in range(3):
            ly = y + size*30//100 + i*size*15//100
            parts.append(_shape_geom("rect", x+size*28//100, ly, size*44//100, size*4//100, P))
    elif icon_type == "calendar":
        # 日历：圆角矩形 + 顶部 lime 条 + 6 个小方块
        parts.append(_shape_geom("roundRect", x+size*8//100, y+size*15//100, size*84//100, size*78//100, W))
        parts.append(_shape_geom("rect", x+size*8//100, y+size*15//100, size*84//100, size*18//100, L))
        # 顶部两个小挂耳
        parts.append(_shape_geom("rect", x+size*22//100, y+size*5//100, size*8//100, size*15//100, W))
        parts.append(_shape_geom("rect", x+size*70//100, y+size*5//100, size*8//100, size*15//100, W))
        # 日期点阵
        for r in range(2):
            for c in range(3):
                dx = x + size*20//100 + c*size*22//100
                dy = y + size*50//100 + r*size*18//100
                parts.append(_shape_geom("rect", dx, dy, size*12//100, size*10//100, P))
    elif icon_type == "cube":
        # 立方体（包装盒）
        parts.append(_shape_geom("cube", x+size*5//100, y+size*5//100, size*80//100, size*80//100, W))
    elif icon_type == "gear":
        # 齿轮（部件装配）
        parts.append(_shape_geom("gear6", x+size*5//100, y+size*5//100, size*90//100, size*90//100, W))
    elif icon_type == "robot":
        # 机器人：头（圆角矩形）+ 天线（小圆）+ 身体（矩形）+ 眼睛
        parts.append(_shape_geom("ellipse", x+size*42//100, y+size*0, size*16//100, size*15//100, W))  # 天线
        parts.append(_shape_geom("roundRect", x+size*20//100, y+size*15//100, size*60//100, size*40//100, W))  # 头
        parts.append(_shape_geom("ellipse", x+size*30//100, y+size*30//100, size*10//100, size*10//100, P))  # 左眼
        parts.append(_shape_geom("ellipse", x+size*60//100, y+size*30//100, size*10//100, size*10//100, P))  # 右眼
        parts.append(_shape_geom("roundRect", x+size*25//100, y+size*60//100, size*50//100, size*35//100, W))  # 身
    elif icon_type == "monitor":
        # 显示器：屏幕 + 底座
        parts.append(_shape_geom("roundRect", x+size*8//100, y+size*10//100, size*84//100, size*60//100, W))
        parts.append(_shape_geom("rect", x+size*15//100, y+size*20//100, size*70//100, size*40//100, P))  # 屏幕里面
        # 屏幕内波形
        parts.append(_shape_geom("rect", x+size*22//100, y+size*38//100, size*56//100, size*4//100, L))
        # 底座
        parts.append(_shape_geom("rect", x+size*42//100, y+size*70//100, size*16//100, size*12//100, W))
        parts.append(_shape_geom("rect", x+size*25//100, y+size*82//100, size*50//100, size*8//100, W))
    elif icon_type == "shield":
        # 盾牌（五边形向下尖） + 内部对勾
        # 用 pentagon 倒置（无 prst 旋转，用 homePlate 替代）
        parts.append(_shape_geom("homePlate", x+size*15//100, y+size*5//100, size*70//100, size*85//100, W))
        # 对勾（两个旋转矩形太复杂，用一个三角组合）
        parts.append(_shape_geom("rtTriangle", x+size*30//100, y+size*38//100, size*40//100, size*22//100, P))
    elif icon_type == "truck":
        # 卡车：车厢矩形 + 车头矩形（高） + 2 个轮子
        parts.append(_shape_geom("rect", x+size*5//100, y+size*30//100, size*55//100, size*38//100, W))   # 车厢
        parts.append(_shape_geom("rect", x+size*60//100, y+size*42//100, size*30//100, size*26//100, W))  # 车头
        # 车窗
        parts.append(_shape_geom("rect", x+size*65//100, y+size*47//100, size*20//100, size*15//100, P))
        # 车轮
        parts.append(_shape_geom("ellipse", x+size*12//100, y+size*68//100, size*20//100, size*20//100, L))
        parts.append(_shape_geom("ellipse", x+size*62//100, y+size*68//100, size*20//100, size*20//100, L))
    elif icon_type == "headset":
        # 耳机：圆环（顶部弧）+ 两个耳罩矩形
        parts.append(_shape_geom("donut", x+size*5//100, y+size*5//100, size*90//100, size*70//100, W))
        # 遮住下半部分（让圆环变成倒 U 形）
        parts.append(_shape_geom("rect", x+size*5//100, y+size*45//100, size*90//100, size*30//100, DC))
        # 两个耳罩
        parts.append(_shape_geom("roundRect", x+size*0, y+size*38//100, size*22//100, size*38//100, W))
        parts.append(_shape_geom("roundRect", x+size*78//100, y+size*38//100, size*22//100, size*38//100, W))
        # 麦克风（小细矩形）
        parts.append(_shape_geom("rect", x+size*8//100, y+size*72//100, size*30//100, size*6//100, L))
    else:
        parts.append(_shape_geom("rect", x, y, size, size, W))
    return parts


def body_p14_platform():
    """P14: 研产供销服一体化平台（按思维导图：研发+生产+供应链+销售+服务）"""
    parts = []
    parts.extend(page_header("研产供销服一体化平台 · 搭建机器人量产的运营主线", "研发 · 生产 · 供应链 · 销售 · 服务 五大业务域 · 一个平台贯通"))
    # 5 大业务域 + 平台底座 + IoT 设施层
    domains = [
        ("研", "研发", "R&D", ["PLM 主版本", "BOM/工艺", "CAE 仿真", "精度检测", "ECN 变更"], COLOR["primary"]),
        ("产", "生产", "PRODUCTION", ["MES 工单", "排产/齐套", "报工追溯", "三大检验", "OEE/EAM"], COLOR["deep_cyan"]),
        ("供", "供应链", "SUPPLY", ["SRM 协同", "WMS 仓储", "线边/委外", "批次/SN", "物料拉动"], COLOR["lime"]),
        ("销", "销售", "SALES", ["订单 → ERP", "客户档案", "需求池", "发货交付", "销售看板"], COLOR["primary"]),
        ("服", "服务", "SERVICE", ["售后客诉", "整机追溯", "返修换件", "经验沉淀", "服务档案"], COLOR["deep_cyan"]),
    ]
    card_w = 2200000
    gap = 130000
    total_w = 5*card_w + 4*gap
    x0 = (SLIDE_W - total_w) // 2
    y0 = 1335000
    card_h = 2900000
    for i, (zh, cn, en, items, color) in enumerate(domains):
        cx = x0 + i*(card_w + gap)
        # 顶部色条
        parts.append(rect_solid(cx, y0, card_w, 80000, color))
        # 主卡片底
        parts.append(rect_solid(cx, y0+80000, card_w, card_h-80000, COLOR["card_bg_light"]))
        # 大字
        parts.append(rect_solid(cx+200000, y0+200000, 580000, 580000, color))
        parts.append(textbox(cx+200000, y0+200000, 580000, 580000,
            [(zh, 36, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
        # 中文标签
        parts.append(textbox(cx+800000, y0+260000, card_w-1000000, 320000,
            [(cn, 20, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+800000, y0+570000, card_w-1000000, 240000,
            [(en, 10, color, True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        # 分割线
        parts.append(rect_solid(cx+200000, y0+880000, card_w-400000, 12700, COLOR["light_gray"]))
        # 要点列表
        for j, it in enumerate(items):
            parts.append(textbox(cx+200000, y0+960000+j*340000, card_w-400000, 300000,
                [("●  ", 10, color, True, "Arial", "Arial"),
                 (it, 11, COLOR["white"], False, "Arial", "微软雅黑")],
                anchor="ctr", align="l"))
    # 底部平台底座（横跨）
    base_y = y0 + card_h + 100000
    parts.append(rect_solid(280000, base_y, 11600000, 60000, COLOR["lime"]))
    parts.append(rect_solid(280000, base_y+60000, 11600000, 480000, COLOR["card_bg_light"]))
    parts.append(textbox(380000, base_y+80000, 2200000, 460000,
        [("一体化平台底座", 14, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"))
    base_items = ["低代码扩展", "工作流引擎", "主数据治理", "码体系", "集成网关", "IoT 数采", "BI 看板"]
    bx0 = 2600000
    bw = (SLIDE_W - bx0 - 280000 - (len(base_items)-1)*80000) // len(base_items)
    for i, it in enumerate(base_items):
        bx = bx0 + i*(bw + 80000)
        parts.append(rect_solid(bx, base_y+120000, bw, 360000, COLOR["deep_cyan"]))
        parts.append(textbox(bx, base_y+120000, bw, 360000,
            [(it, 11, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("研产供销服 · 不是 5 个系统 · 而是 1 条贯穿机器人量产全周期的运营主线",
          13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p15_architecture():
    """P16 业务流程闭环：9 节点方块（含专属图标）+ 箭头 + 下方说明 + 数字主线金句"""
    parts = []
    parts.extend(page_header("覆盖人形机器人量产全过程的核心业务场景",
                             "需求 → 计划 → 齐套 → 装配 → 测试 → 质量 → 仓储 → 售后 · 数字主线贯通"))
    # 9 个业务流程节点：(中文名, 图标类型, 要点列表)
    nodes = [
        ("需求/订单",  "document", ["APS", "产能平衡", "交期承诺"]),
        ("计划排产",  "calendar", ["BOM 校验", "批次追溯", "替代料管理"]),
        ("物料齐套",  "cube",     ["关节模组", "灵巧手", "线束", "电控装配"]),
        ("部件装配",  "gear",     ["工艺指导", "防错校验", "SN 绑定"]),
        ("整机装配",  "robot",    ["工艺指导", "防错校验", "SN 绑定"]),
        ("测试验证",  "monitor",  ["EOL 测试", "运动测试", "标定测试"]),
        ("质量放行",  "shield",   ["检验判定", "异常处理", "质量档案"]),
        ("仓储发货",  "truck",    ["成品入库", "包装", "物流跟踪"]),
        ("售后反馈",  "headset",  ["故障追溯", "问题闭环", "设计改进"]),
    ]
    n = 9
    # 顶部 9 个方块横排（青色方块 + 专属图标）
    box_w = 1100000
    arrow_w = 180000
    total_w = n*box_w + (n-1)*arrow_w
    x0 = (SLIDE_W - total_w) // 2
    box_y = 1400000
    box_h = 1100000
    for i, (cn, icon_type, items) in enumerate(nodes):
        bx = x0 + i*(box_w + arrow_w)
        # 顶部黄绿小三角装饰
        parts.append(rect_solid(bx, box_y, 120000, 60000, COLOR["lime"]))
        # 主方块（青色）
        parts.append(rect_solid(bx, box_y+60000, box_w, box_h-60000, COLOR["primary"]))
        # 中部专属图标（iconfont 风格 · 嵌入 PNG）
        icon_cx = bx + box_w//2
        icon_cy = box_y + 400000
        icon_size = 460000
        icon_file = f"icon_{icon_type if icon_type != 'gear' else 'gear'}.png"
        # 节点类型到图标文件的映射
        icon_map = {
            "document": "icon_document.png",
            "calendar": "icon_calendar.png",
            "cube":     "icon_package.png",
            "gear":     "icon_gear.png",
            "robot":    "icon_robot.png",
            "monitor":  "icon_monitor.png",
            "shield":   "icon_shield.png",
            "truck":    "icon_truck.png",
            "headset":  "icon_headset.png",
        }
        media_name = icon_map.get(icon_type, "icon_document.png")
        parts.append(picture_xml(icon_cx - icon_size//2, icon_cy - icon_size//2,
                                 icon_size, icon_size, media_file=media_name))
        # 中文标题（白色大字）
        parts.append(textbox(bx, box_y+700000, box_w, 380000,
            [(cn, 14, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
        # 箭头（除最后一个）
        if i < n-1:
            ax = bx + box_w + 20000
            ay = box_y + box_h//2 - 30000
            parts.append(rect_solid(ax, ay, arrow_w-40000, 60000, COLOR["primary"]))
    # 中部箭头连线（每个方块到下方说明卡片的连接）省略，用上下间距表现
    # 下方说明卡片（白色边框深色卡片）
    desc_y = box_y + box_h + 200000
    desc_h = 2500000
    for i, (cn, icon_type, items) in enumerate(nodes):
        dx = x0 + i*(box_w + arrow_w)
        # 卡片边框（白色细线）
        parts.append(rect_solid(dx, desc_y, box_w, desc_h, COLOR["card_bg_light"]))
        # 顶部装饰条
        parts.append(rect_solid(dx, desc_y, box_w, 40000, COLOR["lime"]))
        # 要点列表
        for j, item in enumerate(items[:6]):
            parts.append(textbox(dx+80000, desc_y+120000+j*340000, box_w-160000, 320000,
                [("● ", 11, COLOR["primary"], True, "Arial", "Arial"),
                 (item, 10, COLOR["white"], False, "Arial", "微软雅黑")],
                anchor="ctr", align="l"))
    # 底部"数字主线"金句（大字 + 黄绿色高亮）
    summary_y = 5860000
    parts.append(rect_solid(280000, summary_y, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, summary_y, 11600000, 380000,
        [("以 ", 13, COLOR["white"], True, "Arial", "微软雅黑"),
         ("「数字主线」", 16, COLOR["lime"], True, "Arial", "微软雅黑"),
         (" 贯穿计划、制造、质量、供应链与售后 · 实现规模量产 ", 13, COLOR["white"], True, "Arial", "微软雅黑"),
         ("可控、可追溯、可优化", 13, COLOR["lime"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p16_dataline():
    """P16: 数据主线"""
    parts = []
    parts.extend(page_header("数据主线 · 整机 SN 驱动全链路追溯", "所有场景最终都要回到同一条数字主线 · 整机 SN 是这条主线的索引"))
    # 中央大块：整机SN
    parts.append(rect_solid(280000, 1900000, 11600000, 1000000, COLOR["deep_cyan"]))
    parts.append(textbox(280000, 1900000, 11600000, 1000000,
        [("整机 SN", 36, COLOR["lime"], True, "Arial", "Arial"),
         (" · ", 36, COLOR["white"], True, "Arial", "Arial"),
         ("Robot Serial Number", 18, COLOR["white"], False, "Arial", "Arial")],
        anchor="ctr", align="c"))
    # 向下散开的关联节点
    nodes = [
        ("核心件 SN", "电机/减速器/传感器/控制器"),
        ("物料批次", "批次码/供应商/入厂日期"),
        ("工艺工单", "BOM/工艺/操作员"),
        ("质量记录", "IQC/IPQC/FQC/MRB"),
        ("设备 OEE", "工位/设备/异常记录"),
        ("售后记录", "客诉/维修/换件"),
    ]
    nn = len(nodes)
    node_w = (11600000 - 5*100000) // nn
    ny = 3200000
    for i, (cn, desc) in enumerate(nodes):
        nx = 280000 + i*(node_w + 100000)
        # 箭头线
        parts.append(rect_solid(nx + node_w//2 - 6350, 2900000, 12700, 300000, COLOR["primary"]))
        parts.append(rect_solid(nx, ny, node_w, 80000, COLOR["primary"]))
        parts.append(rect_solid(nx, ny+80000, node_w, 1700000, COLOR["card_bg_light"]))
        parts.append(textbox(nx, ny+200000, node_w, 380000,
            [(cn, 16, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
        parts.append(rect_solid(nx+200000, ny+640000, node_w-400000, 12700, COLOR["light_gray"]))
        parts.append(textbox(nx+200000, ny+720000, node_w-400000, 1000000,
            [(desc, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="t", align="c"))
    # 底部结论
    parts.append(rect_solid(280000, 5300000, 11600000, 500000, COLOR["lime"]))
    parts.append(textbox(280000, 5300000, 11600000, 500000,
        [("一根整机 SN · 串起 6 条数据线 · 让每台机器人都有完整的「制造档案」",
          14, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("数据主线 = 业务主线 = 决策主线 · 三线合一 · 才是真正的「一体化」",
          13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p18_base():
    return body_scenario(
        "一体化底座平台 · 消除孤岛",
        "主数据 / 编码 / 工作流 / 集成 / 权限 一处治理",
        "PLATFORM FOUNDATION · ONE GOVERNANCE",
        [
            ("主数据治理", "物料/客户/供应商/工艺 统一", "MDM"),
            ("编码体系", "整机 SN/批次码/库位码 统一规则", "SN/Batch"),
            ("工作流引擎", "审批/通知/流转 飞书无缝集成", "Workflow"),
            ("集成网关", "MES/WMS/QMS/EAM/PLM/ERP 互联", "API/MQ"),
            ("权限模型", "组织/角色/数据权限 一处定义", "IAM"),
            ("低代码扩展", "业务表单/报表/工作流 可扩展", "Low-Code"),
        ],
        "底座的价值不是「平台」· 而是消除业务系统之间的接缝与重复建设"
    )

def body_p19_rd():
    """研发管理：CAE/精度检测 + PLM/BOM/工艺 + ECN（按思维导图补 CAE/精度检测）"""
    return body_scenario(
        "研发管理 · 把试制经验沉淀为量产工艺",
        "CAE 仿真 · 精度检测 · PLM/BOM/工艺 · ECN 变更 · 配置基线 · 全周期协同",
        "R&D · CARRYOVER FROM PILOT TO MASS",
        [
            ("CAE 仿真", "结构/力学/电热 仿真 + 数据回写 PLM", "CAE"),
            ("精度检测", "三坐标/光学/激光 · 与 QMS 联动", "Metrology"),
            ("PLM/BOM 主版本", "PLM 主管 · MES/QMS 订阅", "PLM/BOM"),
            ("工艺路线", "试制工艺 → 量产工艺 沉淀", "Process"),
            ("ECN 变更", "影响分析 · 现场实时下发", "ECN/ECO"),
            ("配置基线", "整机 SN 关联当时配置基线", "Baseline"),
        ],
        "研发管理不是「画图 + Excel」· 是把 CAE+精度数据 沉淀进可复制的量产工艺"
    )

def body_scenario(title, sub, en, items, summary):
    """通用 6 卡片场景页"""
    parts = []
    parts.extend(page_header(title, sub))
    # 6 卡片
    card_w = 3680000
    card_h = 1800000
    gap_x = 200000
    gap_y = 180000
    y0 = 1450000
    for i, (cn, desc, tag) in enumerate(items):
        col = i % 3
        row = i // 3
        cx = (SLIDE_W - 3*card_w - 2*gap_x) // 2 + col*(card_w + gap_x)
        cy = y0 + row*(card_h + gap_y)
        accent = COLOR["primary"] if i % 2 == 0 else COLOR["lime"]
        parts.append(rect_solid(cx, cy, card_w, 80000, accent))
        parts.append(rect_solid(cx, cy+80000, card_w, card_h-80000, COLOR["card_bg_light"]))
        parts.append(textbox(cx+200000, cy+200000, card_w-400000, 460000,
            [(cn, 18, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+200000, cy+700000, card_w-400000, 12700, COLOR["light_gray"]))
        parts.append(textbox(cx+200000, cy+800000, card_w-400000, 800000,
            [(desc, 12, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        # 右上角标签
        parts.append(rect_solid(cx+card_w-1000000, cy+240000, 880000, 280000, COLOR["deep_cyan"]))
        parts.append(textbox(cx+card_w-1000000, cy+240000, 880000, 280000,
            [(tag, 9, COLOR["white"], True, "Arial", "Arial")],
            anchor="ctr", align="c"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [(summary, 13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p20_mes1():
    """MES 场景 1 · 生产追溯（四层 SN 体系：整机→PCBA→模块→部件，按宇树 P44 升级）"""
    return body_psv(
        "MES 场景 1 · 生产追溯 · 四层 SN 体系",
        "整机 SN ⇋ PCBA SN ⇋ 模块 SN ⇋ 部件 SN ⇋ 物料批次 · 一物一码 · 全档案受控",
        ["整机/PCBA/模块/部件/批次 分散多系统", "返修换件后追溯关系易断 · 旧档案未失效",
         "客诉时跨系统手工拉数 · 数日定位", "批次码生成/打印/变更 无受控记录"],
        ["四层 SN 绑定：整机 ↔ PCBA ↔ 模块 ↔ 部件 ↔ 批次", "条码追溯体系：一物一码 + 防呆防错 + 双向追溯",
         "扫码设备选型：扫码枪/PDA + 便携打印 + RFID", "返修换件同步更新当前+历史配置 旧档案归档"],
        ["客诉根因定位 数日 → 10 分钟级", "供应商批次异常正向定位影响整机",
         "全链路追溯覆盖率 100%", "形成机器人「制造档案」 可复用沉淀"],
        "MES 不是「报工系统」· 而是整机制造档案的生成系统 + 一物一码的执行平台"
    )

def body_p21_mes2():
    return body_psv(
        "MES 场景 2 · 报工线上化",
        "工单开工 / 上工 / 报工 / 报检 / 完工 全流程在线",
        ["纸质报工 · 数据滞后", "工单状态不透明 · WIP 不清",
         "报工与质量/物料/设备数据脱节", "工时/产量统计靠人工汇总"],
        ["PDA/工位屏报工 · 实时回写", "工单状态机+流转日志全留痕",
         "报工自动联动 BOM 消耗与质检触发", "工时/产量按工单/工序/人员自动统计"],
        ["WIP 透明度提升 100%", "数据滞后 → 实时",
         "报工录入耗时下降 60%", "工时/产量数据可直接进 KPI"],
        "报工是「数据采集口」· 也是制造档案的写入点"
    )

def body_p22_mes3():
    return body_psv(
        "MES 场景 3 · 齐套检查",
        "BOM 需求 → 库存查询 → 缺料推送 → 红绿放行",
        ["排程下达后才发现缺料", "线边库存账实分离",
         "替代料/呆料无规则", "缺料处理流程靠线下"],
        ["齐套检查嵌入排程下达环节", "线边仓虚拟化 · 账实一致",
         "替代料规则化 · 自动匹配", "缺料推送/审批/补料 全在线"],
        ["缺料停线时间下降 40%", "齐套准确率 95%+",
         "线边呆滞下降 30%", "工单准时齐套率提升 25%"],
        "齐套不是「检查动作」· 而是排程系统的前置门禁"
    )

def body_p23_mes4():
    """生产排产管理（替换原改制管理 · 按思维导图）"""
    return body_psv(
        "MES 场景 4 · 生产排产管理",
        "销售预测 → 主计划 → 物料需求 → 排产 → 齐套前置 · 工单准时齐套",
        ["销售预测/订单波动 排程跟不上", "排产靠 Excel · 调整滞后",
         "MRP 不实时 · 物料缺料后才被发现", "多车间产能均衡靠人工拍脑袋"],
        ["销售预测 + 订单 自动卷入需求池", "主计划 → MRP → 工单 自动拆分",
         "排程引擎按产能/物料/SN双约束", "齐套前置 · 红绿放行嵌入排产"],
        ["排产周期 周 → 天/小时", "工单准时齐套率 +25%",
         "产能利用率 提升 15%", "缺料停线 下降 40%"],
        "排产不是「Excel 作业」· 是销售预测到现场放行的可执行主计划"
    )

def body_p24_wms():
    """WMS PSV 三栏：仓储亮灯/呆滞物料/多类型出入库（按思维导图）"""
    return body_psv(
        "WMS 场景 · 仓储亮灯 + 呆滞预警 + 多类型出入库",
        "找货困难 → 库位亮灯 · 呆滞物料 → 库龄预警 · 多类型出入库 → 策略化管理",
        ["原材料/半成品/成品仓 混存找货困难", "线边余料无系统记录 · 账实不一致",
         "呆滞物料/超期物料 无预警", "委外/线边 进出无标准 · 难对账"],
        ["B 端仓库位亮灯拣选 + 路径指引", "核心件 SN + 批次件 双轨上架/分区",
         "库龄/保质期 双重预警 (180 天阈值)", "委外+线边双虚拟仓 + ABC 拣选优先级"],
        ["找货时间下降 60%", "线边账实一致率 100%",
         "呆滞库存下降 30%", "盘点效率提升 50%"],
        "WMS 不是「库存账本」· 而是 SN/批次/库位 三轴数据的指挥中枢"
    )

def body_p25_qms():
    """QMS PSV 三栏：图纸识别/三坐标/MRB/全流程追溯（按思维导图）"""
    return body_psv(
        "QMS 场景 · 三大检验 + MRB 闭环 + 全流程追溯",
        "识别图纸检验标准 → 三坐标/光学/定制设备 → 检验线上化 → 不合格品评审",
        ["IQC/IPQC/FQC 离线 · 数据滞后", "图纸检验标准提取靠人工 · 漏检多",
         "三坐标/光学/定制设备 数据不上传", "MRB 评审走线下 · 责任难定 · 追溯断"],
        ["三大检验线上化 + AQL/SPC 自动触发", "图纸检验标准识别 + 自动绑定 BOM",
         "测量设备 IoT 对接 (海克斯康/三坐标/光学)", "MRB 流程化 + 多角色协同 + 处置留痕"],
        ["质量异常处理周期 -50%", "检验数据 100% 上线",
         "MRB 责任可追溯率 100%", "客诉根因定位 数日 → 10 分钟"],
        "QMS 不是「单据系统」· 而是制造档案的质量证据链"
    )

def body_p26_eam():
    """EAM PSV 三栏：维修经验库(AI)/备品备件精准管控/全生命周期（按思维导图）"""
    return body_psv(
        "EAM 场景 · 全生命周期 + AI 维修经验库 + 备件精准管控",
        "设备维修经验库 (AI) · 备品备件精准管控 (减少成本) · MTTR/MTBF 实时",
        ["维修知识沉淀在老师傅脑里 · 流失风险高", "备件库存粗放 · 呆滞与短缺并存",
         "OEE/MTTR/MTBF 算不出来 · 决策靠经验", "费用归集靠 Excel · 难按项目核算"],
        ["AI 维修经验库 · 案例自动推荐", "备件以旧换新 + 安全库存预警 + WMS 联动",
         "IoT 实时采集 · OEE/MTTR/MTBF 自动计算", "费用按设备/产品/项目 多维归集"],
        ["维修响应时间 -40%", "备件呆滞库存 -25%",
         "OEE 数据 7 天 → 实时", "维修经验复用率 +60%"],
        "EAM 不是「维修系统」· 而是设备综合成本与经验沉淀的计量平台"
    )

def body_p28_value():
    """P28: 价值收益总览"""
    parts = []
    parts.extend(page_header("价值收益总览 · 4 大类业务价值", "生产效率 · 质量追溯 · 库存成本 · 设备运营 · 上线后落地可量化"))
    items = [
        ("01", "生产效率", "PRODUCTION EFFICIENCY",
         "工单在线 + 报工在线 + 齐套前置\n减少停线等待时间", "+30%", "人均效率提升"),
        ("02", "质量追溯", "QUALITY TRACEABILITY",
         "整机 SN → 部件 SN → 物料批次\n全链路追溯", "100%", "追溯覆盖率"),
        ("03", "库存成本", "INVENTORY COST",
         "批次 / 库龄 / 线边仓 / 呆滞预警\n降低库存风险", "数日→10min", "客诉追溯定位"),
        ("04", "设备运营", "EQUIPMENT OPERATION",
         "点检保养 + 维修 + 备件 + OEE\n数据闭环", "7天→实时", "OEE 数据出具"),
    ]
    card_w = 2800000
    card_h = 3700000
    gap_x = 160000
    x0 = (SLIDE_W - 4*card_w - 3*gap_x) // 2
    y0 = 1450000
    for i, (num, cn, en, desc, big, big_label) in enumerate(items):
        cx = x0 + i*(card_w + gap_x)
        accent = COLOR["primary"] if i%2==0 else COLOR["lime"]
        parts.append(rect_solid(cx, y0, card_w, 100000, accent))
        parts.append(rect_solid(cx, y0+100000, card_w, card_h-100000, COLOR["card_bg_light"]))
        # 编号
        parts.append(textbox(cx+200000, y0+240000, card_w-400000, 380000,
            [(num, 22, COLOR["white"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+620000, card_w-400000, 460000,
            [(cn, 22, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+1080000, card_w-400000, 260000,
            [(en, 9, accent, True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+200000, y0+1390000, card_w-400000, 12700, COLOR["light_gray"]))
        # 描述（双行）
        lines = desc.split('\n')
        for li, ln in enumerate(lines):
            parts.append(textbox(cx+200000, y0+1480000+li*340000, card_w-400000, 320000,
                [(ln, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
                anchor="ctr", align="l"))
        # 大数字
        parts.append(rect_solid(cx+200000, y0+2400000, card_w-400000, 700000, COLOR["deep_cyan"]))
        parts.append(textbox(cx+200000, y0+2400000, card_w-400000, 700000,
            [(big, 24, COLOR["lime"], True, "Arial", "Arial")],
            anchor="ctr", align="c"))
        parts.append(textbox(cx+200000, y0+3150000, card_w-400000, 320000,
            [(big_label, 11, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("运营指标可量化 · 可追踪 · 可复制 · 是客户决策落地的关键证据",
          13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_p29_roadmap():
    """P29: 能力沉淀 + 推进路径"""
    parts = []
    parts.extend(page_header("战略价值 · 4 大能力沉淀 + 4 步推进路径", "从单点信息化到可复制行业模板"))
    # 左侧：能力沉淀
    parts.append(rect_solid(280000, 1700000, 5500000, 80000, COLOR["primary"]))
    parts.append(rect_solid(280000, 1780000, 5500000, 60000, COLOR["card_bg_light"]))
    parts.append(textbox(280000, 1800000, 5500000, 320000,
        [("能力沉淀 · CAPABILITY", 14, COLOR["white"], True, "Arial", "Arial")],
        anchor="ctr", align="l"))
    caps = [
        ("01", "数据资产", "整机 SN + 批次码 + 工艺数据 沉淀"),
        ("02", "运营模型", "MES/WMS/QMS/EAM 业务模型可复用"),
        ("03", "行业模板", "机器人量产专属配置模板"),
        ("04", "组织能力", "MOM 团队建设 + 知识沉淀"),
    ]
    cy = 2200000
    for i, (num, cn, desc) in enumerate(caps):
        bx = 280000
        by = cy + i*820000
        parts.append(rect_solid(bx, by, 100000, 720000, COLOR["lime"]))
        parts.append(rect_solid(bx+100000, by, 5400000, 720000, COLOR["card_bg_light"]))
        parts.append(textbox(bx+200000, by+100000, 600000, 500000,
            [(num, 28, COLOR["white"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(textbox(bx+800000, by+80000, 4500000, 300000,
            [(cn, 16, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(bx+800000, by+380000, 4500000, 300000,
            [(desc, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
    # 右侧：推进路径
    parts.append(rect_solid(6080000, 1700000, 5800000, 80000, COLOR["lime"]))
    parts.append(rect_solid(6080000, 1780000, 5800000, 60000, COLOR["card_bg_light"]))
    parts.append(textbox(6080000, 1800000, 5800000, 320000,
        [("推进路径 · ROADMAP", 14, COLOR["white"], True, "Arial", "Arial")],
        anchor="ctr", align="l"))
    steps = [
        ("Step 1", "蓝图诊断", "2 周 · 痛点梳理 + 总体规划"),
        ("Step 2", "POC 试点", "8 周 · 选 1-2 核心场景 验证"),
        ("Step 3", "全面共建", "6 月 · MES+WMS+QMS+EAM 落地"),
        ("Step 4", "复制扩展", "持续 · 多基地 + 行业模板沉淀"),
    ]
    sy = 2200000
    for i, (st, cn, desc) in enumerate(steps):
        bx = 6080000
        by = sy + i*820000
        parts.append(rect_solid(bx, by, 100000, 720000, COLOR["primary"]))
        parts.append(rect_solid(bx+100000, by, 5700000, 720000, COLOR["card_bg_light"]))
        parts.append(textbox(bx+200000, by+100000, 1100000, 320000,
            [(st, 12, COLOR["primary"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(textbox(bx+200000, by+420000, 1100000, 280000,
            [(cn, 14, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(bx+1400000, by+80000, 4200000, 600000,
            [(desc, 12, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("不是「一次性项目」· 而是「可复用的行业能力沉淀」", 14, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


# ============ v20 新增 body 函数（市场容量/业务流程总览/系统架构/截图集/能力沉淀/推进路径） ============

def body_market_size():
    """P5 ★市场容量：人形机器人产业规模、政策、出货量预测"""
    parts = []
    parts.extend(page_header("人形机器人行业 · 市场容量与产业窗口期", "国家战略 + 产业资本 + 应用爆发 · 制造运营成为下一阶段胜负手"))
    # 上方 4 个核心数据卡
    metrics = [
        ("2025-2030", "MARKET WINDOW", "全球量产元年", "起步至规模量产", COLOR["primary"]),
        ("$38B+", "BY 2035", "全球市场规模", "Goldman Sachs 预测", COLOR["lime"]),
        ("100W+", "ANNUAL UNITS", "2030 年出货量", "工业+消费+特种", COLOR["deep_cyan"]),
        ("3-5×", "GROWTH/YR", "复合增长率", "国内厂商加速", COLOR["primary"]),
    ]
    card_w = 2800000
    card_h = 1700000
    gap = 160000
    x0 = (SLIDE_W - 4*card_w - 3*gap) // 2
    y0 = 1335000
    for i, (big, en, cn, desc, color) in enumerate(metrics):
        cx = x0 + i*(card_w + gap)
        parts.append(rect_solid(cx, y0, card_w, 100000, color))
        parts.append(rect_solid(cx, y0+100000, card_w, card_h-100000, COLOR["card_bg_light"]))
        parts.append(textbox(cx+200000, y0+260000, card_w-400000, 500000,
            [(big, 28, COLOR["lime"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+780000, card_w-400000, 240000,
            [(en, 9, color, True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+200000, y0+1080000, card_w-400000, 12700, COLOR["light_gray"]))
        parts.append(textbox(cx+200000, y0+1140000, card_w-400000, 300000,
            [(cn, 14, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+1440000, card_w-400000, 220000,
            [(desc, 10, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
    # 下方 3 大驱动
    drv_y = 3550000
    parts.append(textbox(280000, drv_y, 11600000, 320000,
        [("三大驱动 · 产业窗口期 · INDUSTRY DRIVERS", 13, COLOR["primary"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="l"))
    drivers = [
        ("政策驱动", "POLICY", "十四五 + 浙江/广东/深圳 专项政策 · 国家产业重点扶持", "国家战略"),
        ("技术驱动", "TECH", "大模型 + 具身智能 + 灵巧手 + 关节模组 · 性能突破", "技术拐点"),
        ("资本驱动", "CAPITAL", "国内一二级市场超百亿资金涌入 · 头部厂商批量融资", "资本加持"),
    ]
    drv_card_w = 3800000
    drv_gap = 200000
    drv_x0 = (SLIDE_W - 3*drv_card_w - 2*drv_gap) // 2
    drv_card_y = drv_y + 380000
    drv_card_h = 1400000
    for i, (cn, en, desc, tag) in enumerate(drivers):
        cx = drv_x0 + i*(drv_card_w + drv_gap)
        accent = [COLOR["primary"], COLOR["lime"], COLOR["deep_cyan"]][i]
        parts.append(rect_solid(cx, drv_card_y, drv_card_w, 80000, accent))
        parts.append(rect_solid(cx, drv_card_y+80000, drv_card_w, drv_card_h-80000, COLOR["card_bg_light"]))
        parts.append(textbox(cx+200000, drv_card_y+200000, drv_card_w-400000, 360000,
            [(cn, 18, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, drv_card_y+580000, drv_card_w-400000, 260000,
            [(en, 10, accent, True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+200000, drv_card_y+900000, drv_card_w-400000, 12700, COLOR["light_gray"]))
        parts.append(textbox(cx+200000, drv_card_y+960000, drv_card_w-400000, 360000,
            [(desc, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("市场容量 ≠ 出货量 · 拼到最后是制造运营能力 · 谁先打通 MOM 谁先吃下规模化红利",
          13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_sys_arch():
    """P17 一体化人形机器人智能工厂解决方案蓝图 · 5 层架构（参考王老师指定样式）"""
    parts = []
    parts.extend(page_header("一体化人形机器人智能工厂解决方案蓝图",
                             "经营决策 · 业务应用 · 平台能力 · 数据采集 · 设备产线 · 端到端闭环"))
    # 5 层（从上到下：层5最顶 - 层1最底）· 中文统一 5 字
    layers = [
        ("5", "经营决策层",
         ["交付达成率", "质量合格率", "生产效率", "库存周转", "供应链风险", "产品可靠性"]),
        ("4", "业务应用层",
         ["计划排产", "生产执行", "物料齐套", "质量追溯", "供应商协同", "仓储物流", "设备管理", "测试分析", "售后闭环"]),
        ("3", "平台能力层",
         ["MES", "APS", "WMS", "QMS", "SRM", "EAM", "数据中台", "AI 分析平台", "数字孪生"]),
        ("2", "数据采集层",
         ["IoT 网关", "设备协议接入", "测试数据采集", "工位数据采集", "边缘缓存", "实时数据处理"]),
        ("1", "设备产线层",
         ["装配工位", "测试设备", "检测设备", "AGV/AMR", "立库", "扫码/RFID", "扭矩工具", "视觉设备"]),
    ]
    y0 = 1380000
    layer_h = 780000
    gap_h = 60000
    label_w = 1100000
    label_x = 280000
    content_x = label_x + label_w + 80000
    content_w = SLIDE_W - content_x - 280000

    for li, (num, cn, items) in enumerate(layers):
        ly = y0 + li * (layer_h + gap_h)
        # 左侧标签块 - 统一深青色底
        parts.append(rect_solid(label_x, ly, label_w, layer_h, COLOR["deep_cyan"]))
        # 大编号 - 黄绿色，居中
        parts.append(textbox(label_x, ly+80000, label_w, 320000,
            [(num, 28, COLOR["lime"], True, "Arial", "Arial")],
            anchor="ctr", align="c"))
        # 中文层名 - 11pt 居中（5 字单行）
        parts.append(textbox(label_x, ly+440000, label_w, 280000,
            [(cn, 11, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
        # 内容卡片
        n = len(items)
        gap_x = 60000
        item_w = (content_w - (n-1)*gap_x) // n
        # 各层用不同色装饰条
        accent = [COLOR["primary"], COLOR["primary"], COLOR["lime"], COLOR["primary"], COLOR["primary"]][li]
        for i, it in enumerate(items):
            ix = content_x + i*(item_w + gap_x)
            parts.append(rect_solid(ix, ly, item_w, layer_h, COLOR["card_bg_light"]))
            parts.append(rect_solid(ix, ly, item_w, 60000, accent))
            parts.append(textbox(ix, ly, item_w, layer_h,
                [(it, 11, COLOR["white"], True, "Arial", "微软雅黑")],
                anchor="ctr", align="c"))
    # 底部金句
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("数据驱动 · 智能协同 · 柔性制造 · 持续优化 · 端到端闭环",
          14, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_capability():
    """P34 能力沉淀（拆自 body_p29_roadmap 左半）"""
    parts = []
    parts.extend(page_header("4 大能力沉淀 · 从单点信息化到可复制的行业模板", "数据资产 · 运营模型 · 行业模板 · 组织能力 · 可复用 · 可输出"))
    caps = [
        ("01", "数据资产", "DATA ASSET",
         "整机 SN + 部件 SN + 物料批次 + 工艺/质量/设备 数据沉淀", "Asset"),
        ("02", "运营模型", "OPERATION MODEL",
         "MES/WMS/QMS/EAM 业务模型可复用 · 标准化 + 配置化", "Model"),
        ("03", "行业模板", "INDUSTRY TEMPLATE",
         "机器人量产专属配置模板 + 业务流程 + 检验标准 + 工艺路线", "Template"),
        ("04", "组织能力", "ORGANIZATION",
         "MOM 团队建设 + 制造运营知识沉淀 + 持续运营机制", "Team"),
    ]
    card_w = 2800000
    card_h = 3700000
    gap_x = 160000
    x0 = (SLIDE_W - 4*card_w - 3*gap_x) // 2
    y0 = 1335000
    for i, (num, cn, en, desc, tag) in enumerate(caps):
        cx = x0 + i*(card_w + gap_x)
        accent = [COLOR["primary"], COLOR["lime"], COLOR["deep_cyan"], COLOR["primary"]][i]
        parts.append(rect_solid(cx, y0, card_w, 100000, accent))
        parts.append(rect_solid(cx, y0+100000, card_w, card_h-100000, COLOR["card_bg_light"]))
        parts.append(textbox(cx+200000, y0+240000, card_w-400000, 600000,
            [(num, 38, COLOR["lime"], True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+860000, card_w-400000, 460000,
            [(cn, 22, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+1340000, card_w-400000, 280000,
            [(en, 10, accent, True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+200000, y0+1660000, card_w-400000, 12700, COLOR["light_gray"]))
        parts.append(textbox(cx+200000, y0+1750000, card_w-400000, 1500000,
            [(desc, 12, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="t", align="l"))
        parts.append(rect_solid(cx+200000, y0+card_h-460000, card_w-400000, 360000, COLOR["deep_cyan"]))
        parts.append(textbox(cx+200000, y0+card_h-460000, card_w-400000, 360000,
            [(tag, 12, COLOR["white"], True, "Arial", "Arial")],
            anchor="ctr", align="c"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("不是「一次性项目」· 而是「可复制 · 可输出 · 可持续」的行业能力沉淀",
          13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_roadmap():
    """P35 推进路径（拆自 body_p29_roadmap 右半 · 4 阶段时间轴）"""
    parts = []
    parts.extend(page_header("4 步推进路径 · 蓝图诊断 → POC 试点 → 全面共建 → 复制扩展", "可验证 · 可控风险 · 6-12 个月分期落地 · 持续输出行业能力"))
    steps = [
        ("Step 1", "蓝图诊断", "BLUEPRINT", "2 周", "痛点梳理 + 总体规划 · 业务/IT/数据 三轴对齐"),
        ("Step 2", "POC 试点", "PILOT POC", "8 周", "选 1-2 核心场景验证 · 跑通业务 + IT 闭环"),
        ("Step 3", "全面共建", "FULL BUILD", "6 月", "MES+WMS+QMS+EAM 落地 · 码体系 + 一体化底座"),
        ("Step 4", "复制扩展", "REPLICATE", "持续", "多基地 + 行业模板沉淀 · 持续迭代 + 能力输出"),
    ]
    card_w = 2800000
    card_h = 3700000
    gap_x = 160000
    x0 = (SLIDE_W - 4*card_w - 3*gap_x) // 2
    y0 = 1335000
    for i, (st, cn, en, dur, desc) in enumerate(steps):
        cx = x0 + i*(card_w + gap_x)
        accent = [COLOR["primary"], COLOR["lime"], COLOR["deep_cyan"], COLOR["primary"]][i]
        parts.append(rect_solid(cx, y0, card_w, 100000, accent))
        parts.append(rect_solid(cx, y0+100000, card_w, card_h-100000, COLOR["card_bg_light"]))
        parts.append(textbox(cx+200000, y0+240000, card_w-400000, 320000,
            [(st, 14, accent, True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+620000, card_w-400000, 480000,
            [(cn, 28, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(textbox(cx+200000, y0+1140000, card_w-400000, 260000,
            [(en, 10, accent, True, "Arial", "Arial")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+200000, y0+1460000, card_w-400000, 12700, COLOR["light_gray"]))
        parts.append(textbox(cx+200000, y0+1560000, card_w-400000, 900000,
            [(desc, 12, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="t", align="l"))
        # 大数字-时间
        parts.append(rect_solid(cx+200000, y0+card_h-840000, card_w-400000, 720000, COLOR["deep_cyan"]))
        parts.append(textbox(cx+200000, y0+card_h-840000, card_w-400000, 720000,
            [(dur, 26, COLOR["lime"], True, "Arial", "Arial")],
            anchor="ctr", align="c"))
        parts.append(textbox(cx+200000, y0+card_h-100000, card_w-400000, 100000,
            [("DURATION", 8, COLOR["text_gray"], True, "Arial", "Arial")],
            anchor="ctr", align="c"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("从「方案咨询」到「全面共建」· 12 个月把机器人 MOM 体系跑通 · 让经验可复用",
          13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


# ============ 业务流程图 + 功能架构 通用渲染（按王老师宇树蓝图v4风格）============

def body_business_flow(title, subtitle, stages, lanes, summary):
    """业务流程图：阶段顶栏 + 角色泳道 + 流程节点"""
    parts = []
    parts.extend(page_header(title, subtitle))
    stages_n = len(stages)
    lanes_n = len(lanes)
    role_col_w = 1100000
    flow_x0 = 280000 + role_col_w + 80000
    flow_total_w = SLIDE_W - 280000 - role_col_w - 80000 - 280000
    stage_w = flow_total_w // stages_n
    y0 = 1450000
    # 阶段顶栏
    for si, stage in enumerate(stages):
        sx = flow_x0 + si*stage_w
        parts.append(rect_solid(sx + 20000, y0, stage_w - 40000, 320000, COLOR["primary"]))
        parts.append(textbox(sx + 20000, y0, stage_w - 40000, 320000,
            [(stage, 13, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
    lane_y0 = y0 + 380000
    lane_total_h = 5780000 - lane_y0
    lane_h = (lane_total_h - (lanes_n-1)*60000) // lanes_n
    for li, lane_data in enumerate(lanes):
        role = lane_data[0]
        stage_nodes_list = lane_data[1:]
        ly = lane_y0 + li * (lane_h + 60000)
        # 角色名块（左侧深青色）
        parts.append(rect_solid(280000, ly, role_col_w, lane_h, COLOR["deep_cyan"]))
        parts.append(textbox(280000, ly, role_col_w, lane_h,
            [(role, 12, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="c"))
        # 每个阶段的节点
        for si in range(stages_n):
            sx = flow_x0 + si*stage_w
            nodes = stage_nodes_list[si] if si < len(stage_nodes_list) else []
            if not nodes: continue
            n_count = len(nodes)
            n_w = stage_w - 60000
            n_h = (lane_h - (n_count-1)*30000) // n_count
            for ni, node in enumerate(nodes):
                nx = sx + 30000
                ny = ly + ni*(n_h + 30000)
                parts.append(rect_solid(nx, ny, n_w, n_h, COLOR["card_bg_light"]))
                parts.append(rect_solid(nx, ny, 40000, n_h, COLOR["lime"]))
                parts.append(textbox(nx + 60000, ny, n_w - 60000, n_h,
                    [(node, 10, COLOR["white"], True, "Arial", "微软雅黑")],
                    anchor="ctr", align="l"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [(summary, 13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


def body_function_arch(title, subtitle, modules, summary):
    """功能架构页：N 个模块 + 各模块功能点"""
    parts = []
    parts.extend(page_header(title, subtitle))
    n = len(modules)
    gap = 180000
    card_w = (11600000 - (n-1)*gap) // n
    card_h = 4100000
    y0 = 1450000
    x_base = 280000
    for i, (mod_name, features) in enumerate(modules):
        cx = x_base + i*(card_w + gap)
        accent = [COLOR["primary"], COLOR["lime"], COLOR["deep_cyan"], COLOR["primary"], COLOR["lime"], COLOR["deep_cyan"]][i % 6]
        parts.append(rect_solid(cx, y0, card_w, 100000, accent))
        parts.append(rect_solid(cx, y0+100000, card_w, card_h-100000, COLOR["card_bg_light"]))
        parts.append(textbox(cx+200000, y0+220000, card_w-400000, 480000,
            [(mod_name, 17, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        parts.append(rect_solid(cx+200000, y0+800000, card_w-400000, 12700, COLOR["light_gray"]))
        for fi, ft in enumerate(features[:7]):
            parts.append(textbox(cx+180000, y0+880000+fi*440000, card_w-360000, 400000,
                [("● ", 11, accent, True, "Arial", "Arial"),
                 (ft, 11, COLOR["white"], False, "Arial", "微软雅黑")],
                anchor="ctr", align="l"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [(summary, 13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return parts


# MES 业务流程 + 功能架构
def body_mes_flow():
    return body_business_flow(
        "MES 业务流程 · 生产管理全链路",
        "工厂建模 · 工单派工 · 领料上线 · 报工报检 · 完工入库",
        ["生产计划", "产前准备", "生产执行", "完工入库"],
        [
            ("计划员",   ["跑 MRP", "下推生产订单"], [],                       [],                                   []),
            ("产线主管", ["排产"],                  ["派工", "查询工单"],     [],                                   []),
            ("操作工",   [],                        ["产前点检", "领料拣配"], ["开工·上工", "条码绑定", "生产加工"], []),
            ("IPQC",     [],                        [],                       ["报检·判定"],                        []),
            ("仓库/WMS", [],                        ["领料交接"],             [],                                   ["完工入库", "标签打印"]),
        ],
        "MES 不是「报工系统」· 是从 MRP 到入库的全链路执行平台 · 每个动作都留痕"
    )

def body_mes_arch():
    return body_function_arch(
        "MES 功能架构 · 5 大模块 + 13 项报表",
        "生产计划 · 工单派工 · 报工入库 · 13 项报表看板 · 全模块协同",
        [
            ("基础数据", ["工厂建模", "产线/工位", "工艺路线", "BOM 关联", "工时标准"]),
            ("生产计划", ["MRP 接入", "主计划下推", "排产引擎", "派工管理", "齐套检查"]),
            ("生产执行", ["开工·上工", "条码绑定·SN", "报工·报检", "异常·安灯", "改制·返修"]),
            ("人员管理", ["人员定位 UWB", "工时统计", "技能矩阵", "绩效看板", "工序交接"]),
            ("报表看板", ["13 项报表", "WIP/进度", "OEE 分析", "齐套率", "生产成本"]),
        ],
        "MES 5 大模块全打通 · 13 项报表让生产数据「会说话」"
    )

# WMS 业务流程 + 功能架构
def body_wms_flow():
    return body_business_flow(
        "WMS 业务流程 · 仓储管理全链路",
        "入库管理 → 在库管理 → 出库管理 · 6 角色协同 + 与 QMS/MES 双向联动",
        ["入库管理", "在库管理", "出库管理"],
        [
            ("供应商/ASN", ["ASN 到货预约"], [], []),
            ("收货员",     ["物料卸货", "扫码收货"], [], []),
            ("IQC 质检",   ["IQC 抽样检验", "合格判定"], [], []),
            ("库管员",     ["上架任务", "上架完成"], ["库存查询", "移库调拨", "周期盘点", "库龄预警"], []),
            ("拣货员",     [], [], ["接收领料申请", "波次拣货", "拣货·复核"]),
            ("发运员",     [], [], ["发运准备", "装车发货"]),
        ],
        "WMS 不是「库存账本」· 是 SN/批次/库位 三轴数据的指挥中枢"
    )

def body_wms_arch():
    return body_function_arch(
        "WMS 功能架构 · 仓+库区+库位 + ASN + PDA",
        "仓库 / 库区 / 库位 · ASN 入库上架 · 库存盘点 · PDA 移动作业",
        [
            ("仓库结构", ["仓库管理", "库区/库位", "策略规则", "亮灯部署", "ABC 分区"]),
            ("入库管理", ["ASN 预约", "扫码收货", "QMS 联动", "上架任务", "标签打印"]),
            ("在库管理", ["库存查询", "移库调拨", "盘点(抽/全/循环)", "库龄预警", "委外/线边虚拟仓"]),
            ("出库管理", ["领料申请", "波次拣货", "亮灯拣选", "复核发运", "ERP 回写"]),
            ("移动应用", ["PDA 收发货", "PDA 盘点", "PDA 上架", "可视化大屏", "管理报表"]),
        ],
        "WMS 5 大模块 · 软硬件结合 · 让账实在线一致"
    )

# QMS 业务流程 + 功能架构
def body_qms_flow():
    return body_business_flow(
        "QMS 业务流程 · 三大检验 + MRB 闭环",
        "来料检验 IQC + 过程检验 IPQC + 成品检验 FQC + 不合格 MRB 处置",
        ["IQC 来料", "IPQC 过程", "FQC 成品", "MRB 处置"],
        [
            ("组长(IQC/IPQC/FQC)", ["生成检验任务", "任务分配"], ["生成检验任务", "任务分配"], ["生成检验任务", "任务分配"], []),
            ("检验员",             ["接收任务", "检验执行"], ["接收任务", "检验执行"], ["接收任务", "检验执行"], []),
            ("取样/三坐标",        ["取样", "三坐标/试装"], [], [], []),
            ("生产/班组",          [], ["MES 报检", "现场处置"], [], []),
            ("质量主管(MRB)",      [], [], [], ["复审", "MES 锁单", "MRB 评审"]),
            ("仓库",               ["来料入库"], [], ["合格入库"], []),
        ],
        "QMS 不是「单据系统」· 是制造档案的质量证据链"
    )

def body_qms_arch():
    return body_function_arch(
        "QMS 功能架构 · 三检 + MRB + 计量 + 报表",
        "IQC / IPQC / FQC 三大检验 · MRB 处置 · 计量器具 · 质量报表",
        [
            ("标准管理", ["检验标准库", "AQL/SPC 规则", "图纸 CAD 识别", "免检规则", "标准变更"]),
            ("检验执行", ["IQC 来料检验", "IPQC 过程巡检", "FQC 出货检验", "任务调度", "现场处置"]),
            ("MRB 评审", ["异常分流", "评审委员会", "处置闭环", "费用归集", "复审追溯"]),
            ("计量器具", ["器具台账", "校准计划", "送检管理", "到期预警", "证书归档"]),
            ("质量报表", ["IPQC SPC", "缺陷分布", "MRB 报表", "供应商质量", "客诉追溯"]),
        ],
        "QMS 5 大模块 · 三检全在线 + 测量设备 IoT 直连 · 检验数据 100% 受控"
    )

# EAM 业务流程 + 功能架构
def body_eam_flow():
    return body_business_flow(
        "EAM 业务流程 · 日常维保 + 故障维修 + 备件保障",
        "IoT 数据采集 + OEE 实时分析 · 飞书审批 · ERP 费用回写",
        ["日常维保", "故障维修", "备件保障"],
        [
            ("操作工",       ["设备自检", "日常作业"], ["扫码报修"], []),
            ("巡检员",       ["定期巡检", "记录结果"], [], []),
            ("设备主管",     ["保养/点检计划"], ["生成维修工单"], []),
            ("维修员",       [], ["接单维修", "维修执行", "维修完工"], []),
            ("备件管理员",   [], [], ["备件出库", "安全库存预警", "采购申请"]),
            ("系统/IoT",     ["运行数据采集"], ["OEE 实时分析"], ["飞书审批", "采购到货看板"]),
        ],
        "EAM 不是「维修系统」· 是设备综合成本和经验沉淀的计量平台"
    )

def body_eam_arch():
    return body_function_arch(
        "EAM 功能架构 · 5 大模块 + IoT 数采",
        "设备台账 · 点检保养 · 故障维修 · 备品备件 · IoT / OEE 监控",
        [
            ("设备台账", ["ERP 主数据同步", "设备 BOM", "电子履历", "责任人/产线", "BOM 变更追溯"]),
            ("点检保养", ["PM 计划日历", "周期点检", "PDA 拍照打卡", "异常上报", "保养标准"]),
            ("故障维修", ["PDA 快速报修", "维修派工", "飞书审批", "AI 维修知识库", "MTTR/MTBF"]),
            ("备品备件", ["申购入库", "以旧换新", "WMS 联动", "安全库存预警", "易损件管理"]),
            ("IoT/OEE",  ["OPC UA/Modbus", "实时数据采集", "OEE 自动计算", "异常告警", "费用归集"]),
        ],
        "EAM 5 大模块 + IoT 实时 · 让维修知识沉淀 + 备件成本透明"
    )


# ============ 图片插入工具 + 截图页 ============

# 全局：当前 slide 的图片引用列表（reset_id 时也会重置）
_CURRENT_IMG_REFS = []

def picture_xml(x, y, w, h, rId=None, name="Picture", media_file=None):
    """生成 <p:pic> XML 节点 · 若提供 media_file 则自动注册 rId"""
    global _CURRENT_IMG_REFS
    if media_file and rId is None:
        rId = f"rImg{len(_CURRENT_IMG_REFS) + 2}"
        _CURRENT_IMG_REFS.append((rId, media_file))
    sid = new_id()
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{sid}" name="{name}"/>'
            f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rId}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')

# 截图页定义：每页 3-4 张截图（媒体名 + 标题 + 说明）
SCREENSHOT_PAGES = {
    "mes": {
        "title": "MES 系统功能展示 · 生产执行可视化",
        "subtitle": "生产调度 · 物料齐套 · 运营驾驶舱 · 一图掌握生产全貌",
        "shots": [
            ("yushu_mes_dashboard.png",  "生产运营驾驶舱",   "车间/班组/工单 多维实时看板"),
            ("yushu_mes_scheduling.png", "生产调度中心",     "产量/合格率/工艺执行 实时监控"),
            ("yushu_mes_kitting.png",    "物料齐套率分析",   "总装物资拉动看板 · 准时齐套率"),
        ],
    },
    "wms_qms": {
        "title": "WMS + QMS 系统功能展示 · 仓储与质量",
        "subtitle": "仓储看板 · 库位亮灯 · 检验线上化 · 海克斯康测量设备直连",
        "shots": [
            ("yushu_wms_dashboard.png",  "WMS 综合看板",     "成品入库/出库 + 实时库存 + 出库情况"),
            ("yushu_wms_warehouse.png",  "WMS 仓储管理看板", "充气库位/放气库位 + 在制工单 + 人员考勤"),
            ("yushu_qms_inspection.png", "SMART Quality 检验", "现场量具+笔记本实时上传 检测数据"),
        ],
    },
    "eam_iot": {
        "title": "EAM + IoT 系统功能展示 · 设备与物联",
        "subtitle": "刀具刃装/拆框 · 智能工厂可视化 · 全生命周期数字化管理",
        "shots": [
            ("yushu_eam_tool.png",         "刀具管理系统",      "TDM 刀具刃装/拆框 全生命周期"),
            ("yushu_iot_visualization.png","智能工厂可视化大屏", "3D 数字孪生 + 实时数据 + 告警联动"),
            ("yushu_mes_dashboard.png",    "数采+EAM 联动",     "OEE 实时计算 + 维修经验库 + 备件管控"),
        ],
    },
}


def render_screenshots_page(key, page_no, chapter_label, section_label):
    """渲染一张系统截图页（独立函数 · 自己处理 image rels）"""
    reset_id()
    cfg = SCREENSHOT_PAGES[key]
    parts = []
    # 主标题 + 副标题（用 page_header）
    parts.extend(page_header(cfg["title"], cfg["subtitle"]))
    # 3 张截图横排
    shots = cfg["shots"]
    n = len(shots)
    shot_w = 3680000
    shot_h = 2200000
    gap = 200000
    x0 = (SLIDE_W - n*shot_w - (n-1)*gap) // 2
    y0 = 1375000
    img_refs = []  # [(rId, filename), ...]
    for i, (media_file, cn, desc) in enumerate(shots):
        cx = x0 + i*(shot_w + gap)
        rId = f"rImg{i+2}"  # rId1 给 layout，从 rId2 开始
        img_refs.append((rId, media_file))
        # 卡片外框
        parts.append(rect_solid(cx, y0, shot_w, 80000, COLOR["lime"] if i%2==0 else COLOR["primary"]))
        parts.append(rect_solid(cx, y0+80000, shot_w, shot_h+80000+560000, COLOR["card_bg_light"]))
        # 图片
        parts.append(picture_xml(cx+80000, y0+160000, shot_w-160000, shot_h-80000, rId, f"Shot{i}"))
        # 标题
        parts.append(textbox(cx+200000, y0+shot_h+200000, shot_w-400000, 360000,
            [(cn, 16, COLOR["white"], True, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
        # 说明
        parts.append(textbox(cx+200000, y0+shot_h+580000, shot_w-400000, 320000,
            [(desc, 11, COLOR["text_gray"], False, "Arial", "微软雅黑")],
            anchor="ctr", align="l"))
    parts.append(rect_solid(280000, 5860000, 11600000, 380000, COLOR["primary"]))
    parts.append(textbox(280000, 5860000, 11600000, 380000,
        [("真实交付项目截图 · 可视化驱动业务 · 让数据替决策说话",
          13, COLOR["white"], True, "Arial", "微软雅黑")],
        anchor="ctr", align="c"))
    return sld_open() + ''.join(parts) + sld_close(), img_refs


# ============ 主流程：生成 36 张 slide ============

CONTENT_RENDERERS = {
    # 章节1：行业介绍
    4:  ("CHAPTER 01 · 行业介绍",        "行业演进",              body_p4_evolution),
    5:  ("CHAPTER 01 · 行业介绍",        "市场容量 · 产业窗口期", body_market_size),
    6:  ("CHAPTER 01 · 行业介绍",        "客户与场景分布",        body_p5_customer),
    7:  ("CHAPTER 01 · 行业介绍",        "业务特征 · 四个并存",   body_p6_features),
    8:  ("CHAPTER 01 · 行业介绍",        "制造复杂性 · 六重门",   body_p7_complexity),
    # 章节2：行业痛点
    10: ("CHAPTER 02 · 行业痛点",        "痛点总览",              body_p9_painpoints),
    11: ("CHAPTER 02 · 行业痛点",        "场景 1 · SCENARIO 01",   body_p10_psv),
    12: ("CHAPTER 02 · 行业痛点",        "场景 2 · SCENARIO 02",   body_p11_psv),
    13: ("CHAPTER 02 · 行业痛点",        "场景 3 · SCENARIO 03",   body_p12_psv),
    # 章节3：整体解决方案
    15: ("CHAPTER 03 · 整体解决方案",     "研产供销服一体化平台",  body_p14_platform),
    16: ("CHAPTER 03 · 整体解决方案",     "业务流程闭环",          body_p15_architecture),
    17: ("CHAPTER 03 · 整体解决方案",     "MOM 系统架构",          body_sys_arch),
    18: ("CHAPTER 03 · 整体解决方案",     "数据主线",              body_p16_dataline),
    # 章节4：落地场景方案
    20: ("CHAPTER 04 · 落地场景 · 底座",  "一体化底座平台",        body_p18_base),
    21: ("CHAPTER 04 · 落地场景 · 研发",  "研发管理 · CAE + 精度", body_p19_rd),
    # MES（业务流程 + 功能架构 + 4 PSV 场景）
    22: ("CHAPTER 04 · 落地场景 · MES",   "MES 业务流程",          body_mes_flow),
    23: ("CHAPTER 04 · 落地场景 · MES",   "MES 功能架构",          body_mes_arch),
    24: ("CHAPTER 04 · 落地场景 · MES",   "MES 场景 1 · 生产追溯", body_p20_mes1),
    25: ("CHAPTER 04 · 落地场景 · MES",   "MES 场景 2 · 报工线上化", body_p21_mes2),
    26: ("CHAPTER 04 · 落地场景 · MES",   "MES 场景 3 · 齐套检查", body_p22_mes3),
    27: ("CHAPTER 04 · 落地场景 · MES",   "MES 场景 4 · 生产排产", body_p23_mes4),
    # WMS（业务流程 + 功能架构 + PSV）
    28: ("CHAPTER 04 · 落地场景 · WMS",   "WMS 业务流程",          body_wms_flow),
    29: ("CHAPTER 04 · 落地场景 · WMS",   "WMS 功能架构",          body_wms_arch),
    30: ("CHAPTER 04 · 落地场景 · WMS",   "WMS · 亮灯+呆滞+多类型出入库", body_p24_wms),
    # QMS（业务流程 + 功能架构 + PSV）
    31: ("CHAPTER 04 · 落地场景 · QMS",   "QMS 业务流程",          body_qms_flow),
    32: ("CHAPTER 04 · 落地场景 · QMS",   "QMS 功能架构",          body_qms_arch),
    33: ("CHAPTER 04 · 落地场景 · QMS",   "QMS · 三检+MRB+全追溯", body_p25_qms),
    # EAM（业务流程 + 功能架构 + PSV）
    34: ("CHAPTER 04 · 落地场景 · EAM",   "EAM 业务流程",          body_eam_flow),
    35: ("CHAPTER 04 · 落地场景 · EAM",   "EAM 功能架构",          body_eam_arch),
    36: ("CHAPTER 04 · 落地场景 · EAM",   "EAM · 维修经验+备件管控", body_p26_eam),
    # 章节5：价值收益
    41: ("CHAPTER 05 · 价值收益",         "价值收益总览",          body_p28_value),
    42: ("CHAPTER 05 · 价值收益",         "4 大能力沉淀",          body_capability),
    43: ("CHAPTER 05 · 价值收益",         "4 步推进路径",          body_roadmap),
}

# 系统截图页
SCREENSHOT_RENDERERS = {
    37: ("CHAPTER 04 · 落地场景 · 系统截图", "MES 系统功能展示",     "mes"),
    38: ("CHAPTER 04 · 落地场景 · 系统截图", "WMS+QMS 系统功能展示", "wms_qms"),
    39: ("CHAPTER 04 · 落地场景 · 系统截图", "EAM+IoT 系统功能展示", "eam_iot"),
}

CHAPTERS = {
    3:  (1, "行业介绍",        "CHAPTER 01 · INDUSTRY CONTEXT",     "市场容量 · 客户分布 · 业务特征 · 制造复杂性"),
    9:  (2, "行业痛点",        "CHAPTER 02 · INDUSTRY PAIN POINTS", "6 大业务域 · 3 个真实业务场景 · 量产阶段的真实诉求"),
    14: (3, "整体解决方案",     "CHAPTER 03 · OVERALL SOLUTION",     "研产供销服平台 · 业务流程 · 系统架构 · 数据主线"),
    19: (4, "落地场景方案",     "CHAPTER 04 · SCENARIO IMPLEMENTATION", "底座 · 研发 · MES · WMS · QMS · EAM · 系统截图"),
    40: (5, "价值收益",        "CHAPTER 05 · VALUE & ROADMAP",      "价值收益 · 能力沉淀 · 推进路径"),
}

TOTAL_SLIDES = 44


def build_slides():
    """生成 TOTAL_SLIDES (36) 张 slide.xml 文件"""
    slides_dir = f"{BUILD_DIR}/ppt/slides"
    rels_dir = f"{slides_dir}/_rels"
    os.makedirs(slides_dir, exist_ok=True)
    os.makedirs(rels_dir, exist_ok=True)

    rels_map = {  # 每张 slide 用哪个 layout
        1:  5,  # 封面
        2:  3,  # 目录
        TOTAL_SLIDES: 2,  # 封底
    }
    for ch_idx in CHAPTERS.keys():
        rels_map[ch_idx] = 3
    # 默认其他为内容页 = layout1
    for i in range(1, TOTAL_SLIDES+1):
        if i not in rels_map:
            rels_map[i] = 1

    for i in range(1, TOTAL_SLIDES+1):
        global _CURRENT_IMG_REFS
        _CURRENT_IMG_REFS = []  # 重置全局图片引用列表
        img_refs = []
        # 生成 XML
        if i == 1:
            xml = render_cover(None)
        elif i == 2:
            xml = render_toc(None)
        elif i in CHAPTERS:
            ch_num, cn, en, desc = CHAPTERS[i]
            xml = render_chapter(ch_num, cn, en, desc, i)
        elif i == TOTAL_SLIDES:
            xml = render_closing(None)
        elif i in SCREENSHOT_RENDERERS:
            chapter_label, section_label, sc_key = SCREENSHOT_RENDERERS[i]
            xml, img_refs = render_screenshots_page(sc_key, i, chapter_label, section_label)
        elif i in CONTENT_RENDERERS:
            chapter_label, section_label, body_fn = CONTENT_RENDERERS[i]
            xml = render_content(chapter_label, section_label, i, body_fn)
            # 收集普通内容页中通过 picture_xml(media_file=...) 注册的图片引用
            img_refs = list(_CURRENT_IMG_REFS)
        else:
            raise RuntimeError(f"未配置 slide {i}")

        # 写入 slide.xml
        with open(f"{slides_dir}/slide{i}.xml", "w", encoding="utf-8") as f:
            f.write(xml_header() + xml)

        # 生成 rels
        layout_id = rels_map[i]
        rels_xml_parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                          '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                          f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" '
                          f'Target="../slideLayouts/slideLayout{layout_id}.xml"/>']
        for rId, media_file in img_refs:
            rels_xml_parts.append(
                f'<Relationship Id="{rId}" '
                f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                f'Target="../media/{media_file}"/>'
            )
        rels_xml_parts.append('</Relationships>')
        with open(f"{rels_dir}/slide{i}.xml.rels", "w", encoding="utf-8") as f:
            f.write(''.join(rels_xml_parts))
    print(f"已生成 {TOTAL_SLIDES} 张 slide.xml")


def update_presentation_meta():
    """更新 presentation.xml、_rels/presentation.xml.rels、[Content_Types].xml"""
    # ----- presentation.xml -----
    pres_path = f"{BUILD_DIR}/ppt/presentation.xml"
    with open(pres_path, encoding="utf-8") as f:
        s = f.read()
    # 新 sldIdLst
    sld_id_xml = ""
    p14_sld_id_xml = ""
    for i in range(1, TOTAL_SLIDES+1):
        sld_id = 256 + i  # 从 257 开始
        r_id = 100 + i    # rId101 起
        sld_id_xml += f'<p:sldId id="{sld_id}" r:id="rId{r_id}"/>'
        p14_sld_id_xml += f'<p14:sldId id="{sld_id}"/>'
    s = re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>',
               f'<p:sldIdLst>{sld_id_xml}</p:sldIdLst>', s, count=1, flags=re.DOTALL)
    s = re.sub(r'<p14:sldIdLst>.*?</p14:sldIdLst>',
               f'<p14:sldIdLst>{p14_sld_id_xml}</p14:sldIdLst>', s, count=1, flags=re.DOTALL)
    with open(pres_path, "w", encoding="utf-8") as f:
        f.write(s)

    # ----- presentation.xml.rels -----
    rels_path = f"{BUILD_DIR}/ppt/_rels/presentation.xml.rels"
    with open(rels_path, encoding="utf-8") as f:
        rels_s = f.read()
    # 移除原有的 slide Relationship
    rels_s = re.sub(r'<Relationship Id="[^"]*" Type="[^"]*/relationships/slide" Target="[^"]*"/>', '', rels_s)
    # 添加新的 slide Relationship
    new_slide_rels = ''
    for i in range(1, TOTAL_SLIDES+1):
        r_id = 100 + i
        new_slide_rels += (f'<Relationship Id="rId{r_id}" '
                          f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
                          f'Target="slides/slide{i}.xml"/>')
    rels_s = rels_s.replace('</Relationships>', new_slide_rels + '</Relationships>')
    with open(rels_path, "w", encoding="utf-8") as f:
        f.write(rels_s)

    # ----- [Content_Types].xml -----
    ct_path = f"{BUILD_DIR}/[Content_Types].xml"
    with open(ct_path, encoding="utf-8") as f:
        ct_s = f.read()
    # 移除原 slide Override
    ct_s = re.sub(r'<Override[^/]*PartName="/ppt/slides/slide[^"]*"[^/]*/>', '', ct_s)
    ct_s = re.sub(r'<Override[^/]*PartName="/ppt/notesSlides/notesSlide[^"]*"[^/]*/>', '', ct_s)
    # 添加新的 slide Override
    new_overrides = ''
    for i in range(1, TOTAL_SLIDES+1):
        new_overrides += (f'<Override PartName="/ppt/slides/slide{i}.xml" '
                         f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    ct_s = ct_s.replace('</Types>', new_overrides + '</Types>')
    with open(ct_path, "w", encoding="utf-8") as f:
        f.write(ct_s)

    print(f"已更新 presentation.xml / rels / [Content_Types].xml")


def pack_pptx():
    """打包 BUILD_DIR 为 pptx"""
    if os.path.exists(OUTPUT_PPTX):
        os.remove(OUTPUT_PPTX)
    with zipfile.ZipFile(OUTPUT_PPTX, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BUILD_DIR):
            for file in files:
                src = os.path.join(root, file)
                rel = os.path.relpath(src, BUILD_DIR)
                zf.write(src, rel)
    print(f"已打包 PPT → {OUTPUT_PPTX}")
    print(f"   文件大小: {os.path.getsize(OUTPUT_PPTX)/1024:.1f} KB")


def main():
    print(f"工作目录: {BUILD_DIR}")
    print(f"输出文件: {OUTPUT_PPTX}")
    print()
    build_slides()
    update_presentation_meta()
    pack_pptx()
    print()
    print("✅ 生成完成！")


if __name__ == "__main__":
    main()
