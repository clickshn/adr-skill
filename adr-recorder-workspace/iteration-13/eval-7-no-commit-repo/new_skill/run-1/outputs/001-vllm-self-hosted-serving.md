# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 고객 문의 요약에 쓰던 OpenAI API를 걷어내고, vLLM으로 자체 인프라에서 LLM을 서빙한다.
- **Scope:** 고객 문의 요약 기능 (`app/llm_client.py`)
- **Decision Source:** Human

---

## Context

### Problem

고객 문의 요약 기능이 OpenAI API(`gpt-4o`)를 직접 호출하고 있다. 요약 대상이 고객 문의 원문이라, 호출할 때마다 고객 데이터가 외부 사업자에게 그대로 전송된다.

### Constraints

- 고객 데이터의 외부 반출이 금지되어 있다.

## Decision

### Selected

- **Technology:** vLLM
- **Architecture:** 외부 LLM API 호출 대신, 자체 인프라에서 운영하는 vLLM 추론 서버를 호출한다. 추론이 내부 경계 안에서 끝난다.
- **Implementation:** `app/llm_client.py`의 OpenAI 클라이언트를 vLLM 서버 클라이언트로 교체하고, `requirements.txt`에서 `openai==1.40.0` 의존성을 제거한다.

## Rationale

1. 고객 데이터 외부 반출 금지 요건을 지키려면 추론이 자체 인프라 안에서 완결되어야 하고, 외부 LLM API 호출은 이 요건과 양립할 수 없다.
2. vLLM으로 자체 서빙하면 고객 문의 원문이 외부 사업자로 전달되지 않는다.

## Alternatives

### OpenAI API (`gpt-4o`) 현행 유지

- **Pros:** 이미 `app/llm_client.py`에 연동되어 동작 중이며, 모델 서빙 인프라를 직접 운영할 필요가 없다.
- **Cons:** 요약 요청마다 고객 문의 원문이 외부 사업자로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 요건에 위배된다.

## Consequences

### Positive

- 고객 문의 원문이 외부로 나가지 않아 데이터 반출 금지 요건을 충족한다.
- 외부 API 사업자에 대한 가용성·요금 정책 의존이 사라진다.

### Negative

- 모델 서빙 인프라(GPU 및 vLLM 서버)를 직접 운영·관리해야 한다.

### Risks

- 자체 서빙 모델의 요약 품질과 응답 지연이 기존 `gpt-4o` 대비 어떻게 달라지는지 아직 측정되지 않았다.
- 서빙 인프라 장애가 곧바로 요약 기능 장애로 이어진다.

## Implementation

- [ ] 구현 작업: vLLM 서버 기동 및 `app/llm_client.py`의 클라이언트 교체, `requirements.txt`에서 `openai` 제거
- [ ] 테스트: 기존 요약 결과와의 비교 검증
- [ ] 모니터링: 추론 지연·오류율·서버 가용성 계측
- [ ] 문서/설정 업데이트: 모델 서빙 엔드포인트 설정값 반영

## Reversibility

- **Reversible:** Partial
- **Rollback:** 코드상으로는 `requirements.txt`에 `openai==1.40.0`을 되돌리고 `app/llm_client.py`를 OpenAI 클라이언트 호출로 복원하면 된다(현재 저장소에 커밋이 없어, 복원 기준점이 될 커밋은 아직 없다). 다만 되돌리려면 고객 데이터 외부 반출 금지라는 외부 요건 자체가 바뀌어야 한다.
- **Migration Cost:** Medium

## AI/ML Details

- **Model:** 미정 — vLLM으로 서빙할 구체 모델은 아직 정해지지 않았다.
- **Inference:** 자체 인프라에서 운영하는 vLLM 추론 서버
