# 王老师的 Skills 统一仓库

这是一个集中管理所有 Claude Code Skills 的仓库，采用软链接方式实现跨 Agent 框架共享。

## 目录结构

```
~/GitHub/wangpeng-skills/skills/     ← Skills 原件（单一真相来源）
    ↓
~/.agents/skills/                    ← 中间层（多工具共享）
    ↓
~/.claude/skills/                    ← Claude Code 入口
~/.codex/skills/                     ← Codex 入口
~/.qoder/skills/                     ← QoderCLI 入口
```

## Skills 列表

### 文档系列
- docx - Word 文档处理
- pptx - PowerPoint 演示文稿
- pdf - PDF 文档处理
- xlsx - Excel 电子表格

### PPT 生成系列
- ppt-master - PPT 生成工具
- ppt-master-plus - PPT 生成增强版
- ppt-master-chrisopal - PPT 生成定制版

### 图片生成系列
- baoyu-image-gen - 宝玉图片生成
- image-gen - 通用图片生成
- guizang-social-card-skill - 社交卡片生成

### 其他
- ui-ux-pro-max - UI/UX 设计
- doc-coauthoring - 文档协作
- yushu-deploy - 宇树项目部署

## 维护说明

1. **更新 Skill**：直接在 `~/GitHub/wangpeng-skills/skills/` 下修改，所有工具自动生效
2. **添加新 Skill**：将新 Skill 放入 `skills/` 目录，然后创建软链接
3. **删除 Skill**：删除软链接，保留或删除原件根据需要决定

## 优势

- **单一真相来源**：Skills 原件只有一份，避免重复维护
- **跨工具共享**：Claude Code、Codex、QoderCLI 共享同一套 Skills
- **更新同步**：更新一次，所有工具立即生效
- **节约空间**：通过软链接避免文件重复
