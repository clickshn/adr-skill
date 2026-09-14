# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 REST+JSON에서 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform 내부 서비스 간 동기 통신 (현재 checkout ↔ inventory 구간 시행, 담당: 플랫폼팀)
- **Decision Source:** Human

---

## Context

docs/decisions.md의 D-007을 이관한 기록이다(이관일 2026-09-11). 원본에 확정일은 따로 없고 시행 시작일(2026-03-02)만 있어 Date에 시행 시작일을 썼다.

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 넘었다.

### Constraints

- 외부 공개 API는 REST를 유지해야 한다.
- 재고 데이터는 실시간성이 필요하다.
- 플랫폼팀 인원이 2명이다.

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST를 쓰는 이원 구성
- **Implementation:** 2026-03-02부터 checkout ↔ inventory 구간에서 시행 중. 인터페이스는 `proto/inventory.proto`의 `inventory.v1.InventoryService/GetStock`에 정의돼 있다.

## Rationale

1. 사내 부하테스트에서 재고 조회 p99가 180ms에서 52ms로 떨어져 SLO(100ms) 안으로 들어왔다.
2. 평균 페이로드 크기가 약 60% 줄었다(4.8KB → 1.9KB).
3. 검토한 대안(GraphQL 페더레이션, REST 유지 + 응답 캐싱)은 운영 인력과 실시간성 제약을 충족하지 못했다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6, 500 VU, 10분, checkout → inventory 재고 조회). REST+JSON 대비 gRPC: p50 41ms → 12ms, p99 180ms → 52ms, 평균 페이로드 4.8KB → 1.9KB. 원본 D-007에 적힌 p99 45ms는 1차 측정(2026-02-11) 값이다. 커넥션 풀 워밍업이 빠져 재측정했고, 벤치 문서는 52ms를 최종값으로 명시한다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현재 인원(플랫폼팀 2명)으로는 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 캐시 무효화가 어려워 재고 데이터의 실시간성 요구를 충족하기 어렵다.

## Consequences

### Positive

- 벤치마크 기준으로 재고 조회 p99가 SLO(100ms) 안으로 들어오고 페이로드가 약 60% 줄었다.

### Negative

- 내부(gRPC)와 외부(REST) 두 프로토콜을 함께 운영하고 proto 스키마를 관리해야 한다.

### Risks

- 시행(2026-03-02) 이후의 운영 환경 p99 실측치는 원본과 저장소 어디에도 없다. 현재 근거는 벤치마크 수치뿐이다.
- 결정 범위는 "내부 서비스 간 동기 호출" 전체지만, 시행된 구간은 checkout ↔ inventory 하나뿐이다. 나머지 구간의 전환 범위와 일정은 기록돼 있지 않다.

## Implementation

- [x] 구현: checkout ↔ inventory 재고 조회 gRPC 전환 (2026-03-02 시행, `proto/inventory.proto`)
- [x] 테스트: 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [ ] 모니터링: 시행 후 운영 환경 p99 측정치 기록
- [ ] 나머지 내부 동기 호출 구간 전환 (범위·일정 미정)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 재고 조회 클라이언트를 REST 호출로 되돌린다. 전환된 범위는 checkout ↔ inventory 구간의 RPC 1개(`GetStock`)뿐이다. 다만 inventory의 기존 REST 재고 조회 엔드포인트가 아직 남아 있는지는 이 저장소에서 확인할 수 없다(서비스 코드 없이 proto만 있음). 롤백하면 원래 문제였던 p99 SLO 초과가 다시 생긴다(벤치 기준 REST p99 180ms).
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007(원본), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`. 관련 커밋: `adb2e90` feat(inventory): gRPC 재고 조회 엔드포인트, `31a2593` docs: gRPC 부하테스트 결과 추가
