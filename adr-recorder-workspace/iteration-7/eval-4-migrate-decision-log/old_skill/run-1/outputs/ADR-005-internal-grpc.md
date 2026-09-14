# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 통신 (현재 시행 구간: checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

이 ADR은 결정 로그 docs/decisions.md의 D-007을 이관한 것이다. 원본 상태는 "확정, 2026-03-02부터 checkout ↔ inventory 구간 시행 중"이고, 담당은 플랫폼팀이다.

### Constraints

- 피크 시간 p99 지연 SLO: 100ms
- 플랫폼팀 인원 2명 (스키마·게이트웨이를 추가로 운영할 여력이 없음)
- 재고 데이터는 실시간성이 필요함 (캐시 무효화가 어려움)

## Decision

### Selected

- **Technology:** gRPC + protobuf (proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Implementation:** 첫 적용 구간은 checkout → inventory 재고 조회다. proto/inventory.proto에 `inventory.v1.InventoryService/GetStock`이 정의되어 있다.

## Rationale

1. 사내 부하테스트에서 p99가 180ms에서 52ms로 줄어 SLO(100ms) 안에 들어왔다.
2. 평균 페이로드가 약 60% 줄었다(4.8KB → 1.9KB). 호출당 직렬화 비용이 줄어 주문당 6회 호출의 누적 지연도 줄어든다.
3. 검토한 대안들은 인력 제약(플랫폼팀 2명)이나 재고 데이터의 실시간성 요구와 맞지 않았다.

## Evidence

- **Benchmark:** bench/grpc-loadtest-2026-02.md (2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회). REST+JSON은 p50 41ms / p99 180ms / 평균 페이로드 4.8KB, gRPC는 p50 12ms / p99 52ms / 1.9KB였다. 원본 D-007에 적힌 p99 45ms는 커넥션 풀 워밍업이 빠진 1차 측정(2026-02-11) 값이다. 벤치 문서가 최종값으로 명시한 52ms를 여기에 기록했다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 이 부담을 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해서 캐시 무효화가 어렵다.
- **Rejected because:** 실시간성이 필요한 재고 조회에는 캐싱이 맞지 않는다.

## Consequences

### Positive

- 부하테스트 기준으로 checkout → inventory 구간 p99가 SLO(100ms) 안에 들어온다(180ms → 52ms).
- 페이로드가 약 60% 줄어든다.
- 외부 공개 API는 REST로 유지되어 외부 소비자에게는 영향이 없다.

### Negative

- 외부용 REST와 내부용 gRPC, 두 프로토콜 스택을 함께 운영해야 한다.
- 내부 인터페이스마다 protobuf 스키마(proto/)를 관리하고 버전(`inventory.v1` 등)을 올려야 한다.

### Risks

- 근거 수치는 부하테스트(k6, 10분)에서 나온 것이다. 저장소에는 전환 후 운영 환경에서 측정한 p99 기록이 없다.
- 원본 결정 로그의 p99 45ms는 폐기된 1차 측정값이다. 원본을 인용하면 개선 폭을 과대 평가할 수 있다.

## Implementation

- [x] 구현 작업: checkout ↔ inventory 구간 gRPC 전환 (2026-03-02부터 시행, proto/inventory.proto)
- [ ] 구현 작업: 나머지 내부 동기 호출 구간 전환 (결정 범위는 내부 동기 호출 전체, 현재 시행 구간은 checkout ↔ inventory뿐)
- [x] 테스트: 부하테스트 (bench/grpc-loadtest-2026-02.md)
- [ ] 모니터링: 전환 구간의 운영 p99를 SLO(100ms) 기준으로 추적 (저장소에서 확인되지 않음)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout → inventory 호출을 REST+JSON으로 되돌린다. 외부 공개 API가 REST로 유지되고 있어 REST 스택 자체는 남아 있지만, inventory의 REST 재고 조회 엔드포인트가 지금도 살아 있는지는 저장소에서 확인할 수 없다. 되돌리면 p99 SLO 초과 문제가 다시 생긴다.
- **Migration Cost:** Low (현재 전환 범위는 1개 구간, 1개 RPC(GetStock)이다. 전환 구간이 늘어날수록 비용도 커진다.)

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** docs/decisions.md (D-007, 원본), bench/grpc-loadtest-2026-02.md, proto/inventory.proto. 두 파일은 커밋 979e62c에서 추가되었다. 커밋 919fb33(feat(inventory): gRPC 재고 조회 엔드포인트)과 4b0137d(docs: gRPC 부하테스트 결과 추가)는 변경 파일이 없는 빈 커밋이다.
