"""adr-recorder 템플릿 준수 여부를 기계적으로 점검한다.

사용법: python check_adr.py <adr.md> [...]
출력: 파일별 JSON (섹션 목록, 비표준 헤더/필드, 빈 필드, 빈 섹션, placeholder, 헤더 필드 값)
"""
import json
import re
import sys
from pathlib import Path

H2_ALLOWED = [
    "Context", "Decision", "Rationale", "Evidence", "Alternatives", "Consequences",
    "Implementation", "Reversibility", "Review Trigger", "References", "AI/ML Details",
]
H3_ALLOWED = {"Problem", "Constraints", "Selected", "Positive", "Negative", "Risks", "Evaluation"}
FIELDS_ALLOWED = {
    "Status", "Date", "Decision", "Scope", "Decision Source", "Confidence",
    "Technology", "Architecture", "Implementation",
    "Benchmark", "Experiment", "Production Data", "Cost",
    "Pros", "Cons", "Rejected because", "Recheck if",
    "Reversible", "Rollback", "Migration Cost",
    "PR", "Issue", "Related ADR", "Documentation",
    "Model", "Evaluation", "Inference",
}
PLACEHOLDER_PATTERNS = [
    r"\bTODO\b", r"\bTBD\b", r"YYYY-MM-DD", r"\{[^}\n]*\}",
    r"High \| Medium \| Low", r"Yes \| Partial \| No", r"Low \| Medium \| High",
    r"Human \| AI-Inferred", r"<!--",
]
FIELD_RE = re.compile(r"^\s*-\s*\*\*([^*]+?):\*\*\s*(.*)$")


def check(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    h1 = next((l for l in lines if l.startswith("# ")), None)
    header_fields, fields, empty_fields, nonstd_fields = {}, [], [], []
    sections, nonstd_h2, nonstd_h3, empty_sections = [], [], [], []
    cur_h2 = None
    in_code = False

    # 섹션 본문이 비었는지 확인하기 위해 헤더 위치 수집
    headers = []
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        m2 = re.match(r"^## (.+?)\s*$", line)
        m3 = re.match(r"^### (.+?)\s*$", line)
        if m2:
            cur_h2 = m2.group(1)
            sections.append(cur_h2)
            headers.append((i, 2, cur_h2))
            if cur_h2 not in H2_ALLOWED:
                nonstd_h2.append(cur_h2)
        elif m3:
            name = m3.group(1)
            headers.append((i, 3, name))
            if cur_h2 != "Alternatives" and name not in H3_ALLOWED:
                nonstd_h3.append(f"{cur_h2} > {name}")
        fm = FIELD_RE.match(line)
        if fm:
            key, val = fm.group(1).strip(), fm.group(2).strip()
            fields.append(key)
            if cur_h2 is None:
                header_fields[key] = val
            if key not in FIELDS_ALLOWED:
                nonstd_fields.append(key)
            if not val:
                # 값이 다음 줄 하위 목록으로 이어지는지 확인
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                if not re.match(r"^\s{2,}[-*\d]", nxt):
                    empty_fields.append(key)

    for idx, (i, level, name) in enumerate(headers):
        end = len(lines)
        for j, lv, _ in headers[idx + 1:]:
            if lv <= level:
                end = j
                break
        body = [l for l in lines[i + 1:end] if l.strip() and l.strip() != "---"]
        if not body:
            empty_sections.append(name)

    placeholders = []
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    for pat in PLACEHOLDER_PATTERNS:
        for m in re.finditer(pat, prose):
            placeholders.append(m.group(0))

    return {
        "file": path.name,
        "h1": h1,
        "header_fields": header_fields,
        "sections": sections,
        "nonstandard_h2": nonstd_h2,
        "nonstandard_h3": nonstd_h3,
        "nonstandard_fields": sorted(set(nonstd_fields)),
        "empty_fields": empty_fields,
        "empty_sections": empty_sections,
        "placeholders": placeholders,
        "confidence_present": "Confidence" in header_fields,
    }


if __name__ == "__main__":
    out = [check(Path(p)) for p in sys.argv[1:]]
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
