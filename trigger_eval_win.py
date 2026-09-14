"""Windows용 description 트리거 평가 러너.

skill-creator의 scripts/run_eval.py와 같은 판정 규칙을 쓴다:
  - `claude -p <query>`를 stream-json으로 실행하고, 첫 도구 호출이 Skill/Read로 대상 스킬을
    가리키면 트리거, 다른 도구가 먼저 나오거나 도구 없이 끝나면 비트리거.
  - 쿼리마다 여러 번 실행해 trigger_rate >= threshold면 "발동"으로 본다.

run_eval.py와 다른 점:
  - select.select 대신 스레드로 stdout을 읽는다(Windows 파이프는 select를 지원하지 않음).
  - 임시 command 파일을 만들지 않고 이미 설치된 스킬(~/.claude/skills/<name>)의 호출 여부를 본다.
    같은 description이 두 번 노출되어 판정이 흐려지는 것을 막기 위해서다.
  - 첫 도구와 입력 일부를 기록해 실패 원인을 볼 수 있게 한다.

사용법:
  python trigger_eval_win.py --eval-set eval_set.json --skill-path <skill dir> \
      --cwd <중립 작업 디렉터리> --model claude-opus-5 --runs-per-query 3 --out results.json
"""
import argparse
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def parse_frontmatter(skill_path: Path) -> tuple[str, str]:
    lines = (skill_path / "SKILL.md").read_text(encoding="utf-8").splitlines()
    name = description = ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            name = line[5:].strip().strip("\"'")
        elif line.startswith("description:"):
            description = line[12:].strip().strip("\"'")
    return name, description


def run_single_query(query: str, skill_name: str, timeout: int, cwd: str, model: str | None) -> dict:
    cmd = [shutil.which("claude"), "-p", query, "--output-format", "stream-json",
           "--verbose", "--include-partial-messages"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL, cwd=cwd, env=env)

    lines: queue.Queue = queue.Queue()

    def reader() -> None:
        for raw in iter(proc.stdout.readline, b""):
            lines.put(raw)
        lines.put(None)

    threading.Thread(target=reader, daemon=True).start()

    info = {"triggered": False, "first_tool": None, "first_tool_input": "", "timed_out": False}
    pending = None
    acc = ""
    deadline = time.time() + timeout
    try:
        while True:
            if time.time() >= deadline:
                info["timed_out"] = True
                return info
            try:
                raw = lines.get(timeout=1.0)
            except queue.Empty:
                continue
            if raw is None:
                return info
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = ev.get("type")
            if etype == "stream_event":
                se = ev.get("event", {})
                stype = se.get("type", "")
                if stype == "content_block_start":
                    cb = se.get("content_block", {})
                    if cb.get("type") == "tool_use":
                        tool = cb.get("name", "")
                        info["first_tool"] = info["first_tool"] or tool
                        if tool in ("Skill", "Read"):
                            pending, acc = tool, ""
                        else:
                            return info
                elif stype == "content_block_delta" and pending:
                    delta = se.get("delta", {})
                    if delta.get("type") == "input_json_delta":
                        acc += delta.get("partial_json", "")
                        if skill_name in acc:
                            info.update(triggered=True, first_tool_input=acc[:200])
                            return info
                elif stype in ("content_block_stop", "message_stop"):
                    if pending:
                        info.update(triggered=skill_name in acc, first_tool_input=acc[:200])
                        return info
                    if stype == "message_stop":
                        return info
            elif etype == "assistant":
                for item in ev.get("message", {}).get("content", []):
                    if item.get("type") != "tool_use":
                        continue
                    tool = item.get("name", "")
                    payload = json.dumps(item.get("input", {}), ensure_ascii=False)
                    info["first_tool"] = info["first_tool"] or tool
                    info["first_tool_input"] = payload[:200]
                    info["triggered"] = tool in ("Skill", "Read") and skill_name in payload
                    return info
            elif etype == "result":
                return info
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-set", required=True)
    ap.add_argument("--skill-path", required=True)
    ap.add_argument("--cwd", required=True, help="claude -p를 실행할 중립 디렉터리")
    ap.add_argument("--model", default=None)
    ap.add_argument("--runs-per-query", type=int, default=3)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--limit", type=int, default=0, help="앞에서 N개 쿼리만 실행(스모크 테스트용)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    if args.limit:
        eval_set = eval_set[:args.limit]
    skill_name, description = parse_frontmatter(Path(args.skill_path))
    Path(args.cwd).mkdir(parents=True, exist_ok=True)

    runs: dict[str, list[dict]] = {item["query"]: [] for item in eval_set}
    started = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_single_query, item["query"], skill_name, args.timeout, args.cwd, args.model): item
                   for item in eval_set for _ in range(args.runs_per_query)}
        done = 0
        for fut in as_completed(futures):
            item = futures[fut]
            try:
                res = fut.result()
            except Exception as e:  # noqa: BLE001 — 한 실행의 실패가 전체를 멈추지 않게
                res = {"triggered": False, "first_tool": None, "first_tool_input": f"ERROR: {e}", "timed_out": False}
            runs[item["query"]].append(res)
            done += 1
            print(f"[{done}/{len(futures)}] {'T' if res['triggered'] else '-'} "
                  f"first={res['first_tool']} {'(timeout) ' if res['timed_out'] else ''}{item['query'][:40]}",
                  file=sys.stderr, flush=True)

    results = []
    for item in eval_set:
        rs = runs[item["query"]]
        rate = sum(r["triggered"] for r in rs) / len(rs)
        fired = rate >= args.threshold
        results.append({
            "query": item["query"],
            "should_trigger": item["should_trigger"],
            "trigger_rate": rate,
            "triggers": sum(r["triggered"] for r in rs),
            "runs": len(rs),
            "pass": fired == item["should_trigger"],
            "first_tools": [r["first_tool"] for r in rs],
            "first_tool_inputs": [r["first_tool_input"] for r in rs],
            "timeouts": sum(r["timed_out"] for r in rs),
        })

    pos = [r for r in results if r["should_trigger"]]
    neg = [r for r in results if not r["should_trigger"]]
    tp = sum(r["pass"] for r in pos)
    fp = sum(not r["pass"] for r in neg)
    summary = {
        "total": len(results),
        "passed": sum(r["pass"] for r in results),
        "accuracy": round(sum(r["pass"] for r in results) / len(results), 3),
        "should_trigger_hit_rate": round(tp / len(pos), 3) if pos else None,
        "should_not_false_trigger_rate": round(fp / len(neg), 3) if neg else None,
        "precision": round(tp / (tp + fp), 3) if (tp + fp) else None,
        "raw_positive_trigger_rate": round(sum(r["trigger_rate"] for r in pos) / len(pos), 3) if pos else None,
        "raw_negative_trigger_rate": round(sum(r["trigger_rate"] for r in neg) / len(neg), 3) if neg else None,
        "elapsed_seconds": round(time.time() - started, 1),
    }
    out = {"skill_name": skill_name, "description": description, "model": args.model,
           "runs_per_query": args.runs_per_query, "threshold": args.threshold,
           "summary": summary, "results": results}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
