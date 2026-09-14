# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 LLM 추론 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 때문에 OpenAI API(gpt-4o) 호출을 중단하고, vLLM으로 LLM을 자체 서빙한다.
- **Scope:** 고객 문의 요약 기능의 LLM 추론 계층 (`app/llm_client.py`)
- **Decision Source:** Human

---

## Context

### Problem

`app/llm_client.py`의 `summarize()`는 고객 문의 원문을 프롬프트에 그대로 넣어 OpenAI API(`gpt-4o`)로 보낸다. 고객 데이터가 외부 서비스로 나가는 구조다.

### Constraints

- 고객 데이터를 외부로 반출할 수 없다.

## Decision

### Selected

- **Technology:** vLLM (자체 서빙)
- **Architecture:** 외부 SaaS LLM API 호출에서 내부 인프라에 둔 자체 호스팅 추론 서버 호출로 바꾼다. 고객 문의 텍스트는 내부 경계 밖으로 나가지 않는다.
- **Implementation:** `app/llm_client.py`의 `OpenAI()` 클라이언트가 호출하는 대상을 자체 vLLM 서버로 교체한다. vLLM은 OpenAI 호환 API 서버를 제공하므로, 기존 `openai` SDK에서 엔드포인트(`base_url`)와 모델명만 바꿔 계속 쓸 수 있다. 어떤 방식으로 붙일지는 아직 정하지 않았다.

## Rationale

1. 고객 데이터 외부 반출 금지를 지키기 위해서다. 지금 구조에서는 고객 문의 원문이 OpenAI로 전송된다.

## Alternatives

### OpenAI API 계속 사용 (현행 유지)

- **Pros:** 이미 `app/llm_client.py`에 구현되어 있어 코드 변경이나 인프라 구축이 필요 없다.
- **Cons:** 고객 문의 원문이 외부(OpenAI) 서버로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지

## Consequences

### Positive

- 고객 데이터가 외부 서비스로 나가지 않으므로 반출 금지 요건을 지킬 수 있다.

### Negative

- 추론 서버(GPU 인프라 포함)를 직접 구축하고 운영해야 한다.
- vLLM으로는 `gpt-4o`를 서빙할 수 없다. 오픈 웨이트 모델로 바꿔야 한다.

### Risks

- 모델이 바뀌면 요약 품질이 기존 `gpt-4o`와 달라질 수 있다. 아직 비교할 평가 기준이 없다.
- 요약 기능 전체가 자체 vLLM 서버 하나의 가용성에 의존하게 된다.

## Implementation

- [ ] 구현 작업: 서빙할 오픈 웨이트 모델을 정하고 내부망에 vLLM 서버를 구축한다. 그다음 `app/llm_client.py`의 호출 대상과 `model="gpt-4o"`를 교체한다.
- [ ] 테스트: 같은 고객 문의로 `summarize()` 결과를 기존 `gpt-4o` 출력과 비교한다.
- [ ] 모니터링: vLLM 서버의 가용성과 응답 지연을 모니터링한다.
- [ ] 문서/설정 업데이트: `requirements.txt`의 `openai==1.40.0` 유지 여부를 정한다(OpenAI 호환 클라이언트로 쓸지 결정). OpenAI API 키 설정과 외부 호출 경로도 제거한다.

## Reversibility

- **Reversible:** Partial
- **Rollback:** 현행 `app/llm_client.py`의 `OpenAI()` 호출로 되돌리면 된다. 기술적으로는 간단하지만, 고객 데이터 외부 반출 금지 정책이 바뀌지 않으면 되돌릴 수 없다.
- **Migration Cost:** Low

## AI/ML Details

- **Model:** 현재는 `gpt-4o`(OpenAI 전용)다. vLLM에서 서빙할 대체 모델은 아직 정하지 않았다.
- **Inference:** 외부 API 호출에서 내부 vLLM 자체 서빙으로 바꾼다.
