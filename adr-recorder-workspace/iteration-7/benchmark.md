# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T06:47:45Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 97% ± 9% | 97% ± 5% | -0.00 |
| Time | 159.3s ± 69.5s | 156.6s ± 67.1s | +2.7s |
| Tokens | 52185 ± 6174 | 51738 ± 5540 | +446 |

## Notes

- 비교 대상: new_skill = v7(Alternatives에 현행 유지 포함, 대화에 재검토 조건이 없으면 Recheck if 생략, 이관 시 Date는 원본 날짜), old_skill = v6. 구성당 1회 실행이라 분산은 측정되지 않음. 이번 회차에 Recheck if 지어내기 assertion 3개(eval1·5·6)를 새로 추가함.
- 합계는 동률: v7 68/70, v6 68/70. 실패한 곳이 다름 — v7은 eval3에서 2개, v6는 eval5·6에서 1개씩.
- v7 개선: Recheck if 생략 규칙이 효과를 냄. v6는 eval5에서 RQ에 '다른 목적으로 Redis를 운영하게 되면', 현행 유지에 'SMTP 지연이 안정되면' 같은 조건을, eval6에서 API 키 안에 '키 회전을 제공하는 외부 서비스나 게이트웨이를 쓸 수 있게 되면'이라는 조건을 지어냄. v7은 셋 다 생략. 새 assertion 3개 중 2개(eval5·6)가 두 버전을 가름.
- v7 회귀(eval3): '현행 유지 포함' 규칙 때문에 '프로세스 메모리 유지'를 대안으로 넣음. 그 기각 사유(서버 3대에서 로그인 풀림)가 대화에 있어 3단계 되묻기 조건('사유가 전혀 없으면')이 사라졌고, 기각한 대안을 되묻지 않음. 결정의 문제 설명이 곧 현행 유지의 기각 사유가 되므로, 현행 유지만 대안으로 나오는 결정에서는 앞으로 되묻기가 거의 발생하지 않을 구조적 위험이 있음.
- 평가셋 긴장: eval3('메모리에서 Redis로… 로그인 풀리는 문제 때문에')과 eval7('OpenAI 대신 vLLM… 반출 금지 때문에')은 둘 다 'X→Y, 이유' 구조인데 eval3은 되묻기를, eval7은 되묻지 않기를 기대함. v6는 둘 다 통과, v7은 eval7만 통과. 현행 유지만 대안일 때 되물을지는 스킬 규칙으로 명시해야 함(사용자 결정 필요).
- assertion 밖 관찰(eval7): v7은 OpenAI 대안의 Recheck if('반출 금지 정책이 바뀌면')도 생략해 Review Trigger가 없음. v6는 이 조건을 넣음. 이 조건은 Reversible: Partial의 근거와 같은 내용이라 대화에서 직접 도출됨 — 생략 규칙이 기각 사유를 뒤집기만 한 조건까지 막는 것은 과할 수 있음.
- 비변별: eval1·2·4·7·8은 두 버전 모두 만점. iteration-6의 v6 eval1 회귀(winston 누락)는 이번 v6 실행에서 재현되지 않음(v6도 winston을 대안으로 넣음) — 1회 실행의 분산으로 보임. eval4 Date도 v6가 규칙 없이 2026-03-02를 써서 v7 Date 규칙의 효과는 이번 데이터로 확인되지 않음.
- 기계 판정: 16개 run 모두 docs/adr/ 밖 변경 없음(check_scope.py), 생성된 ADR 12개 모두 템플릿 위반 없음(check_adr.py), eval7 실행 후 HEAD 없음, eval8 .git 없음.
- 비용: v7 평균 159s / 52185 tokens, v6 평균 157s / 51738 tokens — 차이 작음.