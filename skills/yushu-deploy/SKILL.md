---
name: yushu-deploy
description: 宇树系列项目（Portal/EAM/Portal-API）的代码管理与部署 SOP。当用户提到"宇树"、"yushu"、"portal"、"EAM"、"3010"、"3011"、"8.130.182.148"、部署、上线、回滚、nginx 配置、pm2 后端，或要在这套架构里做任何变更时使用。
---

# 宇树系列部署 SOP

> 适用场景：王老师在 `/Users/wangpeng/Downloads/yushu/xitong/` 下维护的一体化平台 demo，部署到阿里云 `8.130.182.148`。

## 1. 项目地图（最重要，先记这个）

| URL | 端口 | 服务器目录 | 本地源码目录 | GitHub 仓库 | 分支 | 部署模式 |
|---|---|---|---|---|---|---|
| http://8.130.182.148:3010/ | 3010 | `/var/www/yushu-eam` | `iimake-eam-console-rebuild/` | `wangpeng1017/yushueam` | `dev_2026.3.1` | `build:mock`（纯前端 demo） |
| http://8.130.182.148:3011/ | 3011 | `/var/www/yushu-portal` | `iimake-made-portal/iimake-made-portal/` | `wangpeng1017/yushuportal` | `dev_2026.4` | `build:mock` |
| `/admin-api/infra/file/*` | 48080（内网） | `/opt/yushu-portal-api` | `yushu-portal-api/` | `wangpeng1017/yushu-portal-api`（private） | `main` | Node pm2 |
| 文件存储 | - | `/var/www/yushu-portal-files/` | - | - | - | nginx alias `/files/` |
| QMS HTML 子站 | 3011 子路径 `/qms/` | `/var/www/yushu-qms/` | `qms/` | - | - | 直接静态文件 |
| MES HTML | 3011 子路径 `/mes.html` | `/var/www/yushu-portal/mes.html` | `qms/`、`iimake-eam-console-rebuild/_mes-deliverable/` | - | - | 静态文件 |

**两个前端仓库的关系**：
- 都是 fork 自 yudao-vue-pro，结构高度相似（infra/file 这种页面两边都有）
- **不要把 EAM 改动当成 Portal 改动**——这是真踩过的坑。`8.130.182.148:3011` 是 Portal，源码在 `iimake-made-portal/iimake-made-portal/`，不是 `iimake-eam-console-rebuild/`

**两个 github remote**：
- `github`：王老师个人 https://github.com/wangpeng1017/...（**push 用这个**）
- `origin`：内网 GitLab `10.130.9.13:9501`（公网无法访问，不要 push）

## 2. 前端部署流程（Portal 和 EAM 通用）

### 2.1 已经有 deploy.sh，正常按它走

```bash
# Portal（3011）
cd /Users/wangpeng/Downloads/yushu/xitong/iimake-made-portal/iimake-made-portal
./deploy.sh

# EAM（3010）
cd /Users/wangpeng/Downloads/yushu/xitong/iimake-eam-console-rebuild
./deploy.sh
```

### 2.2 手动部署（deploy.sh 跑不通时）

```bash
# 在项目目录
pnpm build:mock                              # mock 模式构建
tar -czf /tmp/dist.tar.gz -C dist .
scp /tmp/dist.tar.gz root@8.130.182.148:/tmp/
ssh root@8.130.182.148 "
  REMOTE=/var/www/yushu-portal              # EAM 改成 yushu-eam
  cp -r \$REMOTE \${REMOTE}-backup-\$(date +%Y%m%d-%H%M%S)
  rm -rf \$REMOTE/assets \$REMOTE/index.html \$REMOTE/favicon.ico \$REMOTE/logo.gif
  tar -xzf /tmp/dist.tar.gz -C \$REMOTE
  rm /tmp/dist.tar.gz
  nginx -s reload
"
rm /tmp/dist.tar.gz
```

