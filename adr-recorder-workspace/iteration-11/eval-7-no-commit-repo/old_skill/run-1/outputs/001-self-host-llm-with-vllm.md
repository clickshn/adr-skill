# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 LLM 추론 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 고객 데이터 외부 반출 금지 때문에 LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환한다.
- **Scope:** app 서비스의 LLM 호출 계층 (`app/llm_client.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`의 `summarize()`는 고객 문의 원문을 프롬프트에 담아 OpenAI API(`gpt-4o`)로 보낸다. 즉 요청할 때마다 고객 데이터가 외부 서비스로 나간다.

### Constraints

- 고객 데이터 외부 반출 금지

## Decision

### Selected

- **Technology:** vLLM (자체 서빙)
- **Architecture:** 외부 SaaS LLM API 호출을 내부 인프라의 vLLM 추론 서버 호출로 바꾼다.
- **Implementation:** `app/llm_client.py`의 OpenAI 클라이언트 호출 대상을 내부 vLLM 엔드포인트로 교체한다. vLLM은 OpenAI 호환 API를 제공하므로, 현재 쓰는 `openai` SDK는 그대로 두고 `base_url`과 `model`만 바꾸는 방식이 가능하다.

## Rationale

1. 고객 데이터 외부 반출 금지: 추론을 자체 인프라에서 돌리면 고객 문의 텍스트가 외부 서비스로 전송되지 않는다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 이미 `app/llm_client.py`에 구현되어 있어 추가 작업이 없다.
- **Cons:** 요청마다 고객 문의 원문이 외부(OpenAI)로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지

## Consequences

### Positive

- 고객 데이터가 내부 인프라 밖으로 나가지 않는다.
- vLLM의 OpenAI 호환 API 덕분에 애플리케이션 코드는 조금만 바꾸면 된다.

### Negative

- 추론 서버(GPU 인프라)를 직접 구축하고 운영해야 한다.

### Risks

- 서빙할 모델이 아직 정해지지 않았다. 교체한 모델의 요약 품질이 현행 `gpt-4o`보다 떨어질 수 있다.

## Implementation

- [ ] 구현 작업: 내부 vLLM 서버 구축, 서빙 모델 선정, `app/llm_client.py`의 `base_url`/`model` 교체
- [ ] 테스트: `summarize()` 요약 결과 품질 회귀 확인
- [ ] 모니터링: vLLM 서버 가용성, 응답 지연, GPU 사용률
- [ ] 문서/설정 업데이트: vLLM 엔드포인트 설정(환경변수), `requirements.txt`의 의존성 정리

## Reversibility

- **Reversible:** Partial
- **Rollback:** `app/llm_client.py`의 `base_url`/`model`을 OpenAI(`gpt-4o`)로 되돌리면 코드는 원복된다. 다만 고객 데이터 외부 반출 금지 정책이 바뀌지 않는 한 되돌릴 수 없다.
- **Migration Cost:** Low

## AI/ML Details

- **Model:** 현행 `gpt-4o` (OpenAI). 자체 서빙 모델은 미정.
- **Inference:** 내부 vLLM 서버 (OpenAI 호환 API)
