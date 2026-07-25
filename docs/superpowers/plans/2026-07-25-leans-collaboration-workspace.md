# LEANS Collaboration Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a shared Git-based project workspace for ChatGPT and Claude with a LEANS handoff board, templates, Obsidian-compatible knowledge notes, workflow scripts, and documentation.

**Architecture:** The workspace is plain Markdown plus a small PowerShell helper so it works locally, in Obsidian, and with assistant file tools. The board remains human-readable while scripts automate the most common handoff actions.

**Tech Stack:** Git, Markdown, PowerShell 5+/7, UTF-8 files.

---

### Task 1: Workspace Skeleton

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `LEANS-Uebergabe.md`
- Create: `LEANS-Uebergabe-ANLEITUNG.md`
- Create: `.templates/uebergabe-chatgpt-an-claude.md`
- Create: `.templates/uebergabe-claude-an-chatgpt.md`
- Create: `knowledge/README.md`
- Create: `knowledge/00-index.md`
- Create: `knowledge/projects/.gitkeep`
- Create: `knowledge/decisions/.gitkeep`
- Create: `knowledge/prompts/.gitkeep`

- [x] Create the Markdown workspace files and folder structure.
- [x] Ensure the board has the exact ChatGPT and Claude sections.
- [x] Keep all user-facing notes Obsidian-compatible.

### Task 2: LEANS Board Helper

**Files:**
- Create: `tests/leans-board.tests.ps1`
- Create: `scripts/leans-board.ps1`

- [x] Write tests that describe checking ChatGPT inbox entries, adding a Claude handoff, and marking a ChatGPT entry as done.
- [x] Run the tests and verify they fail because the helper script does not exist yet.
- [x] Implement the helper script.
- [x] Run the tests and verify they pass.

### Task 3: Git Initialization

**Files:**
- Modify: repository metadata through `git init`

- [ ] Initialize Git in the project folder.
- [x] Review status so the user can see what was created.

Note: Git initialization is blocked in the current Codex sandbox because `.git` metadata writes are denied. Run `git init` locally from the project folder to complete this step.
