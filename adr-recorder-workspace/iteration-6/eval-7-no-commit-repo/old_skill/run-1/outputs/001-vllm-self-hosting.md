# ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 요건에 따라 OpenAI API 대신 vLLM으로 LLM을 자체 서빙한다.
- **Scope:** FastAPI 앱의 LLM 호출 계층 (`app/llm_client.py`, 고객 문의 요약 기능)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`의 `summarize()`는 고객 문의 원문을 프롬프트에 그대로 담아 OpenAI API(`gpt-4o`)로 전송한다. 즉 고객 데이터가 외부 서비스로 반출되는 구조다.

### Constraints

- 고객 데이터의 외부 반출이 금지되어 있다. LLM 추론은 데이터가 외부로 나가지 않는 환경에서 수행되어야 한다.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 추론 서버)
- **Architecture:** 외부 SaaS LLM API 호출을 없애고, 자체 인프라에서 운영하는 vLLM 서버로 추론 요청을 보낸다.
- **Implementation:** `app/llm_client.py`의 OpenAI 클라이언트 호출을 vLLM 엔드포인트 호출로 교체한다. vLLM은 OpenAI 호환 API 서버를 제공하므로 기존 `openai` SDK에 `base_url`만 바꿔 쓰는 방식으로 변경 범위를 줄일 수 있다.

## Rationale

1. 고객 데이터 외부 반출 금지 요건 때문에, 고객 문의 원문을 외부 API로 보내는 현재 구조를 유지할 수 없다. 자체 서빙하면 추론 데이터가 내부 경계를 벗어나지 않는다.

## Alternatives

### OpenAI API (현행 유지)

- **Pros:** 이미 `app/llm_client.py`에서 `gpt-4o`로 동작 중이며, 자체 추론 인프라를 운영할 필요가 없다.
- **Cons:** 고객 문의 원문이 외부 서비스로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지.
- **Recheck if:** 고객 데이터 외부 반출 금지 정책이 변경되는 경우.

## Consequences

### Positive

- 고객 데이터가 외부 LLM 제공자에게 전송되지 않아 반출 금지 요건을 충족한다.

### Negative

- 추론용 서버(GPU 등)와 vLLM 서비스를 직접 운영해야 한다.
- `gpt-4o`를 대체할 모델을 직접 선정·관리해야 한다.

### Risks

- 자체 서빙 모델의 요약 품질이 기존 `gpt-4o`보다 낮을 수 있다.
- 추론 서버의 용량·가용성 문제가 요약 기능 장애로 바로 이어진다.

## Implementation

- [ ] 서빙할 모델을 선정하고 vLLM 서버를 구축한다
- [ ] `app/llm_client.py`의 호출 대상을 vLLM 엔드포인트로 바꾸고 `model="gpt-4o"`를 교체한다
- [ ] 기존 출력과 비교해 요약 품질을 테스트한다
- [ ] vLLM 서버 지연시간·에러율·GPU 사용률 모니터링을 추가한다
- [ ] 엔드포인트/모델명을 설정값으로 분리하고, 불필요해지면 OpenAI API 키 설정을 제거한다

## Reversibility

- **Reversible:** Yes
- **Rollback:** 앱 코드 기준으로는 `app/llm_client.py`의 클라이언트 설정(`base_url`, `model`)을 OpenAI로 되돌리면 된다. 다만 외부 반출 금지 요건이 유지되는 한 실제로 되돌릴 수는 없다.
- **Migration Cost:** Low

## Review Trigger

- 고객 데이터 외부 반출 금지 정책이 변경되는 경우.

## References

- **Documentation:** 영향 코드 `app/llm_client.py`, `requirements.txt`(`openai==1.40.0`) — 저장소에 아직 커밋이 없어 커밋 해시는 없음

## AI/ML Details

- **Inference:** vLLM 자체 서빙 (OpenAI 호환 API), 사용처는 고객 문의 요약
