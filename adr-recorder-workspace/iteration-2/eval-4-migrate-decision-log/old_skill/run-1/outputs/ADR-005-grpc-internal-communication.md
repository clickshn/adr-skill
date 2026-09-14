# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 통신 (현재 checkout ↔ inventory 구간 시행 중)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 지연 SLO: p99 100ms 이하
- 외부 공개 API는 REST로 유지해야 함
- 운영 인원: 플랫폼팀 2명
- 재고 데이터는 실시간성이 필요함 (캐시 적용이 어려움)

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST — 두 프로토콜 병행
- **Implementation:** `proto/inventory.proto`의 `inventory.v1.InventoryService.GetStock` 정의. 2026-03-02부터 checkout ↔ inventory 구간에 시행 중.

## Rationale

1. 부하테스트에서 p99가 180ms → 52ms로 줄어 SLO(100ms)를 충족한다.
2. 평균 페이로드가 4.8KB → 1.9KB로 약 60% 줄어 주문당 6회 호출의 직렬화 비용이 감소한다.
3. 외부 공개 API는 REST로 유지하므로 외부 소비자에게 영향이 없다.

## Evidence

- **Benchmark:** k6, 500 VU, 10분, checkout → inventory 재고 조회 (2026-02-18) — REST+JSON p50 41ms / p99 180ms / 평균 페이로드 4.8KB → gRPC p50 12ms / p99 52ms / 1.9KB. 원본 D-007에 적힌 p99 45ms는 커넥션 풀 워밍업이 누락된 1차 측정(2026-02-11) 값이며, 여기서는 재측정 최종값 52ms를 기재함.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리·게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 운영 부담을 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움
- **Rejected because:** 실시간 재고 데이터의 캐시 무효화 문제를 해결할 수 없음

## Consequences

### Positive

- checkout ↔ inventory 구간 p99 지연이 SLO 안으로 들어옴 (벤치마크 기준)
- 페이로드 크기 감소로 네트워크·직렬화 비용 절감

### Negative

- 내부(gRPC)와 외부(REST) 두 프로토콜을 병행 운영해야 함
- protobuf 스키마(`proto/`)의 버전 관리가 필요함

### Risks

- p99 52ms는 부하테스트 값이며, 프로덕션 실측값은 아직 기록되지 않음
- checkout ↔ inventory 외 내부 구간은 아직 REST로 남아 있어 전환이 부분적인 상태임

## Implementation

- [x] 구현 작업: `proto/inventory.proto`에 `GetStock` 정의, checkout ↔ inventory 구간 적용 (2026-03-02~)
- [ ] 구현 작업: 나머지 내부 서비스 간 동기 호출을 gRPC로 전환
- [x] 테스트: k6 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [ ] 모니터링: 프로덕션 피크 시간 p99 추적 (SLO 100ms)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 호출을 REST 클라이언트로 되돌린다. 외부 공개 API는 REST로 유지 중이어서 영향이 없다.
- **Migration Cost:** Medium

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` (D-007 원본), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto` — 이 파일들은 커밋 d028f54에서 추가됨. d6db083(feat(inventory): gRPC 재고 조회 엔드포인트), cc95ed7(docs: gRPC 부하테스트 결과 추가)는 파일 변경이 없는 커밋임.
