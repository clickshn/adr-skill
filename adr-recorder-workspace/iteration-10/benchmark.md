# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-14T00:18:41Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 100% ± 0% | +0.00 |
| Time | 145.5s ± 62.2s | 135.0s ± 53.1s | +10.5s |
| Tokens | 51478 ± 5528 | 50585 ± 4805 | +893 |

## Notes

- 비교 대상: new_skill = v8, old_skill = v7. v8은 SKILL.md에 한 줄 추가 — 'Recheck if는 대화에 명시된 재검토 조건만 쓰고, 기각 사유를 단순히 뒤집은 조건도 지어낸 것으로 취급한다'. 평가셋은 iteration-9와 같음.
- 합계: v8 70/70, v7 70/70. 16개 run 모두 완료.
- 핵심 확인(기각 사유 반전형 Recheck if): eval5·6·7에서 v8은 Recheck if와 Review Trigger를 하나도 쓰지 않음(3/3). eval5·7 transcript는 새 규칙을 직접 근거로 듦 — 'Redis 운영 부담이 사라지면', '반출 금지가 풀리면 재검토'를 기각 사유 뒤집기로 보고 생략.
- 단, 이번 회차는 v7도 같은 세 곳에서 모두 생략(3/3)해 이 회차만으로는 변별이 안 됨. v7 누적: eval5·6·7 × iteration-7~10 = 12번 중 2번 새어 나옴(둘 다 iteration-9 — eval5 RQ, eval7 반출 금지). v8은 1회차 3번 중 0번이라, 효과를 말하려면 반복 표본이 더 필요.
- 과잉 적용 없음: 대화·원본에 명시된 재검토 조건은 v8도 그대로 유지 — eval1 bunyan '유지보수 재개', eval4 GraphQL '플랫폼팀 4명 이상' 모두 Recheck if와 Review Trigger에 들어감. eval4에서 v8은 REST+캐싱에 조건을 만들지 않은 이유로 새 규칙을 인용.
- assertion 밖 관찰(v8 eval5, 사실 오류): ADR의 Problem과 References가 현행 동기 발송 코드를 커밋 c44bbf9('feat: 가입 인증 메일 발송')에서 추가된 것으로 인용. 실제로 c44bbf9는 파일 변경이 없는 빈 커밋이고 app/mail.py는 8ca7a94에서 추가됨. v8은 `git show --stat c44bbf9`를 실행하고도 커밋 메시지를 보고 인용함. v7은 같은 eval에서 빈 커밋을 걸러내고 8ca7a94를 인용.
- 반대로 eval4에서는 v8이 919fb33·4b0137d가 빈 커밋이고 파일은 979e62c에서 추가됐다고 짚었고, v7은 두 커밋을 설명 없이 References에 인용 — 커밋 인용 정확도는 버전 간 일관된 차이로 보기 어려움. 현재 assertion과 check_adr.py로는 잡히지 않으므로 '인용한 커밋 해시가 실제로 해당 파일을 바꿨다' 류의 assertion 추가를 검토.
- 누락 timing 복구: 이전 세션(b9213c63)이 2026-09-11 16:30 KST에 session limit으로 중단됨. eval4 new, eval5 new·old, eval6 old, eval7 new·old 6개 run은 서브에이전트가 16:29에 정상 종료하고 결과물도 모두 저장했지만, 완료 알림이 오케스트레이터 턴 도중 큐에 쌓였다가 16:30:09에 꺼내진 직후 세션이 끊겨 timing.json을 쓰지 못함. 세션 로그 큐 항목의 usage(subagent_tokens, duration_ms)로 복구했고, 정상 기록된 eval6 new의 값과 대조해 형식이 같음을 확인. 채점 대상 결과물은 영향 없음.
- 같은 이유로 run별 repo 사본도 iteration-10에 복사되지 않은 상태였음 — 이번에 이전 세션 scratchpad의 iter10 작업 저장소를 run-1/repo로 복사해 기계 판정을 실행.
- 기계 판정: 16개 run 모두 docs/adr/ 밖 변경 없음(check_scope.py), 생성된 ADR 12개 모두 템플릿 위반 없음(check_adr.py), eval7 HEAD 없음, eval8 .git 없음.
- 비변별: 이번 회차는 8개 eval 모두 두 버전 만점 — 평가셋이 포화 상태. 이후 개선을 재려면 새 케이스(커밋 인용 정확성, README의 미검증 항목 등)가 필요.
- 비용: v8 평균 146s / 51478 tokens, v7 평균 135s / 50585 tokens(복구한 timing 6건 포함).