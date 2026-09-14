vLLM 자체 서빙 결정을 ADR로 남겼습니다.

**생성:** `docs/adr/001-self-host-llm-with-vllm.md` (ADR-001, Status: Proposed)

- `docs/adr/` 디렉터리가 없어서 새로 만들고 번호를 001부터 시작했습니다.
- 저장소에 커밋이 하나도 없어서 의존성 diff는 비교할 수 없었습니다. 그래서 대화에서 말씀하신 결정과 현재 코드를 근거로 작성했습니다. 현재 코드는 `app/llm_client.py`에서 OpenAI `gpt-4o`를 호출하고, `requirements.txt`에 `openai==1.40.0`이 들어 있습니다.

**주요 내용**
- 결정 근거: 고객 데이터 외부 반출 금지. 지금 `summarize()`는 고객 문의 원문을 OpenAI로 보내고 있습니다.
- 기각한 대안: OpenAI API 유지(현행). 반출 금지 정책에 어긋나서 기각했습니다.
- 되돌릴 수 있는지: Partial. 정책이 바뀌어야만 OpenAI로 돌아갈 수 있습니다.
- 대화에 서빙할 모델 얘기가 없어서 "미정"으로 두었습니다. 재검토 조건도 대화에 없어서 Review Trigger 섹션은 만들지 않았습니다.

`docs/adr/` 밖의 파일(`app/llm_client.py`, `requirements.txt`)은 건드리지 않았습니다.
