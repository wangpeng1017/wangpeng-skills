# NPI阶段数字化应用解决方案接榜挂帅申报 - Design Spec

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | jieban_npi_2026 |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 18 |
| **Design Style** | briefing × tech-enterprise, 深色科技商务风 |
| **Target Audience** | 公司评审委员会：高管+技术专家+财务专家，内部接榜挂帅项目答辩 |
| **Use Case** | 内部项目申报答辩，论证NPI数字化解决方案产品化可行性与商业价值 |
| **Created Date** | 2026-06-22 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 px |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 60px, top 50px, bottom 50px |
| **Content Area** | 1160×620px (x60–x1220, y50–y670) |

---

## III. Visual Theme

### Theme Style

- **Mode**: briefing
- **Visual style**: tech-enterprise
- **Theme**: Dark theme (深蓝底)
- **Tone**: 权威、专业、数据化、创新感强。深蓝背景营造稳重感，橙红+金黄主色传递活力与可信度。

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#00284C` | 页面背景，深海军蓝 |
| **Secondary bg** | `#003A6E` | 卡片背景、区块底色 |
| **Tertiary bg** | `#0D4F8C` | 高亮卡片、章节标题区块 |
| **Primary** | `#F26B43` | 标题装饰、关键章节、高亮数字 |
| **Accent** | `#FBAE40` | 数据强调、进度条、警告色 |
| **Secondary accent** | `#5ACBF0` | 青色点缀、链接、次要指标 |
| **Body text** | `#E8EDF2` | 正文文字（白色系） |
| **Secondary text** | `#9BAABB` | 注释、说明文字 |
| **Tertiary text** | `#6B7F94` | 页脚、辅助信息 |
| **Border/divider** | `#1A4A7A` | 卡片边框、分割线 |
| **Success** | `#52C41A` | 正向指标、✓ |
| **Warning** | `#FF6B6B` | 风险标记、✗ |

### Gradient Scheme

```xml
<!-- 章节opener渐变 -->
<linearGradient id="chapterGrad" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="#F26B43" stop-opacity="0.9"/>
  <stop offset="100%" stop-color="#FBAE40" stop-opacity="0.7"/>
</linearGradient>

<!-- 背景装饰径向渐变 -->
<radialGradient id="bgDecor" cx="85%" cy="15%" r="45%">
  <stop offset="0%" stop-color="#0D4F8C" stop-opacity="0.6"/>
  <stop offset="100%" stop-color="#00284C" stop-opacity="0"/>
</radialGradient>

<!-- 卡片强调渐变 -->
<linearGradient id="cardAccentGrad" x1="0%" y1="0%" x2="0%" y2="100%">
  <stop offset="0%" stop-color="#F26B43" stop-opacity="1"/>
  <stop offset="100%" stop-color="#FBAE40" stop-opacity="1"/>
</linearGradient>
```

---

## IV. Typography System

### Font Plan

**Typography direction**: Modern CJK sans — Microsoft YaHei 统一 CJK+Latin，清晰工整，PPT 跨平台安全。

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Emphasis** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Code** | — | `Consolas, "Courier New"` | `monospace` |

**Per-role font stacks**:
- Title: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Body: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Emphasis: same as Body
- Code: `Consolas, "Courier New", monospace`

### Font Size Hierarchy

**Baseline**: Body font size = 18px (中等密度内容页)

| Purpose | Ratio | Size |
| ------- | ----- | ---- |
| Cover title (hero headline) | ~4x | 72px |
| Chapter opener number | ~4.5x | 80px |
| Page title | 1.8x | 32px |
| Hero number / KPI | 2.2x | 40px |
| Subtitle / card title | 1.4x | 24px |
| **Body content** | **1x** | **18px** |
| Annotation / caption | 0.75x | 14px |
| Page number / footnote | 0.6x | 11px |

---

## V. Layout Principles

### Page Structure

- **Header area**: y0–y75 — 左上角 logo/组织名，右侧页码；高75px
- **Title bar**: y75–y140 — 页标题区域，包含装饰线条和章节标识
- **Content area**: y140–y680 — 主内容区，宽1160px（x60–x1220）
- **Footer area**: y680–y720 — 页码、版权、网址

### Layout Pattern Library

