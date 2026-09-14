# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T02:50:42Z
**Evals**: 1, 2, 3, 4, 5, 6 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 100% ± 0% | +0.00 |
| Time | 120.4s ± 47.7s | 116.8s ± 46.4s | +3.6s |
| Tokens | 48100 ± 4625 | 47813 ± 4719 | +286 |

## Notes

- 비교 대상: new_skill = v4(docs/adr/ 밖 파일 수정 금지 + 이관 후 원본 처리 질문, Evidence는 측정 수치가 있을 때만, 일부 문구 축약), old_skill = v3. 구성당 1회 실행이라 분산은 측정되지 않음.
- 두 버전 모두 전 항목 통과(100%). 이번 1회 실행에서는 v3도 Evidence를 생략하고 docs/adr/ 밖을 건드리지 않아 v4 신규 규칙이 점수 차이로 드러나지 않음.
- 축약 문구로 인한 회귀 없음: '새로 내리는 결정만 Proposed' 삭제 후에도 eval1·3·5·6 모두 Proposed, '원본 문서와 실측값 불일치' 예시 삭제 후에도 eval4에서 45ms/52ms 불일치를 Evidence에 기록, '(빈 섹션·TODO로 채우지 않음)' 삭제 후에도 빈 섹션·TODO 0건.
- v4가 겨냥한 실패는 이전 회차에서만 관찰됨: iteration-3 v3의 정성적 Evidence 생성, iteration-3 v2의 docs/decisions.md 무단 삭제. 둘 다 실행 편차성 실패라, 규칙 추가 효과(실패 확률 감소)는 1회 비교로 측정되지 않음 — eval3·eval4를 구성당 3회 이상 반복하면 확인 가능.
- 행동 차이(assertion 밖): v4는 eval1·eval6에서 코드 불일치를 발견한 뒤 'docs/adr/ 밖이라 수정하지 않았다'고 명시하고 코드 수정을 이어서 할지 물음. v3는 eval6에서 코드 수정 여부를 묻지 않음.
- scope 검사(check_scope.py, fixture 대비 파일 해시 비교): 12개 실행 모두 docs/adr/ 밖 변경 0건.
- 비용: 두 버전 거의 같음(시간 +3.6초, 토큰 +0.6%).