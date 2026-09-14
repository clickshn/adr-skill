# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 고객 데이터 외부 반출 금지 요건에 따라 LLM 추론을 OpenAI API 대신 vLLM 기반 자체 서빙으로 전환한다.
- **Scope:** LLM 호출 계층 (`app/llm_client.py`) — 고객 문의 요약 기능
- **Decision Source:** Human

---

## Context

### Problem

현재 고객 문의 요약 기능은 `app/llm_client.py`에서 OpenAI SDK(`openai==1.40.0`)로 `gpt-4o`를
호출하며, 고객이 보낸 문의 원문을 그대로 프롬프트에 담아 외부 API로 전송한다. 즉 고객 데이터가
사내 경계를 벗어난다.

### Constraints

- 고객 데이터의 외부 반출이 금지되어 있어, 문의 원문을 외부 LLM 서비스로 보낼 수 없다.
- 요약 기능 자체는 유지해야 하므로 LLM 추론 경로를 사내에서 대체해야 한다.
- 현행 호출부는 OpenAI Chat Completions 인터페이스에 의존하고 있다(vLLM이 OpenAI 호환
  엔드포인트를 제공하므로 호출부 변경 범위는 작다).

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 추론 서버)
- **Architecture:** 외부 SaaS LLM API 호출을 사내에 배포한 vLLM 서버 호출로 대체한다. 고객 문의
  텍스트는 사내 네트워크 경계 밖으로 나가지 않는다.
- **Implementation:** `app/llm_client.py`의 클라이언트가 사내 vLLM 엔드포인트를 바라보도록 하고,
  의존성에서 외부 API 사용 전제를 제거한다. (서빙할 모델·배포 형상은 아직 정해지지 않음)

## Rationale

1. 고객 데이터 외부 반출 금지가 강제 요건이므로, 문의 원문을 외부로 보내는 현행 구조는 유지할 수 없다.
2. 추론을 사내에서 수행하면 데이터가 네트워크 경계를 넘지 않아 해당 요건을 구조적으로 충족한다.
3. vLLM은 OpenAI 호환 API를 제공하므로 기존 호출 코드의 변경 범위가 작다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 이미 동작 중이며 추가 인프라·운영 부담이 없다.
- **Cons:** 고객 문의 원문이 외부 서비스로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출이 금지되어 있다.

## Consequences

### Positive

- 고객 문의 데이터가 사내 경계 밖으로 나가지 않아 반출 금지 요건을 충족한다.
- 외부 API 장애·요금제·모델 폐기(deprecation)에 대한 의존이 사라진다.

### Negative

- 추론 서버(GPU 포함) 구축·운영·용량 관리 책임을 직접 지게 된다.
- 자체 서빙 모델의 요약 품질이 현행 `gpt-4o` 대비 달라질 수 있다.

### Risks

- 서빙할 모델과 하드웨어 사양이 아직 정해지지 않아 품질·비용·지연시간을 예측할 수 없다.
- 자체 서버가 단일 장애점이 되면 요약 기능 전체가 중단될 수 있다.

## Implementation

- [ ] 구현 작업: 서빙 모델 선정, vLLM 서버 배포, `app/llm_client.py` 엔드포인트/모델 전환, `requirements.txt` 정리
- [ ] 테스트: 기존 문의 샘플에 대한 요약 품질 비교, 장애 시 동작 확인
- [ ] 모니터링: 추론 지연시간·처리량·에러율·GPU 사용률
- [ ] 문서/설정 업데이트: 엔드포인트 설정값, 배포·운영 문서

## Reversibility

- **Reversible:** Partial
- **Rollback:** 코드 수준에서는 `app/llm_client.py`를 OpenAI 클라이언트 호출로, `requirements.txt`를
  `openai==1.40.0`으로 되돌리면 된다. 다만 되돌리는 순간 고객 데이터가 다시 외부로 나가므로,
  반출 금지 정책이 바뀌지 않는 한 실제로는 되돌릴 수 없다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/llm_client.py` (현행 OpenAI 호출부), `requirements.txt` (`openai==1.40.0`)

## AI/ML Details

- **Model:** 현행 `gpt-4o`(OpenAI API). 자체 서빙할 모델은 아직 정해지지 않았다.
- **Inference:** vLLM 자체 호스팅 서버(OpenAI 호환 엔드포인트). 배포 형상·GPU 사양 미정.