| 页面类型 | 模式 |
| ------- | --- |
| 封面 | 全幅背景 + 居中浮动标题，带几何装饰 |
| 目录 | 5列/5行图标+文字，对称布局 |
| 章节opener | 超大编号 + 标题 + 简短副标题，大量留白 |
| 数据卡片页 | 2×2 或 1×4 卡片网格，每卡含图标+数字+标签 |
| 表格/矩阵 | 全宽表格，斑马纹，图标替代文字 |
| 架构图 | 分层矩形块，箭头连接，顶层AI/底层平台 |
| 三列卡片 | 3等宽卡片，图标居中+标题+要点 |
| 风险矩阵 | 2×3 风险卡片，左侧色标+风险名+应对措施 |
| 组织架构 | 树形，顶部指导委员会→中层→底层执行 |
| 饼图+明细 | 左50%环形图，右50%明细表 |
| 柱状图+卡片 | 上60%grouped bar，下40%汇总KPI卡片 |
| 空白表格 | 全幅表格，表头橙色，12空行 |

### Spacing Specification

**Universal**:
| Element | Value |
| ------- | ----- |
| Safe margin from canvas edge | 60px |
| Content block gap | 28px |
| Icon-text gap | 10px |

**Card-based layouts**:
| Element | Value |
| ------- | ----- |
| Card gap | 24px |
| Card padding | 24px |
| Card border radius | 10px |

---

## VI. Icon Usage Specification

### Source

- **Library**: `tabler-outline`，stroke-width: 2
- **Brand library**: none

### Recommended Icon List

| Purpose | Icon Path | Page |
| ------- | --------- | ---- |
| 技术/AI | `tabler-outline/brain` | P08 |
| 图纸识别 | `tabler-outline/scan` | P08 |
| 文档生成 | `tabler-outline/file-check` | P08 |
| 数据图表 | `tabler-outline/chart-bar` | P04 |
| 目标/考核 | `tabler-outline/target` | P10 |
| 安全/风险 | `tabler-outline/shield-check` | P12 |
| 团队 | `tabler-outline/users` | P13 |
| 预算/金额 | `tabler-outline/coins` | P15 |
| 人民币 | `tabler-outline/currency-yuan` | P16 |
| 数据分析 | `tabler-outline/device-desktop-analytics` | P04 |
| AI机器人 | `tabler-outline/robot` | P07 |
| 增长趋势 | `tabler-outline/trending-up` | P16 |
| 时间进度 | `tabler-outline/clock` | P10 |
| 勋章/奖励 | `tabler-outline/award` | P04 |
| 警告 | `tabler-outline/alert-triangle` | P12 |
| 成功 | `tabler-outline/circle-check` | P05 |
| 失败/缺失 | `tabler-outline/circle-x` | P05 |
| 火箭/速度 | `tabler-outline/rocket` | P04 |
| 层级 | `tabler-outline/layers` | P07 |
| 工厂 | `tabler-outline/building-factory` | P04 |
| CPU/算力 | `tabler-outline/cpu` | P08 |

---

## VII. Visualization Reference List

| Page | Template | Path | Summary-quote | Usage |
| ---- | -------- | ---- | -------------- | ----- |
| P05 | feature_matrix_table | `templates/charts/feature_matrix_table.svg` | "Pick for competitive feature checklist with checkmarks across products. Skip for qualitative scores" | 竞品对比矩阵，5行功能×5列（4竞品+本方案） |
| P10 | bullet_chart | `templates/charts/bullet_chart.svg` | "Pick for 3-7 KPIs each with explicit target + actual. Skip for single metric (use gauge_chart) or it" | 6项考核指标，目标值+当前状态 |
| P15 | donut_chart | `templates/charts/donut_chart.svg` | "Pick for 3-6 part proportions where a center KPI/total deserves emphasis. Skip if no center value to" | 经费预算7科目环形图，中心显示"260万" |
| P16 | grouped_bar_chart | `templates/charts/grouped_bar_chart.svg` | "Pick for 2-4 series side-by-side across the same categories (e.g. YoY/QoQ). Skip if showing composit" | 3年收益预测，每年低/高两条柱 |

**Runners-up considered**:
- `donut_chart` rejected for P10: 考核指标需展示多项KPI+目标对比，donut只适合单一比例；bullet_chart更匹配"当前vs目标"结构
- `pie_chart` rejected for P15: 7个科目超出pie的推荐上限(3-6)，且无法突出中心"260万总额"；donut_chart是最优选择
- `kpi_cards` rejected for P10: KPI卡片缺少目标线对比视觉，bullet_chart的进度条设计能直观展示目标达成度

