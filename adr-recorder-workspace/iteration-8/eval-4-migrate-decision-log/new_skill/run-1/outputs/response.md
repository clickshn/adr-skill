D-007을 `docs/adr/ADR-005-grpc-internal-communication.md`로 옮겼습니다.

- **번호:** `docs/adr/`에 ADR-001~004가 있어서 005를 붙였습니다.
- **Status / Date:** 기존 결정 로그를 옮긴 것이라 Status는 Accepted입니다. Date는 오늘이 아니라 원본에 적힌 시행일인 2026-03-02입니다.
- **Decision Source:** 사람이 기록한 결정이라 Human으로 적었고, 그래서 Confidence는 생략했습니다.
- **Alternatives:** 원본에 있는 두 대안(GraphQL 페더레이션, REST 유지 + 응답 캐싱)과 기각 사유를 그대로 옮겼습니다. Review Trigger에는 "플랫폼팀이 4명 이상으로 늘면 GraphQL 페더레이션 재검토"를 넣었습니다.
- **Reversibility:** 저장소에는 `proto/inventory.proto`만 있고 서비스 코드는 없습니다. 그래서 inventory 쪽 REST 조회 경로가 남아 있는지는 확인하지 못했다고 적었습니다.

**원본과 수치가 다릅니다.** D-007에는 gRPC p99가 "45ms"로 적혀 있습니다. 그런데 근거 문서 `bench/grpc-loadtest-2026-02.md`를 보면 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이고, 최종값은 재측정한 **52ms**입니다. ADR의 Evidence에는 52ms를 쓰고, 그 줄에 차이를 적어 두었습니다. 52ms도 SLO(100ms) 이내라 결정 결론은 바뀌지 않습니다. `docs/decisions.md`는 고치지 않았습니다.

원본 `docs/decisions.md`의 D-007 항목은 어떻게 할까요?

1. 항목을 지운다
2. 항목은 두고 "ADR-005로 이관됨" 표시만 남긴다 (필요하면 45ms → 52ms도 함께 고침)
3. 그대로 둔다
