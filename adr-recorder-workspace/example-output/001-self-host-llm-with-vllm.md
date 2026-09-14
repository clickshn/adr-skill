# ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** LLM 추론을 OpenAI API 호출 대신 자체 인프라의 vLLM 서빙으로 전환한다.
- **Scope:** LLM 추론 서빙 (기존 OpenAI API 호출 구간)
- **Decision Source:** Human

---

## Context

### Problem

지금은 LLM 추론에 OpenAI API를 호출하고 있어, 추론할 때마다 고객 데이터가 외부 서비스로 전송된다. 고객 데이터 외부 반출이 금지되어 있어 이 방식을 유지할 수 없다.

### Constraints

- 고객 데이터는 외부로 반출할 수 없다.

## Decision

### Selected

- **Technology:** vLLM (자체 서빙)
- **Architecture:** 외부 API 대신 자체 인프라에서 vLLM 추론 서버를 운영하고, 애플리케이션은 이 서버로 추론 요청을 보낸다.

## Rationale

1. 고객 데이터를 외부 서비스로 보내지 않고 추론할 수 있어 외부 반출 금지 조건을 지킬 수 있다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 모델 서빙 인프라를 직접 운영하지 않아도 된다.
- **Cons:** 추론할 때 고객 데이터가 외부 서비스로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 조건을 지킬 수 없다.
- **Recheck if:** 고객 데이터 외부 반출 금지 조건이 바뀌어 외부 API 사용이 허용될 때

## Consequences

### Positive

- 고객 데이터가 외부 서비스로 나가지 않는다.

### Negative

- GPU 서버와 vLLM 서빙 환경을 직접 운영해야 한다.
- 서빙할 모델을 직접 고르고 업데이트해야 한다.

### Risks

- 서빙할 모델이 아직 정해지지 않아, 기존 OpenAI 모델 대비 응답 품질 차이를 평가하지 못했다.
- 추론 용량이 부족하면 응답 지연이 늘어날 수 있다.

## Implementation

- [ ] vLLM 서빙 환경 구성과 서빙할 모델 선정
- [ ] 애플리케이션의 OpenAI API 호출을 자체 vLLM 엔드포인트로 전환
- [ ] 테스트: 기존 OpenAI 응답 대비 품질·지연 비교
- [ ] 모니터링: 추론 지연, GPU 사용률, 오류율
- [ ] 문서/설정 업데이트: 추론 엔드포인트 설정, 고객 데이터가 외부로 나가지 않는다는 점을 보안 문서에 반영

## Reversibility

- **Reversible:** Partial
- **Rollback:** 애플리케이션의 추론 요청 대상을 다시 OpenAI API로 바꾸면 기술적으로는 되돌릴 수 있다. 다만 고객 데이터 외부 반출 금지 조건이 유지되는 한 되돌릴 수 없다.

## Review Trigger

- 고객 데이터 외부 반출 금지 조건이 바뀌어 외부 API 사용이 허용되면 OpenAI API 사용을 다시 검토한다.

## AI/ML Details

- **Inference:** 자체 인프라에서 vLLM으로 서빙 (기존: OpenAI API)