---

## VIII. Image Resource List

无外部图片 — 全部使用 SVG 图形元素（图标、图表、几何装饰）。

---

## IX. Content Outline

### Part 0: 封面与导航

#### P01 — 封面 (Cover)

- **Layout**: 全幅深蓝背景 + 右侧橙色几何装饰带 + 左侧浮动标题
- **Rhythm**: anchor
- **Title**: NPI阶段数字化应用解决方案
- **Core message**: 以标杆验证为基础，海克斯康申报NPI数字化产品化项目，争夺接榜挂帅席位。
- **Content**:
  - 主标题（大字，白色）: NPI阶段数字化应用解决方案
  - 副标题（橙红）: 接榜挂帅项目申报
  - 下方信息行: 海克斯康工业互联网研究院  ·  2026年
  - 右侧装饰: 橙色斜向色带 + 线条几何图形
  - 左下角: Hexagon LOGO占位 + 网站 hexagonmi.com.cn

#### P02 — 目录 (Agenda)

- **Layout**: 5行横向条目，每行含编号圆圈+章节名+简短描述
- **Rhythm**: anchor
- **Title**: 目录 CONTENTS
- **Core message**: 五章结构完整覆盖项目申报所需的背景、技术、指标、风险与效益。
- **Content**:
  - 01 · 背景与行业竞品 — 行业机遇与竞争格局
  - 02 · 技术路线 — "1平台+N个AI应用"技术架构
  - 03 · 考核指标 — 可量化、可验证的验收标准
  - 04 · 实施风险及团队保障 — 风险识别与人员组织
  - 05 · 经费预算及经济效益 — 详细预算与收益预测

---

### Part 1: 背景与行业竞品

#### P03 — 章节Opener

- **Layout**: 超大章节编号"01" + 章节标题 + 副标题，右侧橙色装饰带
- **Rhythm**: breathing
- **Core message**: 精密零部件消费电子供应商NPI数字化是巨大蓝海市场，海克斯康有先发优势。

#### P04 — 行业背景与市场机遇

- **Layout**: 上方2个大数据卡片 + 下方3个痛点卡片（带图标）
- **Rhythm**: dense
- **Title**: 行业背景与市场机遇
- **Core message**: Apple供应链精密件制造商NPI数字化需求迫切，磁声标杆已验证方案可行性。
- **Content**:
  - 大数据卡：200+ | Apple供应链精密件制造商（潜在客户池）
  - 大数据卡：50%+ | NPI文档编制耗时占项目周期比例
  - 痛点①（rocket图标）：NPI文档编制人工化 — 全依赖Excel/PPT，无数字化工具
  - 痛点②（device-desktop-analytics图标）：数据分散无法追溯 — CPK/CRR数据手工汇总，易错
  - 痛点③（award图标）：海克斯康磁声标杆已验证 — 2026Q1完成全流程方案验证，具备复制基础

#### P05 — 行业竞品分析

- **Layout**: feature_matrix_table，4竞品 vs 本方案，5维度对比
- **Rhythm**: dense
- **Title**: 竞品对比分析
- **Visualization**: feature_matrix_table
- **Core message**: 现有竞品均无法兼顾NPI专项深度与AI智能辅助，本方案具有差异化竞争优势。
- **Content**（5维度 × 5产品对比）:
  - 维度: NPI专项流程 / AI文档辅助 / 实施周期 / 总成本 / Apple供应链适配
  - SAP PLM: ✗ / ✗ / 18-24月 / 500万+ / ✗
  - PTC Windchill: ✓ / ✗ / 12-18月 / 400万+ / ✗
  - 鼎捷MES/QMS: ✗ / ✗ / 6-12月 / 100-200万 / ✗
  - 明道云: ✗ / ✗ / 3-6月 / 50-100万 / ✗
  - **本方案**: ✓ / ✓ / 13月 / 150-250万 / ✓

---

### Part 2: 技术路线

#### P06 — 章节Opener

- **Layout**: 超大"02" + 章节标题 + 副标题
- **Rhythm**: breathing
- **Core message**: 构建"1个平台+N个AI应用"产品化NPI数字化解决方案。

#### P07 — 技术架构与实现路径

