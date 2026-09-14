# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T06:25:10Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 99% ± 4% | 98% ± 6% | +0.01 |
| Time | 125.2s ± 51.4s | 119.7s ± 48.0s | +5.5s |
| Tokens | 48304 ± 4661 | 47754 ± 4327 | +550 |

## Notes

- 비교 대상: new_skill = v6(대화에 없는 대안을 캐묻지 않고 Alternatives는 대화에 등장한 대안만 정리, 새 결정은 코드가 바뀌어 있어도 Proposed, 외부 조건이 바뀌어야만 되돌릴 수 있으면 Reversible Partial), old_skill = v5. 구성당 1회 실행이라 분산은 측정되지 않음. 두 버전 모두 로드 fallback을 갖고 있어 eval7·8의 로드 차이는 없음.
- v6 규칙 효과: eval7에서 v5는 10/12 — 대화에 기각 사유가 있는데도 '다른 자체 서빙 옵션(Ollama, TGI 등)의 기각 사유를 알려달라'고 되물었고, Reversible을 Yes로 적으면서 Rollback에는 '정책이 유지되는 한 되돌릴 수 없다'고 적어 모순. v6는 12/12(되묻지 않음, Partial).
- Status 규칙: v6는 eval1·3·5·6·7 모두 '코드가 이미 바뀌었어도 새 결정이라 Proposed'라고 근거를 밝히며 Proposed. v5도 이번 실행은 eval1에서 Proposed(iteration-5에서는 Accepted) — 규칙 없는 v5는 실행마다 달라짐.
- v6 새 회귀: eval1에서 Alternatives에 '현행 winston 유지'를 넣지 않고 bunyan만 기록(8/9). 근거: 'winston은 대체되는 기존 상태라 대안으로 두지 않았다. 대안으로 적으면 대화에 없는 Recheck if를 지어내야 한다'. 'Alternatives는 대화에 실제로 등장한 대안만 정리한다' 문구가 현행 유지 대안까지 배제하게 만든 것으로 보임(winston은 대화에 등장). Recheck if는 필수 필드가 아닌데 필수로 오해. 제안: '대화에 등장한 대안(현행 유지 포함)을 정리하고, Recheck if는 대화에 조건이 없으면 줄을 생략한다'.
- 비변별: eval2·3·4·5·6·8은 v5/v6 모두 만점.
- assertion 밖 관찰: eval4에서 v5는 이관 ADR의 Date를 오늘 날짜(2026-09-11)로 적음(v6와 이전 회차는 시행일 2026-03-02).
- 비용: 두 버전 비슷함.