# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T01:57:32Z
**Evals**: 1, 2, 3, 4, 5, 6 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 85% ± 26% | +0.15 |
| Time | 125.9s ± 58.2s | 131.9s ± 45.1s | -6.0s |
| Tokens | 47768 ± 5433 | 47690 ± 4147 | +78 |

## Notes

- 비교 대상: new_skill = 사용자가 수정한 SKILL.md(v2), old_skill = iteration-1 시점 SKILL.md(v1). 구성당 1회 실행이라 분산은 측정되지 않음.
- 차이는 v2 변경이 겨냥한 eval 4·5·6에서만 발생. eval5: v1은 대화에 정성적 기각 사유가 있어도 '기각한 대안과 수치적 근거'를 되물음 → v2는 되묻지 않음. eval4: v1은 이관인데도 원본에 없는 수치·재검토 조건을 되물음 → v2는 되묻지 않음. eval6: v1은 .gitkeep만 있는 기존 디렉터리에서 ADR-001을 임의로 생성 → v2는 ls 확인 후 번호를 되물음.
- 비변별(양쪽 만점): eval1·2·3. eval3은 iteration-1에서 v1이 실패(Glob 빈 결과를 믿고 ADR-001 중복)했던 케이스로, 이번에는 v1도 Glob이 또 빈 결과였지만 git ls-files로 교차 확인해 통과 → v1의 번호 결정은 비결정적(2회 중 1회 성공). v2는 규칙대로 셸 ls로 직접 확인.
- 부작용 관찰: v2 eval4는 '원본에 없어서' Reversibility 섹션을 생략함(템플릿 주석은 '가능하면 항상'). v1 eval4는 저장소 정보로 Reversibility를 작성함. v2 3단계의 '원본에 없는 정보를 새로 캐묻지 않는다'가 '작성하지도 않는다'로 과잉 해석된 것으로 보임 — 현재 assertion으로는 잡히지 않음.
- 판단 필요: eval6 규칙(빈 기존 디렉터리면 번호 확인)은 규칙대로 동작했지만, .gitkeep만 있는 디렉터리는 흔한 '첫 ADR 전' 상태라 한 번의 왕복을 추가할 수 있음. v1 결과물(ADR-001 생성 + src/auth.js 불일치 발견)도 실무적으로는 유용했음.
- 비용: 두 버전이 거의 같음(시간·토큰 차이 5% 미만). v2 eval6은 파일 생성 전에 멈추므로 더 빠름.