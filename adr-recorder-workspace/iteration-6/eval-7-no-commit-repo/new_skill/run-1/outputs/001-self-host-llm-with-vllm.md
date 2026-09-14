# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 LLM 추론 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 정책에 따라 LLM 추론을 OpenAI API에서 vLLM 기반 자체 서빙으로 전환한다.
- **Scope:** LLM 추론 계층 (`app/llm_client.py`의 고객 문의 요약 기능)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`는 OpenAI API(`gpt-4o`)에 고객 문의 원문을 그대로 보내 요약한다. 즉 고객 데이터가 외부 서비스로 나간다.

### Constraints

- 고객 데이터를 외부로 반출해서는 안 된다.
- 현재 의존성은 `requirements.txt`의 `fastapi==0.112.2`, `openai==1.40.0`이다. LLM 호출 지점은 `app/llm_client.py` 한 곳이다.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 추론 서버)
- **Architecture:** 사내 인프라에 vLLM 추론 서버를 두고, 애플리케이션은 외부 LLM API 대신 내부 엔드포인트만 호출한다. 고객 데이터는 사내 네트워크 밖으로 나가지 않는다.
- **Implementation:** `app/llm_client.py`의 `OpenAI()` 클라이언트가 vLLM의 OpenAI 호환 엔드포인트(`base_url`)를 호출하도록 바꾸고, `model="gpt-4o"`를 자체 서빙 모델로 교체한다. 서빙할 모델은 아직 정하지 않았다.

## Rationale

1. 고객 데이터 외부 반출 금지: 외부 SaaS LLM API로 고객 문의 원문을 보내는 현재 구조는 이 정책과 충돌한다. 자체 서빙하면 추론 입력이 내부에만 머문다.

## Alternatives

### OpenAI API (gpt-4o, 현행)

- **Pros:** 현재 `app/llm_client.py`에 구현되어 있어 추가 인프라가 필요 없다.
- **Cons:** 고객 문의 원문이 외부 API로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 정책을 지킬 수 없다.
- **Recheck if:** 고객 데이터 외부 반출 금지 정책이 바뀌거나 완화될 때

## Consequences

### Positive

- 고객 데이터가 외부로 나가지 않아 반출 금지 정책을 지킬 수 있다.
- 외부 LLM API 가용성이나 정책 변경에 휘둘리지 않는다.
- vLLM이 OpenAI 호환 API를 제공하므로 기존 `openai` SDK 호출 코드를 거의 그대로 재사용할 수 있다.

### Negative

- 추론용 GPU 인프라를 확보하고 운영해야 한다.
- 모델 선정·업데이트, 스케일링, 장애 대응을 직접 책임져야 한다.

### Risks

- 자체 서빙하는 모델의 고객 문의 요약 품질이 현행 `gpt-4o`보다 낮을 수 있다.
- 추론 서버 용량이 부족하면 요약 기능의 지연이 커지거나 장애가 날 수 있다.

## Implementation

- [ ] 구현 작업: 서빙할 모델 선정, vLLM 서버 구축, `app/llm_client.py`를 내부 vLLM 엔드포인트와 자체 모델로 전환
- [ ] 테스트: 고객 문의 요약 품질을 현행 `gpt-4o` 결과와 비교
- [ ] 모니터링: 추론 지연, 오류율, GPU 사용률
- [ ] 문서/설정 업데이트: vLLM 엔드포인트 URL을 설정(환경변수)으로 분리하고 OpenAI API 키 제거

## Reversibility

- **Reversible:** Partial
- **Rollback:** 코드는 `app/llm_client.py`의 클라이언트 설정을 OpenAI 기본 엔드포인트와 `gpt-4o`로 되돌리면 복원된다. 하지만 고객 데이터 외부 반출 금지 정책이 유지되는 한 실제로 롤백할 수는 없다.
- **Migration Cost:** Low

## Review Trigger

- 고객 데이터 외부 반출 금지 정책이 바뀌거나 완화될 때

## AI/ML Details

- **Model:** 현행 `gpt-4o`(OpenAI API). 자체 서빙 모델은 미정.
- **Inference:** vLLM 자체 서빙 (사내 인프라, OpenAI 호환 엔드포인트)
