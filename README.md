# Repo README Contract Cleanup Skill

A reusable ChatGPT Skill for repository contract cleanup, README governance, stale API detection, deployment documentation alignment, and production-readiness validation.

This Skill is designed for software projects where the README, API documentation, environment variables, deployment scripts, and actual code may have drifted apart over time.

It enforces one core rule:

> The README should describe the current runnable system, not historical plans, old ports, deleted APIs, fake flows, or abandoned deployment paths.

---

## What This Skill Does

This Skill guides ChatGPT through a full repository documentation and contract cleanup workflow.

It focuses on:

- Auditing the real codebase before editing the README.
- Detecting stale APIs, old ports, obsolete deployment paths, unused environment variables, fake data, mock leakage, hardcoded values, and dead code.
- Building four source-of-truth maps:
  - Current feature modules.
  - Current API contract.
  - Current environment variables.
  - Current deployment topology.
- Cleaning only confirmed-deprecated content.
- Separating uncertain content into a `suspected-deprecated` list instead of deleting it blindly.
- Updating README and related docs only after the codebase contract is verified.
- Producing a final engineering report with validation results.

---

## When To Use This Skill

Use this Skill when you want to:

- Rewrite a README based on the real current code.
- Clean up old project documentation.
- Remove stale deployment instructions.
- Detect old API references.
- Validate frontend/backend API consistency.
- Align `.env.example`, production env templates, Docker Compose, Nginx, and CI/CD files.
- Prepare a repository for production deployment.
- Prepare a codebase before handing it to another engineer or AI coding agent.
- Avoid README drift after multiple rounds of AI-generated code changes.

Typical prompt:

```text
Use the repo-readme-contract-cleanup skill. First do README pre-cleanup governance. Do not rewrite README yet. Audit current code, APIs, env vars, deployment files, stale ports, fake data, old scripts, and output whether the repo is ready for README rewrite.
```

---

## Workflow

The Skill follows this sequence:

```text
Repository audit
  ↓
Stale code / stale docs / stale deployment detection
  ↓
Feature, API, env, deployment contract mapping
  ↓
Confirmed-deprecated cleanup
  ↓
Validation: build / test / health / compose
  ↓
README and documentation rewrite
  ↓
Final cleanup report
```

---

## What It Checks

### 1. Feature Modules

The Skill identifies current real modules from:

- Frontend routes.
- Frontend pages.
- API clients.
- Backend routers.
- Backend services.
- Data models.
- Providers.
- Deployment entrypoints.

It outputs a table like:

| Module | Frontend Entry | Backend API | Data Model | Provider | Status |
|---|---|---|---|---|---|

---

### 2. API Contract

The Skill checks:

- Backend route definitions.
- Frontend API client calls.
- API docs.
- README examples.
- Test coverage.
- Curl examples.
- Deprecated or duplicate routes.

It outputs:

| Method | Path | Purpose | Frontend Caller | Backend Handler | Status |
|---|---|---|---|---|---|

---

### 3. Environment Variables

The Skill compares:

- `.env.example`
- production env templates
- config files
- code-level environment reads
- Docker Compose references
- CI/CD variables
- provider configs

It outputs:

| Variable | Source File | Code Usage | Purpose | Dev Required | Prod Required | Keep/Delete |
|---|---|---|---|---|---|---|

---

### 4. Deployment Topology

The Skill verifies:

- Dockerfiles.
- Docker Compose files.
- Nginx configs.
- host-level reverse proxy rules.
- ports.
- health checks.
- CI/CD deploy scripts.
- production env examples.

It is especially useful when a project has migrated from one topology to another, such as:

```text
Old:
  app container -> 8020
  nginx container -> app:8020

New:
  host Nginx
    /       -> frontend:3000
    /api/   -> backend:8000/api/
    /health -> backend:8000/health
```

---

## Cleanup Rules

The Skill uses strict deletion rules.

