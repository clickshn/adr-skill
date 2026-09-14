D-007을 `docs/adr/ADR-005-grpc-internal-communication.md`로 옮겼습니다.

- **번호:** docs/adr/에 ADR-001부터 004까지 있어서 다음 번호인 005를 붙였습니다.
- **Status:** 원본에 "확정, 시행 중"으로 적혀 있어 Accepted로 했습니다. Date는 시행을 시작한 2026-03-02입니다.
- **Decision Source:** 플랫폼팀이 내린 결정이라 Human으로 했고, 규칙에 따라 Confidence는 넣지 않았습니다.
- **Alternatives:** 원본에 적힌 근거를 그대로 옮겼습니다. 재검토 조건은 GraphQL 페더레이션에만 있어서("플랫폼팀 4명 이상") Review Trigger도 그 한 줄만 적었습니다. "REST 유지 + 응답 캐싱"은 원본에 재검토 조건이 없어 Recheck if 줄을 빼 두었습니다.

**원본과 수치가 다른 곳이 하나 있습니다.** D-007에는 gRPC 전환 후 p99가 45ms로 적혀 있습니다. 그런데 근거 문서 `bench/grpc-loadtest-2026-02.md`를 보면 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이고, 최종값은 **52ms**입니다(재측정 2026-02-18). ADR에는 52ms를 쓰고, 이 차이를 Evidence에 한 줄로 적었습니다. 52ms여도 SLO(100ms) 안이라 결정 근거는 그대로입니다. 페이로드 약 60% 감소(4.8KB → 1.9KB)는 원본과 벤치 문서가 같습니다.

**`docs/decisions.md`에서 D-007 항목을 지웠습니다.** D-001부터 D-004도 ADR-001부터 004로 옮기면서 로그에서 빠진 것으로 보여, 같은 방식을 따랐습니다. 원본에 포인터를 남기고 싶으시면 `git checkout -- docs/decisions.md`로 되돌린 뒤 한 줄만 추가하면 됩니다.
