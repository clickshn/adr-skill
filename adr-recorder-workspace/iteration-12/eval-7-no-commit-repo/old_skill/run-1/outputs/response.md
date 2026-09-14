ADR을 새로 기록했습니다.

**생성한 파일:** `docs/adr/001-self-hosted-llm-serving-with-vllm.md`

- `docs/adr/` 디렉터리 자체가 없어서 기존 ADR이 하나도 없는 상태였습니다. 그래서 질문 없이 **001번**으로 시작했습니다.
- 이 저장소는 아직 커밋이 없어(HEAD 없음) 의존성 diff와 커밋 기록에서는 근거를 얻지 못했고, 현재 작업 트리의 `app/llm_client.py`와 `requirements.txt`(`openai==1.40.0`, `gpt-4o` 호출)를 배경 근거로 사용했습니다.

기록한 내용 요약:

- **Status:** Proposed — 새로 내리는 결정이라 코드 상태와 무관하게 Proposed로 시작했습니다.
- **Decision Source:** Human (직접 말씀하신 결정이라 Confidence 필드는 생략).
- **Alternatives:** 대화에 등장한 "OpenAI API 유지(현행)" 하나만 정리했고, 기각 사유는 말씀하신 "고객 데이터 외부 반출 금지"를 그대로 썼습니다. 재검토 조건은 언급이 없어 지어내지 않고 비워뒀습니다(그래서 Review Trigger 섹션도 만들지 않았습니다).
- **Evidence:** 실측 수치가 없어 섹션을 만들지 않았고, 정성적 관찰은 Context에 넣었습니다.
- **Reversibility:** Partial — 코드 롤백 자체는 쉽지만, 반출 금지 정책이 바뀌지 않는 한 실제로는 되돌릴 수 없어서 Yes가 아닌 Partial로 표기했습니다.

`app/llm_client.py`와 `requirements.txt`는 손대지 않았습니다. 이 스킬은 `docs/adr/` 안의 파일만 만들고 수정합니다. 실제 전환 작업(엔드포인트 변경, 의존성 정리)도 필요하시면 말씀해 주세요.

참고로 서빙할 모델과 배포 형상은 대화에 없어서 "미정"으로 적어두었습니다. 정해지면 AI/ML Details 쪽을 채워 넣겠습니다.
