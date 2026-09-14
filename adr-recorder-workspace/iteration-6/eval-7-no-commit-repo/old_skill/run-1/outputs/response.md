ADR로 기록했습니다. `docs/adr/`에 기존 ADR이 없어서 **001번**부터 시작했습니다. 디렉터리도 새로 만들었습니다.

**생성 파일:** `docs/adr/001-vllm-self-hosting.md`, "ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환"

**기록한 내용**
- **Context:** 지금 `app/llm_client.py`의 `summarize()`는 고객 문의 원문을 그대로 OpenAI `gpt-4o`에 보냅니다. 고객 데이터 외부 반출 금지 요건과 충돌합니다.
- **Decision:** vLLM으로 자체 서빙합니다. vLLM은 OpenAI 호환 API를 제공하므로, 기존 `openai` SDK에서 `base_url`과 `model`만 바꾸면 코드 변경이 작습니다.
- **Alternatives:** 현행 OpenAI API를 대안으로 두고, 말씀하신 반출 금지를 기각 사유로 적었습니다. Review Trigger는 "반출 금지 정책이 바뀌는 경우"입니다.
- **Consequences / Implementation / Reversibility:** 모델 선정, 추론 서버 운영 부담, 요약 품질 저하 위험, 모니터링 항목을 넣었습니다. 롤백은 코드상으로는 쉽지만(Low), 반출 금지 요건이 유지되는 한 실제로는 되돌릴 수 없다고 적었습니다.
- 사용자가 직접 내린 결정이라 Decision Source는 Human이고, 그래서 Confidence는 넣지 않았습니다. 측정 수치가 없어서 Evidence 섹션도 뺐습니다.
- Status는 템플릿 기본값인 **Proposed**입니다. 이미 확정된 결정이면 Accepted로 바꿔 드리겠습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다. `requirements.txt`와 `app/llm_client.py`도 그대로입니다.

ADR을 채우려면 두 가지가 더 필요합니다.
1. vLLM으로 **서빙할 모델**은 무엇인가요? 정해지면 AI/ML Details의 Model 항목에 넣겠습니다.
2. OpenAI 말고 검토했다가 기각한 대안이 있었나요? 예를 들어 Ollama나 TGI 같은 다른 자체 서빙 도구, 또는 데이터가 외부로 나가지 않는 전용 클라우드 배포가 있었다면 **기각 사유**를 알려주세요.
