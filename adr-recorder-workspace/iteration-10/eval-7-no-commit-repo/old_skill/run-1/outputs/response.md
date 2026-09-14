ADR로 기록했습니다: `docs/adr/001-self-host-llm-with-vllm.md`

- `docs/adr/` 디렉터리가 없어서 새로 만들고 **001번**부터 시작했습니다.
- 저장소에 아직 커밋이 없어 git diff로 확인할 변경분은 없었습니다. 대화에서 말씀하신 결정과 현재 코드(`app/llm_client.py`, `requirements.txt`)를 근거로 작성했습니다.

**요약**
- **Decision:** 고객 데이터 외부 반출 금지 정책에 따라 OpenAI API 대신 vLLM으로 LLM을 자체 서빙
- **Status:** Proposed. 새로 내린 결정이고, 코드는 아직 OpenAI(`gpt-4o`)를 호출하고 있습니다.
- **Alternatives:** OpenAI API 유지(현행). 외부 반출 금지 정책 위배로 기각했습니다.
- **Reversibility:** Partial. 코드는 쉽게 되돌릴 수 있지만, 반출 금지 정책이 바뀌어야만 되돌릴 수 있습니다.
- **Implementation:** vLLM은 OpenAI 호환 API를 제공하므로 `app/llm_client.py`에서 `base_url`과 모델명만 바꿔 `openai` SDK를 그대로 쓰는 방식을 체크리스트에 적었습니다.

**빠진 내용**
- 측정 수치가 없어 Evidence는 비웠습니다. 대화에 재검토 조건이 없어 Review Trigger도 비웠습니다.
- vLLM으로 서빙할 모델이 정해지지 않아 Risks와 AI/ML Details에 "미정"으로 적었습니다.
- `docs/adr/` 밖의 파일은 수정하지 않았습니다.
