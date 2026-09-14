D-007을 `docs/adr/ADR-005-internal-grpc.md`로 옮겼습니다. 기존 ADR이 001~004까지 있어서 번호는 005로 붙였습니다.

- **Status:** 원본에 "확정, 2026-03-02부터 시행 중"으로 적혀 있어서 Proposed가 아닌 Accepted로 했습니다. Date는 시행 시작일인 2026-03-02입니다.
- **Decision Source:** 플랫폼팀이 내린 결정이라 Human으로 했고, 규칙에 따라 Confidence 필드는 뺐습니다.
- **Alternatives / Review Trigger:** GraphQL 페더레이션과 REST 유지 + 응답 캐싱을 원본에 적힌 기각 사유 그대로 옮겼습니다. 재검토 조건은 원본에 있는 "플랫폼팀 4명 이상" 하나뿐이라 Review Trigger에도 그것만 넣었습니다.

**수치 불일치가 하나 있습니다.** D-007에는 gRPC p99가 **45ms**로 적혀 있습니다. 그런데 `bench/grpc-loadtest-2026-02.md`를 보면 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정값이고, 재측정한 최종값은 **52ms**입니다. ADR에는 최종값 180ms → 52ms를 썼고(SLO 100ms는 여전히 충족), 이 차이는 Evidence 섹션에 한 줄로 남겼습니다. 페이로드 약 60% 감소(4.8KB → 1.9KB)는 원본과 벤치 문서가 일치합니다.

원본에 없는 내용은 추측해서 채우지 않았습니다. Reversibility(롤백 방법, 전환 비용)가 원본에 없어서 그 섹션은 넣지 않았습니다. `docs/decisions.md`의 D-007 항목도 그대로 두었습니다. 이관 표시가 필요하면 말씀해 주세요.
