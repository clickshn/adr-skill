# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 호출 (현재 checkout ↔ inventory 구간 시행 중)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 외부 공개 API는 REST로 유지해야 한다.
- 플랫폼팀 인원이 2명이라 스키마 관리·게이트웨이 운영 부담이 큰 방식은 감당할 수 없다.
- 재고 데이터는 실시간성이 필요하다.

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC로 전환하고 외부 공개 API는 REST를 유지한다.
- **Implementation:** `proto/inventory.proto`에 `inventory.v1.InventoryService.GetStock`을 정의했고, 2026-03-02부터 checkout ↔ inventory 구간에 시행 중이다.

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회 p99가 SLO(100ms) 이내로 내려갔다.
2. 페이로드 크기가 약 60% 줄었다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md`(2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회) 결과는 REST+JSON → gRPC 기준 p50 41ms → 12ms, p99 180ms → 52ms, 평균 페이로드 4.8KB → 1.9KB(약 60% 감소)다. 원본 로그(D-007)의 p99 45ms는 커넥션 풀 워밍업을 빠뜨려 폐기된 1차 측정값(2026-02-11)이며, 벤치 문서가 밝힌 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어난 경우

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 재고 데이터의 실시간성 요구 때문에 캐시 무효화가 어렵다.

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 52ms로 SLO(100ms) 이내가 된다(부하테스트 기준).
- 호출당 페이로드가 약 60% 줄어든다.

### Negative

- 내부 통신은 gRPC, 외부 공개 API는 REST로 두 프로토콜을 함께 운영해야 한다.
- protobuf 스키마(`proto/`)를 관리하고 버전을 붙여야 한다(현재 `inventory.v1`).

### Risks

- 결정은 내부 동기 호출 전체가 대상이지만 시행된 곳은 checkout ↔ inventory 구간뿐이다. 나머지 구간의 전환 일정은 원본에 기록이 없다.

## Implementation

- [x] 구현 작업: checkout ↔ inventory 구간 gRPC 전환(`proto/inventory.proto`, 2026-03-02 시행). 나머지 내부 구간은 기록 없음
- [x] 테스트: 부하테스트 `bench/grpc-loadtest-2026-02.md`
- [ ] 모니터링: 원본과 저장소에 기록 없음
- [ ] 문서/설정 업데이트: `docs/decisions.md`의 D-007 원본 처리(삭제 또는 이관 표시). 사용자 확인 대기

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 재고 조회를 REST+JSON 호출로 되돌리고 `InventoryService.GetStock` gRPC 엔드포인트를 걷어낸다. 되돌리면 피크 시간 p99 SLO 초과 문제가 다시 생긴다. 저장소에 서비스 코드가 없어서 REST 경로가 아직 남아 있는지는 확인하지 못했다.
- **Migration Cost:** Low (현재 전환 범위가 checkout ↔ inventory 1구간, RPC 1개(`GetStock`)뿐이다)

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:**
  - `docs/decisions.md` D-007 (원본 결정 로그)
  - `bench/grpc-loadtest-2026-02.md` (부하테스트 결과)
  - `proto/inventory.proto` (gRPC 서비스 정의)
  - 커밋 `979e62c`: 위 파일이 모두 이 커밋에서 추가됐다. `919fb33`(feat(inventory): gRPC 재고 조회 엔드포인트)와 `4b0137d`(docs: gRPC 부하테스트 결과 추가)는 파일 변경이 없는 빈 커밋이다.
