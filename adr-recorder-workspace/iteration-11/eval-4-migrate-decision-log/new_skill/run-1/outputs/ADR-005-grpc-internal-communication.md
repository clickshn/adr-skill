# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 통신 (현재 checkout ↔ inventory 구간 시행 중)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 넘었다.

### Constraints

- p99 지연 SLO는 100ms다.
- 외부 공개 API는 REST로 유지한다.
- 플랫폼팀 인원이 2명이라 운영 부담이 큰 방식은 쓸 수 없다.
- 재고 데이터는 실시간성이 필요하다.

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC로 하고, 외부 공개 API는 REST로 유지한다.
- **Implementation:** 2026-03-02부터 checkout ↔ inventory 구간에서 시행 중이다. 이 저장소에서 확인되는 산출물은 `proto/inventory.proto`(`inventory.v1.InventoryService/GetStock`)뿐이다.

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회의 p99가 REST+JSON 180ms에서 gRPC 52ms로 줄어 SLO(100ms) 안에 들어왔다.
2. 평균 페이로드가 약 60% 줄어 직렬화 비용이 줄었다.
3. 대안인 GraphQL 페더레이션은 현 인원으로 운영할 수 없고, REST 유지 + 응답 캐싱은 재고 데이터의 실시간성 요구와 맞지 않았다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6, 500 VU, 10분, checkout → inventory 재고 조회). REST+JSON에서 gRPC로 p50은 41ms → 12ms, p99는 180ms → 52ms, 평균 페이로드는 4.8KB → 1.9KB(약 60% 감소)다. 원본 D-007에 적힌 p99 45ms는 1차 측정값(2026-02-11)이다. 이 측정은 커넥션 풀 워밍업을 빠뜨려서 다시 측정했고, 벤치 문서는 재측정값 52ms를 최종값으로 명시한다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 그 부담을 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어난 경우.

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해서 캐시 무효화가 어렵다.
- **Rejected because:** 재고 데이터의 실시간성 요구 때문에 캐시 무효화가 어렵다.

## Consequences

### Positive

- 벤치 기준으로 checkout → inventory 재고 조회 p99가 SLO(100ms) 안에 들어온다.
- 호출당 페이로드가 약 60% 줄어든다.

### Negative

- 외부 공개 API(REST)와 내부 통신(gRPC)에서 두 프로토콜을 함께 운영해야 한다.
- 내부 인터페이스마다 protobuf 스키마(`proto/`)를 관리해야 한다.

### Risks

- 이 기록의 근거는 벤치 수치뿐이다. 2026-03-02 시행 이후 운영 환경의 p99 실측치는 원본 로그에도 저장소에도 없다.

## Implementation

- [x] 재고 조회 protobuf 정의 (`proto/inventory.proto`)
- [x] checkout ↔ inventory 구간 gRPC 전환 (2026-03-02부터 시행)
- [ ] 나머지 내부 서비스 간 동기 호출 전환 (원본에 대상 구간과 일정이 적혀 있지 않음)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout → inventory 재고 조회를 REST 호출로 되돌린다. 되돌리면 피크 시간 p99 SLO 초과 문제도 다시 생긴다. 서비스 코드가 이 저장소에 없어서 REST 엔드포인트가 아직 남아 있는지는 확인하지 못했다.
- **Migration Cost:** Low. 현재 시행 구간은 checkout ↔ inventory 1개이고, 정의된 RPC도 `GetStock` 1개다.

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 다시 검토한다.

## References

- **Documentation:**
  - `docs/decisions.md` D-007 (원본 결정 로그)
  - `bench/grpc-loadtest-2026-02.md` (부하테스트 결과)
  - `proto/inventory.proto` (gRPC 인터페이스 정의)
  - 커밋 `8c3a73e`: 위 세 파일이 이 커밋에서 추가되었다. 메시지가 gRPC 관련인 `7d7cef8`, `ea70f75`는 `git show --stat` 결과 변경 파일이 없는 빈 커밋이라 인용하지 않았다.
