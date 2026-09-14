vLLM 자체 서빙 결정을 ADR로 기록했습니다.

**생성한 파일:** `docs/adr/001-self-host-llm-with-vllm.md`

- `docs/adr/` 디렉터리가 없어서 새로 만들고 **ADR-001**로 시작했습니다.
- 이 저장소에는 아직 커밋이 없어서 git diff로 변경 이력을 볼 수 없었습니다. 그래서 말씀하신 내용과 현재 작업 트리(`app/llm_client.py`, `requirements.txt`)를 근거로 작성했습니다.

**핵심 내용**
- **Status: Proposed.** 새로 내린 결정이고, 코드는 아직 OpenAI를 호출하고 있습니다(`app/llm_client.py`에서 `OpenAI()`로 `gpt-4o` 호출, `requirements.txt`에 `openai==1.40.0`).
- **Decision Source: Human.** 직접 말씀하신 결정이라 Confidence 필드는 넣지 않았습니다.
- **Constraints / Rationale:** 고객 데이터 외부 반출 금지. 지금은 고객 문의 원문을 OpenAI로 보내 요약하고 있습니다.
- **Alternatives:** 대화에 나온 "OpenAI API 유지(현행)"만 적었습니다. 기각 사유는 반출 금지 요건 위반이고, 반출 금지 정책이 풀리거나 완화되면 다시 검토하도록 Review Trigger에 남겼습니다.
- **Reversibility: Partial.** 코드는 쉽게 되돌릴 수 있지만, 반출 금지 정책이 바뀌지 않는 한 실제로 되돌릴 수는 없습니다.
- **Evidence:** 측정 수치가 없어서 섹션을 만들지 않았습니다. vLLM으로 서빙할 모델은 대화에서 정해지지 않아 "미정"으로 적었습니다.

`docs/adr/` 밖의 파일(코드, `requirements.txt` 등)은 수정하지 않았습니다.
