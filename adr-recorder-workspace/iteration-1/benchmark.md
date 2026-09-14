# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T00:51:15Z
**Evals**: 1, 2, 3, 4 (1 runs each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 96% ± 7% | 54% ± 10% | +0.42 |
| Time | 111.5s ± 52.9s | 88.2s ± 22.2s | +23.2s |
| Tokens | 46570 ± 5014 | 42706 ± 2569 | +3864 |

## Notes

- 스킬 적용 시 통과율 96% vs 기준선 54% (+42%p). 각 구성당 1회 실행이라 분산은 측정되지 않음.
- 변별력 있는 항목: 템플릿 구조 준수(Review Trigger/Evidence/References, 비표준 섹션 없음), 새 결정은 Proposed(기준선은 2/2 Accepted), 대안 추측 금지(기준선은 eval3에서 대안 3개를 지어냄), 빈 요청에서 탐색 없이 되묻기(eval2: 도구 5회/40초 vs 7회/62초).
- 비변별 항목(양쪽 모두 통과): eval2 '파일 미생성'·'되묻기', 'Decision Source Human + Confidence 없음'(기준선은 기존 ADR 헤더를 복사해 우연히 충족), 'AI/ML 섹션 없음', '지어낸 수치 없음', eval4 '45ms/52ms 불일치 기록'.
- 스킬 적용 시 유일한 실패: eval3 번호 규칙. Glob이 Windows 경로에서 빈 결과를 반환했고 이를 그대로 믿어 기존 0001이 있는데도 ADR-001(3자리)을 만들어 번호가 중복됨. 기준선은 ls로 확인해 0002를 맞힘. SKILL.md에 다음 번호와 파일명 형식을 정하는 방법이 없는 것이 근본 원인.
- 비용: 스킬 적용 시 평균 +23초, +3.9k 토큰(약 +9%). SKILL.md 읽기와 더 많은 섹션(Implementation, Reversibility) 작성 때문.
- 관찰: eval4에서 3단계 '대안 수치 근거 되묻기'가 이관(migration) 상황에서도 발동함. 원본에 정성적 사유만 있는 대안(REST+캐싱) 때문인데, 이미 확정된 과거 결정에서는 과한 질문일 수 있음.