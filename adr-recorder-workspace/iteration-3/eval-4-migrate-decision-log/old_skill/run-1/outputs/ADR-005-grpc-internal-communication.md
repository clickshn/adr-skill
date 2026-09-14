# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 통신 (2026-03-02부터 checkout ↔ inventory 구간 시행 중)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 넘는다.

### Constraints

- p99 지연 SLO: 100ms
- 운영 인력: 플랫폼팀 2명
- 재고 데이터는 실시간성이 필요함
- 외부 공개 API는 REST로 유지

## Decision

### Selected

- **Technology:** gRPC (protobuf)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST (이원화)
- **Implementation:** checkout ↔ inventory 재고 조회 구간부터 전환, 2026-03-02 시행

## Rationale

1. 사내 부하테스트에서 p99가 180ms → 52ms로 줄어 SLO(100ms) 안에 들어온다.
2. 평균 페이로드가 약 60% 줄어(4.8KB → 1.9KB) REST+JSON 직렬화 비용 문제를 직접 해결한다.
3. 대안(GraphQL 페더레이션, REST 유지 + 응답 캐싱)은 운영 인력 제약과 재고 데이터 실시간성 요구 때문에 기각했다.

## Evidence

- **Benchmark:** 사내 부하테스트(2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회) 결과 REST+JSON 대비 gRPC: p50 41ms → 12ms, p99 180ms → 52ms, 평균 페이로드 4.8KB → 1.9KB. 원본 D-007에 적힌 p99 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이고, 벤치 문서의 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 큼
- **Rejected because:** 현재 인원(플랫폼팀 2명)으로는 그 운영 부담을 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해서 캐시 무효화가 어려움
- **Rejected because:** 재고 데이터의 실시간성 요구와 캐시 무효화 난이도

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 SLO 안으로 들어옴 (벤치 기준 52ms)
- 호출당 페이로드가 약 60% 줄어듦

### Negative

- 내부(gRPC)와 외부(REST)로 통신 프로토콜이 이원화됨

### Risks

- 커넥션 풀 워밍업이 빠지면 측정·운영 성능이 달라질 수 있음 (1차 부하테스트에서 45ms로 잘못 측정된 원인)

## Implementation

- [x] checkout ↔ inventory 재고 조회 gRPC 엔드포인트 구현 및 시행 (2026-03-02~)
- [x] 부하테스트로 전환 효과 검증 (bench/grpc-loadtest-2026-02.md)
- [ ] 나머지 내부 서비스 간 동기 호출 전환

## Reversibility

- **Reversible:** Partial
- **Rollback:** 외부 공개 API는 REST 그대로라서 영향이 없다. 내부 전환 구간은 REST 호출로 다시 돌려야 한다.
- **Migration Cost:** Medium

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘면 GraphQL 페더레이션 재검토

## References

- **Documentation:** docs/decisions.md D-007 (원본 결정 로그), bench/grpc-loadtest-2026-02.md, 커밋 25dad14 (feat(inventory): gRPC 재고 조회 엔드포인트), 15d4779 (docs: gRPC 부하테스트 결과 추가)
