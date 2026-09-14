ADR을 만들었습니다.

**`docs/adr/001-vllm-self-hosting.md`**: ADR-001, LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- `docs/adr/` 디렉터리가 없어서 새로 만들고 001번부터 시작했습니다.
- 저장소에 아직 커밋이 없어 의존성 diff는 비어 있었습니다. 대화에서 밝혀주신 결정을 근거로 작성했습니다.
- **Status: Proposed**: 새로 내린 결정이고, `app/llm_client.py`와 `requirements.txt`는 아직 OpenAI(`gpt-4o`, `openai==1.40.0`)를 쓰고 있습니다.
- **Alternatives**: 대화에 나온 현행 유지(OpenAI API)만 넣었고, 기각 사유는 "고객 데이터 외부 반출 금지"입니다. 재검토 조건은 대화에 없어서 Recheck if와 Review Trigger는 넣지 않았습니다.
- **Reversibility: Partial**: 코드는 `base_url`과 모델명만 되돌리면 복귀할 수 있습니다. 하지만 반출 금지 정책이 바뀌어야 실제로 되돌릴 수 있습니다.
- 측정 수치가 없어 Evidence 섹션은 만들지 않았습니다.
- vLLM으로 서빙할 모델은 대화에서 정해지지 않았습니다. AI/ML Details에 미정으로 적어 두었으니 정해지면 채워 넣으시면 됩니다.

`docs/adr/` 밖의 파일(`app/llm_client.py`, `requirements.txt` 등)은 수정하지 않았습니다.
