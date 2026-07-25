# LEANS Live Collaboration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a folder-native live coordination layer so ChatGPT/Codex and Claude can share current activity, review requests, and file-change events inside one permanent Windows workspace.

**Architecture:** A single PowerShell command surface stores untracked runtime data in `.leans-live/`. `state.json` holds the latest declared activity, `events.jsonl` records append-only events, and `reviews/*.json` holds one review request per file. Durable task handoffs remain in `LEANS-Uebergabe.md`; GitHub remains the version history.

**Tech Stack:** Windows PowerShell 5.1 compatible scripts, built-in .NET JSON and file APIs, Git, and the existing standalone PowerShell test style.

---

## Planned File Structure

- Modify: `.gitignore` - excludes local runtime state.
- Create: `scripts/leans-live.ps1` - live status, announcements, review lifecycle, and watcher command.
- Create: `scripts/install-leans-live.ps1` - creates or updates the stable `C:\Users\semir\Documents\LEANS-Live` working copy.
- Create: `tests/leans-live.tests.ps1` - standalone tests for every supported command and safety boundary.
- Create: `docs/LEANS-Live.md` - practical operating guide for both desktop apps.
- Modify: `README.md` - links the live workflow from the project entry point.
- Modify: `AGENTS.md` - requires the live status check and work announcement before shared edits.

### Runtime Data Contract

`state.json` must be written as UTF-8 JSON with this shape:

```json
{
  "version": 1,
  "updatedAt": "2026-07-25T15:30:00.0000000+02:00",
  "assistants": {
    "chatgpt": {
      "activity": "Implementing status command",
      "paths": ["scripts/leans-live.ps1"],
      "updatedAt": "2026-07-25T15:30:00.0000000+02:00"
    }
  }
}
```

Each `events.jsonl` line must have `id`, `timestamp`, `type`, `from`, `to`, `message`, `paths`, and `reviewId`. Review files must have `id`, `from`, `to`, `status`, `question`, `paths`, `createdAt`, and `updatedAt`.

### Task 1: Add Runtime Ignore Rules And Failing Test Scaffold

**Files:**
- Modify: `.gitignore`
- Create: `tests/leans-live.tests.ps1`
- Test: `tests/leans-live.tests.ps1`

- [ ] **Step 1: Add the live runtime directory to Git ignores**

Append this exact line to `.gitignore`:

```gitignore
.leans-live/
```

- [ ] **Step 2: Write the failing announce/status test**

Create `tests/leans-live.tests.ps1` using a temporary test root and this initial assertion helper:

```powershell
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $Root "scripts/leans-live.ps1"
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("leans-live-test-" + [guid]::NewGuid().ToString("N"))

function Assert-Contains {
    param([string]$Haystack, [string]$Needle, [string]$Message)
    if (-not $Haystack.Contains($Needle)) { throw $Message }
}

try {
    New-Item -ItemType Directory -Path $TempRoot | Out-Null
    & $Script announce -WorkspacePath $TempRoot -Assistant chatgpt -Activity "Writing tests" -Paths "tests/leans-live.tests.ps1" | Out-Null
    $status = & $Script status -WorkspacePath $TempRoot | Out-String
    Assert-Contains $status "chatgpt" "status should show the announcing assistant."
    Assert-Contains $status "Writing tests" "status should show the current activity."
}
finally {
    if (Test-Path -LiteralPath $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force }
}
```

- [ ] **Step 3: Run the test to verify it fails**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\leans-live.tests.ps1
```

Expected: failure because `scripts/leans-live.ps1` does not exist.

- [ ] **Step 4: Commit the ignore rule and failing test**

```powershell
git add .gitignore tests/leans-live.tests.ps1
git commit -m "test: define live coordination status behavior"
```

### Task 2: Implement State, Events, Announcements, And Status

**Files:**
- Create: `scripts/leans-live.ps1`
- Modify: `tests/leans-live.tests.ps1`
- Test: `tests/leans-live.tests.ps1`

- [ ] **Step 1: Define the command surface and runtime paths**

Start `scripts/leans-live.ps1` with these parameters and validation rules:

```powershell
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("start", "status", "announce", "request-review", "acknowledge-review", "complete-review")]
    [string]$Command,

    [string]$WorkspacePath = ".",
    [ValidateSet("chatgpt", "claude")]
    [string]$Assistant,
    [ValidateSet("chatgpt", "claude")]
    [string]$Target,
    [string]$Activity,
    [string[]]$Paths = @(),
    [string]$Question,
    [string]$ReviewId,
    [string]$Outcome,
    [int]$DurationSeconds = 0,
    [switch]$Notify
)

