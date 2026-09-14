# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 고객 문의 요약용 LLM 추론을 OpenAI API 호출에서 vLLM 기반 자체 서빙으로 전환한다.
- **Scope:** 고객 문의 요약 서비스 (FastAPI 앱, `app/llm_client.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 고객 문의 요약 기능은 `app/llm_client.py`에서 OpenAI 클라이언트로 `gpt-4o`를 호출한다.
요약 대상이 고객이 보낸 문의 원문이므로, 매 호출마다 고객 데이터가 외부 API로 전송된다.

### Constraints

- 고객 데이터의 외부 반출이 금지되어 있어, 추론 요청 본문이 외부 사업자에게 전달되는 구조를 유지할 수 없다.
- 요약 기능 자체는 계속 제공해야 하므로 LLM 추론을 없애는 선택지는 없다.

## Decision

### Selected

- **Technology:** vLLM으로 오픈 모델을 자체 호스팅하여 추론을 처리한다.
- **Architecture:** 외부 OpenAI API 의존을 제거하고, 통제된 자체 인프라 안의 vLLM 추론 서버를 앱이 호출하는 구조로 바꾼다.
- **Implementation:** `app/llm_client.py`의 OpenAI 클라이언트 호출을 vLLM 서버 호출로 교체하고, `requirements.txt`의 `openai==1.40.0` 의존성을 정리한다.

## Rationale

1. 고객 데이터 외부 반출 금지 요건을 만족하려면 추론 데이터가 자체 인프라 경계를 벗어나지 않아야 한다.
2. vLLM으로 자체 서빙하면 요약 기능을 유지하면서 데이터 전송 경로를 내부로 한정할 수 있다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 이미 동작 중이며 추가 인프라 운영 부담이 없다.
- **Cons:** 요약 요청 본문(고객 문의 원문)이 외부 사업자로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 정책에 위배된다.

## Consequences

### Positive

- 고객 문의 데이터가 자체 인프라 밖으로 나가지 않는다.
- 외부 API 사업자의 가용성·요금 정책 변화에 대한 의존이 사라진다.

### Negative

- 추론 서버(GPU 포함) 운영·모니터링 책임을 직접 떠안게 된다.
- 모델 선택·업데이트를 자체적으로 관리해야 한다.

### Risks

- 자체 서빙 모델의 요약 품질이 `gpt-4o` 대비 어느 정도인지 아직 측정되지 않았다.
- 자체 추론 서버의 용량 부족 시 요약 지연 또는 실패가 발생할 수 있다.

## Implementation

- [ ] vLLM 서빙 환경 구성 및 사용할 오픈 모델 확정
- [ ] `app/llm_client.py`의 OpenAI 호출을 vLLM 클라이언트 호출로 교체
- [ ] `requirements.txt`에서 `openai` 제거 및 필요한 의존성 반영
- [ ] 요약 품질 비교 테스트 (기존 `gpt-4o` 결과 대비)
- [ ] 추론 서버 가용성·지연 모니터링
- [ ] 배포/운영 문서 및 설정 업데이트

## Reversibility

- **Reversible:** Partial
- **Rollback:** 코드 수준으로는 `app/llm_client.py`의 OpenAI 호출 코드와 `requirements.txt`의 `openai==1.40.0`을 되돌리면 복구되지만, 실제로 되돌리려면 고객 데이터 외부 반출 금지 정책이 먼저 바뀌어야 한다. (현재 저장소에는 커밋이 없어 복원 기준이 될 커밋 해시가 없다.)
- **Migration Cost:** Medium

## References

- **Documentation:** `app/llm_client.py` (현행 OpenAI 호출 지점), `requirements.txt`

## AI/ML Details

- **Model:** 미정 — vLLM으로 서빙할 오픈 모델은 아직 확정되지 않음 (현행: `gpt-4o`)
- **Inference:** 자체 인프라 내 vLLM 추론 서버
