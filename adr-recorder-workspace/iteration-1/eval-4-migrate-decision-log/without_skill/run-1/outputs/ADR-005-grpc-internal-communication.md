# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02 (checkout ↔ inventory 구간 시행 시작일. 원 기록에 확정일 별도 표기 없음)
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환한다. 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform
- **Decision Source:** Human
- **Owner:** 플랫폼팀
- **Migrated From:** docs/decisions.md D-007 (2026-09-11 이관)

## Context

- checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다.
- REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 넘었다.

## Decision

- 내부 서비스 간 **동기** 호출은 gRPC(protobuf)로 전환한다.
- 외부 공개 API는 REST를 유지한다.
- 2026-03-02부터 checkout ↔ inventory 구간에 시행 중이다. 해당 인터페이스는 `proto/inventory.proto`(`inventory.v1.InventoryService/GetStock`)에 있다.

## Rationale

사내 부하테스트 결과(`bench/grpc-loadtest-2026-02.md`, 2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회):

| 프로토콜 | p50 | p99 | 평균 페이로드 |
| -------- | --: | --: | ------------: |
| REST+JSON | 41ms | 180ms | 4.8KB |
| gRPC | 12ms | 52ms | 1.9KB |

- p99: 180ms → 52ms. SLO 100ms 이내로 들어온다.
- 페이로드 크기: 약 60% 감소 (4.8KB → 1.9KB).

> 수치 정정: 원 결정 로그(D-007)에는 p99가 "180ms → 45ms"로 적혀 있다. 부하테스트 문서를 보면 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정값(2026-02-11)이고, 재측정한 최종값은 **52ms**다. 이 ADR은 최종값을 쓴다. 두 값 모두 SLO 100ms 이내이므로 결론은 달라지지 않는다.

## Alternatives Considered

1. **GraphQL 페더레이션**: 기각. 스키마 관리와 게이트웨이 운영 부담을 현재 인원(플랫폼팀 2명)으로 감당할 수 없다.
2. **REST 유지 + 응답 캐싱**: 기각. 재고 데이터는 실시간성이 필요해서 캐시 무효화가 어렵다.

## Consequences

- 내부 동기 호출에서는 protobuf 스키마(`proto/`)가 서비스 간 계약이 된다. 이후 스키마 버전 관리(`inventory.v1` 같은 패키지 버전)가 필요하다.
- 외부 공개 API(REST)와 내부 API(gRPC) 두 가지 방식을 함께 운영하게 된다.
- 비동기 호출(큐, 이벤트 등)은 이 결정의 범위 밖이다.

## Re-evaluation Triggers

- 플랫폼팀이 **4명 이상**으로 늘어나면 GraphQL 페더레이션을 다시 검토한다.
