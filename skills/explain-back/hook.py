#!/usr/bin/env python3
"""Claude Code Stop hook: if this turn edited code, make Claude explain the change back before it stops.

Reads the hook's JSON on stdin. Prints {"decision": "block", "reason": ...} when the turn since the
user's last prompt used an edit tool, so Claude continues and writes the explain-back. Silent otherwise.
Run `python3 hook.py --selftest` to check it.
"""
import json, os, sys, tempfile

EDIT_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}
MIN_LINES = 3  # ponytail: skip typo-sized edits; raise it if the explain-back feels naggy
# Only these count. Prose (README, LICENSE, notes) and binaries never trigger an explain-back.
# ponytail: a fixed list; add an extension here when a language is missing
CODE = {".kt", ".kts", ".java", ".scala", ".groovy", ".gradle", ".py", ".ipynb", ".js", ".jsx", ".mjs",
        ".cjs", ".ts", ".tsx", ".vue", ".svelte", ".html", ".css", ".scss", ".go", ".rs", ".swift",
        ".m", ".mm", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".rb", ".php", ".dart", ".lua", ".sh",
        ".bash", ".zsh", ".sql", ".json", ".yaml", ".yml", ".toml", ".xml", ".properties"}
CODE_NAMES = {"Dockerfile", "Makefile"}


def is_code(path):
    name = os.path.basename(path)
    return name in CODE_NAMES or os.path.splitext(name)[1].lower() in CODE

PROMPT = """Before you finish, explain back the code change you just made to the person who will own it. Don't repeat what your last message already said. Under 150 words, plain language, no code dump:
1. What now happens differently: behavior the user would notice, not a list of files.
2. The path: the steps from trigger to result, each with file:line.
3. Choices you made that they didn't ask for: defaults, limits, names, libraries. Say "none" if none.
4. One apply-it question, such as "what would happen if..." or "which file would you change to...". Don't give the answer. When they reply, say whether it's right and point to the file:line.
If WORLD.md exists at the repo root, tell 1 and 2 using its places and characters."""


def edited_lines_this_turn(transcript_path, project_dir):
    """Lines written by edit tools since the user's last real prompt (tool results don't count).
    Only files inside the project count: scratch files, temp output and prose don't."""
    root = os.path.realpath(project_dir) + os.sep if project_dir else None
    try:
        with open(transcript_path) as f:
            entries = [json.loads(line) for line in f if line.strip()]
    except (OSError, ValueError):
        return 0
    lines = 0
    for e in reversed(entries):
        content = (e.get("message") or {}).get("content")
        if e.get("type") == "user":
            is_tool_result = isinstance(content, list) and any(
                isinstance(c, dict) and c.get("type") == "tool_result" for c in content)
            if not is_tool_result:
                break  # reached the prompt that started this turn
        elif e.get("type") == "assistant" and isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") in EDIT_TOOLS:
                    inp = c.get("input") or {}
                    path = os.path.realpath(inp.get("file_path") or inp.get("notebook_path") or "")
                    if not root or not path.startswith(root) or not is_code(path):
                        continue
                    text = inp.get("new_string") or inp.get("content") or inp.get("new_source") or ""
                    text += "".join(ed.get("new_string", "") for ed in inp.get("edits") or [])
                    lines += max(1, text.count("\n") + 1)
    return lines


def decide(hook_input):
    if os.environ.get("EXPLAIN_BACK") == "off" or hook_input.get("stop_hook_active"):
        return None  # already explained once this stop, or switched off
    # ponytail: claude -p and scheduled jobs set this to 0 (observed in 2.1.x, undocumented);
    # if it ever disappears, put EXPLAIN_BACK=off in those jobs instead
    if os.environ.get("CLAUDE_CODE_SESSION_ATTENDED") == "0":
        return None  # nobody is there to answer the question
    project = hook_input.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR", "")
    if edited_lines_this_turn(hook_input.get("transcript_path", ""), project) < MIN_LINES:
        return None
    return {"decision": "block", "reason": PROMPT}


def selftest():
    def transcript(*entries):
        f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
        f.write("\n".join(json.dumps(e) for e in entries))
        f.close()
        return f.name
    user = lambda text: {"type": "user", "message": {"role": "user", "content": text}}
    result = {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}}
    tool = lambda name, **inp: {"type": "assistant", "message": {"role": "assistant",
                                "content": [{"type": "tool_use", "name": name, "input": inp}]}}
    os.environ.pop("CLAUDE_CODE_SESSION_ATTENDED", None)
    proj = tempfile.mkdtemp()
    src = os.path.join(proj, "fetch.py")
    run = lambda t, **kw: decide({"transcript_path": t, "cwd": proj, **kw})
    five = "a\nb\nc\nd\ne"
    edit_turn = transcript(user("add retry"), tool("Edit", file_path=src, old_string="x", new_string=five), result)
    assert run(edit_turn)["decision"] == "block", "edit this turn should block"
    assert run(edit_turn, stop_hook_active=True) is None, "must not loop"
    read_turn = transcript(user("what does x do"), tool("Read", file_path=src), result)
    assert run(read_turn) is None, "read-only turn should pass"
    old_edit = transcript(user("add retry"), tool("Write", file_path=src, content=five), result, user("thanks"))
    assert run(old_edit) is None, "edit from an earlier turn should pass"
    typo = transcript(user("fix typo"), tool("Edit", file_path=src, old_string="teh", new_string="the"), result)
    assert run(typo) is None, "typo-sized edit should pass"
    multi = transcript(user("rename"), tool("MultiEdit", file_path=src, edits=[{"new_string": "a\nb"}, {"new_string": "c\nd"}]), result)
    assert run(multi)["decision"] == "block", "MultiEdit counts its edits"
    outside = transcript(user("draft"), tool("Write", file_path="/tmp/scratch/report.html", content=five), result)
    assert run(outside) is None, "files outside the project should pass"
    notes = transcript(user("notes"), tool("Write", file_path=os.path.join(proj, "NOTES.md"), content=five), result)
    assert run(notes) is None, "prose files should pass"
    lic = transcript(user("add license"), tool("Write", file_path=os.path.join(proj, "LICENSE"), content=five), result)
    assert run(lic) is None, "extensionless prose like LICENSE should pass"
    kt = transcript(user("guard"), tool("Edit", file_path=os.path.join(proj, "app", "Parser.KT"), new_string=five), result)
    assert run(kt)["decision"] == "block", "code extensions count, in any case"
    docker = transcript(user("image"), tool("Write", file_path=os.path.join(proj, "Dockerfile"), content=five), result)
    assert run(docker)["decision"] == "block", "Dockerfile counts as code"
    os.environ["CLAUDE_CODE_SESSION_ATTENDED"] = "0"
    assert run(edit_turn) is None, "unattended runs (claude -p, cron) should pass"
    os.environ.pop("CLAUDE_CODE_SESSION_ATTENDED")
    assert run("/nonexistent") is None, "missing transcript should pass"
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        out = decide(json.load(sys.stdin))
        if out:
            print(json.dumps(out))
