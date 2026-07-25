---
name: codex-exec
description: 需求分析/方案设计/最终验证由 Claude Code 做，实际代码改动委派给 Codex CLI（OpenAI）全自动执行后由 Claude Code 审查结果。当王老师说"用 Codex 执行"、"codex 跑一下"、"/codex-exec"时使用。适用范围不限于单个项目，任意本地代码仓库都可以用。
---

# codex-exec — Claude 规划验证 + Codex CLI 执行 协同模式

> 角色分工（王老师 2026-07-25 拍板）：**Claude Code 负责需求分析、方案设计、最终验证**；
> **Codex CLI 负责实际代码改动**，用 `--dangerously-bypass-approvals-and-sandbox` 全自动执行、
> 不中途打断确认；**整个任务一次性交给 Codex**（不拆成小步骤逐步喂指令）。

## 前提检查（首次使用或怀疑环境变化时）

```bash
which codex
codex --version
```

确认已安装、已登录（`codex exec "echo test" --skip-git-repo-check` 能正常应答）。

默认使用 Claude Code 当前工作目录为 Codex 的执行目录。如果目标是其他项目，用 `-C <dir>` 指定。

## 模型选择

Codex CLI 用 `-m` 参数指定模型，会直接调用该模型执行。常用选项：

```bash
codex exec -m o3 "..."          # OpenAI o3
codex exec -m gpt-5.1 "..."     # GPT-5.1
codex exec -m o4-mini "..."     # o4-mini（轻量快速）
```

不指定 `-m` 则用 Codex 配置文件中的默认模型。对于复杂代码改动建议用 `o3` 或 `gpt-5.1`，简单机械性任务可用 `o4-mini`。

王老师有特殊偏好可以在指令中指定模型，否则 Claude 根据任务复杂度自行选择。

## 执行流程

### 第 1 步：Claude 自己先做需求分析（不要跳过，不要外包给 Codex）

- 读相关代码，确认改动范围、受影响文件、现有约定/风格
- 遇到真正的设计决策（多种合理方案、影响面不确定）→ 停下来问王老师，不要替他拍板
- 想清楚"验证标准"是什么（怎么判断 Codex 做对了），因为第 3 步要靠这个来审查

### 第 2 步：写清楚任务指令，调用 Codex

因为是 `--dangerously-bypass-approvals-and-sandbox` 全自动模式，Codex 执行期间**没有人能叫停它**，所以任务指令必须把边界写死，不能含糊：

```bash
codex exec "<完整任务指令，见下方模板>" \
  -m <模型名> \
  -C "<目标项目绝对路径>" \
  --dangerously-bypass-approvals-and-sandbox \
  --skip-git-repo-check
```

| 参数 | 说明 |
|------|------|
| `-m <model>` | 指定模型，如 `o3`、`gpt-5.1`、`o4-mini` |
| `-C <dir>` | 工作目录（绝对路径），相当于 qodercli 的 `--cwd` |
| `--dangerously-bypass-approvals-and-sandbox` | 全自动执行，不打断确认，不沙箱限制 |
| `--skip-git-repo-check` | 允许在非 git 仓库执行（安全，Codex 只是不需要 git 上下文） |

可选附加参数：

| 参数 | 场景 |
|------|------|
| `--ephemeral` | 不需要保留会话记录时（省磁盘） |
| `-o <file>` | 把 Codex 最后一条消息写入文件，方便 Claude 后续解析 |
| `--json` | 输出 JSONL 流，适合自动化解析（但噪声大，通常不需要） |

**任务指令模板**（每次按需裁剪，但边界这几条不能省）：

```
<需求背景 + 具体要改什么，讲清楚，因为它不知道这次对话之前发生了什么>

严格边界（不可违反）：
- 只改动跟这个任务直接相关的文件，不做无关重构/顺手清理
- 不要执行 git commit / git push
- 不要跑任何部署/发版脚本（deploy-fast.sh、生产 SOP 里的命令等）
- 不要执行任何数据库写操作（UPDATE/DELETE/INSERT/迁移），除非任务本身明确要求
- 改完后跑一遍项目已有的类型检查/单元测试命令，把结果原样报告出来，不要自己判断"应该没问题"就不跑

完成后用简短的中文总结：改了哪些文件、每个文件改了什么、跑了什么验证命令、结果如何。
```

- `-C` 用目标项目的绝对路径，不要假设是当前项目——王老师用这套协同可能是任意仓库
- 如果王老师明确要求"分小步骤走"，改用多次 `codex exec` 调用来拆分任务，不要死守
  一次性全交这个默认值

### 第 3 步：Claude 独立验证（不能因为是 Codex 改的就降低审查标准）

Codex 报"完成"不等于真的对——跟审查子 Agent 产出一个标准：

1. `git status` / `git diff` 看它实际改了哪些文件，跟任务范围对不对得上
2. 独立跑一遍类型检查/相关测试（不要只信 Codex 自己报的"跑过了"）
3. 读几个关键改动点的代码，确认逻辑对、没有引入本可以避免的问题
4. 检查边界有没有被违反：有没有偷偷 commit、有没有碰不该碰的文件
5. （可选）如果改动量大且是 git 仓库，可用 `codex review` 做一次额外的自动化审查

### 第 4 步：向王老师报告

按这次会话一直在用的报告风格：改了什么、验证了什么（含具体命令和结果）、发现的问题（如果有）、还剩什么没做。**不要**因为代码是 Codex 写的就少一道审查——王老师要看到的是"这活干得对不对"，不是"谁干的"。

## 边界情况

- Codex 执行中途报错/卡住/产出明显不对 → 不要重复无脑重试，把情况告诉王老师，问是重新组织指令再试，还是 Claude 自己接手改
- 涉及生产部署、危险数据操作等本来就要跟王老师确认的动作 → 依然要确认，不因为走了协同模式就自动降级成"Codex 都能做"
- Codex 登录态过期 → 让王老师跑 `codex login` 重新认证
- sandbox 权限不足导致某些命令被拦截 → 确认任务确实需要，然后加 `-s danger-full-access` 或直接用 `--dangerously-bypass-approvals-and-sandbox`

## Codex CLI vs qodercli 关键差异速查

| 维度 | qodercli | Codex CLI |
|------|----------|-----------|
| 执行命令 | `qodercli -p "..." --cwd <dir>` | `codex exec "..." -C <dir>` |
| 全自动模式 | `--permission-mode bypass_permissions` | `--dangerously-bypass-approvals-and-sandbox` |
| 指定模型 | 配置文件预设 | `-m <model>` 命令行直接指定 |
| 沙箱控制 | 无 | `-s read-only/workspace-write/danger-full-access` |
| 非 git 仓库 | 默认支持 | 需 `--skip-git-repo-check` |
| 内置审查 | 无 | `codex review` |
| MCP 集成 | 无 | `codex mcp-server`（可注册到 Claude Code） |
| 输出捕获 | 标准输出 | `-o <file>` + `--json` 两种方式 |
| 提供方 | 国产 | OpenAI |
