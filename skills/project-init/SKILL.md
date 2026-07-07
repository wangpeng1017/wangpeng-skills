---
name: project-init
description: 新项目初始化：判定项目类型→加载对应 profile→按清单落地王老师的三层规则体系（PRD、PROJECT_INDEX.md、项目级 CLAUDE.md、docs/_INDEX.md、git init）。当王老师说"新建项目"、"初始化项目"、"/project-init"，或在一个没有 CLAUDE.md/PRD 的新目录里开始正式开发时使用。
---

# project-init — 新项目初始化

> 目的：把 `~/.claude/CLAUDE.md` 三层规则体系（L0 全局 / L1 项目类型 / L2 项目专属）在新项目里**可靠落地**，
> 不依赖模型自觉。执行完向王老师报告清单。

## 第 1 步：判定项目类型（路由表）

| 类型 | 识别特征 | 加载 profile |
|------|---------|-------------|
| **Web 开发** | `package.json` + `next.config`/React/Prisma | `~/.claude/profiles/web-nextjs.md` |
| **工业互联网** | 部署 SOP/生产环境/MES/设备产线/上位机 | `~/.claude/profiles/industrial-iot.md` |
| **自动化脚本** | 单文件/scripts 下一次性 Node/Py、运维诊断 | `~/.claude/profiles/automation-script.md` |
| **文档生成** | 产出 pptx/docx/方案/投标 | `~/.claude/profiles/doc-generation.md` |

- 一个项目可叠加多份（如 LIMS = web-nextjs + industrial-iot）
- **判断不清就问王老师，不要猜**

## 第 2 步：Read 对应 profile

立即 `Read` 第 1 步命中的 profile 文件（叠加类型全部读），本会话按其规则工作。

## 第 3 步：初始化清单（按类型裁剪）

按顺序执行，已存在的文件跳过（**绝不覆盖已有内容**）：

### 所有类型
1. `git init`（如未初始化）+ `.gitignore`
2. **项目级 `CLAUDE.md` 骨架**，只写项目专属家规，不复制全局规则：
   - 项目一句话 + 技术栈
   - 部署路径/命令/服务器信息（如有生产环境，标"最高优先级"）
   - 必读文件指针（PROJECT_INDEX.md、PRD.md）

### Web 开发 / 工业互联网（正式项目）
3. `docs/PRD.md` — 从 `~/.claude/reference/prd-template.md` 初始化，状态标记 🔴待开发 🟡开发中 🟢已完成 ⚫已废弃
4. `docs/_INDEX.md` — docs 目录索引
4b. `docs/SHIP-PROFILE.md` — 发版档案，从 ship skill 的 `PROFILE-TEMPLATE.md` 初始化（构建/测试/测试环境/生产发版命令；部署方式未定的字段先标 TODO，问王老师）。这是 `/ship` 通用流程的项目接口
5. **`PROJECT_INDEX.md`（L1 项目地图）** — 新项目先写骨架，包含：
   - 项目一句话 + 技术栈表
   - 核心业务链路（Mermaid 图 + 关键不变量）
   - 目录结构（只列施工常去处）
   - 功能域地图（页面↔API↔lib↔数据模型对照，随开发补全）
   - 文档指针
   - 文件头注明维护策略：**不做严格同步，大版本手动刷新，过期时以真实代码为准**
   （存量项目参考样例：`~/Downloads/0103limsnext/PROJECT_INDEX.md`）

### 自动化脚本 / 文档生成（轻量项目）
只做 1-2，PRD/PROJECT_INDEX 不建（YAGNI）；脚本按 profile 里的输出断言规范写。

## 第 4 步：报告

```
项目类型：X（+叠加 Y）| 已加载 profile：...
已创建：CLAUDE.md / docs/PRD.md / PROJECT_INDEX.md / ...
已跳过（已存在）：...
```

## 铁律

- 已有文件**只补指针不覆盖**；发现现状与预期不符先报告王老师
- 本 skill 只做初始化，不写业务代码
- 老项目补索引也可用本 skill（跳过已存在项，只补缺的）
