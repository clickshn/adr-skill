# ADR-001: LLM 호출을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 정책에 따라 OpenAI API 대신 vLLM으로 LLM을 자체 서빙한다.
- **Scope:** app/llm_client.py (고객 문의 요약 LLM 호출)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`의 `summarize()`는 고객 문의 원문을 OpenAI API(`gpt-4o`)로 보내 요약한다. 즉 고객 데이터가 외부 서비스로 전송된다.

### Constraints

- 고객 데이터 외부 반출 금지.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 서빙)
- **Architecture:** 외부 SaaS LLM API 호출 → 내부 인프라에서 운영하는 vLLM 서빙 엔드포인트 호출
- **Implementation:** `app/llm_client.py`의 LLM 호출 대상을 OpenAI API에서 자체 vLLM 엔드포인트로 교체

## Rationale

1. 고객 데이터 외부 반출 금지 정책을 지키려면 추론이 내부 인프라 안에서 이루어져야 하며, 자체 서빙은 고객 데이터가 외부로 나가지 않게 한다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 현재 코드(`app/llm_client.py`, `openai==1.40.0`)가 이미 사용 중이라 추가 작업이 없다.
- **Cons:** 고객 문의 원문이 외부(OpenAI)로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 정책에 위배된다.

## Consequences

### Positive

- 고객 데이터가 내부 인프라를 벗어나지 않아 외부 반출 금지 정책을 지킬 수 있다.

### Negative

- 모델 서빙 인프라(GPU 서버, 배포, 운영)를 직접 책임져야 한다.

### Risks

- 서빙할 모델이 아직 정해지지 않았다. `gpt-4o`를 대체하는 모델로 요약 품질이 달라질 수 있다.

## Implementation

- [ ] vLLM 서빙 환경 구축 및 서빙 모델 선정
- [ ] `app/llm_client.py`의 `OpenAI()` 클라이언트와 `model="gpt-4o"`를 vLLM 엔드포인트와 서빙 모델로 교체 (vLLM은 OpenAI 호환 API를 제공하므로 `openai` SDK를 `base_url` 변경으로 재사용할 수 있다)
- [ ] 테스트: 교체 후 `summarize()` 요약 결과 확인
- [ ] 모니터링: vLLM 서버 가용성과 응답 지연 모니터링
- [ ] 문서/설정 업데이트: `requirements.txt`의 `openai` 의존성 유지 여부 정리, 엔드포인트 설정 추가

## Reversibility

- **Reversible:** Partial
- **Rollback:** `app/llm_client.py`의 클라이언트 설정을 OpenAI API로 되돌리면 코드상 복귀는 가능하다. 다만 고객 데이터 외부 반출 금지 정책이 바뀌지 않는 한 되돌릴 수 없다.
- **Migration Cost:** Low

## AI/ML Details

- **Model:** 현재 `gpt-4o` (OpenAI). vLLM으로 서빙할 모델은 미정.
- **Inference:** 외부 API 추론 → vLLM 자체 호스팅 추론