**注意**：3011 的 `/var/www/yushu-portal/` 里除了构建产物，还有手工放进去的 `mes.html`、`quality-trace.html`、`unitree-theme/`、`_build_unitree_mes.py` 等子文件。**不能 `rm -rf $REMOTE/*`，会误删！** 只 rm 前端构建产物名（`assets/`、`index.html`、`favicon.ico`、`logo.gif`）。

### 2.3 mock 模式 vs stage 模式

- 3010 和 3011 当前都是 **`build:mock`**（纯前端 demo，所有 `/admin-api/*` 由前端 mock-bridge 拦截返回假数据）
- **不要随便切到 `build:stage`**——stage 会要求真后端 `/admin-api`，但服务器上**没有 yudao 后端运行**（只有 mysql 容器 + 我们这个轻量 file 后端）

### 2.4 让某些接口走真后端（穿透 mock）

修改 `src/mock-bridge.ts`，在 `tryMatchMock` 开头加：
```typescript
if (url.includes('/some-prefix/')) return null  // 返回 null 让请求走真 axios
```
然后服务器配 nginx 把对应路径 proxy_pass 到真后端。**目前只有 `/infra/file/` 走了这种穿透**。

## 3. 后端服务（yushu-portal-api）

```bash
# 本地修改后：
cd /Users/wangpeng/Downloads/yushu/xitong/yushu-portal-api
git add -A && git commit -m "..."
git push origin main

# 服务器更新：
ssh root@8.130.182.148
cd /opt/yushu-portal-api
git pull
npm install --omit=dev  # 仅在依赖变化时跑
pm2 restart yushu-portal-api
pm2 logs yushu-portal-api --lines 20 --nostream  # 验证
```

**健康检查**：
```bash
ssh root@8.130.182.148 'node -e "http=require(\"http\");http.get(\"http://127.0.0.1:48080/admin-api/infra/file/health\",r=>{let d=\"\";r.on(\"data\",c=>d+=c);r.on(\"end\",()=>console.log(d))})"'
# 期望返回 {"code":200,"data":"OK","msg":"","success":true}
```

## 4. nginx 配置管理

**配置文件位置**：`/etc/nginx/conf.d/yushu-portal.conf`（3011）、`/etc/nginx/conf.d/yushu-eam.conf`（3010）

**改之前必须备份**：
```bash
ssh root@8.130.182.148 "cp /etc/nginx/conf.d/yushu-portal.conf /etc/nginx/conf.d/yushu-portal.conf.bak.\$(date +%Y%m%d-%H%M%S)"
```

**改完一定先 `nginx -t` 再 reload**：
```bash
nginx -t && nginx -s reload
```

**Portal nginx 配置样本**：见 `yushu-portal-api` 仓库的 `deploy/yushu-portal.conf.sample`。

## 5. 服务器环境清单（避免踩坑）

| 项 | 现状 |
|---|---|
| OS | Linux（CentOS/RHEL 系，**没有 curl/wget 默认安装**） |
| Node | v20.19.6（`/usr/bin/node`） |
| npm | 10.8.2，**没有 pnpm** |
| pm2 | 已装 |
| nginx | 已装，conf.d 自动 include |
| 数据库 | 仅 docker 容器：`mysql-lims:3308`（LIMS 用）、`mysql-npi:3307`（NPI 用），**没有 yudao 后端的 mysql** |
| 后端服务 | `lims-next` (pm2)、`npi-demo` (pm2)、`yushu-portal-api` (pm2)，**没有任何 Java 进程** |
| 测试 HTTP | 用 `node -e 'http.get(...)'`，**不要用 curl/wget**（机器上没有） |

## 6. 备份与回滚

### 前端回滚
```bash
ssh root@8.130.182.148 "ls -d /var/www/yushu-portal-backup-*"  # 看可用备份
ssh root@8.130.182.148 "
  rm -rf /var/www/yushu-portal/assets /var/www/yushu-portal/index.html
  cp -r /var/www/yushu-portal-backup-YYYYMMDD-HHMMSS/* /var/www/yushu-portal/
  nginx -s reload
"
```

