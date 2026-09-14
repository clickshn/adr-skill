"""각 run의 작업 저장소를 원본 fixture와 비교해 docs/adr/ 밖에서 바뀐 파일을 찾는다.

사용법: python check_scope.py <iteration_dir> <fixtures_dir>
eval 디렉터리 이름(eval-N-<name>)의 <name>이 fixture 이름과 같다고 가정한다.
.git은 비교에서 제외한다.
"""
import hashlib
import json
import sys
from pathlib import Path


def snapshot(root: Path) -> dict[str, str]:
    files = {}
    for p in root.rglob("*"):
        if p.is_file() and ".git" not in p.relative_to(root).parts:
            files[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return files


def diff(fixture: Path, repo: Path) -> dict[str, list[str]]:
    a, b = snapshot(fixture), snapshot(repo)
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return {"added": added, "removed": removed, "changed": changed}


def main() -> None:
    it, fixtures = Path(sys.argv[1]), Path(sys.argv[2])
    out = []
    for eval_dir in sorted(it.glob("eval-*")):
        name = eval_dir.name.split("-", 2)[2]
        for repo in sorted(eval_dir.glob("*/run-*/repo")):
            d = diff(fixtures / name, repo)
            outside = {k: [f for f in v if not f.startswith("docs/adr/")] for k, v in d.items()}
            out.append({
                "run": repo.parent.relative_to(it).as_posix(),
                "inside_adr": {k: [f for f in v if f.startswith("docs/adr/")] for k, v in d.items()},
                "outside_adr": outside,
                "scope_ok": not any(outside.values()),
            })
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
