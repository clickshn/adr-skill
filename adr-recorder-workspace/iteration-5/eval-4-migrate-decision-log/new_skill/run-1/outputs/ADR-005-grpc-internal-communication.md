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

- 내부 호출 p99 지연 SLO는 100ms다.
- 외부 공개 API는 REST로 유지해야 한다.
- 플랫폼팀은 2명이다. 이 인원으로 운영 부담을 감당할 수 있어야 한다.
- 재고 데이터는 실시간성이 필요하다.

## Decision

### Selected

- **Technology:** gRPC + Protocol Buffers (proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** checkout ↔ inventory 구간부터 적용 (2026-03-02 시행). 계약은 `proto/inventory.proto`에 정의한다(`inventory.v1.InventoryService.GetStock`).

## Rationale

1. 사내 부하테스트에서 재고 조회 p99가 180ms에서 52ms로 줄어 SLO(100ms) 안으로 들어왔다.
2. 평균 페이로드 크기가 약 60% 줄었다(4.8KB → 1.9KB).
3. 외부 공개 API는 REST로 유지하므로 외부 클라이언트에는 영향이 없다.

## Evidence

- **Benchmark:** 2026-02-18 k6 부하테스트(500 VU, 10분, checkout → inventory 재고 조회). REST+JSON p50 41ms / p99 180ms / 평균 페이로드 4.8KB, gRPC p50 12ms / p99 52ms / 평균 페이로드 1.9KB. 원본 결정 로그(D-007)는 p99를 45ms로 적었지만, 이 값은 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 결과다. 벤치 문서가 최종값으로 명시한 52ms를 기재한다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 그 운영 부담을 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어난 경우

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해서 캐시 무효화가 어렵다.
- **Rejected because:** 실시간성이 필요한 재고 데이터에 캐시 무효화를 적용하기 어렵다.

## Consequences

### Positive

- checkout → inventory 재고 조회 p99 지연이 SLO 안으로 들어온다(부하테스트 기준 52ms).
- 서비스 간 전송 페이로드가 약 60% 줄어든다.

### Negative

- 내부(gRPC)와 외부(REST) 두 가지 통신 방식을 함께 운영해야 한다.
- 서비스 간 계약을 protobuf 스키마(`proto/`)로 관리하고 버전을 붙여야 한다.

### Risks

- 개선 수치는 부하테스트 기준이다. 시행 이후 운영 환경의 p99 실측치는 기록돼 있지 않다.
- 원본 결정 로그의 p99 값(45ms)이 최종 측정값(52ms)과 다르다. 원본을 인용할 때 수치가 틀릴 수 있다.

## Implementation

- [x] 구현 작업: checkout ↔ inventory 재고 조회 gRPC 전환 (2026-03-02 시행, `proto/inventory.proto`)
- [ ] 구현 작업: 나머지 내부 서비스 간 동기 호출 전환 (결정 범위. 원본에는 진행 현황이 없다)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout → inventory 호출을 REST+JSON으로 되돌린다. 외부 공개 API가 REST로 유지되므로 REST 스택은 남아 있다. 현재 전환된 구간은 checkout ↔ inventory 하나지만, 다른 구간이 전환될수록 롤백 범위가 커진다.
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007(원본 결정 로그), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`. 관련 커밋: 7b5dcd9(위 파일 최초 추가), 46e7d7b `feat(inventory): gRPC 재고 조회 엔드포인트`, ea4a163 `docs: gRPC 부하테스트 결과 추가`.
