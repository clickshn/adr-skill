이 결정을 ADR로 기록했습니다: `docs/adr/001-self-host-llm-with-vllm.md`

- `docs/adr/` 디렉터리가 없어서 새로 만들고 번호는 **001**부터 시작했습니다.
- 저장소에 아직 커밋이 없어서 의존성 diff와 커밋 기록은 비어 있습니다. 대화에서 말씀하신 결정과 현재 코드(`app/llm_client.py`, `requirements.txt`)를 바탕으로 작성했습니다.

**요약**
- **Status:** Proposed (새 결정이고 코드는 아직 OpenAI(`gpt-4o`)를 호출하고 있습니다)
- **Decision:** LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환
- **근거:** 고객 데이터 외부 반출 금지. 지금 `summarize()`는 고객 문의 원문을 OpenAI로 보냅니다.
- **Alternatives:** OpenAI API 유지(현행). 고객 데이터 외부 반출 금지 때문에 기각했습니다.
- **Reversibility:** Partial. 코드는 `base_url`/`model`만 되돌리면 되지만, 정책이 바뀌어야 되돌릴 수 있습니다.
- **Implementation:** vLLM은 OpenAI 호환 API를 제공하므로 `openai` SDK는 그대로 두고 `base_url`과 `model`만 바꾸는 방식을 체크리스트에 적었습니다.

말씀에 없던 재검토 조건과 측정 수치는 추측해서 넣지 않았습니다. 그래서 Review Trigger와 Evidence 섹션은 없습니다. 서빙할 모델이 아직 정해지지 않은 점은 Risks와 AI/ML Details에 적어 두었습니다.