$ErrorActionPreference = "Stop"
$RuntimePath = Join-Path (Resolve-Path -LiteralPath $WorkspacePath) ".leans-live"
$StatePath = Join-Path $RuntimePath "state.json"
$EventsPath = Join-Path $RuntimePath "events.jsonl"
$ReviewsPath = Join-Path $RuntimePath "reviews"
$WatcherLockPath = Join-Path $RuntimePath "watcher.lock"
```

- [ ] **Step 2: Add atomic JSON and event helpers**

Implement `Ensure-Runtime`, `Write-JsonAtomically`, `Read-State`, `Write-State`, and `Add-Event`. `Write-JsonAtomically` must write a sibling temporary file named with a GUID, then move it over the destination with `Move-Item -Force`. `Add-Event` must serialize a single ordered object with `ConvertTo-Json -Compress` and append exactly one UTF-8 line.

- [ ] **Step 3: Implement `announce`**

Require non-empty `Assistant` and `Activity`. Replace only the state entry whose name equals the supplied assistant, preserve the other assistant's state, then append an `announce` event. Emit:

```text
Live activity recorded for chatgpt.
```

- [ ] **Step 4: Implement `status`**

Print exactly three sections: `Current activity`, `Open reviews`, and `Recent events`. Missing state, review, or event files must produce an empty section instead of an error. Include the most recent 10 events from `events.jsonl`.

- [ ] **Step 5: Extend the test for persisted runtime data**

After the existing status assertions, add:

```powershell
$state = Get-Content -LiteralPath (Join-Path $TempRoot ".leans-live\state.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($state.assistants.chatgpt.paths[0] -ne "tests/leans-live.tests.ps1") {
    throw "announce should persist the affected path."
}

$events = Get-Content -LiteralPath (Join-Path $TempRoot ".leans-live\events.jsonl") -Encoding UTF8
if ($events.Count -ne 1) { throw "announce should append exactly one event." }
```

- [ ] **Step 6: Run the test to verify it passes**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\leans-live.tests.ps1
```

Expected: the command exits with code 0 and raises no assertion.

- [ ] **Step 7: Commit the live state core**

```powershell
git add scripts/leans-live.ps1 tests/leans-live.tests.ps1
git commit -m "feat: add live activity status"
```

### Task 3: Implement The Safe Review Lifecycle

**Files:**
- Modify: `scripts/leans-live.ps1`
- Modify: `tests/leans-live.tests.ps1`
- Test: `tests/leans-live.tests.ps1`

- [ ] **Step 1: Add a failing review lifecycle test**

Add this sequence inside the test `try` block:

```powershell
$reviewOutput = & $Script request-review -WorkspacePath $TempRoot -Assistant chatgpt -Target claude -Question "Please check the live script." -Paths "scripts/leans-live.ps1" | Out-String
if ($reviewOutput -notmatch "Review requested: ([a-f0-9-]+)") { throw "request-review should return a review id." }
$reviewId = $Matches[1]

& $Script acknowledge-review -WorkspacePath $TempRoot -Assistant claude -ReviewId $reviewId | Out-Null
& $Script complete-review -WorkspacePath $TempRoot -Assistant claude -ReviewId $reviewId -Outcome "Approved" | Out-Null

$completed = Get-Content -LiteralPath (Join-Path $TempRoot ".leans-live\reviews\$reviewId.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($completed.status -ne "completed") { throw "complete-review should preserve a completed review record." }
if ($completed.outcome -ne "Approved") { throw "complete-review should save the outcome." }
```

- [ ] **Step 2: Run the test to verify it fails**

Run the same test command. Expected: failure because review commands are not implemented.

- [ ] **Step 3: Implement `request-review`**

