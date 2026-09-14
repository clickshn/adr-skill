ADR을 새로 기록했습니다: `docs/adr/001-vllm-self-hosted-serving.md`

저장소에 `docs/adr/` 디렉터리 자체가 없어서(기존 ADR 없음) 질문 없이 **001번**으로 시작했습니다.

작성 내용 요약:

- **Decision:** 고객 문의 요약용 LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환
- **Status:** Proposed — 새로 내리는 결정이라 코드 변경 여부와 무관하게 Proposed로 시작했습니다.
- **Context:** `app/llm_client.py`가 `gpt-4o`로 고객 문의 원문을 요약하고 있어 매 호출마다 고객 데이터가 외부로 전송되는 점, 그리고 외부 반출 금지 제약을 적었습니다.
- **Alternatives:** 대화에 나온 대안인 "OpenAI API 유지(현행)"만 정리하고, 기각 사유는 말씀하신 그대로 고객 데이터 외부 반출 금지로 적었습니다. 재검토 조건은 언급이 없어 `Recheck if` 줄과 Review Trigger 섹션은 만들지 않았습니다.
- **Reversibility:** 코드는 되돌릴 수 있지만 실제 복귀는 외부 반출 금지 정책이 바뀌어야 가능하므로 `Partial`로 표기했습니다. 아직 커밋이 하나도 없는 저장소라 롤백 기준 커밋 해시는 인용하지 않았습니다.
- 측정된 수치가 없어 Evidence 섹션은 만들지 않았고, 품질 비교는 Implementation 체크리스트와 Risks에 넣었습니다.
- **AI/ML Details:** vLLM으로 서빙할 오픈 모델이 아직 정해지지 않아 `Model`은 "미정"으로 남겨두었습니다. 모델이 확정되면 알려주시면 채워 넣겠습니다.

`docs/adr/` 밖의 파일(`requirements.txt`, `app/llm_client.py`)은 건드리지 않았고, 커밋도 만들지 않았습니다.
