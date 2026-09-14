결정을 `docs/adr/001-self-host-llm-with-vllm.md`에 ADR로 기록했습니다. 저장소에 `docs/adr/` 폴더도, 기존 ADR도 없어서 001번부터 시작했습니다.

**기록한 내용**
- **결정:** LLM 추론을 OpenAI API(`gpt-4o`)에서 vLLM 자체 서빙으로 전환합니다.
- **이유:** 고객 데이터를 외부로 내보내면 안 됩니다. 지금은 `app/llm_client.py`가 고객 문의 원문을 OpenAI로 보내 요약하고 있어 이 정책과 맞지 않습니다.
- **기각한 대안:** 기존 OpenAI API입니다. 반출 금지 정책을 지킬 수 없어 기각했습니다. 이 정책이 바뀌면 결정을 다시 검토하도록 Review Trigger에 넣었습니다.
- **Status:** 새로 내린 결정이고 코드는 아직 OpenAI를 쓰고 있어서 `Proposed`로 두었습니다.
- **Reversible:** `Partial`로 적었습니다. 코드는 `app/llm_client.py` 한 곳만 되돌리면 되지만, 반출 금지 정책이 유지되는 한 실제로 되돌릴 수는 없기 때문입니다.
- **Implementation 체크리스트:** 모델 선정, vLLM 서버 구축, 클라이언트 전환, 요약 품질 비교, 모니터링, 설정 정리를 넣었습니다. vLLM이 OpenAI 호환 API를 제공하므로 기존 `openai` SDK 코드는 `base_url`과 모델명만 바꿔 쓸 수 있을 것으로 봤습니다.

아직 서빙할 모델이 정해지지 않아 모델명은 "미정"으로 두었습니다. 모델이 정해지면 AI/ML Details에 추가하면 됩니다.
