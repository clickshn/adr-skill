# ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 정책에 따라 LLM 추론을 OpenAI API 대신 vLLM 기반 자체 서빙으로 전환한다.
- **Scope:** LLM 호출 계층 (`app/llm_client.py` — 고객 문의 요약)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/llm_client.py`의 `summarize()`는 고객 문의 원문을 프롬프트에 담아 OpenAI API(`gpt-4o`, `openai==1.40.0`)로 전송한다. 고객 데이터가 외부 서비스로 나가는 구조다.

### Constraints

- 고객 데이터 외부 반출 금지 정책: LLM 추론 요청·응답에 담긴 고객 데이터가 사내 인프라 밖으로 나가서는 안 된다.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 추론 서버)
- **Architecture:** 외부 SaaS API(OpenAI) 직접 호출 → 사내 인프라에서 운영하는 vLLM 추론 서버 호출
- **Implementation:** `app/llm_client.py`의 호출 대상을 자체 vLLM 엔드포인트로 교체한다. 서빙할 모델은 아직 정해지지 않았다.

## Rationale

1. 고객 데이터 외부 반출 금지 정책을 지키려면 고객 문의 원문이 외부 API로 전송되지 않아야 한다. 자체 서빙을 하면 추론 전 과정이 사내 인프라 안에서 이루어진다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 현재 코드(`app/llm_client.py`, `gpt-4o`)가 이미 사용 중이라 추가 구현이나 인프라 운영이 필요 없다.
- **Cons:** 고객 문의 원문이 외부(OpenAI)로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 정책에 위배된다.
- **Recheck if:** 고객 데이터 외부 반출 금지 정책이 바뀌거나 완화될 때

## Consequences

### Positive

- 고객 문의 데이터가 외부 서비스로 전송되지 않으므로 반출 금지 정책을 지킬 수 있다.

### Negative

- 추론 서버(vLLM)와 서빙 모델을 직접 운영·관리해야 한다.
- `gpt-4o`를 대체할 서빙 모델을 새로 선정해야 한다.

### Risks

- 자체 서빙 모델의 요약 품질이 기존 `gpt-4o`보다 낮을 수 있다(아직 비교하지 않음).
- 현재 `OpenAI()`는 코드에 `base_url` 지정 없이 생성된다. 전환 후에도 `openai` SDK를 그대로 쓰는데 엔드포인트 설정(예: `OPENAI_BASE_URL`)이 빠지면, 요청이 기본값인 외부 OpenAI API로 조용히 나갈 수 있다.

## Implementation

- [ ] vLLM 추론 서버 구축 및 서빙 모델 선정
- [ ] `app/llm_client.py`의 호출 대상을 vLLM 엔드포인트로 교체 (vLLM의 OpenAI 호환 서버를 쓰면 `openai` SDK에 `base_url`과 `model`만 바꿔 유지 가능)
- [ ] 기존 `gpt-4o` 대비 요약 품질 비교 테스트
- [ ] 외부 OpenAI 엔드포인트로 나가는 호출이 남아 있지 않은지 모니터링(egress 확인)
- [ ] `requirements.txt`·엔드포인트·모델 설정 업데이트, OpenAI API 키 제거

## Reversibility

- **Reversible:** Partial
- **Rollback:** `app/llm_client.py`의 호출 대상을 OpenAI API로 되돌리면 코드는 복귀되지만, 고객 데이터 외부 반출 금지 정책이 바뀌지 않는 한 실제로 되돌릴 수는 없다. 저장소에 아직 커밋이 없어 git으로 돌아갈 기준 시점도 없다.
- **Migration Cost:** Low

## Review Trigger

- 고객 데이터 외부 반출 금지 정책이 바뀌거나 완화될 때

## AI/ML Details

- **Model:** 기존 `gpt-4o`(OpenAI API) → 자체 서빙 모델 미정
- **Evaluation:** 미실시 — 전환 전후 요약 품질 비교 필요
- **Inference:** OpenAI API 원격 호출 → 사내 vLLM 추론 서버
