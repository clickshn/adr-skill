ADR-001을 생성했습니다.

- 파일: `docs/adr/001-openai-to-vllm-self-hosting.md`
- 제목: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환
- Status: **Proposed** — 새로 내리는 결정이고, 현재 `app/llm_client.py`는 아직 OpenAI(`gpt-4o`)를 호출하고 있습니다.

참고 사항:

- `docs/adr/` 디렉터리가 없어서 번호를 **001**부터 시작했습니다.
- 이 저장소에는 아직 커밋이 없어서 의존성 diff나 커밋 기록을 참고할 수 없었습니다. 그래서 말씀하신 결정 내용과 현재 코드(`app/llm_client.py`, `requirements.txt`)를 기준으로 작성했습니다.
- 대안에는 대화에서 나온 **OpenAI API 유지(현행)** 하나만 넣었고, 기각 사유는 "고객 데이터 외부 반출 금지 위배"로 적었습니다. 재검토 조건은 말씀하신 게 없어서 Recheck if와 Review Trigger는 뺐습니다.
- Reversibility는 **Partial**로 표기했습니다. 코드는 쉽게 되돌릴 수 있지만, 반출 금지 정책이 바뀌지 않는 한 OpenAI로 돌아갈 수 없기 때문입니다.
- vLLM에 올릴 모델은 아직 정해지지 않았다고 보고 AI/ML Details에 "미정"으로 적었습니다. 측정 수치가 없어서 Evidence 섹션과 평가 표는 넣지 않았습니다.
- `docs/adr/` 밖의 파일(코드, `requirements.txt` 등)은 수정하지 않았습니다.
