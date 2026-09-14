D-007을 `docs/adr/ADR-005-grpc-internal-communication.md`로 옮겼습니다.

- **번호:** docs/adr/에 ADR-001~004가 이미 있어서 005로 만들었습니다.
- **Status / Source:** 기존 결정 로그를 옮기는 것이라 Status는 Accepted입니다. 플랫폼팀이 내린 결정이라 Decision Source는 Human이고, 그래서 Confidence 필드는 뺐습니다.
- **Date:** 원본에 확정일이 없어서 원본에 적힌 시행 시작일 2026-03-02를 넣었습니다.
- **수치가 원본과 다릅니다:** D-007에는 gRPC p99가 45ms로 적혀 있습니다. 그런데 D-007이 근거로 든 `bench/grpc-loadtest-2026-02.md`를 보면, 45ms는 커넥션 풀 워밍업을 빼먹은 1차 측정(2026-02-11) 값입니다. 벤치 문서는 다시 측정한 52ms를 최종값으로 적어 두었습니다. 그래서 ADR에는 최종값(p99 180ms → 52ms, 페이로드 4.8KB → 1.9KB로 약 60% 감소)을 쓰고, 이 차이를 Evidence에 한 줄로 남겼습니다. 두 값 모두 SLO(100ms) 안이라 결정의 결론은 같습니다.
- **Alternatives / Review Trigger:** 원본에 있는 대안 두 가지(GraphQL 페더레이션, REST 유지 + 응답 캐싱)만 옮겼습니다. Review Trigger에는 원본에 있는 재검토 조건 "플랫폼팀 4명 이상" 하나만 넣었습니다. 응답 캐싱은 원본에 재검토 조건이 없어서 그 칸은 비워 두었습니다.
- **Implementation / References:** 저장소에서 관련 커밋 919fb33(`proto/inventory.proto`, gRPC 재고 조회 엔드포인트)과 4b0137d(부하테스트 결과)를 찾아 연결했습니다.
- `docs/decisions.md`는 수정하지 않았습니다.

원본 `docs/decisions.md`의 D-007 항목은 어떻게 할까요?
1. 항목을 삭제한다
2. 항목은 남기고 "ADR-005로 이관됨" 표시만 붙인다 (원하시면 이때 45ms도 52ms로 고쳐 두겠습니다)
