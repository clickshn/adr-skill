# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T07:18:19Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 99% ± 4% | 94% ± 9% | +0.05 |
| Time | 151.4s ± 63.2s | 170.1s ± 72.4s | -18.7s |
| Tokens | 50522 ± 4921 | 51010 ± 5075 | -487 |

## Notes

- 비교 대상: new_skill = v7, old_skill = v6 — iteration-7·8과 같은 버전의 세 번째 표본. 평가셋 변경: eval3의 expected_output과 다섯 번째 assertion을 eval7과 같은 논리(현행 유지 대안 + 기각 사유가 대화에 있으면 Alternatives에 정리하고 되묻지 않음)로 교체.
- 합계: v7 69/70, v6 66/70. 16개 run 모두 완료(이전 회차의 API 오탐 없음).
- eval3(새 기준): v7은 현행 유지(프로세스 메모리)를 대안으로 넣고 되묻지 않아 8/8. v6는 Alternatives를 만들지 않고 기각 대안을 되물어 6/8 — 평가셋을 v7 논리로 바꾼 결과가 그대로 반영됨. v7은 세 회차 모두 같은 행동(3/3)이라 안정적.
- v7 새 실패(eval5): RQ에 대화에 없는 Recheck if('Redis를 운영하게 되어 새 인프라 부담이 사라지는 경우')를 넣음. v7의 Recheck if 생략은 eval5·6 기준 iteration-7 2/2, iteration-8 2/2, iteration-9 1/2 — 규칙이 대부분 지켜지지만 기각 사유를 뒤집은 조건은 가끔 새어 나옴. v6는 같은 두 eval에서 세 회차 6/6 모두 지어냄.
- assertion 밖 관찰(eval7): v7이 이번에는 '반출 금지 정책이 해제·완화될 때' Recheck if를 넣음(iteration-7·8에서는 생략). 즉 이번 회차 v7은 eval5·7 두 곳에서 '기각 사유 뒤집기형' Recheck if를 씀 — 이 유형을 허용할지 명시적으로 막을지 규칙 정리가 필요.
- eval4 Date: v7은 세 회차 모두 원본 시행일 2026-03-02. v6는 iteration-7 ✓, iteration-8 ✗, iteration-9 ✓ — 규칙 없는 v6는 실행마다 달라짐.
- 기계 판정: 16개 run 모두 docs/adr/ 밖 변경 없음(check_scope.py), 생성된 ADR 12개 모두 템플릿 위반 없음(check_adr.py), eval7 HEAD 없음, eval8 .git 없음.
- 비변별: eval1·2·7·8은 두 버전 모두 만점(세 회차 연속). eval4는 v6의 Date 분산이 있을 때만 변별.
- 비용: v7 평균 151s / 50522 tokens, v6 평균 170s / 51010 tokens.