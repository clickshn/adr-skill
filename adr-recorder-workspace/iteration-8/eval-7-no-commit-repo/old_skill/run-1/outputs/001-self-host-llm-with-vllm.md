# ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 때문에 OpenAI API 대신 vLLM으로 LLM을 자체 서빙한다.
- **Scope:** app/llm_client.py (고객 문의 요약 기능의 LLM 호출 경로)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`의 `summarize()`는 고객 문의 원문을 프롬프트에 담아 OpenAI API(`gpt-4o`)로 보낸다. 즉 고객 데이터가 외부 서비스로 나간다. 작성 시점에 저장소에는 커밋이 없어 diff로 확인할 수 있는 변경은 없고, 코드와 `requirements.txt`(`openai==1.40.0`)는 아직 OpenAI 기준이다.

### Constraints

- 고객 데이터 외부 반출 금지: 고객 문의 텍스트는 사내 인프라 밖으로 나가면 안 된다.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 추론 서버)
- **Architecture:** 외부 SaaS LLM API(OpenAI) 호출을 사내 인프라에서 운영하는 vLLM 추론 서버 호출로 바꾼다. 고객 데이터는 사내 네트워크 안에서만 처리된다.
- **Implementation:** `app/llm_client.py`의 호출 대상을 vLLM 서버로 교체한다. vLLM은 OpenAI 호환 API를 제공하므로 `openai` SDK에 `base_url`과 `model`만 바꿔 호출 코드 변경을 최소화할 수 있다. 서빙할 모델은 아직 정하지 않았다.

## Rationale

1. 고객 데이터 외부 반출 금지 때문에 고객 문의 원문을 외부 API(OpenAI)로 보낼 수 없다. 자체 서빙하면 데이터가 사내 인프라 밖으로 나가지 않는다.

## Alternatives

### OpenAI API 계속 사용 (현행 유지)

- **Pros:** `app/llm_client.py`에 이미 연동되어 있어(`gpt-4o`, `openai==1.40.0`) 추가 구현이 필요 없다.
- **Cons:** 고객 문의 원문이 외부(OpenAI)로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 요건을 충족할 수 없다.
- **Recheck if:** 고객 데이터 외부 반출 금지 정책이 완화되거나 바뀔 때.

## Consequences

### Positive

- 고객 문의 데이터가 사내 인프라 안에서만 처리되어 외부 반출 금지 요건을 충족한다.

### Negative

- 추론 서버(GPU 등)를 직접 구축하고 운영해야 한다.
- 서빙할 모델을 새로 골라야 하고, `gpt-4o`와 요약 품질이 달라질 수 있다.

### Risks

- 선정한 모델의 한국어 고객 문의 요약 품질이 기존 수준에 못 미칠 수 있다.
- 자체 추론 서버의 가용성·용량 문제가 곧바로 요약 기능 장애가 된다.
- 전환을 마치기 전까지는 현재 코드가 계속 고객 데이터를 OpenAI로 보낸다(작성 시점 `app/llm_client.py` 기준).

## Implementation

- [ ] 구현 작업: 서빙 모델 선정, 사내 인프라에 vLLM 추론 서버 구축, `app/llm_client.py`의 `OpenAI()` 클라이언트를 vLLM 엔드포인트(`base_url`)와 새 `model` 값으로 전환
- [ ] 테스트: 기존 `gpt-4o` 대비 요약 품질 비교, 요청이 외부 네트워크로 나가지 않는지 확인
- [ ] 모니터링: vLLM 서버 지연 시간·처리량·GPU 사용률
- [ ] 문서/설정 업데이트: vLLM 엔드포인트·모델명 설정 추가, OpenAI API 키 등 외부 연동 설정 제거

## Reversibility

- **Reversible:** Partial
- **Rollback:** 코드상으로는 `app/llm_client.py`의 `base_url`/`model`을 OpenAI 설정으로 되돌리면 된다. 하지만 고객 데이터 외부 반출 금지 정책이 바뀌지 않는 한 OpenAI로 돌아갈 수 없다.
- **Migration Cost:** Low

## Review Trigger

- 고객 데이터 외부 반출 금지 정책이 완화되거나 바뀔 때 (OpenAI API 재검토)

## AI/ML Details

- **Model:** 미정 (현재 쓰는 `gpt-4o`를 대체할 자체 서빙용 모델 선정 필요)
- **Evaluation:** 아직 안 함. 전환 전에 `gpt-4o` 대비 고객 문의 요약 품질을 비교해야 한다.
- **Inference:** vLLM 자체 서빙 (OpenAI 호환 API), 사내 인프라
