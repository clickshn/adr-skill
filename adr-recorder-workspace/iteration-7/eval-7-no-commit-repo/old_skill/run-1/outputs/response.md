ADR-001을 만들었습니다: `docs/adr/001-self-host-llm-with-vllm.md`

- **번호:** `docs/adr/` 디렉터리가 없어서(기존 ADR 없음) 001번부터 시작했습니다.
- **Status: Proposed.** 새로 내린 결정이라 Proposed로 두었습니다. 참고로 `app/llm_client.py`는 아직 OpenAI `gpt-4o`를 호출하고 있습니다.
- **근거 자료:** 저장소에 커밋이 없어서 git diff와 커밋 이력은 비어 있었습니다. 요청 내용과 `app/llm_client.py`, `requirements.txt`를 근거로 작성했습니다.
- **Alternatives:** 대화에 나온 대안인 OpenAI API(현행)만 정리했습니다. 기각 사유는 "고객 데이터 외부 반출 금지"입니다. Review Trigger는 "해당 정책이 바뀌거나 완화될 때"입니다.
- **Reversibility: Partial.** 코드는 쉽게 되돌릴 수 있지만, 실제로 되돌리려면 반출 금지 정책이 먼저 바뀌어야 합니다.
- **생략한 섹션:** 측정 수치가 없어 Evidence를 뺐고, 참조할 PR·이슈·문서가 없어 References도 뺐습니다.
- **Risks에 적은 내용:**
  - `OpenAI()`를 `base_url` 없이 만들면 기본 엔드포인트가 api.openai.com입니다. 전환할 때 설정이 빠진 경로가 하나라도 남으면 고객 데이터가 계속 외부로 나갈 수 있습니다.
  - 자체 서빙할 모델은 아직 정해지지 않았습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
