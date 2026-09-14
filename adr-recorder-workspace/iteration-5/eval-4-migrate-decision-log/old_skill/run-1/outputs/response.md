D-007을 `docs/adr/ADR-005-internal-rest-to-grpc.md`로 옮겼습니다. 기존 ADR이 001–004까지 있어서 005번을 붙였습니다. `docs/decisions.md`는 수정하지 않았습니다.

**원본 수치가 벤치 문서와 다릅니다.** D-007에는 p99가 180ms → 45ms로 적혀 있습니다. 그런데 `bench/grpc-loadtest-2026-02.md`에 따르면 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정값이고, 다시 측정한 최종값은 **52ms**입니다. ADR에는 52ms를 적고, 이유를 Evidence에 한 줄로 남겼습니다. 52ms도 SLO(100ms)보다 낮으니 결정 자체는 그대로 유효합니다.

ADR 주요 항목:
- **Status:** 원본에 "확정·시행 중"으로 되어 있어 Accepted로 했습니다.
- **Date:** 시행 시작일인 2026-03-02입니다.
- **Decision Source:** 원본에 담당(플랫폼팀)이 적힌 사람의 결정이라 Human으로 했고, 그래서 Confidence는 넣지 않았습니다.
- **Alternatives:** 원본의 기각 사유만 옮겼습니다. 원본에 없는 장점이나 REST 캐싱의 재검토 조건은 채우지 않았습니다.
  - GraphQL 페더레이션: 플랫폼팀 2명으로 운영 불가
  - REST + 응답 캐싱: 재고 실시간성 때문에 캐시 무효화가 어려움
- **Review Trigger:** "플랫폼팀이 4명 이상으로 늘면 GraphQL 페더레이션 재검토"
- **저장소에서 확인해 채운 섹션:**
  - Implementation: `proto/inventory.proto`의 `InventoryService.GetStock` 기준. 나머지 내부 호출 전환과 운영 모니터링은 저장소에서 확인되지 않아 미완료로 두었습니다.
  - Reversibility: 현재 전환된 RPC가 1개라 되돌리기 쉽습니다(Low). 다만 REST로 돌아가면 p99가 다시 SLO를 넘습니다.

원본 `docs/decisions.md`의 D-007 항목은 어떻게 할까요?
1. 항목을 삭제
2. 항목은 두고 "→ ADR-005로 이관됨" 표시만 추가
3. 그대로 둠

원본의 "p99 45ms"도 52ms로 바로잡을지 함께 알려주세요.
