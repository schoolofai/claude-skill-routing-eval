"""eval_skill_routing.py - routing eval for the five skills in .claude/skills.

Calls scripts/which_skill.py::which_skill() unchanged (max_turns=1, tools denied except Skill) once per
(case, rep) and grades the routing decision by exact match. No judge.

    .venv/bin/python scripts/eval_skill_routing.py --approve-harness        # user, once; records the harness sha and exits
    .venv/bin/python scripts/eval_skill_routing.py --ids c02,c04 --reps 1    # pilot
    .venv/bin/python scripts/eval_skill_routing.py                           # baseline, 3 reps
    .venv/bin/python scripts/eval_skill_routing.py --selftest                # oracle / null / error checks, no API calls
    .venv/bin/python scripts/eval_skill_routing.py --summary                 # recompute headline from results.jsonl
    .venv/bin/python scripts/eval_skill_routing.py --regrade                 # re-apply grade() to stored rows (no model calls)

Output: .claude/hillclimb/skill-routing/<variant>/{results.jsonl,errors.jsonl,traces/<id>_rep<k>.json}
"""
import argparse, asyncio, hashlib, json, math, random, sys, tempfile, time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FLOW = REPO / ".claude/hillclimb/skill-routing"
SKILLS = ["announce", "changelog", "pr-description", "release-notes", "weekly-update"]
MAX_ATTEMPTS = 3          # per (case, rep): harness/serving errors are retried with jittered backoff
sys.path.insert(0, str(HERE))


# ---- grading ---------------------------------------------------------------------------------
def grade(expected: str, skill):
    """Exact match on the first Skill call. A first move that is not a Skill call (Bash, text only) is a miss."""
    if expected == "none":
        ok = skill not in SKILLS      # no Skill call, or a skill outside our five (e.g. built-in code-review): neither is our routing
        return {"correct": float(ok), "specificity": float(ok)}
    ok = skill == expected
    return {"correct": float(ok), "recall": float(ok)}


def miss_class(expected: str, skill, first_tool):
    if expected == "none":
        return f"false_trigger:{skill}" if skill in SKILLS else None
    if skill == expected:
        return None
    if skill is None:
        return f"no_skill:first_tool={first_tool or 'text_only'}"
    return f"wrong_skill:{skill}"


# ---- harness-integrity gate --------------------------------------------------------------------
def harness_sha():
    state = json.loads((FLOW / "_state.json").read_text())
    h = hashlib.sha256()
    for rel in sorted(set(state.get("harness_paths", []))):
        h.update(rel.encode()); h.update(hashlib.sha256((REPO / rel).read_bytes()).digest())
    return h.hexdigest()


def gate(approve: bool):
    cur, f = harness_sha(), FLOW / ".harness_sha"
    if approve:
        f.write_text(cur + "\n"); print(f"harness approved: {cur[:12]}"); sys.exit(0)
    if not f.exists() or f.read_text().strip() != cur:
        print("harness changed (or never approved). Review it, then run once with --approve-harness.", file=sys.stderr)
        sys.exit(2)


