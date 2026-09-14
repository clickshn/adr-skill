`docs/adr/001-self-hosted-vllm-instead-of-openai.md`를 새로 만들었습니다.

- **번호:** `docs/adr/` 디렉터리 자체가 없어서(기존 ADR 0건) 질문 없이 001로 시작했습니다.
- **Status:** 새로 내리는 결정이라 Proposed로 뒀습니다(코드 반영 여부와 무관).
- **Decision Source:** Human(사용자가 직접 내린 결정)이라 Confidence 필드는 생략했습니다.
- **근거 수집:** 이 저장소에는 아직 커밋이 없어서(`git diff HEAD` 실패, `git log` 비어 있음) 의존성 diff를 쓸 수 없었습니다. 대신 현재 작업 트리 상태 — `requirements.txt`의 `openai==1.40.0`, `app/llm_client.py`의 `gpt-4o` 호출로 고객 문의 원문을 요약하는 코드 — 를 Context 근거로 삼았습니다.
- **Alternatives:** 대화에 나온 대안은 "OpenAI 유지(현행)" 하나이고 기각 사유(고객 데이터 외부 반출 금지)가 명시돼 있어 추가로 되묻지 않았습니다. 재검토 조건은 대화에 없어서 Recheck if 줄과 Review Trigger 섹션은 만들지 않았습니다(기각 사유를 뒤집은 조건은 지어낸 것으로 취급).
- **Evidence:** 벤치마크·비용 같은 실측 수치가 없어 섹션을 만들지 않고, 정성적 배경은 Context에 넣었습니다.
- **Reversibility:** 코드 롤백 자체는 작지만 되돌리려면 고객 데이터 반출 금지 정책이 바뀌어야 하므로 Yes가 아니라 Partial로 적었습니다. 또 커밋이 없어 복원 기준 커밋이 없다는 점도 적어뒀습니다.
- **미정 사항:** vLLM에 올릴 오픈 웨이트 모델이 아직 정해지지 않아 AI/ML Details의 Model에 미정으로 표시하고 Risks에도 남겼습니다.

이 스킬은 `docs/adr/` 안의 파일만 만들고 고치므로 `app/llm_client.py`와 `requirements.txt`는 건드리지 않았습니다. 실제 코드 전환(엔드포인트·모델명 교체, 의존성 정리)도 진행할까요?
