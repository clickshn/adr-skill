# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T02:12:12Z
**Evals**: 1, 2, 3, 4, 5, 6 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 98% ± 6% | 89% ± 27% | +0.09 |
| Time | 130.9s ± 50.2s | 91.1s ± 34.6s | +39.8s |
| Tokens | 48847 ± 4277 | 45122 ± 3551 | +3726 |

## Notes

- 비교 대상: new_skill = v3(빈 디렉터리면 001로 시작하고 알림, '캐묻지 않는다'의 범위 명확화), old_skill = v2(iteration-2의 new). 구성당 1회 실행이라 분산은 측정되지 않음.
- eval6 차이는 설계 변경에 따른 예상 결과: v3는 .gitkeep만 있는 디렉터리에서 ls 확인 후 질문 없이 ADR-001을 만들고 응답에 알림(6/6). v2는 자기 규칙대로 번호를 되물어 파일을 만들지 않음(2/6).
- v3 유일한 실패: eval3에서 실측 수치 없이 정성적 관측(사용자 보고)만으로 Evidence 섹션을 생성. v3는 Evidence 규칙을 바꾸지 않았고 v2는 iteration-2·3 모두 생략했으므로 실행 편차로 보임. SKILL.md에 'Evidence는 실측 수치가 있을 때만, 정성적 관측은 Context에'를 명시하면 편차를 줄일 수 있음.
- eval4 Reversibility: 이번엔 v2도 작성함 → iteration-2의 v2 생략은 실행 편차였을 가능성. v3 명확화의 효과는 1회 실행으로 입증되지 않음. 다만 v3의 Rollback이 더 구체적(전환된 RPC 수, 확인 못 한 REST 핸들러 명시).
- 범위 확장 관찰: eval4에서 v2는 사용자 확인 없이 docs/decisions.md의 D-007을 삭제함. v3는 원본을 건드리지 않고 삭제·이관 표시 여부를 물음. 현재 assertion에 없음 — SKILL.md에 '원본 결정 로그는 수정하지 않고 후속 처리는 사용자에게 묻는다'를 추가하는 것을 고려.
- 비변별(양쪽 만점): eval1·2·4·5. eval5는 v2도 첫 번호로 진행하며 사실을 알렸음.
- 코드 불일치 탐지(package.json과 require 불일치)는 실행마다 편차: eval1 v2 실행은 src/logger.js를 읽지 않아 놓침, v3는 eval1·6 모두 발견. assertion에는 없음.
- 비용: v3 평균 +40초, +3.7k 토큰(+8%). eval6에서 v3는 ADR 전체를 작성하고 v2는 질문 후 멈춘 설계 차이가 일부를 차지하며, v3 실행들이 저장소를 더 조사함(eval1 도구 15회 vs 8회).