- **Layout**: 三层分层架构图（顶部AI应用层、中间平台层、底部数据层）+ 左侧标签
- **Rhythm**: dense
- **Title**: 技术架构：1平台 + N个AI应用
- **Core message**: "1个NPI研发协同平台"承载业务在线化，"N个AI智能体"驱动文档生成效率提升30%+。
- **Content**:
  - 顶层（AI应用层，橙色背景）: 图纸OCR识别 | Q-Plan自动生成 | FAI/CRR报告 | DFM规则推荐 | …
  - 中层（平台层，深蓝卡片）: 项目管理 | 任务调度 | 图纸评审 | 进度看板 | 多端协同
  - 底层（数据层，青色）: 图纸库 | 工艺知识库 | DFM规则库 | 问题经验库 | 检验标准库
  - 左侧集成标签: ERP / MES / QMS / 企微飞书

#### P08 — 关键技术突破

- **Layout**: icon_grid，3列等宽卡片
- **Rhythm**: dense
- **Title**: 三大关键技术突破
- **Visualization**: icon_grid
- **Core message**: 图纸智能识别、知识库RAG检索、多模态文档生成三项技术协同，实现NPI全链路AI辅助。
- **Content**:
  - 卡片①（scan图标）: 工程图纸智能识别 — AABB碰撞盒+GNN边生成+OCR，图纸识别准确率目标≥85%
  - 卡片②（brain图标）: RAG知识库检索 — 历史DR问题库+DFM规则库，专业解决方案智能推荐
  - 卡片③（file-check图标）: 多模态文档自动生成 — 23类NPI表单AI辅助填写，编制效率提升≥30%

---

### Part 3: 考核指标

#### P09 — 章节Opener

- **Layout**: 超大"03" + 章节标题 + 副标题
- **Rhythm**: breathing
- **Core message**: 设立可量化、可验证、可追溯的项目验收标准，确保申报指标客观可信。

#### P10 — 考核指标详表

- **Layout**: bullet_chart（6行KPI，每行含目标线+进度条）+ 右侧分类标签
- **Rhythm**: dense
- **Title**: 考核指标（可量化 · 可验证 · 可追溯）
- **Visualization**: bullet_chart
- **Core message**: 六项指标覆盖交付时效、功能完成度、业务效益、用户体验，全部可在系统日志中客观核查。
- **Content**（指标名 | 目标值 | 验证方式）:
  - 项目总工期 | ≤13个月 | 合同节点+里程碑签收
  - NPI文档编制效率提升 | ≥30% | 上线前后工时对比
  - 图纸OCR识别准确率 | ≥85% | 标准测试集评测
  - 平台功能交付率 | 100% | 功能清单逐项验收
  - 用户满意度 | ≥4.0/5.0 | 系统内问卷
  - 活跃用户占比（上线3月内） | ≥80% | 系统登录日志

---

### Part 4: 实施风险及团队保障

#### P11 — 章节Opener

- **Layout**: 超大"04" + 章节标题
- **Rhythm**: breathing
- **Core message**: 识别5大主要风险并制定应对措施，配备8人专业团队保障高质量交付。

#### P12 — 实施风险识别与应对

- **Layout**: 2列×3行风险卡片（+1个总结条），每卡含风险级别色标+名称+应对措施
- **Rhythm**: dense
- **Title**: 实施风险识别与应对措施
- **Core message**: 5大风险均有明确应对策略，技术风险通过分阶段交付化解，业务风险通过深度调研防范。
- **Content**（级别 | 风险名称 | 应对措施）:
  - 高 | AI图纸识别准确率 | 分阶段交付，先平台后AI；85%兜底+人工复核
  - 中 | 需求变更 | 整体规划期深度调研2月；分级变更管理机制
  - 中 | 客户数据质量 | 双方联合数据治理工作组；优先高优先级表单数据
  - 低 | 客户人员配合 | 签订项目责任书；里程碑检查节点；双周→单周报
  - 低 | 春节用工风险 | 排期规避春节前后关键节点；知识沉淀降低人员依赖

#### P13 — 项目团队组织保障

- **Layout**: 树形组织架构图（3层）+ 右侧团队优势卡片
- **Rhythm**: dense
- **Title**: 项目团队组织保障
- **Core message**: 8人实战团队+指导委员会双保险，熟悉Apple供应链NPI业务，交付风险可控。
- **Content**:
  - 顶层: 指导委员会（双方公司领导）
  - 中层: 甲方项目经理 | 乙方项目总监
  - 执行层（海克斯康）: 项目经理×1 | 技术经理×1 | 业务顾问×1 | 开发工程师×3 | AI工程师×1
  - 右侧3个优势卡片: ✓ 磁声标杆实战团队 | ✓ Hexagon ORCA自研AI | ✓ 成熟实施方法论

