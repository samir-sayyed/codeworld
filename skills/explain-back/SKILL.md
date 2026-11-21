---
name: explain-back
description: Make sure the person who owns the code understands every AI change before moving on. After a coding turn, explain back what now happens differently, the path from trigger to result with file:line, the choices made that nobody asked for, and one apply-it question held back until the user answers. Ships a Claude Code Stop hook (hook.py) that triggers this automatically whenever a turn edited code. Use when the user says "explain back", "explain what you changed", "make me understand this change", "/explain-back", or wants to stop vibe-coding blind.
---

# Explain Back

People who generate code and then engage with it understand it about as well as people who wrote it by hand. People who just hand the work over don't. (Anthropic's 2026 trial with 52 engineers: 65–86% on a quiz about the code they wrote, against 24–39%.) This skill makes the engage step cheap and automatic.

## On demand

When invoked, explain back the most recent change in this session (or the one the user names), in under 150 words, no code dump:

1. **What now happens differently.** Describe behavior the user would notice, not a list of files.
2. **The path.** The steps from trigger to result, each with `file:line`.
3. **Choices made for you.** Defaults, limits, names and libraries the user didn't ask for. Say "none" if there are none.
4. **One apply-it question.** For example "what would happen if…" or "which file would you change to…". Don't give the answer. When they reply, say whether it's right and point to the `file:line`.

If `WORLD.md` exists at the repo root, tell 1 and 2 using its places and characters (see `examples/WORLD.md` in the codeworld repo).

## Automatic: the Stop hook

`hook.py` runs when Claude is about to stop. If that turn used Edit, MultiEdit, Write or NotebookEdit for 3 or more lines, it blocks the stop once and asks for the explain-back above. These pass straight through:
- read-only turns
- typo-sized edits
- files outside the project
- `.md` and `.txt` files
- unattended runs (`claude -p`, cron and launchd jobs)
- the explain-back itself

It needs Python 3 and nothing to install.

Add it to `~/.claude/settings.json` (every project) or a project's `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python3 ~/.claude/skills/explain-back/hook.py" } ] }
    ]
  }
}
```

Turn it off for one session with `EXPLAIN_BACK=off claude`. Check it with `python3 hook.py --selftest`.

Limits: edits made through Bash (`sed`, heredocs) aren't seen, and the edit size is counted from the new text only.
