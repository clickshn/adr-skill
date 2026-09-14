# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 호출 (1차 적용: checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 외부 공개 API는 REST를 유지해야 한다.
- 플랫폼팀 인원이 2명이라 운영 부담이 큰 구조는 감당할 수 없다.
- 재고 데이터는 실시간성이 필요하다.
- 이관 원본인 docs/decisions.md D-007에는 확정일이 따로 적혀 있지 않다. Date는 원본에 기재된 시행 시작일(2026-03-02)을 따른다.

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** checkout ↔ inventory 재고 조회 구간(`inventory.v1.InventoryService/GetStock`, proto/inventory.proto)에 1차 적용했으며 2026-03-02부터 시행 중

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회 p99가 180ms에서 52ms로 줄어 SLO(100ms) 안에 들어왔다.
2. 평균 페이로드 크기가 약 60% 줄었다(4.8KB → 1.9KB).
3. 대안인 GraphQL 페더레이션은 현 인원으로 운영이 불가능하고, REST 유지 + 응답 캐싱은 재고 데이터의 실시간성 요구와 맞지 않는다.

## Evidence

- **Benchmark:** k6, 500 VU, 10분, checkout → inventory 재고 조회 (2026-02-18, bench/grpc-loadtest-2026-02.md). REST+JSON은 p50 41ms / p99 180ms / 평균 페이로드 4.8KB, gRPC는 p50 12ms / p99 52ms / 1.9KB. 원본 D-007에 적힌 "p99 45ms"는 커넥션 풀 워밍업이 빠진 1차 측정(2026-02-11) 값이다. 벤치 문서는 재측정한 52ms를 최종값으로 명시하므로 이 ADR은 최종값을 쓴다. 두 값 모두 SLO 안이라 결론은 같다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 그 운영 부담을 현 인원(플랫폼팀 2명)으로 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.

## Consequences

### Positive

- checkout → inventory 재고 조회의 p99 지연이 SLO 안으로 들어온다(부하테스트 기준 52ms).
- 서비스 간 페이로드가 약 60% 줄어든다.

### Negative

- 내부(gRPC)와 외부(REST) 두 가지 통신 방식을 함께 운영해야 한다.
- 내부 호출 계약을 protobuf 스키마(proto/)로 관리해야 한다.

### Risks

- 근거 수치는 부하테스트 결과이며, 시행 이후 프로덕션 지연 측정 자료는 저장소에 없다.
- 원본 결정 로그에 폐기된 1차 측정값(p99 45ms)이 남아 있어 수치가 혼동될 수 있다.

## Implementation

- [x] 구현 작업: inventory gRPC 재고 조회 엔드포인트 (proto/inventory.proto, 커밋 919fb33). checkout ↔ inventory 구간은 2026-03-02부터 시행 중
- [ ] 구현 작업: 나머지 내부 서비스 간 동기 호출 전환 (대상 구간은 원본에 명시되지 않음)
- [x] 테스트: k6 부하테스트 (bench/grpc-loadtest-2026-02.md, 커밋 4b0137d)
- [ ] 모니터링: 전환 구간 p99 SLO(100ms) 추적 (저장소에서 관련 설정은 확인되지 않음)
- [ ] 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 재고 조회 호출을 REST+JSON으로 되돌린다. 현재 gRPC 계약은 proto/inventory.proto의 단일 RPC(GetStock) 하나라 범위가 작고, 외부 공개 API는 REST 그대로라 외부 영향은 없다. 되돌리면 피크 시간 p99 SLO 초과 문제가 다시 생긴다. 저장소에 서비스 코드가 없어 기존 REST 엔드포인트가 남아 있는지는 확인하지 못했다.
- **Migration Cost:** Low (현재 전환 범위 기준이며, 전환 구간이 늘어날수록 커진다)

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어날 때 (GraphQL 페더레이션 재검토)

## References

- **Documentation:** docs/decisions.md D-007 (이관 원본), bench/grpc-loadtest-2026-02.md, 커밋 919fb33 (feat(inventory): gRPC 재고 조회 엔드포인트), 커밋 4b0137d (docs: gRPC 부하테스트 결과 추가)
