`docs/adr/` 디렉터리가 아직 없어서 기존 ADR 없이 **001번**으로 시작했습니다.

**생성한 파일:** `docs/adr/001-vllm-self-hosted-serving.md`

주요 내용은 이렇게 정리했습니다.

- **Status: Proposed** — 새로 내리는 결정이라 Proposed로 시작했습니다.
- **Decision Source: Human** — 직접 말씀하신 결정이라 Confidence 필드는 생략했습니다.
- **Context** — `app/llm_client.py`가 `gpt-4o`로 고객 문의 원문을 요약 요청하고 있어, 호출할 때마다 고객 데이터가 외부로 나간다는 점을 문제로 적었습니다. 제약은 "고객 데이터 외부 반출 금지"입니다.
- **Alternatives** — 말씀하신 대안(OpenAI API 현행 유지)과 기각 사유가 명확해서 추가로 여쭙지 않았습니다.
- **Reversibility: Partial** — 코드는 `requirements.txt`의 `openai==1.40.0`과 `app/llm_client.py`를 되돌리면 되지만, 실제로 되돌리려면 외부 반출 금지 요건 자체가 바뀌어야 해서 Yes가 아닌 Partial로 표기했습니다. 아직 저장소에 커밋이 없어 복원 기준 커밋은 인용하지 않았습니다.
- **Evidence 섹션은 생략**했습니다 — 측정 수치가 없어서, 품질·지연 비교가 아직 검증되지 않았다는 점은 Consequences의 Risks에 적어뒀습니다.
- **Review Trigger 섹션도 생략**했습니다 — 대화에 명시된 재검토 조건이 없어서 Recheck if를 지어내지 않았습니다.
- **AI/ML Details** — 서빙할 구체 모델은 정해진 게 없어 "미정"으로 남겨뒀습니다.

두 가지만 확인 부탁드립니다.

1. vLLM으로 서빙할 모델이 정해지면 알려주세요. AI/ML Details의 Model을 채우겠습니다.
2. 재검토 조건(예: 어떤 상황이면 외부 API를 다시 검토할지)이 있으면 말씀해 주세요. 그때 Alternatives의 Recheck if와 Review Trigger를 추가하겠습니다.

파일 생성만 했고 커밋은 하지 않았습니다.
