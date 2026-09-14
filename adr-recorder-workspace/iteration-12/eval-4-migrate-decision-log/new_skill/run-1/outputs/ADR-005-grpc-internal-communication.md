# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출을 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform (checkout ↔ inventory 내부 통신)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 내부 호출 p99 지연 SLO 100ms.
- 재고 데이터는 실시간성이 필요해 응답 캐싱으로 호출량을 줄이기 어렵다.
- 운영 인력은 플랫폼팀 2명.
- 외부 공개 API의 REST 계약은 그대로 유지해야 한다.

## Decision

### Selected

- **Technology:** gRPC + Protocol Buffers(proto3).
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지(프로토콜 이원화).
- **Implementation:** `proto/inventory.proto`의 `inventory.v1.InventoryService.GetStock`로 재고 조회를 제공하며, 2026-03-02부터 checkout ↔ inventory 구간에 시행 중이다.

## Rationale

1. 부하테스트에서 p99 지연이 SLO(100ms) 아래로 내려와 문제의 직접 원인인 직렬화 비용을 해소했다.
2. 평균 페이로드가 절반 이하로 줄어 주문당 6회 호출되는 구간의 네트워크 비용을 함께 줄였다.
3. 전환 범위를 내부 호출로 한정해 외부 공개 API 소비자에게 영향을 주지 않는다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (k6, 500 VU, 10분, checkout → inventory 재고 조회) — p99 180ms → 52ms, p50 41ms → 12ms, 평균 페이로드 4.8KB → 1.9KB(약 60% 감소). 결정 로그 D-007에 적힌 "p99 45ms"는 커넥션 풀 워밍업이 누락된 1차 측정(2026-02-11) 값이며, 재측정 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 운영 부담을 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어난다.

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 캐시 무효화 난이도 때문에 실시간 재고 조회에 적용할 수 없다.

## Consequences

### Positive

- 재고 조회 p99 지연이 SLO(100ms) 안으로 들어왔다.
- 페이로드 축소로 checkout ↔ inventory 구간의 네트워크 사용량이 줄었다.
- 외부 공개 API는 REST 그대로라 외부 소비자 영향이 없다.

### Negative

- 내부 gRPC와 외부 REST 두 프로토콜을 동시에 운영·관리해야 한다.
- protobuf 스키마 정의와 코드 생성 파이프라인이 새로 필요하다.

### Risks

- proto 스키마 변경 시 필드 번호 호환성을 깨면 서비스 간 호출이 깨진다.
- 커넥션 풀 워밍업이 누락되면 측정·운영 모두에서 지연이 악화된다(1차 부하테스트에서 실제로 관측됨).

## Implementation

- [x] 구현 작업 — `proto/inventory.proto`에 `InventoryService.GetStock` 정의 및 엔드포인트 제공
- [ ] 테스트
- [ ] 모니터링
- [ ] 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 재고 조회를 기존 REST 엔드포인트 호출로 되돌리고 `InventoryService` 사용을 중단한다. 현재 전환 범위가 `GetStock` 1개 RPC라 되돌릴 표면이 좁다.
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md`의 D-007(원본 결정 로그), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto` — 세 파일 모두 커밋 `ac6b178`에 포함되어 있다.
