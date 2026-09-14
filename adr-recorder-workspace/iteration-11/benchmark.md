# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-14T00:58:53Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8, 9 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 100% ± 0% | +0.00 |
| Time | 161.5s ± 67.8s | 144.8s ± 54.5s | +16.7s |
| Tokens | 53710 ± 6919 | 51750 ± 5105 | +1960 |

## Notes

- 비교 대상: new_skill = v9, old_skill = v8. v9는 SKILL.md에 3줄 추가 — '커밋 해시를 근거로 인용할 때는 git show --stat으로 실제 변경을 확인하고, 빈 커밋이면 인용하지 않고 실제 변경 커밋을 다시 찾는다'. 평가셋 변경: 케이스 9(commit-citation-trap) 추가 — 빈 커밋의 존재를 정확히 짚는 것은 허용하는 수정된 assertion 적용.
- 합계: v9 73/73, v8 73/73. 18개 run 모두 완료. eval1 v9의 첫 실행은 API safeguards 오탐(reasoning_extraction)으로 중단되어, 작업 저장소를 fixture로 되돌리고 재실행함(timing은 재실행 값).
- eval9(커밋 인용 함정): 두 버전 모두 통과 — 이 회차에서는 변별 안 됨. v9는 실제 변경 커밋 aedc21c만 인용하고 빈 커밋 a8b6a4a는 응답에서 '인용하지 않았다'고 설명. v8도 git log --stat·git show로 직접 확인해 aedc21c를 근거로 인용하고, a8b6a4a는 '변경 파일이 없는 빈 커밋'이라고 명시(허용 조건). 메시지가 결정과 정확히 일치하는 노골적인 함정은 규칙 없이도 잡힘.
- 변별 신호는 assertion 밖에서 나옴(check_citation.py로 전체 run의 인용 해시를 저장소 커밋과 대조): 빈 커밋을 근거로 인용한 경우 v9 0건, v8 2건. v8 eval5는 현행 app/mail.py의 출처로 빈 커밋 286b20c('feat: 가입 인증 메일 발송')를 Problem과 References에 인용 — iteration-10 eval5와 같은 오류가 2회 연속. v8 eval6은 Context에서 파트너 연동의 근거로 빈 커밋 1f85596('feat: 파트너 주문 조회 API')을 인용.
- 두 오류 모두 커밋 메시지가 결정과 느슨하게만 연결되는 부수적 인용에서 나옴 — 케이스 9처럼 결정 자체를 가리키는 커밋은 v8도 검증하지만, 배경 설명용 인용에서는 메시지를 그대로 믿음. v9는 같은 두 eval에서 실제 추가 커밋(eval5 751f118, eval6 dbbeb0a)을 인용했고, eval3·5에서는 빈 커밋(5a76edd, 286b20c)을 걸러냈다고 응답에 명시. eval4에서는 두 버전 모두 빈 커밋 7d7cef8·ea70f75를 '빈 커밋'으로 정확히 표시.
- 제안: '인용한 커밋 해시는 모두 실제 파일 변경이 있는 커밋이다'를 커밋을 인용할 수 있는 모든 eval의 공통 assertion으로 넣으면 eval5·6이 변별됨. 판정은 check_citation.py(한글이 붙은 해시도 인식하도록 영숫자 경계 사용)로 자동화 가능 — 레포 루트 검증 도구로 편입 검토.
- 기각 사유 반전형 Recheck if(v8에서 추가한 규칙): eval5·6·7에서 v9·v8 모두 생략(각 3/3). v8 누적은 iteration-10·11 합쳐 6/6 생략.
- 기계 판정: 18개 run 모두 docs/adr/ 밖 변경 없음(check_scope.py), 생성된 ADR 14개 모두 템플릿 위반 없음(check_adr.py), eval7 HEAD 없음, eval8 .git 없음.
- 비변별: 9개 eval 모두 두 버전 만점 — assertion 기준으로는 평가셋이 여전히 포화 상태. 이번 회차의 버전 차이는 위의 커밋 인용 대조에서만 드러남.
- 비용: v9 평균 161s / 53710 tokens, v8 평균 145s / 51750 tokens. 도구 호출은 v9 합계 105회, v8 103회로 git show 확인 규칙의 추가 부담은 거의 없음.