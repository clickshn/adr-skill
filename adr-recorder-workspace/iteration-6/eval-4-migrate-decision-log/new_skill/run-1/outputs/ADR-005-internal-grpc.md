# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 서비스 간 내부 동기 통신 (현재 checkout ↔ inventory 구간 시행)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- p99 지연 SLO 100ms
- 외부 공개 API는 REST 유지
- 운영 인원: 플랫폼팀 2명
- 재고 데이터는 실시간성이 필요함
- docs/decisions.md D-007에서 이관한 기록이다. 원본에는 확정일이 따로 없어서 Date에는 시행 시작일(2026-03-02)을 적었다.

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST
- **Implementation:** `proto/inventory.proto`에 `inventory.v1.InventoryService/GetStock` 정의. 2026-03-02부터 checkout ↔ inventory 구간에서 시행 중

## Rationale

1. 사내 부하테스트에서 재고 조회 p99가 180ms에서 52ms로 떨어져 SLO(100ms) 안으로 들어왔다.
2. 평균 페이로드 크기가 약 60% 줄었다.
3. GraphQL 페더레이션은 현 인원으로 운영하기 어렵고, REST 응답 캐싱은 재고 데이터의 실시간성 요구와 맞지 않는다(Alternatives 참고).

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6, 500 VU, 10분, checkout → inventory 재고 조회): REST+JSON p50 41ms / p99 180ms / 평균 페이로드 4.8KB → gRPC p50 12ms / p99 52ms / 1.9KB (페이로드 약 60% 감소). 원본 D-007에 적힌 p99 45ms는 1차 측정(2026-02-11)값인데, 커넥션 풀 워밍업을 빠뜨려 재측정했다. 벤치 문서가 밝힌 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 캐시 무효화가 어렵다
- **Rejected because:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움

## Consequences

### Positive

- 부하테스트 기준 checkout → inventory 재고 조회 p99가 SLO(100ms) 안으로 들어온다(52ms).
- 호출당 페이로드가 약 60% 줄어든다.

### Negative

- 내부는 gRPC, 외부는 REST라서 두 프로토콜을 함께 운영해야 한다.
- 내부 인터페이스 계약을 `proto/` 아래 protobuf 스키마로 관리해야 한다.

### Risks

- 개선 수치는 부하테스트 결과다. 운영 환경에서 잰 수치는 기록되어 있지 않다.
- 결정 범위는 내부 동기 호출 전체인데, 시행 중인 구간은 checkout ↔ inventory뿐이다.

## Implementation

- [x] 재고 조회 RPC 정의 (`proto/inventory.proto`, `InventoryService/GetStock`)
- [x] 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [x] checkout ↔ inventory 구간 시행 (2026-03-02~)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout → inventory 재고 조회를 REST+JSON 호출로 되돌린다. 되돌리면 피크 시간 p99 SLO 초과 문제가 다시 생긴다. 저장소에는 `proto/inventory.proto`만 있고, 서비스 코드와 기존 REST 엔드포인트가 남아 있는지는 확인되지 않는다.
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007(원본 결정 로그), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`. 두 파일은 커밋 b32fc3b에서 추가되었다. 관련 커밋 c32c6dc(feat(inventory): gRPC 재고 조회 엔드포인트)와 102695e(docs: gRPC 부하테스트 결과 추가)에는 파일 변경이 없다.
