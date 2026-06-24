# 海克斯康深色背景 PPT 模板 · 设计规范

> 慧新全智工业互联（青岛）· Hexagon MI Powerpoint Template_16-9_zh_2020 风格
> 适用于：智能工厂解决方案、MOM/MES 行业方案、企业数字化转型方案、深色科技感商务汇报

---

## I. 模板概览

| 属性 | 描述 |
| --- | --- |
| **模板名称** | `hexagon_dark` · 海克斯康深色背景 · 慧新全智模板 |
| **关键词** | 海克斯康、慧新全智、深色背景、Hexagon、智能工厂、MOM、MES、工业互联、青绿科技感 |
| **适用场景** | 智能制造方案 / 工业互联网 / 数字化转型 / MES/WMS/QMS/EAM 行业方案 / 深色科技商务汇报 |
| **设计基调** | 深色科技感 · 工业感 · 数据驱动 · 信息密度高 |
| **主题模式** | 深色主题（深墨青背景 + 青色+黄绿强调 + 白色文字） |

---

## II. 画布规范

| 属性 | 值 |
| --- | --- |
| **格式** | 16:9 |
| **尺寸** | 12192000 × 6858000 EMU (1920×1080 视觉) |
| **页边距** | 左右 280000 EMU，顶部 80000 EMU，底部 280000 EMU |

---

## III. 配色体系（来源: theme1.xml Hexagon scheme）

### 主色
| 角色 | 值 | 用途 |
| --- | --- | --- |
| **dark_bg** 深墨青背景 | `#003D4A` | 全局深色背景（layout1 自带径向渐变） |
| **primary** 主青色 | `#0097BA` | 主色强调、章节小标题、卡片色条 |
| **lime** 黄绿强调 | `#A5D867` | 高亮装饰、数字突出、副标题装饰条 |
| **deep_cyan** 深青蓝 | `#005072` | 表头/底带/卡片底色 |
| **light_cyan** 浅青 | `#85CDDB` | 辅助文字、英文标识 |

### 辅色
| 角色 | 值 | 用途 |
| --- | --- | --- |
| **orange** | `#ED8B00` | 警示/痛点标识 |
| **red** | `#E74C3C` | 业务影响/严重负面 |
| **green** | `#509E2F` | 次要正面 |
| **white** | `#FFFFFF` | 文字主色 |
| **text_gray** | `#C8D3D7` | 卡片描述文字（深底浅灰）|
| **card_bg_light** | `#0F3D4A` | 卡片底色（深青蓝半暗）|

---

## IV. 字体方案

| 角色 | 中文 | 英文 |
| --- | --- | --- |
| **major** | 微软雅黑 | Arial |
| **minor** | 微软雅黑 | Arial |

**字号梯度**：
- 封面主标题：48-60pt
- 章节封面：30pt
- 内容主标题：32pt
- 副标题：17pt
- 卡片标题：28pt
- 要点文字：14pt
- 关键数字：18-36pt
- 底部金句：15pt
- 英文标识：9-13pt

---

## V. 5 类页型版式

### 1. 封面（cover）
- 全屏深青色背景（image7.png 波浪+数字流）
- 左上：慧新全智 Logo 横版（image9.png）
- 中部：主副标题 + 中间装饰横条（image10.png 青绿渐变）
- 底部：3 个亮点标签（左侧青条 + 中文 + 英文）
- 右下：合作 Logo（image4.png）

### 2. 目录页（toc）
- 全屏深青色背景
- 左上：大字"目录" 64pt + 副标题
- 中部：5 个章节卡片（深青底 + 大编号 + CN + EN + 描述）
- 右下：圆形 Logo

### 3. 章节过渡页（chapter）
- 全屏深青色背景
- 中部黑色圆角横条标题：青色编号 + 顿号 + CN 章节名
- 下方黄绿色子项描述
- 底部英文 CHAPTER 标识

### 4. 内容页（content）
- 深色径向渐变背景（image2.jpeg）
- **主标题**：y=80000 · 32pt · 白色加粗
- **副标题**：y=686000 · 17pt · 白色（与 layout 自带黑色倒梯形 image5.png 上沿平齐）
- **不带顶栏**（去掉 CHAPTER 提示，主标题居中靠上即可）
- **不带页码**（按王老师指定移除）
- **底部金句条**：青色（primary）底 · 白色 14-15pt · y=5860000
- 主体内容 y0 起始：1450000（与副标题间距 ≈ 400K · 紧凑）

### 5. 封底（ending）
- 深青色背景 + 立体环形装饰（image6.jpeg）
- 大字 "THANK YOU" 80pt 白色
- "Visit" + 公司全称 + 网址
- 右下圆形 Logo

---

## VI. 三栏卡片版式（核心 · 痛点页 / PSV 页）

### 标准三栏卡片
- 卡片宽 3680000 EMU，高 4180000 EMU
- 间距 200000 EMU
- 顶部色条 160000 高（彩色 accent）
- 卡片底色 `card_bg_light` = #0F3D4A
- 顶部 80×80pt 白色线性图标（来自 icons/ 目录）
- EN 标签 13pt（accent 色）居中
- CN 标题 28pt 白色加粗 居中
- 分割线（accent 色，400000 宽 20000 高）居中
- 要点列表 14pt 白色 + 14pt accent 色 ● 装饰

### 关键数字突出格式
当要点形如 `"3-7 天：客诉响应周期"` 时（含 `：` 或 `:` 或 `·`），自动拆为：
- 数字 18pt accent 色加粗
- 描述 13pt 白色

