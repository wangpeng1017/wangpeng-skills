"""生成 9 个统一线性风格的图标（白色细描线 · 平面风 · 模仿 iconfont 标准）"""
import os
import cairosvg

OUT_DIR = "/Users/wangpeng/Downloads/yushu/projects/humanoid_case/template_analysis/v19_build/ppt/media"

# 统一样式
STROKE = "#FFFFFF"
SW = 5  # stroke-width
COMMON_ATTRS = f'fill="none" stroke="{STROKE}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"'

def svg_wrap(content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<g {COMMON_ATTRS}>
{content}
</g>
</svg>'''

ICONS = {
    # 1. 文档/订单
    "icon_document": '''
<rect x="25" y="12" width="50" height="76" rx="3"/>
<line x1="35" y1="32" x2="65" y2="32"/>
<line x1="35" y1="46" x2="65" y2="46"/>
<line x1="35" y1="60" x2="55" y2="60"/>
<circle cx="32" cy="32" r="0.5" fill="#FFFFFF"/>
''',
    # 2. 日历
    "icon_calendar": '''
<rect x="15" y="22" width="70" height="65" rx="3"/>
<line x1="15" y1="40" x2="85" y2="40"/>
<line x1="30" y1="14" x2="30" y2="28"/>
<line x1="70" y1="14" x2="70" y2="28"/>
<circle cx="30" cy="52" r="2.5" fill="#FFFFFF" stroke="none"/>
<circle cx="46" cy="52" r="2.5" fill="#FFFFFF" stroke="none"/>
<circle cx="62" cy="52" r="2.5" fill="#FFFFFF" stroke="none"/>
<circle cx="30" cy="68" r="2.5" fill="#FFFFFF" stroke="none"/>
<circle cx="46" cy="68" r="2.5" fill="#FFFFFF" stroke="none"/>
<circle cx="62" cy="68" r="2.5" fill="#A5D867" stroke="none"/>
''',
    # 3. 包装盒（立方体）
    "icon_package": '''
<polygon points="50,12 84,28 84,72 50,88 16,72 16,28"/>
<polyline points="16,28 50,42 84,28"/>
<line x1="50" y1="42" x2="50" y2="88"/>
<line x1="32" y1="20" x2="68" y2="36"/>
''',
    # 4. 齿轮（标准齿轮+小齿轮组合，表"部件装配"）
    "icon_gear": '''
<path d="M44 14 L56 14 L57 22 L63 25 L70 21 L78 29 L74 36 L77 42 L85 43 L85 55 L77 56 L74 62 L78 69 L70 77 L63 73 L57 76 L56 84 L44 84 L43 76 L37 73 L30 77 L22 69 L26 62 L23 56 L15 55 L15 43 L23 42 L26 36 L22 29 L30 21 L37 25 L43 22 Z"/>
<circle cx="50" cy="49" r="9"/>
''',
    # 5. 机器人
    "icon_robot": '''
<line x1="50" y1="8" x2="50" y2="18"/>
<circle cx="50" cy="8" r="2.5" fill="#FFFFFF" stroke="none"/>
<rect x="28" y="20" width="44" height="32" rx="5"/>
<circle cx="40" cy="36" r="3.5" fill="#FFFFFF" stroke="none"/>
<circle cx="60" cy="36" r="3.5" fill="#FFFFFF" stroke="none"/>
<rect x="30" y="56" width="40" height="32" rx="4"/>
<line x1="30" y1="68" x2="20" y2="78"/>
<line x1="70" y1="68" x2="80" y2="78"/>
<line x1="42" y1="88" x2="42" y2="94"/>
<line x1="58" y1="88" x2="58" y2="94"/>
''',
    # 6. 显示器/测试
    "icon_monitor": '''
<rect x="12" y="18" width="76" height="50" rx="3"/>
<line x1="34" y1="80" x2="66" y2="80"/>
<line x1="50" y1="68" x2="50" y2="80"/>
<polyline points="22,52 32,38 42,55 52,32 62,48 78,38"/>
''',
    # 7. 盾牌/质量
    "icon_shield": '''
<path d="M50 12 L78 22 L78 48 C78 68 65 80 50 88 C35 80 22 68 22 48 L22 22 Z"/>
<polyline points="36,52 46,62 64,42"/>
''',
    # 8. 卡车/仓储发货
    "icon_truck": '''
<rect x="10" y="35" width="48" height="32" rx="2"/>
<path d="M58 47 L72 47 L86 58 L86 67 L58 67 Z"/>
<rect x="64" y="51" width="14" height="10"/>
<line x1="10" y1="67" x2="86" y2="67"/>
<circle cx="24" cy="75" r="7"/>
<circle cx="72" cy="75" r="7"/>
''',
    # 9. 耳机/售后
    "icon_headset": '''
<path d="M22 60 Q22 22 50 22 Q78 22 78 60"/>
<rect x="14" y="56" width="14" height="22" rx="3"/>
<rect x="72" y="56" width="14" height="22" rx="3"/>
<polyline points="22,78 22,86 32,86"/>
<circle cx="36" cy="86" r="2.5" fill="#FFFFFF" stroke="none"/>
''',
    # 10. 眼睛（现状/观察）
    "icon_eye": '''
<path d="M10 50 Q30 22 50 22 Q70 22 90 50 Q70 78 50 78 Q30 78 10 50 Z"/>
<circle cx="50" cy="50" r="14"/>
<circle cx="50" cy="50" r="5" fill="#FFFFFF" stroke="none"/>
''',
    # 11. 警告三角（痛点）
    "icon_alert": '''
<path d="M50 14 L90 80 L10 80 Z"/>
<line x1="50" y1="38" x2="50" y2="60"/>
<circle cx="50" cy="70" r="3" fill="#FFFFFF" stroke="none"/>
''',
    # 12. 下降趋势（业务影响/损失）
    "icon_loss": '''
<polyline points="12,28 32,46 50,38 68,58 86,76"/>
<polyline points="86,76 86,58 70,76"/>
<line x1="12" y1="86" x2="86" y2="86"/>
''',
    # 13. 对勾（解决方案）
    "icon_check": '''
<circle cx="50" cy="50" r="36"/>
<polyline points="32,52 44,64 68,40"/>
''',
    # 14. 上升图表（价值收益）
    "icon_chart": '''
<polyline points="14,70 32,52 50,58 68,38 86,22"/>
<polyline points="86,22 86,38 70,22"/>
<line x1="14" y1="86" x2="86" y2="86"/>
<rect x="20" y="58" width="8" height="22" fill="#FFFFFF" stroke="none" opacity="0.3"/>
<rect x="38" y="48" width="8" height="32" fill="#FFFFFF" stroke="none" opacity="0.3"/>
<rect x="56" y="38" width="8" height="42" fill="#FFFFFF" stroke="none" opacity="0.3"/>
<rect x="74" y="28" width="8" height="52" fill="#FFFFFF" stroke="none" opacity="0.3"/>
''',
}

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, content in ICONS.items():
        svg = svg_wrap(content)
        png_path = f"{OUT_DIR}/{name}.png"
        cairosvg.svg2png(bytestring=svg.encode('utf-8'),
                         write_to=png_path,
                         output_width=512,
                         output_height=512)
        print(f"  ✓ {name}.png")
    print(f"\n共生成 {len(ICONS)} 个图标到 {OUT_DIR}")

if __name__ == "__main__":
    main()
