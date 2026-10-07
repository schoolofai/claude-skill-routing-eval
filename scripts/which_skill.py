"""which_skill.py - send one request to Claude Code (via the Claude Agent SDK) inside this repo
and report which of our skills it picks first, if any.

Nothing is executed: every tool except Skill is denied, and the session stops after one model turn.
Uses your Claude Code login (no API key needed).

    python scripts/which_skill.py "write the release notes for 1.4.0"
"""
import asyncio, json, sys, time
from pathlib import Path
from claude_agent_sdk import (query, ClaudeAgentOptions, HookMatcher, AssistantMessage, ResultMessage,
                              ResultError, ToolUseBlock, TextBlock)

REPO = Path(__file__).resolve().parent.parent


async def _deny_all_but_skill(inp, tool_use_id, ctx):
    if inp.get("tool_name") == "Skill":
        return {}
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": "routing check only: tools are disabled"}}


async def which_skill(request: str, model: str = "sonnet", effort: str = "low") -> dict:
    """Return {"skill": name or None, "first_tool", "text", "model", "usage", "cost_usd", "latency_s"}."""
    opts = ClaudeAgentOptions(
        cwd=str(REPO), model=model, effort=effort,
        max_turns=1,                      # one model turn: we only want its first move
        skills="all",                     # every skill in .claude/skills is listed, like a normal session
        setting_sources=["project"],
        hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[_deny_all_but_skill])]},
    )
    t0, tools, text, served, result = time.time(), [], "", None, None
    try:
        async for m in query(prompt=request, options=opts):
            if isinstance(m, AssistantMessage):
                served = served or m.model
                for b in m.content:
                    if isinstance(b, ToolUseBlock):
                        tools.append({"name": b.name, "input": b.input})
                    elif isinstance(b, TextBlock):
                        text += b.text
            elif isinstance(m, ResultMessage):
                result = m
    except ResultError as e:            # max_turns=1 ends the session with this on purpose
        if e.subtype != "error_max_turns":
            raise
    skill = next((t["input"].get("skill") for t in tools if t["name"] == "Skill"), None)
    return {"skill": skill, "first_tool": tools[0]["name"] if tools else None, "tools": tools,
            "text": text, "model": served,
            "usage": result.usage if result else None,
            "cost_usd": result.total_cost_usd if result else None,
            "latency_s": round(time.time() - t0, 2)}


if __name__ == "__main__":
    out = asyncio.run(which_skill(" ".join(sys.argv[1:]) or "write the release notes for 1.4.0"))
    print(json.dumps({k: out[k] for k in ("skill", "first_tool", "model", "cost_usd", "latency_s")}))
