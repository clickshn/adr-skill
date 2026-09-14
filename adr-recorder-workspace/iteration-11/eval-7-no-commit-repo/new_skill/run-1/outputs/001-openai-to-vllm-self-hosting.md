# ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 고객 데이터 외부 반출 금지 때문에 OpenAI API 대신 vLLM으로 LLM을 자체 서빙한다.
- **Scope:** LLM 추론 계층 (app/llm_client.py의 고객 문의 요약 기능)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`의 `summarize()`는 OpenAI SDK(`openai==1.40.0`)로 `gpt-4o`를 호출하며, 고객 문의 원문을 프롬프트에 그대로 담아 외부(OpenAI) API로 전송한다. 즉 고객 데이터가 매 요청마다 회사 밖으로 나간다.

### Constraints

- 고객 데이터의 외부 반출이 금지되어 있다. 고객 데이터를 다루는 LLM 추론은 외부 API가 아니라 자체 인프라 안에서 처리해야 한다.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 서빙)
- **Architecture:** 외부 SaaS LLM API 호출 대신, 자체 인프라에 vLLM 추론 서버를 두고 애플리케이션이 이 서버를 호출한다.
- **Implementation:** `app/llm_client.py`의 OpenAI 클라이언트 호출을 자체 vLLM 서버 호출로 교체한다. 현재 저장소 코드는 아직 OpenAI(`gpt-4o`)를 호출하고 있다.

## Rationale

1. 고객 데이터 외부 반출 금지 정책을 지키려면 고객 문의 원문이 외부 API로 전송되지 않아야 하며, 자체 서빙은 데이터를 내부 인프라 안에 둔다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 이미 `app/llm_client.py`에 구현되어 동작 중인 방식이라 추가 작업이 없다.
- **Cons:** 고객 문의 원문이 외부(OpenAI)로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 정책에 위배된다.

## Consequences

### Positive

- 고객 문의 데이터가 외부 API로 전송되지 않아 반출 금지 정책을 준수할 수 있다.

### Negative

- 추론 서버(vLLM)와 그 실행 인프라를 직접 운영해야 한다.

### Risks

- vLLM에 올릴 모델이 아직 정해지지 않았으며, 기존 `gpt-4o` 대비 요약 품질이 달라질 수 있다.

## Implementation

- [ ] vLLM 추론 서버 구축 및 서빙 모델 선정
- [ ] `app/llm_client.py`의 OpenAI 호출(`OpenAI()`, `model="gpt-4o"`)을 vLLM 서버 호출로 교체
- [ ] 요약 결과 품질 및 고객 데이터가 외부로 나가지 않는지 테스트
- [ ] vLLM 서버 상태·지연시간 모니터링
- [ ] `requirements.txt`(`openai==1.40.0`) 및 접속 설정 업데이트

## Reversibility

- **Reversible:** Partial
- **Rollback:** 코드상으로는 `app/llm_client.py`를 OpenAI 클라이언트 호출로 되돌리면 되지만, 고객 데이터 외부 반출 금지 정책이 바뀌지 않는 한 OpenAI로 되돌릴 수 없다.
- **Migration Cost:** Medium

## AI/ML Details

- **Model:** 기존 `gpt-4o`(OpenAI) → vLLM 서빙 모델 (미정)
- **Inference:** 외부 OpenAI API 호출 → 자체 인프라 vLLM 서버
