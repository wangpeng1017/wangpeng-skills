---
name: image-gen
description: 调用 wisart.kuaileshifu.com gpt-image-2 API 生成图片。当用户说"生图"、"生成图片"、"画一张"、"AI生图"时自动触发。无需配置，开箱即用。
version: 1.0.0
---

# 生图 Skill — wisart gpt-image-2

## 触发词
用户说以下任意词即触发本 skill（无需输入 /image-gen）：
- 生图、生成图片、生成一张图、画一张、AI 生图、帮我生图
- 配合描述词使用，如："生图：NPI 流程图"、"帮我生成一张苹果供应链的图"

## 执行步骤

1. **理解用户意图**，将描述翻译为英文 prompt（中文 prompt 效果较差）
2. **确定尺寸**：
   - PPT 配图（横版）→ `1536x1024`（默认）
   - 正方形图标 → `1024x1024`
   - 竖版海报 → `1024x1536`
3. **调用 gen.py**：
   ```bash
   python3 ~/.claude/skills/image-gen/gen.py "英文prompt" 输出路径.png [尺寸]
   ```
4. **Read 生成的图片**展示给用户
5. **告知路径**，方便用户后续使用

## API 信息（内置，无需用户配置）
- Base URL: `https://wisart.kuaileshifu.com/v1`
- Model: `gpt-image-2`
- Key: 已内置 gen.py，勿外泄

## Prompt 写作指南

gpt-image-2 对描述性英文 prompt 效果最好：

```
# 数据可视化 / 信息图
"Clean modern infographic showing [topic], dark navy blue background, 
 teal accent colors, geometric shapes, professional business style, 
 high contrast white text, minimalist design"

# 流程图 / 架构图
"Professional flowchart diagram of [process], dark theme, 
 connecting arrows, color-coded stages, clean flat design style"

# 背景图 / 封面
"Abstract technology background, [color] gradient, 
 circuit board patterns, particle effects, futuristic digital art"

# 图标 / 插图
"Flat icon illustration of [subject], simple geometric style, 
 [color] palette, white background, minimal detail"
```

## 默认输出路径

- 单次生图：`~/Downloads/gen_YYYYMMDD_HHMMSS.png`
- PPT 配图：存放在当前项目的 `workspace/images/` 目录下

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| HTTP 429 | 频率限制 | 等待 10s 重试 |
| HTTP 401 | key 失效 | 告知王老师更新 key |
| timeout | 网络慢 | 重试一次（生图通常需 15-45s）|
