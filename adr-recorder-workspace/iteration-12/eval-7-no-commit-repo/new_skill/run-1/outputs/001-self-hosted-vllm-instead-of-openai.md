# ADR-001: OpenAI API 대신 vLLM 자체 서빙으로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 고객 문의 요약 LLM 호출을 OpenAI API에서 자체 호스팅 vLLM 서버로 전환한다.
- **Scope:** 고객 문의 요약 기능 (`app/llm_client.py`)
- **Decision Source:** Human

---

## Context

### Problem

고객 문의 요약 기능은 현재 OpenAI API(`openai==1.40.0`, 모델 `gpt-4o`)를 직접 호출한다. 요약 입력은 고객이 보낸 문의 원문이므로, 호출할 때마다 고객 데이터가 외부 사업자 인프라로 전송된다.

### Constraints

- 고객 데이터의 외부 반출이 금지되어 있다. 따라서 고객 문의 원문을 외부 API로 보내는 현재 구조는 유지할 수 없다.
- 애플리케이션은 OpenAI Python SDK 인터페이스(`chat.completions.create`)에 이미 의존하고 있다.
- 저장소에 아직 커밋이 없어(작업 트리 전체가 untracked) 변경 이력 기준의 복원 지점이 없다.

## Decision

### Selected

- **Technology:** vLLM (자체 호스팅 추론 서버)
- **Architecture:** 외부 SaaS API 호출을 사내 인프라 내부의 vLLM 추론 서버 호출로 대체한다. 고객 데이터는 신뢰 경계 밖으로 나가지 않는다.
- **Implementation:** vLLM의 OpenAI 호환 서버를 사용해 `app/llm_client.py`의 클라이언트 생성부를 사내 엔드포인트(`base_url`)로 바꾸고, `requirements.txt`에서 `openai` 의존을 vLLM 서빙 구성에 맞게 정리한다. 모델명은 `gpt-4o`에서 자체 서빙 모델명으로 교체한다.

## Rationale

1. 고객 데이터 외부 반출 금지 정책을 구조적으로 만족시킨다. 접근 통제나 계약이 아니라, 데이터가 애초에 외부로 나가지 않는 배치로 요구사항을 충족한다.
2. vLLM은 OpenAI 호환 API를 제공하므로 기존 SDK 호출 형태를 거의 그대로 유지할 수 있고, 애플리케이션 코드 변경 범위가 엔드포인트/모델명 수준으로 작다.

## Alternatives

### OpenAI API 유지 (현행)

- **Pros:** 현재 코드가 이미 동작하며 운영 부담이 없다. 별도 추론 인프라가 필요 없다.
- **Cons:** 요약 대상인 고객 문의 원문이 외부 사업자로 전송된다.
- **Rejected because:** 고객 데이터 외부 반출이 금지되어 있어 정책상 사용할 수 없다.

## Consequences

### Positive

- 고객 문의 원문이 사내 인프라를 벗어나지 않아 데이터 반출 금지 요건을 만족한다.
- 외부 API 요금과 호출량 제한, 외부 서비스 장애에 대한 의존이 사라진다.

### Negative

- 추론 서버(GPU 포함) 운영·용량 관리·업그레이드 책임이 팀으로 넘어온다.
- 모델 품질이 `gpt-4o` 기준과 달라질 수 있어 요약 결과 품질의 재검증이 필요하다.

### Risks

- vLLM에 올릴 오픈 웨이트 모델이 아직 정해지지 않았다. 모델 선택에 따라 요약 품질과 필요한 GPU 사양이 크게 달라진다.
- 자체 서빙 용량이 부족하면 지연이나 실패가 발생하는데, 정책상 외부 API로 폴백할 수 없다.

## Implementation

- [ ] vLLM OpenAI 호환 서버 기동 및 서빙 모델 확정
- [ ] `app/llm_client.py`의 `base_url`·모델명 교체, `requirements.txt` 의존성 정리
- [ ] 기존 OpenAI 응답과 요약 품질 비교 테스트
- [ ] 추론 서버 지연·에러율·GPU 사용률 모니터링 추가
- [ ] 배포/환경변수 문서 업데이트 (엔드포인트, 모델명)

## Reversibility

- **Reversible:** Partial
- **Rollback:** 코드 상으로는 `app/llm_client.py`를 OpenAI 클라이언트 호출로 되돌리고 `requirements.txt`의 `openai==1.40.0`을 복원하면 된다(변경 범위가 작음). 다만 되돌리려면 고객 데이터 외부 반출 금지 정책 자체가 바뀌어야 하므로 기술적 롤백만으로는 복귀할 수 없다. 현재 저장소에는 커밋이 없어 되돌릴 기준 커밋도 존재하지 않는다.
- **Migration Cost:** Medium

## AI/ML Details

- **Model:** vLLM에 올릴 오픈 웨이트 모델 미정 (현행은 OpenAI `gpt-4o`)
- **Inference:** 사내 인프라에서 vLLM OpenAI 호환 서버로 서빙하고, 애플리케이션은 `base_url`과 모델명만 사내 엔드포인트로 교체한다.
