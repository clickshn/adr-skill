결정을 ADR로 기록했습니다.

**생성한 파일:** `docs/adr/001-self-host-llm-with-vllm.md`

- `docs/adr/` 디렉터리가 없어서 **ADR-001**부터 시작했습니다.
- 저장소에 아직 커밋이 없어서 의존성 diff는 비교할 수 없었습니다. 그래서 대화 내용과 현재 코드(`requirements.txt`, `app/llm_client.py`)를 근거로 작성했습니다.

**요약**
- **Status:** Proposed (현재 코드는 여전히 OpenAI `gpt-4o`를 호출하고 있어 아직 적용 전입니다.)
- **Decision:** OpenAI API 대신 vLLM으로 LLM 자체 서빙
- **Decision Source:** Human (말씀하신 결정이라 Confidence는 생략했습니다.)
- **Context:** `app/llm_client.py`가 고객 문의 원문을 OpenAI로 전송하고 있고, 고객 데이터를 외부로 반출하면 안 된다는 제약이 있습니다.
- **Alternatives:** OpenAI API(현행 유지)를 반출 금지 정책 위배로 기각했습니다. Review Trigger는 "반출 금지 정책이 바뀌거나 해제될 때"입니다.
- **Implementation/Reversibility:** vLLM의 OpenAI 호환 서버를 쓰면 `openai` SDK는 그대로 두고 `base_url`과 모델명만 바꿔 전환할 수 있습니다. 그래서 기술적으로는 쉽게 되돌릴 수 있습니다(Migration Cost: Low).
- Evidence 섹션은 실측 수치가 없어서 만들지 않았습니다. References도 연결할 PR, 이슈, 문서가 없어서 만들지 않았습니다.

`docs/adr/` 밖의 파일(`app/llm_client.py`, `requirements.txt` 등)은 수정하지 않았습니다.

vLLM 외에 비교한 자체 서빙 옵션(예: TGI, Ollama 등)이나 서빙할 모델이 정해졌다면, 기각한 대안과 근거를 알려주세요. Alternatives와 AI/ML Details에 반영하겠습니다.
