# SHIP-PROFILE.md 模板（复制到项目 docs/SHIP-PROFILE.md 后填写）

> 本档案是 `/ship` 通用流程的项目接口：ship 的每一步执行**这里声明的命令**。
> 与部署文档的关系：本档案只放"ship 要执行的命令与顺序"，原理/排障细节链接到部署文档。

```markdown
# SHIP-PROFILE — <项目名> 发版档案

## 构建与静态检查
- 类型检查: <如 npx tsc --noEmit>
- Lint: <命令 或 "未配置">
- 构建: <如 npm run build>

## 测试矩阵（全绿定义，任一失败禁止发版）
| 层 | 命令 | 覆盖内容 |
|----|------|---------|
| L1 单测 | <命令> | <说明> |
| L2 ... | <命令>（按项目增删层数） | <说明> |

- UI 改动验证方式: <如 手写 playwright 断言脚本 / 人工冒烟清单>

## 测试环境
- 部署命令: <命令>
- 地址: <URL>
- 冒烟方式: <curl /api/health、登录走一遍 xxx>
- 部署文档: <docs/部署文档-xxx.md>

## 生产环境
- 发版前确认: <如何查生产当前 HEAD（git log -1 位置/方式）>
- 发版命令/流程: <命令 或 SOP 文档指针>
- 地址: <URL>
- 数据写操作备份方式: <如 mysqldump 命令模板>
- 部署文档: <docs/部署文档-xxx.md>

## GitHub
- 远程/分支: <origin/master 等>
- 排除目录: <artifacts/ 等不入库的产物>

## 文档同步清单
- <docs/PRD.md（功能条目+变更历史）/ CHANGELOG.md / docs/_INDEX.md ...>

## 项目专属铁律（ship 开局一并 Read）
- <如 docs/skills/ship-铁律-LIMS.md；没有则删本节>
```
