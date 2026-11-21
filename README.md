# codeworld

**Understand the code your AI writes.**

AI writes code faster than anyone can read it. Developers and vibe coders ship features they can't explain, fix bugs that break other features, and get stuck when they have to change something months later. Writing code got fast. Understanding it didn't.

codeworld makes the understanding step cheap and automatic. The first tool is **explain-back**: after every AI change, Claude Code tells you what now happens differently, the path through the code, the choices it made that you didn't ask for, and asks you one question about it.

## Why

In a 2026 trial by Anthropic, engineers who used AI scored 50% on a quiz about code they had just written, against 67% for engineers who wrote it by hand. *How* they used AI mattered more than whether they did:

- **Generated code, then asked questions about it:** 65–86%, as good as writing it by hand or better.
- **Handed the task over, or let AI do the debugging:** 24–39%.

explain-back turns the second habit into the first without extra effort. The full research, with sources and caveats, is in [docs/research.md](docs/research.md).

## What explain-back looks like

You ask Claude Code:

> Make get_json retry up to 3 times with a short backoff when the request fails.

Claude edits `fetch.py`. Before it can finish, explain-back makes it write this (real output):

> **1. What's different:** A failed request no longer fails on the first try. `get_json` quietly retries and only gives up after three failed attempts.
>
> **2. The path:** `fetch.py:4` loops up to 3 times → `:6-7` makes the request → `:8` catches the error → `:9-10` gives up on the last attempt → `:11` waits 0.5 s, then 1 s, and tries again.
>
> **3. Choices you didn't ask for:** 0.5 s doubling backoff, a new `retries=3` parameter, and it catches every error, **including 404 Not Found**.
>
> **4. Question:** If the server returns 404, what happens, and which line would you change so it fails immediately?

You asked for retries. You probably didn't know it would also retry pages that don't exist. Now you know, before it ships. Answer the question and Claude tells you whether you're right, with the file and line.

## How it works

explain-back is a [Claude Code Stop hook](https://docs.claude.com/en/docs/claude-code/hooks): a small Python script that Claude Code runs each time Claude is about to finish a reply.

```
you ask for a change
  → Claude edits code and tries to finish
  → Claude Code runs hook.py with the session's details
      → did this turn edit 3+ lines of code inside the project?
          no  → stay silent, Claude finishes
          yes → block the finish once, with the explain-back instructions
  → Claude writes the explain-back and tries to finish again
  → hook.py sees it's the second try and stays silent
```

Step by step:

1. **Claude Code calls the hook** and passes it JSON: the project folder, the path to the session transcript, and `stop_hook_active` (whether this finish was already blocked once).
2. **Quiet checks.** The hook stays silent if `EXPLAIN_BACK=off` is set, if this is the second try (so it never loops), or if nobody is watching. Headless runs like `claude -p`, cron and launchd jobs set `CLAUDE_CODE_SESSION_ATTENDED=0`.
3. **What changed this turn.** It reads the transcript backwards to your last message and collects the `Edit`, `MultiEdit`, `Write` and `NotebookEdit` calls since then.
4. **Does it count.** Files outside the project folder and `.md` and `.txt` files are ignored. If fewer than 3 lines were written, it stays silent.
5. **Ask for the explain-back.** It prints `{"decision": "block", "reason": "..."}`. Claude Code doesn't let Claude finish and gives it the reason as new instructions.

It stays silent for:

| Situation | Why |
|---|---|
| Questions, reading code | No edits |
| Typo fixes | Fewer than 3 lines |
| Notes in `.md` / `.txt` | Prose, not code |
| Scratch files outside the project | Not your project's code |
| `claude -p`, cron, launchd | Nobody there to answer |
| `EXPLAIN_BACK=off claude` | Switched off |

## Tell it in your app's world (optional)

Add a `WORLD.md` to your repo root. It maps your app's features to places in a world that fits what your product is about, and explain-backs then use those places, still with file:line:

> The Dispatch Tower now skips riders more than 5 km from the kitchen (`src/dispatch/assignRider.ts:42`), so a far-away free rider no longer beats a nearby busy one.

That's how an explain-back reads for the made-up pizza app in [examples/WORLD.md](examples/WORLD.md), a city of kitchens, a dispatch tower and riders. Pick a world that fits your product: a nutrition app could be a restaurant kitchen, a music app a concert hall. Use the example as a template.

## Install

Needs Claude Code and Python 3. Nothing else.

```bash
git clone https://github.com/samir-sayyed/codeworld.git ~/codeworld
```

```bash
ln -s ~/codeworld/skills/explain-back ~/.claude/skills/explain-back
```

Then add the hook to `~/.claude/settings.json` (all projects) or `<project>/.claude/settings.json` (one project):

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python3 ~/.claude/skills/explain-back/hook.py" } ] }
    ]
  }
}
```

Check it:

```bash
python3 ~/codeworld/skills/explain-back/hook.py --selftest
```

You can also ask for an explain-back on demand: `/explain-back`.

## Limits

- Edits made through shell commands (`sed`, heredocs) aren't seen.
- "The project" is the folder Claude Code started in, not the git root.
- Line numbers in an explain-back come from Claude and are sometimes off by one.
- `CLAUDE_CODE_SESSION_ATTENDED` isn't documented. If a future Claude Code drops it, set `EXPLAIN_BACK=off` in your scheduled jobs.
- Tested on Claude Code 2.1.x on macOS.

## Roadmap

- **explain-back**: done.
- **Before you change it:** ask "I want X" and see which parts of the app and which house rules it touches, before any code is written.
- **Choices log:** record the decisions from each session into the repo while they're made, instead of reconstructing them later.
- **World generator:** build a `WORLD.md` and an interactive map of any repo from its code, with every place linked to real files.
- **Fix-loop breaker:** after two failed fixes, replay the broken flow step by step.

## Repo layout

```
skills/explain-back/hook.py    the Stop hook (Python stdlib, --selftest)
skills/explain-back/SKILL.md   the skill, for on-demand use and install notes
examples/WORLD.md              a world template for a made-up app
docs/research.md               the research behind this project
```
