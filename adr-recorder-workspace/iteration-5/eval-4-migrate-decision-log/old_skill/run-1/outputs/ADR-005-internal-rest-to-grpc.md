# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform — 내부 서비스 간 동기 호출 (현재 시행 구간: checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.
이 ADR은 docs/decisions.md의 D-007(상태: 확정, 2026-03-02부터 checkout ↔ inventory 구간 시행 중, 담당: 플랫폼팀)을 2026-09-11에 이관한 것이다.

### Constraints

- 피크 시간 p99 지연 SLO 100ms
- 외부 공개 API는 REST 유지
- 운영 인력: 플랫폼팀 2명
- 재고 데이터는 실시간성이 필요함

## Decision

### Selected

- **Technology:** gRPC (protobuf)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** checkout ↔ inventory 재고 조회부터 적용 (proto/inventory.proto, `inventory.v1.InventoryService.GetStock`), 2026-03-02부터 시행 중

## Rationale

1. 주문당 평균 6회인 재고 조회에서 REST+JSON 직렬화 비용이 피크 시간 p99 SLO(100ms) 초과의 원인이었다.
2. 사내 부하테스트에서 gRPC로 바꾸면 p99가 SLO 이내로 내려왔고, 페이로드 크기는 약 60% 줄었다.

## Evidence

- **Benchmark:** k6, 500 VU, 10분, checkout → inventory 재고 조회 (2026-02-18 최종 측정): REST+JSON p50 41ms / p99 180ms / 평균 페이로드 4.8KB → gRPC p50 12ms / p99 52ms / 1.9KB (페이로드 약 60% 감소). 원본 로그의 "p99 45ms"는 커넥션 풀 워밍업 누락으로 다시 측정한 1차 측정(2026-02-11) 값이라, 벤치 문서가 최종값으로 명시한 52ms를 적었다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 그 운영 부담을 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움
- **Rejected because:** 실시간 재고 데이터에서는 캐시 무효화를 감당하기 어려움

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 SLO(100ms) 이내로 들어옴 (부하테스트 기준 180ms → 52ms)
- 호출당 페이로드 약 60% 감소 (4.8KB → 1.9KB)

### Negative

- 내부(gRPC)와 외부(REST) 두 프로토콜을 함께 운영해야 함
- protobuf 스키마(proto/inventory.proto)를 관리해야 함

### Risks

- 현재 시행 구간은 checkout ↔ inventory뿐이라, 다른 내부 동기 호출은 전환이 끝날 때까지 REST와 섞여 있음
- 시행(2026-03-02) 이후의 운영 환경 p99 실측치가 저장소에 없어, 부하테스트에서 본 개선폭이 운영에서도 유지되는지는 확인되지 않음

## Implementation

- [x] 구현 작업: checkout → inventory 재고 조회 gRPC 전환 (`InventoryService.GetStock`)
- [ ] 구현 작업: 나머지 내부 서비스 간 동기 호출 gRPC 전환
- [x] 테스트: 부하테스트 (bench/grpc-loadtest-2026-02.md)
- [ ] 모니터링: 운영 환경 p99 지표·알림 (저장소에서 확인되지 않음)
- [x] 문서/설정 업데이트: D-007 → 본 ADR 이관

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 재고 조회 호출을 REST+JSON으로 되돌린다. 그러면 부하테스트 기준 p99 180ms로 SLO(100ms)를 다시 초과하게 된다. 저장소에 서비스 코드가 없어, 기존 REST 엔드포인트가 남아 있는지는 확인할 수 없다.
- **Migration Cost:** Low (현재 시행 범위인 RPC 1개 기준. 전환 구간이 늘어날수록 커짐)

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 다시 검토

## References

- **Documentation:** docs/decisions.md (D-007 원본), bench/grpc-loadtest-2026-02.md, proto/inventory.proto, 커밋 46e7d7b (feat(inventory): gRPC 재고 조회 엔드포인트), ea4a163 (docs: gRPC 부하테스트 결과 추가)
