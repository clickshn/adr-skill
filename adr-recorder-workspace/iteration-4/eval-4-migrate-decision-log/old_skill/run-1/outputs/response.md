D-007을 ADR로 옮겼습니다. 새 파일은 `docs/adr/ADR-005-grpc-internal-communication.md`입니다.

**옮긴 내용**
- **번호:** 이미 있는 ADR-001~004 다음 번호인 005를 붙였습니다.
- **Status:** Accepted로 했습니다. 원본에 "확정, 2026-03-02부터 checkout ↔ inventory 구간 시행 중"으로 적혀 있기 때문입니다. Date는 시행일인 2026-03-02입니다.
- **Decision Source:** 기록된 사람의 결정이라 Human으로 했고, 그래서 Confidence 필드는 뺐습니다.
- **대안:** 원본의 두 대안(GraphQL 페더레이션, REST 유지 + 응답 캐싱)과 기각 근거를 그대로 옮겼습니다. Review Trigger는 원본의 재검토 조건 하나로, 플랫폼팀이 4명 이상이 되면 GraphQL을 다시 검토한다는 내용입니다.
- **Evidence:** `bench/grpc-loadtest-2026-02.md`의 k6 부하테스트 수치를 넣었습니다.

**확인이 필요한 점**
- **p99 수치 불일치:** D-007에는 gRPC p99가 45ms로 적혀 있지만, 벤치 문서의 최종값은 52ms입니다. 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정값입니다. ADR에는 52ms를 쓰고, 불일치 사실은 Evidence에 한 줄로 남겼습니다. 두 값 모두 SLO 100ms 안이라 결론은 같습니다.
- **빈 커밋:** 관련 커밋 adb2e90과 31a2593에는 파일 변경이 없습니다. `proto/inventory.proto`와 벤치 문서는 실제로 b1e5947에서 추가됐습니다. 이 사실은 References에 적어 두었습니다.
- **롤백 경로:** 저장소에 서비스 구현 코드가 없어서, 되돌릴 때 쓸 inventory의 REST 엔드포인트가 아직 남아 있는지는 확인하지 못했습니다.

`docs/decisions.md`는 수정하지 않았습니다. 로그에서 D-007을 지울까요, 아니면 "ADR-005로 이관" 표시만 남길까요? 원본의 p99 45ms도 52ms로 고칠까요?
