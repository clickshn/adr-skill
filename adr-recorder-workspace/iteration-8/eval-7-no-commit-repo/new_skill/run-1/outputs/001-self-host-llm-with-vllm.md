# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 LLM 추론 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지를 지키기 위해 LLM 추론을 OpenAI API에서 vLLM 기반 자체 서빙으로 옮긴다.
- **Scope:** app/llm_client.py (고객 문의 요약 LLM 추론 계층)
- **Decision Source:** Human

---

## Context

### Problem

지금 `app/llm_client.py`의 `summarize()`는 OpenAI API(`gpt-4o`, `openai==1.40.0`)를 호출하는데, 고객 문의 원문을 프롬프트에 그대로 담아 외부(OpenAI) 서버로 보낸다.

### Constraints

- 고객 데이터 외부 반출 금지: 고객 문의 텍스트를 조직 밖의 서비스로 보내면 안 된다.

## Decision

### Selected

- **Technology:** vLLM
- **Architecture:** 외부 LLM API를 호출하지 않고 내부 인프라에서 vLLM으로 LLM을 직접 서빙한다. 애플리케이션은 내부 엔드포인트만 호출한다.
- **Implementation:** `app/llm_client.py`의 추론 호출 대상을 OpenAI API에서 내부 vLLM 서버로 바꾼다. 서빙할 모델은 아직 정하지 않았다.

## Rationale

1. 고객 데이터 외부 반출 금지 정책 때문에 고객 문의 원문을 외부 API로 보내는 지금 구조는 유지할 수 없다.
2. vLLM으로 직접 서빙하면 추론 요청과 응답이 내부 인프라 안에서 처리되므로 고객 데이터가 밖으로 나가지 않는다.

## Alternatives

### OpenAI API 유지 (현행, gpt-4o)

- **Pros:** 이미 `app/llm_client.py`에 구현되어 있어 인프라를 따로 준비할 필요가 없다.
- **Cons:** 고객 문의 원문이 외부(OpenAI) 서버로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 정책에 어긋난다.

## Consequences

### Positive

- 고객 데이터가 외부로 반출되지 않으므로 정책을 지킬 수 있다.

### Negative

- GPU 서버 같은 추론 인프라를 직접 구축하고 운영해야 한다.
- gpt-4o를 대신할 서빙 모델을 새로 골라야 한다.

### Risks

- 직접 서빙하는 모델의 요약 품질이 기존 gpt-4o보다 떨어질 수 있다.
- 자체 서빙이 장애가 나도 외부 API로 폴백하면 정책 위반이다. 따라서 가용성을 내부에서 확보해야 한다.

## Implementation

- [ ] 구현 작업: vLLM으로 서빙할 모델을 고르고 내부 서빙 환경을 구축한다. `app/llm_client.py`의 호출 대상을 내부 vLLM 엔드포인트로 바꾼다. vLLM은 OpenAI 호환 API 서버를 제공하므로 기존 `openai` SDK를 그대로 두고 `base_url`만 바꾸는 방법도 있다.
- [ ] 테스트: 요약 품질을 기존 gpt-4o와 비교하고, 외부 API로 나가는 트래픽이 없는지 확인한다.
- [ ] 모니터링: vLLM 서버의 지연 시간, 처리량, GPU 사용률을 본다.
- [ ] 문서/설정 업데이트: `model="gpt-4o"`와 `OpenAI()` 기본 설정(`OPENAI_API_KEY` 환경변수)에 걸린 의존을 정리하고 `requirements.txt`에 반영한다.

## Reversibility

- **Reversible:** Partial
- **Rollback:** 고객 데이터 외부 반출 금지 정책이 바뀌어야만 되돌릴 수 있다. 정책이 허용하면 `app/llm_client.py`의 호출 대상을 다시 OpenAI API(`gpt-4o`)로 돌리면 된다. 이 저장소에는 아직 커밋이 없어 git으로 돌아갈 기준 시점이 없으니, 전환하기 전에 현재 코드를 커밋해 두는 편이 좋다.
- **Migration Cost:** Low (LLM을 호출하는 곳이 `app/llm_client.py` 한 곳뿐)

## AI/ML Details

- **Model:** 기존 `gpt-4o`(OpenAI API) → vLLM 서빙 모델은 미정
- **Inference:** 내부 인프라에서 vLLM으로 직접 서빙
