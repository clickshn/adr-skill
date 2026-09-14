# ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 정책에 따라 OpenAI API 대신 vLLM으로 LLM을 자체 서빙한다.
- **Scope:** LLM 추론 계층 (`app/llm_client.py`의 고객 문의 요약 기능)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`는 `openai` SDK(`openai==1.40.0`)로 OpenAI API의 `gpt-4o` 모델을 호출한다. 이때 고객 문의 원문을 프롬프트에 그대로 넣어 외부로 전송한다. 즉 고객 데이터가 회사 밖 서비스로 나간다.

### Constraints

- 고객 데이터를 외부로 반출해서는 안 된다.
- 기존 코드는 OpenAI Chat Completions 인터페이스(`client.chat.completions.create`)에 맞춰 작성돼 있다.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 추론 서버)
- **Architecture:** 외부 SaaS LLM API 호출을 내부 인프라에서 운영하는 vLLM 추론 서버 호출로 바꾼다. 고객 데이터는 내부 네트워크 밖으로 나가지 않는다.
- **Implementation:** vLLM이 제공하는 OpenAI 호환 API 서버를 쓰면 `openai` SDK를 그대로 두고 `OpenAI(base_url=...)`와 모델명만 바꿔 전환할 수 있다.

## Rationale

1. 고객 데이터 외부 반출 금지 정책을 지키려면 추론이 내부 인프라 안에서 이뤄져야 한다.

## Alternatives

### OpenAI API (현행 유지)

- **Pros:** 이미 `app/llm_client.py`에 연동돼 있어 추가 작업이 없다. `gpt-4o`를 쓸 수 있고 추론 인프라를 직접 운영하지 않아도 된다.
- **Cons:** 고객 문의 원문이 외부 서비스로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 정책에 위배된다.
- **Recheck if:** 고객 데이터 외부 반출 금지 정책이 바뀌거나 해제될 때

## Consequences

### Positive

- 고객 데이터가 외부 LLM 제공자에게 전송되지 않는다.
- OpenAI 호환 API를 쓰면 애플리케이션 코드 변경이 작다.

### Negative

- GPU 서버 등 추론 인프라를 직접 준비하고 운영해야 한다.
- 모델 선정, 업데이트, 용량 관리를 팀이 직접 맡아야 한다.

### Risks

- 자체 서빙할 오픈 모델의 요약 품질이 기존 `gpt-4o`보다 낮을 수 있다.
- vLLM 서버가 내부 단일 장애 지점이 될 수 있다.

## Implementation

- [ ] vLLM 추론 서버 구축과 서빙할 모델 선정
- [ ] `app/llm_client.py`의 `OpenAI()` 클라이언트에 내부 vLLM 엔드포인트(`base_url`)를 지정하고 `model="gpt-4o"`를 자체 서빙 모델명으로 교체
- [ ] 고객 문의 요약 품질 회귀 테스트 (기존 `gpt-4o` 결과와 비교)
- [ ] vLLM 서버 가용성·지연시간·GPU 사용률 모니터링
- [ ] 외부 OpenAI API 키·설정 제거, 엔드포인트 설정 문서화

## Reversibility

- **Reversible:** Yes
- **Rollback:** `openai` SDK를 유지하면 `app/llm_client.py`의 `base_url`과 모델명을 원래 OpenAI 설정으로 되돌리면 된다. 단, 고객 데이터 반출 금지 정책이 바뀌지 않는 한 되돌릴 수 없다.
- **Migration Cost:** Low

## Review Trigger

- 고객 데이터 외부 반출 금지 정책이 바뀌거나 해제될 때 (OpenAI API 재검토)

## AI/ML Details

- **Inference:** vLLM 자체 서빙 (OpenAI 호환 API 엔드포인트, 내부망)
