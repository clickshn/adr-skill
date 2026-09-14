`docs/adr/` 디렉터리가 없어서(기존 ADR 없음) **001번부터** 시작했습니다.

**생성:** `docs/adr/001-self-host-llm-with-vllm.md` — ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed — 새로 내린 결정이라 Proposed로 시작합니다.
- **Decision Source:** Human — 직접 말씀하신 결정이라 Confidence는 넣지 않았습니다.
- **Alternatives:** 대화에 나온 "OpenAI API 유지(현행)"만 넣었습니다. 기각 사유는 "고객 데이터 외부 반출 금지 정책 위배"입니다.
- **Review Trigger:** 고객 데이터 외부 반출 금지 정책이 바뀌거나 완화될 때
- **Reversibility:** Partial — 코드는 쉽게 되돌릴 수 있지만, 정책이 바뀌지 않으면 실제로는 되돌릴 수 없어서 Partial로 적었습니다.
- **Evidence:** 측정 수치가 없어서 섹션을 만들지 않았습니다.

코드에서 확인해 반영한 내용:
- 현재 `app/llm_client.py`의 `summarize()`는 고객 문의 원문을 OpenAI `gpt-4o`로 보냅니다(`openai==1.40.0`). 이 내용을 Context에 적었습니다.
- `OpenAI()`가 `base_url` 없이 생성됩니다. 전환 후에도 `openai` SDK를 그대로 쓰는데 엔드포인트 설정이 빠지면, 요청이 외부 OpenAI로 조용히 나갈 수 있습니다. 이 위험을 Risks에 적었습니다.
- 저장소에 아직 커밋이 없어서 git diff/log로 확인할 수 있는 변경은 없었습니다.

서빙할 모델은 대화에 나오지 않아서 "미정"으로 두었습니다. `app/llm_client.py`와 `requirements.txt`는 수정하지 않았습니다.