# ---- one attempt -------------------------------------------------------------------------------
def _usage(u):
    u = u or {}
    return {"input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0),
            "cache_read_input_tokens": u.get("cache_read_input_tokens", 0),
            "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0)}


def served_ok(requested: str, served) -> bool:
    return bool(served) and requested.lower() in served.lower()   # alias 'sonnet' -> a claude-sonnet-* id


class AttemptError(Exception):
    def __init__(self, cls, msg, out=None): super().__init__(msg); self.cls, self.out = cls, out


async def attempt(fn, case, model, effort, timeout_s):
    try:
        out = await asyncio.wait_for(fn(case["prompt"], model=model, effort=effort), timeout_s)
    except asyncio.TimeoutError:
        raise AttemptError("timeout", f"wall-clock ceiling {timeout_s}s")
    except Exception as e:
        raise AttemptError("harness_error", f"{type(e).__name__}: {e}")
    if not served_ok(model, out.get("model")):
        raise AttemptError("model_mismatch", f"requested {model!r}, served {out.get('model')!r}", out)
    u = _usage(out.get("usage"))
    # Trusting a zero: a successful case must carry real usage/cost/latency.
    if not (u["input_tokens"] + u["cache_read_input_tokens"] + u["cache_creation_input_tokens"] > 0
            and u["output_tokens"] > 0 and (out.get("cost_usd") or 0) > 0):
        raise AttemptError("incomplete_row", f"missing usage/cost: usage={out.get('usage')} cost={out.get('cost_usd')}", out)
    return out


async def run_case(fn, case, rep, model, effort, timeout_s, vdir, sem, lock, sleep=asyncio.sleep):
    async with sem:
        for n in range(1, MAX_ATTEMPTS + 1):
            try:
                out = await attempt(fn, case, model, effort, timeout_s)
            except AttemptError as e:
                row = {"prompt_id": case["prompt_id"], "rep": rep, "attempt": n, "failure_class": e.cls,
                       "message": str(e), "model": (e.out or {}).get("model"), "usage": _usage((e.out or {}).get("usage")) if e.out else None}
                async with lock:
                    with open(vdir / "errors.jsonl", "a") as f: f.write(json.dumps(row) + "\n")
                if e.cls == "timeout" or n == MAX_ATTEMPTS:
                    return
                await sleep(min(30, 2 ** n) * (0.5 + random.random()))   # jittered backoff
                continue
            g, tools = grade(case["expected"], out["skill"]), out.get("tools") or []
            row = {"prompt_id": case["prompt_id"], "prompt": case["prompt"], "tags": case["tags"], "rep": rep,
                   "status": "ok", "stop_reason": None,   # which_skill() does not surface stop_reason
                   "expected": case["expected"], "skill": out["skill"], "first_tool": out["first_tool"],
                   "grade": g, "model": out["model"], "usage": _usage(out["usage"]),
                   "latency_s": out["latency_s"], "sdk_cost_usd": out["cost_usd"], "attempts": n,
                   "meta": {"miss_class": miss_class(case["expected"], out["skill"], out["first_tool"])}}
            trace = [{"role": "user", "content": case["prompt"]}]
            trace += [{"role": "tool_call", "name": t["name"], "content": json.dumps(t["input"], indent=2)} for t in tools]
            if out.get("text"): trace.append({"role": "assistant", "content": out["text"]})
            async with lock:
                (vdir / "traces").mkdir(exist_ok=True)
                (vdir / "traces" / f"{case['prompt_id']}_rep{rep}.json").write_text(json.dumps(trace, indent=2))
                with open(vdir / "results.jsonl", "a") as f: f.write(json.dumps(row) + "\n")   # row last: resume key
            return


# ---- summary -----------------------------------------------------------------------------------
def summarize(vdir: Path):
    rows = [json.loads(l) for l in (vdir / "results.jsonl").read_text().splitlines() if l.strip()] if (vdir / "results.jsonl").exists() else []
    errs = [json.loads(l) for l in (vdir / "errors.jsonl").read_text().splitlines() if l.strip()] if (vdir / "errors.jsonl").exists() else []
    ok = [r for r in rows if r["status"] == "ok"]
    if not ok: print("no scored rows"); return
    by_case = defaultdict(list)
    for r in ok: by_case[r["prompt_id"]].append(r["grade"]["correct"])
    means = [sum(v) / len(v) for v in by_case.values()]
    n = len(means); mu = sum(means) / n
    se = math.sqrt(sum((m - mu) ** 2 for m in means) / (n - 1) / n) if n > 1 else float("nan")
    print(f"correct {mu:.1%} +/- {1.96 * se:.1%} (95% CI over {n} cases, {len(ok)} scored runs); errors: {len(errs)} failed attempts "
          f"{dict(Counter(e['failure_class'] for e in errs))}")
    conf = Counter((r["expected"], r["skill"] or "(none)") for r in ok)
    pred = Counter(r["skill"] for r in ok if r["skill"])
    print(f"{'skill':16}{'recall':>8}{'precision':>11}")
    for s in SKILLS:
        rs = [r for r in ok if r["expected"] == s]
        rec = sum(r["grade"]["correct"] for r in rs) / len(rs) if rs else float("nan")
        prec = conf[(s, s)] / pred[s] if pred[s] else float("nan")
        print(f"{s:16}{rec:>8.0%}{prec:>11.0%}")
    nn = [r for r in ok if r["expected"] == "none"]
    if nn: print(f"{'none (specif.)':16}{sum(r['grade']['correct'] for r in nn) / len(nn):>8.0%}")
    print("confusion (expected -> picked):")
    for (e, p), c in sorted(conf.items()):
        if e != p and not (e == "none" and p == "(none)"): print(f"  {e:15} -> {p:15} x{c}")
    print("miss classes:", dict(Counter(r["meta"]["miss_class"] for r in ok if r["meta"]["miss_class"])))
    lat = sorted(r["latency_s"] for r in ok); cost = [r["sdk_cost_usd"] for r in ok]
    print(f"latency_s median {lat[len(lat)//2]:.1f} (max {lat[-1]:.1f}); sdk cost/run ${sum(cost)/len(cost):.4f} (total ${sum(cost):.3f})")


def regrade(vdir: Path):
    """Re-apply grade() to stored rows (no model calls) after a grader change."""
    p = vdir / "results.jsonl"; rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    for r in rows:
        r["grade"] = grade(r["expected"], r["skill"]); r["meta"]["miss_class"] = miss_class(r["expected"], r["skill"], r["first_tool"])
    p.write_text("".join(json.dumps(r) + "\n" for r in rows)); print(f"regraded {len(rows)} rows")


# ---- selftest (no API) -------------------------------------------------------------------------
def selftest(cases):
    print(f"oracle/null on {len(cases)} cases")
    mean = lambda f: sum(grade(c["expected"], f(c))["correct"] for c in cases) / len(cases)
    print(f"  oracle (expected label as the answer)   {mean(lambda c: None if c['expected']=='none' else c['expected']):.1%}  (want 100%)")
    print(f"  null: never invokes a skill              {mean(lambda c: None):.1%}  (= share of 'none' cases)")
    print(f"  null: always 'release-notes'             {mean(lambda c: 'release-notes'):.1%}")
    print(f"  null: always 'changelog'                 {mean(lambda c: 'changelog'):.1%}")
    # induced failures must land in errors.jsonl and never in results.jsonl
    async def boom(prompt, **kw): raise RuntimeError("induced SDK error")
    async def hang(prompt, **kw): await asyncio.sleep(60)
    async def wrong_model(prompt, **kw):
        return {"skill": "changelog", "first_tool": "Skill", "tools": [], "text": "", "model": "claude-haiku-x",
                "usage": {"input_tokens": 1, "output_tokens": 1}, "cost_usd": 0.01, "latency_s": 1.0}
    async def zero(prompt, **kw):
        return {"skill": "changelog", "first_tool": "Skill", "tools": [], "text": "", "model": "claude-sonnet-x",
                "usage": {}, "cost_usd": 0.0, "latency_s": 0.0}
    async def fine(prompt, **kw):
        return {"skill": "changelog", "first_tool": "Skill", "tools": [{"name": "Skill", "input": {"skill": "changelog"}}],
                "text": "", "model": "claude-sonnet-x", "usage": {"input_tokens": 9, "output_tokens": 3}, "cost_usd": 0.01, "latency_s": 1.2}
    async def go():
        with tempfile.TemporaryDirectory() as d:
            ok_all = True
            for name, fn, want_cls in [("api error", boom, "harness_error"), ("hang", hang, "timeout"),
                                       ("wrong model", wrong_model, "model_mismatch"), ("zero usage", zero, "incomplete_row")]:
                v = Path(d) / name.replace(" ", "_"); v.mkdir()
                await run_case(fn, cases[0], 0, "sonnet", "low", 0.2, v, asyncio.Semaphore(1), asyncio.Lock(), sleep=lambda s: asyncio.sleep(0))
                errs = [json.loads(l) for l in (v / "errors.jsonl").read_text().splitlines()]
                scored = (v / "results.jsonl").exists()
                good = errs and all(e["failure_class"] == want_cls for e in errs) and not scored
                ok_all &= bool(good)
                print(f"  induced {name:12} -> errors.jsonl x{len(errs)} [{errs[0]['failure_class']}], results.jsonl written: {scored}  {'OK' if good else 'FAIL'}")
            v = Path(d) / "fine"; v.mkdir()
            await run_case(fine, cases[0], 0, "sonnet", "low", 5, v, asyncio.Semaphore(1), asyncio.Lock())
            row = json.loads((v / "results.jsonl").read_text()); tr = json.loads((v / "traces" / f"{cases[0]['prompt_id']}_rep0.json").read_text())
            good = row["status"] == "ok" and "correct" in row["grade"] and len(tr) >= 2
            ok_all &= good; print(f"  well-formed attempt -> row + trace written  {'OK' if good else 'FAIL'}")
            return ok_all
    sys.exit(0 if asyncio.run(go()) else 1)


# ---- main --------------------------------------------------------------------------------------
async def main(a):
    from which_skill import which_skill
    cases = [json.loads(l) for l in (FLOW / "cases.jsonl").read_text().splitlines() if l.strip()]
    if a.ids: cases = [c for c in cases if c["prompt_id"] in set(a.ids.split(","))]
    vdir = FLOW / a.variant; (vdir / "traces").mkdir(parents=True, exist_ok=True)
    done = set()
    if (vdir / "results.jsonl").exists():
        done = {(r["prompt_id"], r["rep"]) for r in map(json.loads, (vdir / "results.jsonl").read_text().splitlines()) if r}
    todo = [(c, k) for c in cases for k in range(a.reps) if (c["prompt_id"], k) not in done]
    print(f"{len(todo)} runs to do ({len(done)} already done) on model={a.model} effort={a.effort}", flush=True)
    sem, lock, t0, finished = asyncio.Semaphore(a.concurrency), asyncio.Lock(), time.time(), 0

    async def one(c, k):
        nonlocal finished
        await run_case(which_skill, c, k, a.model, a.effort, a.timeout_s, vdir, sem, lock)
        finished += 1
        print(f"  {finished}/{len(todo)} done, {time.time() - t0:.0f}s", flush=True)
    await asyncio.gather(*(one(c, k) for c, k in todo))
    summarize(vdir)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--variant", default="baseline"); p.add_argument("--model", default="sonnet")
    p.add_argument("--effort", default="low"); p.add_argument("--reps", type=int, default=3)
    p.add_argument("--ids"); p.add_argument("--timeout-s", type=float, default=180)
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--approve-harness", action="store_true"); p.add_argument("--selftest", action="store_true")
    p.add_argument("--summary", action="store_true"); p.add_argument("--regrade", action="store_true")
    a = p.parse_args()
    cases = [json.loads(l) for l in (FLOW / "cases.jsonl").read_text().splitlines() if l.strip()]
    if a.selftest: selftest(cases)
    if a.regrade: regrade(FLOW / a.variant); summarize(FLOW / a.variant); sys.exit(0)
    if a.summary: summarize(FLOW / a.variant); sys.exit(0)
    gate(a.approve_harness)
    asyncio.run(main(a))