### nginx 回滚
```bash
ssh root@8.130.182.148 "
  ls /etc/nginx/conf.d/yushu-portal.conf.bak.*
  cp /etc/nginx/conf.d/yushu-portal.conf.bak.YYYYMMDD-HHMMSS /etc/nginx/conf.d/yushu-portal.conf
  nginx -t && nginx -s reload
"
```

### 后端回滚
```bash
ssh root@8.130.182.148 "cd /opt/yushu-portal-api && git log --oneline -10"
ssh root@8.130.182.148 "cd /opt/yushu-portal-api && git checkout <commit-sha> && pm2 restart yushu-portal-api"
```

### 文件存储备份
```bash
ssh root@8.130.182.148 "tar -czf /tmp/yushu-portal-files-\$(date +%Y%m%d).tar.gz -C /var/www/yushu-portal-files ."
scp root@8.130.182.148:/tmp/yushu-portal-files-*.tar.gz ~/Downloads/
```

## 7. Git 提交规范

参考 Portal 仓库现有 commit 风格：

```
feat(scope): 描述
fix(scope): 描述
refactor(scope): 描述
```

**scope 约定**：`portal`、`eam`、`api`、`mes`、`qms`、`trace`

**push 目标**：永远 `git push github <branch>`，**不要 push 到 origin**（内网 GitLab，公网访问不了）。

## 8. 常见踩坑（真发生过的）

1. **搞错项目**：3011 看到的页面在 `iimake-made-portal/`，不是 `iimake-eam-console-rebuild/`。同步改两边之前先确认目标 URL 是哪个端口。
2. **mock 模式没有真后端**：服务器上没 Java、没 yudao，stage/prod 模式无法工作；要让某接口"真"，必须 mock-bridge 放行 + 单独搭后端 + nginx 反代。
3. **服务器没 curl/wget**：测 HTTP 用 `node -e 'http.get(...)'`。
4. **pnpm 在服务器上没有**：服务器用 npm；本地用 pnpm。
5. **vue-office/docx 的 postinstall 被 pnpm 拦截**：必须在 `package.json` 加 `pnpm.onlyBuiltDependencies: ["@vue-office/docx"]`，或本地手动跑 `node node_modules/@vue-office/docx/lib/script/postinstall.js`。
6. **`rm -rf /var/www/yushu-portal/*` 是危险动作**：里面有手工放的 `mes.html` 等文件。只删构建产物（assets / index.html / favicon.ico / logo.gif）。
7. **nginx `client_max_body_size` 默认 1MB**：要传大文件必须显式设大（当前是 `0` 不限）。

## 9. 关键备忘

- 服务器 SSH：`ssh root@8.130.182.148`（已配 .claude/settings.json 永久放行）
- GitHub 账号：`wangpeng1017`（gh CLI 已登录，有 `repo` 权限）
- nginx 配置目录：`/etc/nginx/conf.d/`
- pm2 进程列表：`ssh root@8.130.182.148 "pm2 list"`
- 文件存储位置：`/var/www/yushu-portal-files/`（用户上传的 docx/图片等）

## 10. 不要做的事

- ❌ 不要在 `8.130.182.148` 上启动 yudao 后端（机器资源紧张，且 mock demo 不需要）
- ❌ 不要 push 到 `origin`（内网 GitLab，公网访问不了，会卡住）
- ❌ 不要把 `yushu-portal-api` 设成 public 仓库（暴露服务器 IP 和架构）
- ❌ 不要在不备份的情况下改 nginx 配置或 `rm -rf` 部署目录
- ❌ 不要把 `build:mock` 改成 `build:stage`/`build:prod` 然后部署上去（会要求不存在的真后端）