### 三栏类型 1：痛点对比页（章节2 专用）
| 栏 | accent | 图标 |
| --- | --- | --- |
| 现状描述 PRESENT STATE | `#85CDDB` 浅青 | icon_eye.png 眼睛 |
| 痛点表现 PAIN POINTS | `#ED8B00` 橙 | icon_alert.png 警告三角 |
| 业务影响 BUSINESS IMPACT | `#E74C3C` 红 | icon_loss.png 下降趋势 |

底部金句：**橙色 (orange) 底** + ⚠ 符号 + 警示语 15pt

### 三栏类型 2：PSV 解决方案页（章节4 通用）
| 栏 | accent | 图标 |
| --- | --- | --- |
| 业务痛点 PAIN POINT | `#ED8B00` 橙 | icon_alert.png |
| 解决方案 SOLUTION | `#0097BA` 青 | icon_check.png 对勾圆 |
| 价值收益 VALUE | `#A5D867` 黄绿 | icon_chart.png 上升柱状 |

底部金句：**青色 (primary) 底** + 主张文案 15pt

---

## VII. 其他常用版式

### 多卡片网格（5/6 列）
- 用于：研产供销服平台、MES/WMS 功能架构、价值收益总览
- 每卡顶部 80-100K 色条 + 卡片底色 + 大标题（22-28pt）+ 要点

### 业务流程图（角色泳道）
- 横向 4 阶段顶栏（青色色块）
- 左侧 5-6 角色泳道列（深青色 12-13pt）
- 每个阶段-角色交叉点放节点卡片（深底+黄绿左条）

### 5 层架构图
- 左侧 1200K 宽标签列（统一深青色）+ 大编号 28pt 黄绿 + CN 11pt
- 右侧每层 N 个内容卡（深底 + 顶部色条 + 11pt 白色文字）
- 底部金句

### 9 节点业务流程
- 顶部 9 个青色方块（彩色色条 + 80pt 白色专属图标 + CN 14pt）
- 方块间青色箭头
- 下方 9 个深色说明卡片（顶部 lime 细条 + 要点）
- 底部金句含黄绿色"数字主线"高亮

---

## VIII. 14 个 iconfont 风格图标

统一规范：512×512 PNG, 透明背景, 白色描线 stroke-width=5, 圆角端点

| 图标 | 用途 |
| --- | --- |
| icon_document.png | 文档/订单/计划 |
| icon_calendar.png | 日历/排产 |
| icon_package.png | 包装/物料齐套 |
| icon_gear.png | 齿轮/部件装配/底座 |
| icon_robot.png | 机器人/整机装配 |
| icon_monitor.png | 显示器/测试验证 |
| icon_shield.png | 盾牌/质量放行 |
| icon_truck.png | 卡车/仓储发货 |
| icon_headset.png | 耳机/售后反馈 |
| icon_eye.png | 眼睛/现状观察 |
| icon_alert.png | 警告三角/痛点 |
| icon_loss.png | 下降趋势/业务影响 |
| icon_check.png | 对勾圆/解决方案 |
| icon_chart.png | 上升柱状/价值收益 |

新增图标方法：编辑 `generate_icons.py`，按既有规范添加 SVG path，统一描线 5pt、白色、圆角端点。

---

## IX. 调用方式

### 完整生成（推荐）
基于 `build_template.py` 改造：
1. 修改 `BASE_DIR` / `WORK_DIR` / `BUILD_DIR` / `OUTPUT_PPTX` 为新项目路径
2. 准备好基础模板：复制 `template_huixin.pptx` 解压后的目录到 `BUILD_DIR`（保留 theme1.xml + slideMasters + slideLayouts + media + 9 张原始装饰图）
3. 复制 14 个图标到 `BUILD_DIR/ppt/media/`
4. 修改 `CONTENT_RENDERERS` / `CHAPTERS` / `TOTAL_SLIDES` 适配新方案
5. 修改/新增 `body_*` 函数定义每一页内容
6. 运行 `python3 build_template.py`

### 关键 API 速查
- `page_header(title, subtitle)` — 主标题+副标题
- `body_pain_only(...)` — 痛点三栏（现状/痛点/影响）
- `body_psv(...)` — PSV 三栏（痛点/方案/价值）
- `body_business_flow(stages, lanes, summary)` — 角色泳道流程图
- `body_function_arch(modules, summary)` — N 模块功能架构
- `body_scenario(items, summary)` — 6 卡片场景页
- `picture_xml(x, y, w, h, media_file=...)` — 嵌入图片自动注册 rels
- `_render_three_col_card(...)` — 通用三栏卡片
- `make_icon(type, cx, cy, size)` — prstGeom 图标（已废弃，改用 picture_xml + iconfont PNG）

### 注意事项
1. 内容页背景由 layout1 自动提供（深色径向渐变），**严禁**在 slide 上覆盖白色矩形
2. 副标题 y=686000 与 layout 自带黑色倒梯形（x=285750, y=746259）上沿对齐
3. 图标用 picture_xml 嵌入 PNG，不用 prstGeom 自绘
4. 数字突出格式用 `"数字：描述"` 含 `：/:/· `分隔，自动拆分
5. 全 PPT 不放页码（王老师确认偏好）
6. 章节4 模块完整三件套：业务流程 + 功能架构 + PSV 三栏
7. 章节2 痛点页只讲痛点，方案和价值留给章节4 + 章节5
