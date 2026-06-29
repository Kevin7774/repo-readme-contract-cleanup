---
name: repo-readme-contract-cleanup
description: 通用仓库 readme、api 文档、部署文档与工程契约清理流程。use when the user asks to update or rewrite a repository readme, remove stale docs/code/deploy configs, audit current features/apis/env vars, clean ai-generated redundancy, de-slop hardcoded/mock/dead content, align development and production deployment docs, or create an engineering governance checklist before documenting a codebase.
---

# Repo README Contract Cleanup

## Goal

Execute a repository documentation-prep workflow before writing or updating README files. Treat README as an external engineering contract: only document what the current code, tests, configuration, and deployment path prove.

Use this skill to turn a messy repository into a documented, deployable, and maintainable state without doing risky large rewrites.

## Core Rule

Do **not** start by rewriting README. First prove the current repository state.

Use this order:

```text
current code passes checks
  -> readme-pre engineering governance
  -> feature/api/env/deploy contract maps
  -> remove confirmed stale content
  -> run validation and smoke checks
  -> update readme/docs
  -> defer architecture evolution to a separate phase
```

## Decision Boundary

### Allowed in the README-pre cleanup phase

- Delete confirmed stale README/docs/deploy instructions.
- Delete confirmed obsolete nginx, compose, ci, script, env example entries.
- Delete production-path fake success, demo fallback, hardcoded old host/port/domain values.
- Update `.env.example`, production env examples, compose, nginx, ci, and deploy docs to the current topology.
- Add or update smoke tests and contract tests that lock the current API/deploy contract.
- Generate feature, API, environment-variable, and deployment maps from real code.

### Not allowed in the README-pre cleanup phase

- Do not split large files only for aesthetics.
- Do not rewrite orchestrators, providers, search/ranking pipelines, or core business workflows.
- Do not rename API paths unless the old path is fully proven unused and broken.
- Do not change database schema unless a test or code path proves a defect.
- Do not rewrite frontend pages.
- Do not delete uncertain scripts, tests, or providers; mark them as “疑似废弃，需要人工确认”.

## Workflow

### 1. Establish Worktree Baseline

Start every repository task by showing the current worktree state:

```bash
git status --short
git diff --stat
git diff --name-only
```

Classify files into:

| Class | Meaning |
|---|---|
| current user/request scope | files expected to change now |
| pre-existing changes | files already modified before this task |
| generated artifacts | cache, build outputs, pyc, dist, coverage |
| risky shared contract files | README, docs, compose, nginx, ci, env examples |

If the worktree is dirty, avoid broad destructive cleanup until scope is clear.

### 2. Build the Four Contract Maps

Create these four maps from real code and config before editing README.

#### Feature Map

| 模块 | 用户入口 | 前端入口 | 后端 API | 数据模型 | provider/外部服务 | 状态 | 证据文件 |
|---|---|---|---|---|---|---|---|

#### API Map

Extract from framework route registration, router files, OpenAPI, frontend API clients, and tests.

| Method | Path | 用途 | 前端调用位置 | 后端处理位置 | 是否鉴权 | 是否保留 | 证据 |
|---|---|---|---|---|---|---|---|

#### Environment Map

Search `.env*`, config files, deployment templates, and code reads such as `os.getenv`, `os.environ`, settings classes, and service config `_env` fields.

| 变量名 | 来源文件 | 代码读取位置 | 用途 | 开发是否需要 | 生产是否需要 | 是否保留 |
|---|---|---|---|---|---|---|

#### Deployment Map

Separate development and production.

| 环境 | 服务 | 启动方式 | 端口 | 健康检查 | 依赖 | 配置文件 |
|---|---|---|---|---|---|---|

For the user's AI recruiting project, prefer the latest split topology when the repository evidence supports it:

```text
宿主机 nginx
  /       -> 127.0.0.1:3000
  /api/   -> 127.0.0.1:8000/api/
  /health -> 127.0.0.1:8000/health
```

For other repositories, infer the topology from code and deploy files; do not copy this topology blindly.

### 3. Scan for Stale and Redundant Content

