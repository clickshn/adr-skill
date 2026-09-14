# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST로 유지한다.
- **Scope:** checkout-platform / 서비스 간 내부 동기 호출 (현재 시행 구간: checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 넘었다.

### Constraints

- p99 지연 SLO는 100ms다.
- 플랫폼팀이 2명이라 스키마 관리나 게이트웨이 운영처럼 운영 부담이 큰 방식은 감당하기 어렵다.
- 재고 데이터는 실시간성이 필요하다.
- 외부 공개 API는 REST로 유지한다.

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST로 둔다.
- **Implementation:** 2026-03-02부터 checkout ↔ inventory 구간에 적용 중이다. 인터페이스는 `proto/inventory.proto`의 `inventory.v1.InventoryService/GetStock`에 정의돼 있다.

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회의 p99가 SLO(100ms) 안으로 들어왔다. 180ms에서 52ms로 줄었다(최종값 기준, 아래 Evidence 참고).
2. 같은 테스트에서 페이로드 크기가 약 60% 줄었다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회). REST+JSON에서 gRPC로 바꾸자 p50은 41ms → 12ms, p99는 180ms → 52ms, 평균 페이로드는 4.8KB → 1.9KB(약 60% 감소)로 줄었다. 원본 로그(D-007)의 p99 45ms는 2026-02-11 1차 측정값이다. 이 측정은 커넥션 풀 워밍업이 빠져 있었고, 벤치 문서는 재측정값 52ms를 최종값으로 명시한다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마를 관리하고 게이트웨이를 운영해야 한다.
- **Rejected because:** 그 운영 부담을 현 인원(플랫폼팀 2명)으로 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어난다.

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 재고 데이터의 실시간성 요구 때문에 캐시 무효화가 어렵다.

## Consequences

### Positive

- checkout → inventory 재고 조회의 p99가 SLO(100ms) 안으로 들어온다(부하테스트 최종값 52ms).
- 서비스 간 페이로드 크기가 약 60% 줄어든다.

### Negative

- 내부 통신은 gRPC, 외부 공개 API는 REST라서 두 프로토콜을 함께 운영해야 한다.

### Risks

- 원본 결정 로그(D-007)에 적힌 p99(45ms)가 벤치 문서의 최종값(52ms)과 다르다. 근거를 인용할 때는 벤치 문서의 최종값을 기준으로 삼는다.

## Implementation

- [x] gRPC 전환 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [x] checkout ↔ inventory 구간 gRPC 전환 (2026-03-02 시행, `proto/inventory.proto`)
- [ ] 그 밖의 내부 서비스 간 동기 호출 구간 전환 (원본 기준 시행 범위는 checkout ↔ inventory 구간뿐)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 호출을 REST+JSON 클라이언트로 되돌리고 gRPC `InventoryService`를 걷어낸다. 저장소에는 서비스 코드가 없고 `proto/inventory.proto`만 있어서, REST 엔드포인트를 병행 유지하고 있는지는 확인할 수 없었다. 롤백하면 피크 시간 p99 SLO 초과 문제가 다시 생긴다.
- **Migration Cost:** Low (현재 전환된 구간은 checkout ↔ inventory 1곳, RPC는 `GetStock` 1개)

## Review Trigger

- GraphQL 페더레이션: 플랫폼팀이 4명 이상으로 늘어나면 다시 검토한다.

## References

- **Documentation:**
  - `docs/decisions.md` D-007 (원본 결정 로그)
  - `bench/grpc-loadtest-2026-02.md` (부하테스트 결과)
  - `proto/inventory.proto` (gRPC 인터페이스 정의)
  - 커밋 `8c3a73e`: 위 파일들이 추가된 커밋이다. 커밋 `ea70f75`(feat(inventory): gRPC 재고 조회 엔드포인트)와 `7d7cef8`(docs: gRPC 부하테스트 결과 추가)은 변경 파일이 없는 빈 커밋이다.