It may delete:

- Confirmed obsolete deployment files.
- Confirmed old Nginx configs.
- Confirmed old ports and service names.
- Confirmed unused environment variables.
- Confirmed stale README sections.
- Confirmed fake success paths in production code.
- Confirmed dead scripts with no entrypoint, test, docs, or deployment reference.

It must not delete:

- Test fixtures just because they contain `mock`, `fake`, or `demo`.
- Unclear scripts without human confirmation.
- Core business logic during README cleanup.
- Database models unless explicitly required.
- API paths unless they are proven unused or obsolete.
- Large modules just for style reasons.

Uncertain items are placed into:

```text
Suspected deprecated, needs human confirmation
```

---

## Recommended Repository Structure

This repository contains:

```text
repo-readme-contract-cleanup/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── prompt-template.md
│   └── readme-template.md
├── scripts/
│   └── repo_contract_scan.py
└── dist/
    └── skill.zip
```

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Main skill instructions |
| `agents/openai.yaml` | ChatGPT Skill metadata |
| `references/prompt-template.md` | Long-form prompt for Codex, Claude Code, Cursor, or other coding agents |
| `references/readme-template.md` | README rewrite template |
| `scripts/repo_contract_scan.py` | Helper scanner for ports, env vars, API-like paths, mock/fake/demo markers, and hardcoded values |
| `dist/skill.zip` | Uploadable ChatGPT Skill package |

---

## How To Use In ChatGPT

Upload `dist/skill.zip` to your ChatGPT Skills library.

Then ask:

```text
Use repo-readme-contract-cleanup to audit this repository before rewriting README. Do not modify README first.
```

Or:

```text
Use repo-readme-contract-cleanup to find stale APIs, stale deployment files, old environment variables, fake data, hardcoded values, and README drift.
```

---

## How To Use With Coding Agents

You can also copy `references/prompt-template.md` into:

- Codex
- Claude Code
- Cursor
- Windsurf
- GitHub Copilot Workspace
- other AI coding agents

Recommended instruction:

```text
Do not rewrite README first. First perform README pre-cleanup governance, build current feature/API/env/deployment maps, delete only confirmed deprecated content, validate build/test/health/compose, then report whether README rewrite can begin.
```

---

## Validation Checklist

A repository is ready for README rewrite only when:

- Current feature modules are known.
- Current API routes are known.
- Frontend API calls match backend routes.
- Current environment variables are known.
- `.env.example` has no obsolete variables.
- Production env template matches current deployment.
- Docker Compose matches current topology.
- Nginx config matches current topology.
- Health check works.
- Build and tests pass or failures are documented.
- Confirmed-deprecated files are removed.
- Uncertain files are listed separately instead of deleted blindly.

---

## Example Final Report

The Skill asks ChatGPT to produce a report like:

```markdown
# README Pre-Cleanup Governance Report

## 1. Can README rewrite begin?

Conclusion: yes / no

## 2. Confirmed current feature modules

| Module | Frontend Entry | Backend API | Data Model | Status |
|---|---|---|---|---|

## 3. Confirmed current APIs

| Method | Path | Purpose | Frontend Caller | Backend Handler |
|---|---|---|---|---|

## 4. Confirmed deployment topology

## 5. Deleted deprecated content

| Content | Type | File | Reason | Evidence |
|---|---|---|---|---|

## 6. Fixed inconsistencies

| Issue | File | Fix | Validation |
|---|---|---|---|

## 7. Suspected deprecated but not deleted

| Content | File | Why uncertain | Needs confirmation |
|---|---|---|---|

## 8. Validation results

| Check | Command | Result |
|---|---|---|
```

---

## Design Principle

This Skill is intentionally conservative.

It does not treat cleanup as a refactor. It treats cleanup as contract alignment.

The goal is not to make the code perfect.

The goal is to make the repository truthful, runnable, explainable, and safe to document.