Search for stale content categories:

| Category | Examples |
|---|---|
| old ports/topology | old app ports, obsolete service names, old nginx upstreams |
| old api | docs mention nonexistent endpoints; frontend calls removed endpoints; backend has unused routes |
| old env vars | env example variables no longer read; code reads missing env vars |
| hardcoded values | old domains, ips, local absolute paths, fake tokens, old registry paths |
| ai slop | fake success, placeholder output, stale comments, duplicated docs, obsolete examples |
| mock misuse | production code containing mock/fake/demo behavior |
| dead deploy files | unused compose, nginx, ci, release scripts |
| generated junk | `__pycache__`, `.pyc`, build outputs committed by mistake |

When useful, run the bundled scanner:

```bash
python <skill_dir>/scripts/repo_contract_scan.py /path/to/repo --out /tmp/repo-contract-scan.md
```

Treat scanner output as hints, not truth. Confirm with references and tests before deleting.

### 4. Apply the Deletion Standard

Delete only when at least one strong evidence chain exists:

```text
no route entry + no frontend call + no test + no deploy reference + no config reference
```

or:

```text
explicitly conflicts with the current validated deployment contract
```

Use this classification:

| Status | Action |
|---|---|
| confirmed current | document and protect |
| confirmed stale | delete or update |
| test fixture | keep unless it leaks into production behavior |
| uncertain | do not delete; list under “疑似废弃，需要人工确认” |

### 5. Validate Before README Rewrite

Run the repository's actual checks. Prefer these when applicable:

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend build
pnpm --dir frontend test
pnpm --dir frontend lint
python -m compileall app scripts tests
pytest -q
curl -fsS http://127.0.0.1:8000/health
docker compose config --no-interpolate
```

Adapt commands to the repository. If a command cannot run because a dependency is missing, say so explicitly and provide the exact command for the user's machine.

### 6. Rewrite README Only After Contracts Are Stable

README must include only current, verified facts:

1. project purpose and non-goals
2. core modules table
3. architecture diagram/text topology
4. current API table and examples
5. directory structure
6. local development setup
7. production deployment setup
8. environment variables
9. tests and validation
10. troubleshooting
11. removed/deprecated content summary if useful

Do not preserve “historically supported” workflows in README. Put migration history in changelog/runbook if needed.

## Required Report Format

For README-pre cleanup, finish with:

```markdown
## README 前置工程治理报告

### 1. 当前仓库是否适合开始重写 README
结论：可以开始 / 还不能开始
原因：

### 2. 已确认保留的功能模块
| 模块 | 前端入口 | 后端 API | 数据模型 | 状态 |
|---|---|---|---|---|

### 3. 已确认保留的 API
| Method | Path | 用途 | 前端调用 | 后端文件 |
|---|---|---|---|---|

### 4. 已确认保留的部署方式

### 5. 已删除的废弃内容
| 内容 | 类型 | 文件 | 删除原因 | 证据 |
|---|---|---|---|---|

### 6. 已修复的不一致内容
| 问题 | 文件 | 修复方式 | 验证方式 |
|---|---|---|---|

### 7. 疑似废弃但未删除
| 内容 | 文件 | 为什么不确定 | 建议谁确认 |
|---|---|---|---|

### 8. 当前不建议在 README 前做的大重构
| 重构项 | 为什么暂缓 | 建议放到什么时候 |
|---|---|---|

### 9. 验收结果
| 验收项 | 命令 | 结果 |
|---|---|---|

### 10. 下一步 README 重写建议
```

For final README rewrite, finish with:

```markdown
## README 更新报告

### 1. README 更新了什么
### 2. 当前真实功能模块
### 3. 当前真实 API
### 4. 当前开发环境启动方式
### 5. 当前生产部署方式
### 6. 删除的陈旧内容
### 7. 验收结果
### 8. 剩余风险
```

## Prompt Template for Code Agents

When the user wants a prompt for Codex, Claude Code, Cursor, or another code agent, provide a concise executable prompt that preserves these rules:

- first audit, then edit
- README is contract, not marketing
- delete only confirmed stale content
