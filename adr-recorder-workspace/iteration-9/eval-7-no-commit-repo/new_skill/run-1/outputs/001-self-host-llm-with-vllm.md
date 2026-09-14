# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 LLM 추론 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 요건에 따라 LLM 추론을 OpenAI API에서 vLLM 기반 자체 서빙으로 전환한다.
- **Scope:** LLM 추론 계층 (`app/llm_client.py` — 고객 문의 요약 기능)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`의 `summarize()`는 고객 문의 원문을 OpenAI API(`gpt-4o`)로 보내 요약한다. 고객 데이터가 회사 외부의 서드파티 API로 전송되는 구조다.
저장소에 아직 커밋이 없어 git diff로 변경 이력을 확인할 수 없었으며, 이 문서는 대화 내용과 현재 작업 트리를 기준으로 작성했다.

### Constraints

- 고객 데이터의 외부 반출 금지.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 서빙)
- **Architecture:** 외부 SaaS LLM API 호출을 자체 인프라에서 서빙하는 추론 서버 호출로 대체해, 고객 데이터가 내부망 밖으로 나가지 않게 한다.
- **Implementation:** `app/llm_client.py`의 OpenAI API 호출을 자체 vLLM 서버 호출로 교체한다. (작성 시점 기준 코드는 아직 OpenAI `gpt-4o`를 호출하고 있다.)

## Rationale

1. 고객 데이터 외부 반출 금지 요건 때문에 고객 문의 원문을 외부 API로 보내는 현재 구조를 유지할 수 없다. 자체 서빙은 데이터가 내부 인프라 안에 머물게 한다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 이미 `app/llm_client.py`에 구현되어 있어 추가 작업·인프라가 필요 없다.
- **Cons:** 고객 문의 원문이 외부(OpenAI)로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 요건을 위반한다.
- **Recheck if:** 고객 데이터 외부 반출 금지 정책이 해제되거나 완화될 때

## Consequences

### Positive

- 고객 데이터가 외부 서비스로 전송되지 않아 반출 금지 요건을 충족한다.

### Negative

- 추론 서버(GPU 인프라 포함)의 구축·운영 책임을 직접 진다.
- 서빙할 모델의 선정·배포·업데이트를 직접 관리해야 한다.

### Risks

- 자체 서빙 모델의 요약 품질이 현재 `gpt-4o` 대비 떨어질 수 있다. 전환 전 품질 확인이 필요하다.

## Implementation

- [ ] `app/llm_client.py`의 `OpenAI()` 클라이언트와 `gpt-4o` 호출을 자체 vLLM 서버 호출로 교체 (vLLM의 OpenAI 호환 서버를 쓰면 `openai` SDK의 `base_url`만 바꿔 재사용 가능)
- [ ] 테스트: 고객 문의 요약 결과 품질을 기존 `gpt-4o` 결과와 비교
- [ ] 모니터링: vLLM 서버 가용성·지연 시간·GPU 사용률
- [ ] 문서/설정 업데이트: vLLM 엔드포인트·모델명 설정, OpenAI API 키 의존 제거, `requirements.txt` 정리

## Reversibility

- **Reversible:** Partial
- **Rollback:** 코드상으로는 `app/llm_client.py`의 클라이언트 설정을 OpenAI API로 되돌리면 되지만, 고객 데이터 외부 반출 금지 요건이 유지되는 한 실제 롤백은 불가하다.
- **Migration Cost:** Medium

## Review Trigger

- 고객 데이터 외부 반출 금지 정책이 해제되거나 완화될 때 (OpenAI API 유지 재검토)

## AI/ML Details

- **Model:** 현행 OpenAI `gpt-4o` → vLLM으로 서빙할 모델은 아직 정해지지 않음
- **Inference:** 자체 인프라의 vLLM 서버