Require `Assistant`, `Target`, `Question`, and at least one path. Reject `Assistant -eq Target`. Generate a UUID, write the review JSON as that UUID followed by `.json`, set `status` to `open`, then append a `review-request` event. Emit the generated UUID with this format:

```text
Review requested: $reviewId
```

- [ ] **Step 4: Implement acknowledgement and completion authorization**

`acknowledge-review` must require that `Assistant` equals the file's `to` value and change only `status` to `acknowledged`. `complete-review` must enforce the same ownership, require `Outcome`, set `status` to `completed`, preserve the review file, and append a completion event. A requester must receive this error if it attempts either operation:

```text
Only the addressed assistant can update this review.
```

- [ ] **Step 5: Add the cross-assistant rejection test**

Before Claude acknowledges the review, add:

```powershell
try {
    & $Script acknowledge-review -WorkspacePath $TempRoot -Assistant chatgpt -ReviewId $reviewId | Out-Null
    throw "The requester must not be allowed to acknowledge its own review."
}
catch {
    Assert-Contains $_.Exception.Message "Only the addressed assistant" "review ownership should be enforced."
}
```

- [ ] **Step 6: Run the full test and commit**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\leans-live.tests.ps1
```

Then commit:

```powershell
git add scripts/leans-live.ps1 tests/leans-live.tests.ps1
git commit -m "feat: add live review requests"
```

### Task 4: Add File Watching, Locking, And Optional Notification

**Files:**
- Modify: `scripts/leans-live.ps1`
- Modify: `tests/leans-live.tests.ps1`
- Test: `tests/leans-live.tests.ps1`

- [ ] **Step 1: Add a failing watcher-lock test**

Create `.leans-live\watcher.lock` in the temporary workspace, then assert a second watcher cannot start:

```powershell
$lockPath = Join-Path $TempRoot ".leans-live\watcher.lock"
@{ pid = 99999; startedAt = "2026-07-25T15:00:00+02:00" } | ConvertTo-Json | Set-Content -LiteralPath $lockPath -Encoding UTF8

try {
    & $Script start -WorkspacePath $TempRoot -DurationSeconds 1 | Out-Null
    throw "start should reject an existing watcher lock."
}
catch {
    Assert-Contains $_.Exception.Message "A LEANS live watcher is already running" "watcher lock should prevent two watchers."
}
```

- [ ] **Step 2: Implement watcher locking**

Implement `Acquire-WatcherLock` and `Release-WatcherLock`. A lock must contain the current PID and timestamp. If the existing lock PID is running, `start` must throw `A LEANS live watcher is already running.` If the PID is absent, replace the stale lock.

- [ ] **Step 3: Implement `start` with a bounded test mode**

Use `System.IO.FileSystemWatcher` for the workspace root, include subdirectories, and filter `*.*`. Ignore `.git`, `.leans-live`, and `.obsidian`. For every change, create a `file-change` event with the relative path. `DurationSeconds = 0` means run until `Ctrl+C`; a positive duration exits after that many seconds and always releases the lock in `finally`.

- [ ] **Step 4: Add opt-in Windows notification fallback**

When `-Notify` is supplied for a review request or a watcher event, invoke:

```powershell
& msg.exe $env:USERNAME /TIME:30 "LEANS Live: $Message" 2>$null
```

Do not fail the main command if `msg.exe` is unavailable. The event stream remains the source of truth.

- [ ] **Step 5: Complete test output and run the suite**

At the end of `tests/leans-live.tests.ps1`, after all assertions, add:

```powershell
Write-Host "PASS leans-live workflow"
```

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\leans-live.tests.ps1
```

Expected: `PASS leans-live workflow`.

- [ ] **Step 6: Commit watcher behavior**

```powershell
git add scripts/leans-live.ps1 tests/leans-live.tests.ps1
git commit -m "feat: watch shared workspace changes"
```

### Task 5: Create The Stable Workspace Installer And Operating Guide

**Files:**
- Create: `scripts/install-leans-live.ps1`
- Create: `docs/LEANS-Live.md`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Test: manual two-session verification

- [ ] **Step 1: Implement the stable workspace installer**

Create `scripts/install-leans-live.ps1` with parameters:

