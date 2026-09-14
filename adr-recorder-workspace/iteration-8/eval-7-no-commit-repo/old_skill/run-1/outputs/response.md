ADR로 기록했습니다: `docs/adr/001-self-host-llm-with-vllm.md`

- `docs/adr/` 디렉터리가 없어서 새로 만들고 001번부터 시작했습니다.
- 이 저장소에는 아직 커밋이 없어서 의존성 diff와 커밋 기록을 확인할 수 없었습니다. 그래서 말씀하신 내용과 현재 코드를 바탕으로 작성했습니다.
- **Status:** Proposed입니다. 새로 내린 결정이라서입니다. 결정은 사용자께서 직접 말씀하신 것이므로 **Decision Source:** Human이고, Confidence는 적지 않았습니다.
- **Alternatives:** "OpenAI API 계속 사용"을 적었습니다. 기각 사유는 말씀하신 고객 데이터 외부 반출 금지입니다. Review Trigger는 "외부 반출 금지 정책이 완화되거나 바뀔 때"입니다.
- **Reversibility:** Partial입니다. 코드로는 쉽게 되돌릴 수 있지만, 정책이 바뀌지 않는 한 OpenAI로 돌아갈 수 없기 때문입니다.
- 측정 수치가 없어서 Evidence 섹션은 만들지 않았습니다.

참고할 점:
- 지금 `app/llm_client.py`는 아직 OpenAI(`gpt-4o`)를 호출하고, `requirements.txt`에도 `openai==1.40.0`이 있습니다. 전환을 마치기 전까지는 고객 문의 원문이 계속 외부로 나가므로 이 점을 Risks에 적었습니다. 이 스킬은 `docs/adr/` 밖의 파일을 바꾸지 않아서 코드는 그대로 두었습니다.
- vLLM으로 서빙할 모델은 아직 정해지지 않은 것으로 보고 AI/ML Details에 "미정"으로 적었습니다. 모델이 정해지면 알려주세요. 그 부분을 채우겠습니다.
