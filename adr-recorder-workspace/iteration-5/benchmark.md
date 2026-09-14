# Skill Benchmark: adr-recorder

**Model**: claude-opus-5
**Date**: 2026-09-11T05:59:31Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 runs each per configuration)

## Summary

| Metric | New Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 97% ± 5% | 74% ± 46% | +0.24 |
| Time | 122.9s ± 49.9s | 102.1s ± 55.2s | +20.8s |
| Tokens | 48104 ± 4460 | 46576 ± 4714 | +1529 |

## Notes

- 비교 대상: new_skill = v5(v4 + 컨텍스트 명령 2개에 '2>/dev/null || echo' fallback), old_skill = v4. 구성당 1회 실행이라 분산은 측정되지 않음.
- fallback 효과: eval7(커밋 없는 git 저장소) v4 0/10 — git diff/log가 exit 128로 끝나 스킬 로드 실패, v5 9/10. eval8(git 저장소 아님) v4 0/6 — exit 129/128로 로드 실패, v5 6/6. 로드 실패 실행에서 '아무 작업도 안 해서' 충족된 항목(파일 미생성, 커밋 없음 등)은 통과로 세지 않음.
- 회귀 없음: 커밋이 있는 eval1–6에서는 fallback이 발동하지 않으며 v4/v5 점수가 모두 같음.
- 새로 드러난 회귀(v4·v5 공통): eval1에서 두 버전 모두 새로 내린 결정인데 Status를 Accepted로 기록. package.json 교체가 이미 된 것을 '시행됨'으로 판단한 것으로 보임. v4에서 '새로 내리는 결정만 Proposed로 시작한다' 문구를 뺀 영향으로 추정(iteration-4에서는 우연히 Proposed). eval3·5·6·7은 '아직 구현 전'이라는 이유로 Proposed. 규칙 복원 권장: '새로 내리는 결정은 구현 진행 여부와 관계없이 Proposed로 시작한다'.
- v5 eval7 1건 실패: 대화에 기각 사유가 있는데도 '비교한 다른 자체 서빙 옵션(TGI, Ollama 등)이 있으면 기각한 대안과 근거를 알려달라'고 되물음 — 3단계 위반(1회 관찰). assertion 밖으로는 Review Trigger를 처음에 빠뜨렸다가 스스로 추가했고, Reversible: Yes와 Rollback의 '정책이 바뀌지 않는 한 되돌릴 수 없다'가 서로 맞지 않음(Partial이 더 정확).
- 비용: v4는 eval7·8에서 로드 실패로 즉시 끝나 시간·토큰이 적게 나오므로, 평균 시간·토큰 차이는 품질 비교에 의미가 적음.