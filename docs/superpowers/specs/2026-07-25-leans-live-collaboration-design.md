# LEANS Live Collaboration Design

## Status

Approved by the user on 2026-07-25. This document defines the first version of live coordination between ChatGPT/Codex and Claude on one Windows PC.

## Goal

Both assistants work from one permanent local project folder, see current work and review requests immediately, and hand work to one another without relying on a chat transcript. GitHub remains the shared version history and backup.

## Scope

The implementation has two layers:

1. A folder-native coordination layer that works whenever both assistants can access the project folder.
2. Optional MCP client configuration for Claude Desktop and Codex when the required app settings are available.

The folder-native layer is the required foundation. MCP configuration must not be a prerequisite for seeing the current state of the shared folder.

## Permanent Workspace

The GitHub repository will be cloned into a stable location outside generated Codex task folders:

`C:\Users\semir\Documents\LEANS-Live`

Both desktop apps must open this exact folder. The existing repository remains the source for the first clone; the permanent workspace becomes the everyday working copy.

## Live State

Runtime coordination data lives in `.leans-live/` and is excluded from Git:

- `state.json` records each assistant's latest declared activity.
- `events.jsonl` is an append-only event stream for work updates, handoffs, acknowledgements, and review requests.
- `reviews/` contains one small JSON file per open review request.
- `watcher.lock` prevents two local watchers from claiming the same runtime role.

The tracked `LEANS-Uebergabe.md` remains the durable task handoff. The live area is a fast status and review signal, not a replacement for the board.

## Commands

`scripts/leans-live.ps1` will provide these commands:

- `start`: watches the project and publishes relevant file changes to the event stream.
- `status`: prints the current state, newest events, and pending reviews.
- `announce`: records the current assistant, activity, and affected path.
- `request-review`: creates a review request for the other assistant.
- `acknowledge-review`: records that the addressed assistant has taken ownership of a review.
- `complete-review`: records the outcome and removes the open review file.

All writes use a temporary file followed by an atomic rename where possible. Failed writes retry briefly and return a clear error instead of silently replacing another assistant's state.

## Workflow

1. Each assistant starts by reading `LEANS-Uebergabe.md` and running `status`.
2. Before changing shared files, the assistant writes an `announce` event naming its area of work.
3. When one assistant needs a second set of eyes, it creates a `request-review` event with the target, paths, and concrete question.
4. The addressed assistant acknowledges, reviews, and records the result.
5. Important finished work still receives a normal durable board entry and a Git commit.

## Notifications And Limits

The watcher will create immediate local events and optional Windows notifications for new handoffs and review requests. It cannot make a closed or idle chat produce a response on its own. The next active action by either assistant reads the current live state before work begins.

No assistant may mark the other's work complete, overwrite a live review request, or modify files outside the shared workspace because of a live event.

## Client Integration

Claude Desktop can use a local MCP server. Codex custom-app support depends on the account or workspace developer settings. The implementation therefore supplies configuration examples and a local MCP adapter only after the folder-native core works and is tested.

## Verification

Automated PowerShell tests will verify:

- event creation and ordering;
- atomic state updates;
- review lifecycle from request through completion;
- rejection of an attempt to complete another assistant's review;
- watcher lock behavior; and
- that `.leans-live/` is ignored by Git.

Manual verification will use two PowerShell sessions to simulate Codex and Claude writing to the same folder.
