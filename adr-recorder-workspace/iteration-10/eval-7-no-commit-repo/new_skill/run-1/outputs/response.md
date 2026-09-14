ADR-001을 만들었어요: `docs/adr/001-self-host-llm-with-vllm.md`

`docs/adr/` 디렉터리가 없어서 새로 만들고 **001번부터** 시작했어요.

**기록한 내용**
- **Status:** Proposed (새로 내린 결정이라 이 상태로 시작해요)
- **Decision:** 고객 데이터 외부 반출 금지 때문에 OpenAI API(`gpt-4o`) 대신 vLLM으로 자체 서빙
- **Context:** `app/llm_client.py`의 `summarize()`가 고객 문의 원문을 그대로 OpenAI로 보내고 있어요. 이게 제약을 어기는 부분이라 문제로 적었어요.
- **Alternatives:** OpenAI API 계속 사용(현행 유지). 기각 사유는 말씀하신 고객 데이터 외부 반출 금지를 그대로 썼어요. 재검토 조건은 대화에 나오지 않아서 Recheck if와 Review Trigger는 넣지 않았어요.
- **Reversibility:** Partial. 코드는 쉽게 되돌릴 수 있지만, 반출 금지 정책이 바뀌어야만 OpenAI로 돌아갈 수 있어서요.
- **AI/ML Details:** vLLM으로는 `gpt-4o`를 서빙할 수 없어서 대체 오픈 웨이트 모델이 필요해요. 아직 정해지지 않아 "미정"으로 적었어요.
- 측정 수치가 없어서 Evidence는 넣지 않았어요. 관련 PR·이슈·커밋이 없어서 References도 뺐어요.

**참고**
- 이 저장소는 아직 커밋이 하나도 없어서 git diff와 git log로 변경 내역을 볼 수 없었어요. 그래서 대화 내용과 현재 파일(`requirements.txt`, `app/llm_client.py`)만 보고 작성했어요.
- `docs/adr/` 밖의 파일은 건드리지 않았어요. `app/llm_client.py`와 `requirements.txt`(`openai==1.40.0`)는 그대로예요. vLLM이 OpenAI 호환 API를 제공해서 기존 `openai` SDK에서 `base_url`만 바꾸는 방법도 있어요. 이 선택지는 ADR의 Implementation 항목에 적어 뒀어요.
