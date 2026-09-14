# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출을 gRPC(protobuf)로 전환하고 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform (checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 외부 공개 API는 기존 소비자를 위해 REST 계약을 유지해야 한다.
- 재고 데이터는 실시간성이 필요해 응답 캐싱으로 지연을 흡수하기 어렵다.
- 플랫폼팀 인원이 2명이라 운영 부담이 큰 방식은 감당하기 어렵다.

## Decision

### Selected

- **Technology:** gRPC + protobuf (proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC로 전환, 외부 공개 API는 REST 유지 (내부/외부 프로토콜 분리)
- **Implementation:** `proto/inventory.proto`의 `inventory.v1.InventoryService.GetStock`으로 재고 조회 제공. 2026-03-02부터 checkout ↔ inventory 구간에 시행 중.

## Rationale

1. 부하테스트에서 p99 지연이 180ms → 52ms로 떨어져 SLO(100ms) 안으로 들어왔다.
2. 평균 페이로드가 4.8KB → 1.9KB로 약 60% 줄어 주문당 6회 호출의 누적 직렬화·전송 비용이 감소한다.
3. 내부 통신만 바꾸고 외부 REST 계약은 그대로 두어 외부 소비자 영향이 없다.
4. protobuf 스키마가 서비스 간 계약을 명시적으로 고정해 준다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6 / 500 VU / 10분, checkout → inventory 재고 조회) — p50 41ms → 12ms, p99 180ms → 52ms, 평균 페이로드 4.8KB → 1.9KB. (2026-02-11 1차 측정의 p99 45ms는 커넥션 풀 워밍업 누락으로 무효, 재측정값 52ms가 최종.)

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 운영 부담을 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어난다.

### REST 유지 + 응답 캐싱 (현행 유지)

- **Pros:** 기존 통신 방식을 그대로 두므로 전환 비용이 없다.
- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 캐시 무효화 난이도 때문에 재고 조회에 적용할 수 없다.

## Consequences

### Positive

- 재고 조회 p99 지연이 SLO 이내로 복귀하고 네트워크 페이로드가 감소한다.
- protobuf 스키마로 서비스 간 계약이 코드로 고정된다.

### Negative

- 내부 gRPC와 외부 REST 두 스택을 동시에 유지해야 한다.
- protobuf 스키마 버전 관리와 코드 생성 과정이 새로 필요하다.

### Risks

- 아직 전환하지 않은 내부 구간이 남아 있어 REST/gRPC 혼재 상태가 이어질 수 있다.
- 스키마 하위 호환을 깨는 변경 시 서비스 간 배포 순서 의존이 생긴다.

## Implementation

- [x] 구현 작업 — `proto/inventory.proto` 정의 및 gRPC 재고 조회 엔드포인트
- [x] 테스트 — k6 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [ ] 모니터링
- [ ] 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** 내부 호출을 기존 REST 경로로 되돌리고 `proto/inventory.proto` 기반 gRPC 스텁·클라이언트를 제거한다. 외부 공개 API는 REST를 유지했으므로 외부 계약 변경은 필요 없다.
- **Migration Cost:** Medium

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007 (원본 결정 로그), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto` — 커밋 b32fc3b
