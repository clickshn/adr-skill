"""각 run의 새 ADR이 인용한 커밋 해시가 실제 파일 변경이 있는 커밋인지 확인한다.

사용법: python check_citation.py <iteration_dir>
각 run 저장소(eval-*/*/run-*/repo)에서 커밋별 변경 파일을 읽고, 새로 생기거나 바뀐
docs/adr/*.md의 16진수 토큰(7~40자)을 커밋으로 해석해 real(파일 변경 있음) / empty(빈 커밋)로 나눈다.
빈 커밋 해시가 나온 줄에 '빈 커밋'·'변경 파일이 없' 같은 표시가 있으면 그 커밋이 변경을
담고 있지 않다고 짚은 언급으로 보고 허용한다. 그 밖의 빈 커밋 인용은 위반이다.
커밋으로 해석되지 않는 토큰은 unresolved로 따로 보여준다(판정에는 쓰지 않음).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

# \b는 한글도 단어 문자로 봐서 '0c08f5e에서' 같은 인용을 놓친다 — 영숫자 경계로 판정
HEX = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
EMPTY_FLAG = re.compile(r"빈 커밋|변경(된)? 파일이 (하나도 )?없|파일 변경이 없|empty commit", re.I)
# 추가
LOCATION_FLAG = re.compile(r"HEAD|기준|시점|복원", re.I)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8").stdout


def commits(repo: Path) -> dict[str, dict]:
    out = {}
    for line in git(repo, "log", "--format=%H %s").splitlines():
        full, subj = line.split(" ", 1)
        out[full] = {"subject": subj, "files": git(repo, "show", "--name-only", "--format=", full).split()}
    return out


def check(repo: Path) -> dict:
    cs = commits(repo)
    status = git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
    adrs = [repo / l[3:] for l in status if l[3:].startswith("docs/adr/") and l[3:].endswith(".md")]
    citations, unresolved = [], set()
    for adr in adrs:
        for i, line in enumerate(adr.read_text(encoding="utf-8").splitlines(), 1):
            for tok in HEX.findall(line):
                hits = [h for h in cs if h.startswith(tok)]
                if not hits:
                    unresolved.add(tok)
                    continue
                c = cs[hits[0]]
                kind = "real" if c["files"] else "empty"
                citations.append({
                    "file": adr.name, "line": i, "hash": tok, "subject": c["subject"], "kind": kind,
                    "flagged_empty": kind == "empty" and bool(EMPTY_FLAG.search(line) or LOCATION_FLAG.search(line)),
                    "text": line.strip(),
                })
    violations = [c for c in citations if c["kind"] == "empty" and not c["flagged_empty"]]
    return {
        "adrs": [a.name for a in adrs],
        "cited_real": sorted({c["hash"] for c in citations if c["kind"] == "real"}),
        "cited_empty_flagged": sorted({c["hash"] for c in citations if c["flagged_empty"]}),
        "violations": violations,
        "unresolved": sorted(unresolved),
        "citation_ok": not violations,
    }


def main() -> None:
    it = Path(sys.argv[1])
    out = []
    for repo in sorted(it.glob("eval-*/*/run-*/repo")):
        if not (repo / ".git").exists():
            continue
        out.append({"run": repo.parent.relative_to(it).as_posix(), **check(repo)})
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
