# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T07:07:13Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 98% ± 4% | 96% ± 6% | +0.03 |
| Time | 156.1s ± 63.8s | 162.0s ± 83.5s | -5.8s |
| Tokens | 51988 ± 5497 | 52508 ± 7252 | -520 |

## Notes

- 비교 대상: new_skill = v7, old_skill = v6 — iteration-7과 같은 버전의 두 번째 표본. 평가셋 변경: eval3의 '기각한 대안을 되물었다' assertion을 eval7과 같은 '대화에 기각 사유가 있으므로 … 되묻지 않았다'로 교체.
- 실행 실패: old_skill eval3는 API safeguards 오탐(reasoning_extraction)으로 3회 모두 중단되어 채점에서 빠짐. old_skill 평균은 7개 eval 기준이라 위 표의 Pass Rate를 그대로 비교하면 안 됨. eval3을 뺀 같은 조건 비교: v7 62/62, v6 59/62. 전체 합계: v7 69/70, v6 59/62.
- v7의 유일한 실패(eval3): 'Alternatives 섹션과 Review Trigger 섹션이 모두 없다' — v7은 두 회차 모두 '프로세스 메모리 유지(현행)'를 대안으로 넣음. 이 assertion은 새로 바꾼 '대화에 기각 사유가 있으므로 되묻지 않았다'와 전제가 충돌함(기각 사유가 있다 = 현행 유지를 대안으로 본다는 뜻). eval3 expected_output도 여전히 '대안 없음, 생성 후 되물음'이라 평가셋 정리가 필요.
- v6 실패: eval4 Date를 이관일 2026-09-11로 적음(원본 시행일 2026-03-02가 아님). iteration-7에서는 맞게 적었으므로 규칙이 없는 v6는 실행마다 달라짐. v7은 두 회차 모두 시행일 — Date 규칙 효과가 이번에 처음 확인됨. eval5·6에서는 대화에 없는 Recheck if를 다시 지어냄(두 회차 합쳐 4/4).
- 두 회차 종합(v7): Recheck if 생략 4/4(eval5·6), eval1·5·6·7에서 현행 유지를 대안으로 포함, eval3에서 현행 유지 대안 때문에 되묻지 않음 2/2 — 규칙의 효과와 부작용 모두 재현됨.
- assertion 밖 관찰(eval7): v7은 두 회차 모두 '반출 금지 정책이 바뀌면' Recheck if를 생략해 Review Trigger가 없음. v6는 두 회차 모두 넣음.
- 기계 판정: 완료된 15개 run 모두 docs/adr/ 밖 변경 없음(check_scope.py), 생성된 ADR 12개 모두 템플릿 위반 없음(check_adr.py), eval7 HEAD 없음, eval8 .git 없음.
- 비변별: eval1·2·7·8은 두 버전 모두 만점(두 회차 연속).
- 비용: v7 평균 156s / 51988 tokens, v6 평균 162s / 52508 tokens(v6는 7개 run).