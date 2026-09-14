# ADR-001: LLM 추론을 OpenAI API에서 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 고객 데이터 외부 반출 금지 때문에 OpenAI API 대신 vLLM으로 LLM을 자체 서빙한다.
- **Scope:** app — 고객 문의 요약 LLM 호출 (`app/llm_client.py`)
- **Decision Source:** Human

---

## Context

### Problem

`app/llm_client.py`의 `summarize()`는 고객 문의 원문을 프롬프트에 넣어 OpenAI API(`gpt-4o`)로 보낸다. 고객 데이터가 외부 서비스로 전송되는 구조다.
현재 코드와 `requirements.txt`(`openai==1.40.0`)는 아직 OpenAI를 쓰고 있다. 저장소에 커밋이 없어 의존성 diff로 확인되는 변경도 없다.

### Constraints

- 고객 데이터 외부 반출 금지.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 LLM 추론 서버)
- **Architecture:** LLM 추론을 외부 API(api.openai.com)가 아닌 자체 인프라의 vLLM 서버에서 처리하고, 애플리케이션은 내부 엔드포인트만 호출한다.
- **Implementation:** vLLM의 OpenAI 호환 API 서버를 띄우고, `app/llm_client.py`의 `OpenAI()` 클라이언트가 그 엔드포인트(`base_url`)와 서빙 모델명을 쓰게 바꾼다. 기존 `openai` SDK 호출 코드는 그대로 둘 수 있다.

## Rationale

1. 추론을 자체 인프라에서 처리하면 고객 문의 원문이 외부로 나가지 않아 고객 데이터 외부 반출 금지 요건을 충족한다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** `app/llm_client.py`에 이미 구현되어 있어 추가 작업이 없다. 추론 인프라를 직접 운영할 필요가 없다.
- **Cons:** 고객 문의 원문이 외부(OpenAI)로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출 금지 정책에 위배된다.

## Consequences

### Positive

- 고객 데이터가 자체 인프라 밖으로 나가지 않는다.
- 외부 LLM API 계정·키에 의존하지 않게 된다.

### Negative

- GPU 서버 등 추론 인프라를 직접 마련하고 운영해야 한다.
- vLLM으로 서빙할 모델을 새로 선정하고 검증해야 한다.

### Risks

- 선정한 모델의 요약 품질이 현행 `gpt-4o`보다 낮을 수 있다.
- 추론 서버의 장애와 용량 부족이 곧바로 서비스 장애로 이어지고, 이를 자체적으로 대응해야 한다.

## Implementation

- [ ] 내부 인프라에 vLLM OpenAI 호환 서버 배포 (서빙 모델 선정 포함)
- [ ] `app/llm_client.py`: `OpenAI(base_url=<vLLM 엔드포인트>)`로 바꾸고 `model="gpt-4o"`를 서빙 모델명으로 교체 (엔드포인트·모델명은 환경변수로 분리)
- [ ] 테스트: `summarize()` 응답 형식 호환성과 요약 품질 확인
- [ ] 모니터링: vLLM 서버 가용성, 지연 시간, GPU 사용률
- [ ] 문서/설정 업데이트: 배포 설정에서 OpenAI API 키 제거, 외부 LLM API로 나가는 트래픽이 없는지 확인

## Reversibility

- **Reversible:** Partial
- **Rollback:** `app/llm_client.py`의 `base_url`과 모델 설정을 기본값(OpenAI, `gpt-4o`)으로 되돌리면 코드상으로는 바로 복귀할 수 있다. 다만 고객 데이터 외부 반출 금지 정책이 바뀌지 않는 한 OpenAI로 되돌릴 수 없다.
- **Migration Cost:** Low (코드 변경 범위가 `app/llm_client.py` 한 파일이고, `openai` SDK를 계속 쓴다)

## AI/ML Details

- **Model:** 현행 `gpt-4o`(OpenAI). vLLM으로 서빙할 모델은 아직 정해지지 않았다.
- **Inference:** vLLM 자체 호스팅, OpenAI 호환 API로 내부 호출