```powershell
param(
    [string]$RepositoryUrl = "https://github.com/leanstechgmbh-create/leans-collaboration.git",
    [string]$Destination = "C:\Users\semir\Documents\LEANS-Live"
)
```

If `$Destination\.git` exists, run `git -C $Destination pull --ff-only` and output `Updated LEANS-Live.`. If the destination exists without `.git`, throw `Destination exists but is not a Git repository: $Destination`. Otherwise clone the repository and output `Created LEANS-Live.`.

- [ ] **Step 2: Document the operating workflow**

Create `docs/LEANS-Live.md` with these exact daily commands:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 status
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 announce -Assistant chatgpt -Activity "Reviewing the workflow guide" -Paths "docs/LEANS-Live.md"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 request-review -Assistant chatgpt -Target claude -Question "Confirm the daily workflow is clear." -Paths "docs/LEANS-Live.md"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 start -Notify
```

Explain that both apps must open `C:\Users\semir\Documents\LEANS-Live`, that the board remains durable, and that an inactive chat cannot autonomously respond to an event.

- [ ] **Step 3: Update entry-point instructions**

Add a `## Live Zusammenarbeit` section to `README.md` linking `docs/LEANS-Live.md`. Add two AGENTS rules after the board check: run `leans-live.ps1 status` and announce the file area before editing shared files.

- [ ] **Step 4: Manually verify with two PowerShell sessions**

In session A:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 announce -Assistant chatgpt -Activity "Manual verification" -Paths "README.md"
$reviewOutput = powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 request-review -Assistant chatgpt -Target claude -Question "Confirm visibility." -Paths "README.md"
$reviewId = ([regex]::Match($reviewOutput, "Review requested: ([a-f0-9-]+)")).Groups[1].Value
Set-Content -LiteralPath .\.leans-live\manual-review-id.txt -Value $reviewId -Encoding UTF8
```

In session B:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 status
$reviewId = (Get-Content -LiteralPath .\.leans-live\manual-review-id.txt -Raw -Encoding UTF8).Trim()
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 acknowledge-review -Assistant claude -ReviewId $reviewId
```

Expected: session B sees ChatGPT activity and the open review, then the review changes to `acknowledged`.

- [ ] **Step 5: Run the automated suite and verify Git ignores runtime data**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\leans-live.tests.ps1
New-Item -ItemType Directory -Force .\.leans-live | Out-Null
Set-Content -LiteralPath .\.leans-live\probe.txt -Value "ignored" -Encoding UTF8
git status --short
Remove-Item -LiteralPath .\.leans-live -Recurse -Force
```

Expected: the test prints `PASS leans-live workflow`, and `git status --short` does not list `.leans-live\probe.txt`.

- [ ] **Step 6: Commit documentation and installer**

```powershell
git add scripts/install-leans-live.ps1 docs/LEANS-Live.md README.md AGENTS.md
git commit -m "docs: add LEANS live workflow"
```

### Task 6: Publish And Hand Off To Claude

**Files:**
- Modify: `LEANS-Uebergabe.md`
- Test: `tests/leans-live.tests.ps1`

- [ ] **Step 1: Push all commits**

Run:

```powershell
git push
```

Expected: `main -> main` with no rejected updates.

- [ ] **Step 2: Record a durable Claude handoff**

Use the existing board helper:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-board.ps1 add-claude -Title "LEANS Live pruefen" -WhatBuilt "Lokale Live-Koordination mit Status, Review-Queue und Watcher erstellt." -Location "C:\Users\semir\Documents\LEANS-Live / main" -NextStep "Claude soll den Ordner oeffnen, status ausfuehren und eine Test-Review an ChatGPT erstellen."
```

- [ ] **Step 3: Commit and push the handoff**

```powershell
git add LEANS-Uebergabe.md
git commit -m "chore: hand off LEANS live workflow to Claude"
git push
```

- [ ] **Step 4: Final verification**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\leans-board.tests.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\leans-live.tests.ps1
git status --short --branch
git log -1 --oneline
```

Expected: both test scripts print `PASS`, the status is clean on `main...origin/main`, and the newest commit is the Claude handoff.
