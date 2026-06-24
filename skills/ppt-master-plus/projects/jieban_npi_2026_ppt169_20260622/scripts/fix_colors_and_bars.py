"""
fix_colors_and_bars.py
修复两个问题:
1. 去掉右侧两个竖条 (P01封面的polygon+右矩形, P03/P06/P09/P11/P14章节页的右双栏)
2. 颜色克制: 每页不超过3种颜色，去掉 #FBAE40/#52C41A/#9B59B6/#FF6B6B，统一到橙色(#F26B43)+青色(#5ACBF0)体系
"""
import re
import os
import sys

SVG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "svg_output")

# ─── 颜色替换表 ────────────────────────────────────────────────────────────────
# 只保留: #00284C/#003A6E/#1A4A7A(背景族) + #F26B43(主橙) + #5ACBF0(辅蓝) + #E8EDF2/#9BAABB(文本)
COLOR_MAP = [
    ("#FBAE40", "#F26B43"),   # 黄橙 → 橙 (统一橙色族)
    ("#52C41A", "#5ACBF0"),   # 绿   → 蓝绿 (去除绿色)
    ("#9B59B6", "#F26B43"),   # 紫   → 橙
    ("#FF6B6B", "#F26B43"),   # 红警示 → 橙
    ("#0D4F8C", "#003A6E"),   # 中蓝  → 深蓝 (背景族统一)
    ("#E67E22", "#F26B43"),   # 旧橙  → 主橙
]

# ─── 去除右侧竖条的 regex 模式 ─────────────────────────────────────────────────
# 封面 P01: 半透明平行四边形装饰
COVER_POLYGON_PATTERN = re.compile(
    r'\s*<polygon\s+points="840,0\s+1280,0\s+1280,720\s+940,720"[^/]*/>\s*\n?',
    re.DOTALL
)
# 封面 P01: 右侧不透明橙色矩形条 x=1200 width=80
COVER_SOLID_BAR_PATTERN = re.compile(
    r'\s*<rect\s+x="1200"\s+y="0"\s+width="80"\s+height="720"[^/]*/>\s*\n?',
    re.DOTALL
)
# 章节页 P03/06/09/11/14: 宽底色条 x=1170 width=110
CHAPTER_WIDE_BAR_PATTERN = re.compile(
    r'\s*<rect\s+x="1170"\s+y="0"\s+width="110"\s+height="720"[^/]*/>\s*\n?',
    re.DOTALL
)
# 章节页 P03/06/09/11/14: 细橙条 x=1235 width=45
CHAPTER_THIN_BAR_PATTERN = re.compile(
    r'\s*<rect\s+x="1235"\s+y="0"\s+width="45"\s+height="720"[^/]*/>\s*\n?',
    re.DOTALL
)

# ─── 主处理 ────────────────────────────────────────────────────────────────────
def fix_svg(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 颜色替换
    for old_color, new_color in COLOR_MAP:
        content = content.replace(old_color, new_color)

    # 2. 去除右侧竖条
    content = COVER_POLYGON_PATTERN.sub('\n', content)
    content = COVER_SOLID_BAR_PATTERN.sub('\n', content)
    content = CHAPTER_WIDE_BAR_PATTERN.sub('\n', content)
    content = CHAPTER_THIN_BAR_PATTERN.sub('\n', content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    svg_files = sorted([f for f in os.listdir(SVG_DIR) if f.endswith('.svg')])
    changed = []
    unchanged = []

    for fname in svg_files:
        fp = os.path.join(SVG_DIR, fname)
        if fix_svg(fp):
            changed.append(fname)
        else:
            unchanged.append(fname)

    print(f"修改了 {len(changed)} 个文件:")
    for f in changed:
        print(f"  ✓ {f}")
    if unchanged:
        print(f"\n无需修改: {len(unchanged)} 个")
    print("\n完成。")


if __name__ == '__main__':
    main()