---

### Part 5: 经费预算及经济效益

#### P14 — 章节Opener

- **Layout**: 超大"05" + 章节标题
- **Rhythm**: breathing
- **Core message**: 总投入260万，3年预期收入2550-3900万，ROI显著，投入回收期约14-18个月。

#### P15 — 经费预算明细

- **Layout**: 左50% donut_chart（7色段，中心"260万"），右50%明细表格（7行）
- **Rhythm**: dense
- **Title**: 5.1 经费预算明细（按科目）
- **Visualization**: donut_chart
- **Core message**: 总预算260万，人员费占比最高(57.7%)，算力与工具费保障AI能力建设，预算结构合理透明。
- **Content**（科目 | 金额 | 占比 | 颜色）:
  - 人员费 | 150万 | 57.7% | #F26B43
  - 服务器算力费 | 25万 | 9.6% | #FBAE40
  - 大模型API费 | 20万 | 7.7% | #5ACBF0
  - 不可预见费 | 28万 | 10.8% | #0D4F8C
  - 软件工具费 | 10万 | 3.8% | #52C41A
  - 技术培训费 | 12万 | 4.6% | #9B59B6
  - 差旅外勤费 | 15万 | 5.8% | #E67E22

#### P16 — 经济效益分析

- **Layout**: 上60% grouped_bar_chart（3年×低/高两值），下40%三列产品定价卡+总收益KPI
- **Rhythm**: dense
- **Title**: 5.2 经济效益分析
- **Visualization**: grouped_bar_chart
- **Core message**: 3年累计收入2550-3900万，毛利率35-40%，投入回收期约14-18个月，商业价值明确。
- **Content**:
  - 柱状图3组（低值/高值）: 2026年: 300/450万 | 2027年: 750/1200万 | 2028年: 1500/2250万
  - 定价卡①: 基础版 80~100万/套（NPI协同平台，无AI）
  - 定价卡②: 标准版 150~180万/套（平台+AI辅助，8-12个场景）
  - 定价卡③: 旗舰版 200~250万/套（全部AI应用，23类表单）
  - 总收益KPI: 3年累计 2,550~3,900万元 | 回收期 14~18个月

#### P17 — 潜在客户清单（待补充）

- **Layout**: 全幅表格（表头+12空行），表头橙色，表格深蓝斑马纹
- **Rhythm**: dense
- **Title**: 5.3 潜在客户清单（待补充）
- **Core message**: 10家以上精密件制造商构成初期市场，由王老师在答辩前补充具体客户信息。
- **Content**:
  - 表头: 序号 | 客户名称 | 产品方向 | 所在地 | 当前沟通状态 | 优先级
  - 12行空白预留
  - 底部小字提示: * 请在答辩前补充具体客户信息

---

### Part 6: 结尾

#### P18 — 结束页

- **Layout**: 居中大字 + 下方联系信息 + 背景几何装饰
- **Rhythm**: anchor
- **Core message**: 感谢评审，期待申报获批，共同推进NPI数字化产品化落地。
- **Content**:
  - 主文: 感谢评审委员会
  - 副文: 期待与各位共同推进NPI数字化产品化落地
  - 联系信息区（空白，供填写）
  - Hexagon logo + hexagonmi.com.cn

---

## X. Speaker Notes Requirements

每页配一份简短演讲备注，保存于 `notes/total.md`，涵盖关键论点和过渡语。

---

## XI. Technical Constraints Reminder

1. viewBox: `0 0 1280 720`
2. 背景使用 `<rect>` 元素，禁用 `rgba()`，使用 `stop-opacity`
3. 文字换行使用 `<tspan>`，禁用 `<foreignObject>`
4. 禁止: `mask`, `<style>`, `class`, `foreignObject`, `textPath`, `animate*`, `script`
5. 图标使用 `<use data-icon="tabler-outline/icon-name" width="28" height="28" stroke-width="2"/>`
6. 文字中的 XML 特殊字符必须转义: `&amp;` `&lt;` `&gt;`，特殊符号使用原始 Unicode
7. `<g opacity="...">` 禁止，在子元素上单独设置 opacity
