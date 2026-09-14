# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 REST+JSON에서 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 서비스 간 내부 동기 통신 (시행 구간: checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- p99 지연 SLO 100ms
- 외부 공개 API는 REST를 유지한다 (전환 범위는 내부 서비스 간 동기 호출로 한정)
- 플랫폼팀 2명: 스키마 관리·게이트웨이 운영 부담이 큰 방식은 감당할 수 없음
- 재고 데이터는 실시간성이 필요함

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** 2026-03-02부터 checkout ↔ inventory 구간에서 시행 중. 계약은 `proto/inventory.proto`(`inventory.v1.InventoryService/GetStock`)에 정의돼 있다.

## Rationale

1. 사내 부하테스트에서 재고 조회 p99가 180ms → 52ms로 줄어 SLO(100ms) 안으로 들어왔다.
2. 평균 페이로드 크기가 약 60% 줄었다(4.8KB → 1.9KB).
3. GraphQL 페더레이션은 현 인원으로 운영할 수 없고, 응답 캐싱은 재고 실시간성 요구와 맞지 않는다(Alternatives 참조).

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6, 500 VU, 10분, checkout → inventory 재고 조회). REST+JSON은 p50 41ms / p99 180ms / 평균 페이로드 4.8KB, gRPC는 p50 12ms / p99 52ms / 1.9KB. 원본 로그(D-007)에 적힌 "p99 45ms"는 1차 측정(2026-02-11) 값이며, 커넥션 풀 워밍업을 빠뜨려 재측정했다. 여기서는 벤치 문서에 적힌 최종값 52ms를 쓴다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리·게이트웨이 운영 부담
- **Rejected because:** 그 부담을 현 인원(플랫폼팀 2명)으로 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘면

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움
- **Rejected because:** 실시간 재고 요구와 캐싱이 양립하기 어려움

## Consequences

### Positive

- checkout → inventory 재고 조회의 p99 지연과 페이로드 크기가 줄었다(Evidence 참조).
- 외부 공개 API 계약은 그대로다.

### Negative

- 내부는 gRPC, 외부는 REST로 두 프로토콜을 함께 운영해야 한다.
- 서비스 간 계약을 `.proto` 파일로 관리해야 한다.

### Risks

- 결정 범위는 모든 내부 동기 호출인데 시행 구간은 아직 checkout ↔ inventory뿐이다. 나머지 구간의 전환 일정은 원본 로그에 없다.

## Implementation

- [x] 구현 작업: checkout ↔ inventory 구간 gRPC 전환 (2026-03-02 시행, `proto/inventory.proto`)
- [ ] 구현 작업: 나머지 내부 서비스 간 동기 호출 전환
- [x] 테스트: 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [ ] 모니터링: 저장소에서 확인되지 않음
- [ ] 문서/설정 업데이트: `docs/decisions.md` D-007 원본 처리(삭제 또는 이관 표시), 사용자 확인 대기

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout → inventory 호출을 REST+JSON 경로로 되돌리고, 필요하면 `proto/inventory.proto`를 제거한다. 외부 공개 API는 REST 그대로라 영향이 없다. 커밋 `919fb33`은 파일 변경이 없는 커밋이라 `git revert`로는 아무것도 되돌리지 못한다. 저장소에는 proto 정의만 있고 서비스 코드가 없어서, REST 경로가 아직 남아 있는지는 확인되지 않는다. 롤백하면 전환 전 문제(피크 시 p99 SLO 초과)가 다시 생길 수 있다.
- **Migration Cost:** Low (현재 시행 구간 1곳, RPC 1개 `GetStock`. 전환 구간이 늘수록 커짐)

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘면 → GraphQL 페더레이션 재검토

## References

- **Documentation:** `docs/decisions.md` D-007(원본 결정 로그), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`. 관련 커밋: `919fb33` feat(inventory): gRPC 재고 조회 엔드포인트, `4b0137d` docs: gRPC 부하테스트 결과 추가 (두 커밋 모두 파일 변경이 없고, 위 파일들은 `979e62c`에서 추가됨)
