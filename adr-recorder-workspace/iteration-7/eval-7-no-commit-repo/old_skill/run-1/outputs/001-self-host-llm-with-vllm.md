# ADR-001: LLM 호출을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 때문에 OpenAI API 대신 vLLM으로 LLM을 자체 서빙한다.
- **Scope:** app/llm_client.py (LLM 호출 계층, 고객 문의 요약 기능)
- **Decision Source:** Human

---

## Context

### Problem

`app/llm_client.py`의 `summarize()`는 고객 문의 원문을 OpenAI API(`gpt-4o`)로 보내 요약한다. 즉 지금 구조에서는 요청마다 고객 데이터가 외부 서비스로 전송된다.

### Constraints

- 고객 데이터를 외부로 내보내면 안 된다(고객 데이터 외부 반출 금지).
- 현재 의존성: `fastapi==0.112.2`, `openai==1.40.0` (`requirements.txt`). 저장소에 아직 커밋이 없어서 비교할 git diff나 이력이 없다.

## Decision

### Selected

- **Technology:** vLLM (자체 서빙 LLM 추론 서버)
- **Architecture:** 외부 SaaS LLM API(OpenAI) 호출을 없애고, 내부에서 운영하는 vLLM 서버로 추론 요청을 보낸다.
- **Implementation:** `app/llm_client.py`의 `OpenAI()` 클라이언트와 `gpt-4o` 호출을 vLLM 서버 호출로 바꾼다.

## Rationale

1. 고객 데이터 외부 반출 금지 정책을 지키려면 추론을 내부 인프라에서 해야 한다. OpenAI API는 고객 문의 원문을 외부로 보내야 하므로 이 정책과 충돌한다.

## Alternatives

### OpenAI API (현행 유지)

- **Pros:** 이미 `app/llm_client.py`에 구현되어 있다(`gpt-4o`). 서빙 인프라를 따로 운영하지 않아도 된다.
- **Cons:** 고객 문의 원문이 외부(OpenAI) 서버로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지에 위배된다.
- **Recheck if:** 고객 데이터 외부 반출 금지 정책이 바뀌거나 완화될 때

## Consequences

### Positive

- 고객 데이터가 내부 인프라 밖으로 나가지 않아 반출 금지 정책을 지킬 수 있다.

### Negative

- vLLM 서버와 그 아래 추론 인프라를 직접 운영해야 한다.
- `gpt-4o`는 vLLM으로 서빙할 수 없으므로 자체 서빙할 모델을 새로 골라야 한다(아직 미정).

### Risks

- `OpenAI()`를 `base_url` 없이 만들면 기본 엔드포인트가 api.openai.com이다. 전환 과정에서 설정이 빠진 경로가 하나라도 남으면 고객 데이터가 계속 외부로 나갈 수 있다.
- 자체 서빙 모델의 요약 품질이 `gpt-4o`에 못 미칠 수 있다(아직 측정하지 않음).

## Implementation

- [ ] vLLM 서버 구축 및 서빙 모델 선정
- [ ] `app/llm_client.py`를 vLLM 엔드포인트 호출로 전환. vLLM의 OpenAI 호환 서버를 쓰면 `openai` SDK는 그대로 두고 `base_url`과 `model`만 바꿀 수 있다.
- [ ] 테스트: 요약 품질 비교, 외부 엔드포인트(api.openai.com)로 나가는 호출이 없는지 확인
- [ ] 모니터링: vLLM 서버 가용성과 지연 시간
- [ ] 문서/설정 업데이트: 엔드포인트·모델 설정, 필요하면 `requirements.txt` 정리

## Reversibility

- **Reversible:** Partial (코드상으로는 되돌릴 수 있지만, 고객 데이터 외부 반출 금지 정책이 바뀌어야만 실제로 되돌릴 수 있다)
- **Rollback:** `app/llm_client.py`의 클라이언트 설정을 OpenAI 기본 엔드포인트와 `gpt-4o`로 되돌린다. `openai==1.40.0` 의존성은 `requirements.txt`에 그대로 남아 있다.
- **Migration Cost:** Low (LLM 호출 코드가 `app/llm_client.py`의 `summarize()` 한 곳뿐이다)

## Review Trigger

- 고객 데이터 외부 반출 금지 정책이 바뀌거나 완화될 때 (OpenAI API 재검토)

## AI/ML Details

- **Model:** 현재 `gpt-4o`(OpenAI). 자체 서빙할 모델은 미정.
- **Inference:** vLLM 자체 서빙(내부 인프라)
