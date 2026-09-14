D-007을 `docs/adr/ADR-005-grpc-internal-communication.md`로 옮겼습니다. docs/adr/에 ADR-001~004가 있어서 번호는 005입니다.

**반영 내용**
- **Status: Accepted.** 원본에 "확정, 2026-03-02부터 checkout ↔ inventory 구간 시행 중"으로 적혀 있어서입니다.
- **Decision Source: Human.** 그래서 Confidence 필드는 뺐습니다.
- **Context / Decision / Alternatives:** 원본의 배경, 결정, 대안 두 개(GraphQL 페더레이션, REST 유지 + 응답 캐싱)와 기각 사유를 그대로 옮겼습니다.
- **Review Trigger:** 원본에 재검토 조건이 있는 건 "플랫폼팀 4명 이상이면 GraphQL 페더레이션 재검토" 하나라 그것만 넣었습니다.
  - REST+캐싱 쪽은 원본에 재검토 조건이 없어서 비워 두었습니다.
- **Evidence:** `bench/grpc-loadtest-2026-02.md`의 실측값을 넣었습니다.
- **Implementation / Reversibility:** `proto/inventory.proto`와 커밋 c32c6dc, 102695e를 보고 작성했습니다.
  - 저장소에 서비스 코드가 없어서 REST 재고 조회 엔드포인트가 아직 남아 있는지는 확인하지 못했습니다. 이 점은 Rollback 항목에 적어 두었습니다.

**원본과 벤치 수치가 다릅니다**
D-007 근거에는 gRPC p99가 **45ms**로 적혀 있습니다. 그런데 벤치 문서를 보면 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이고, 다시 잰 **최종값은 52ms**입니다. ADR에는 최종값 52ms를 쓰고 이 차이를 Evidence에 한 줄로 적었습니다. 52ms도 SLO(100ms) 안이라 결론은 같습니다. 페이로드 약 60% 감소(4.8KB → 1.9KB)는 원본과 맞습니다.

`docs/decisions.md`는 건드리지 않았습니다. 두 가지 여쭤볼게요.
1. 원본 D-007 항목을 지울까요, 아니면 "ADR-005로 이관됨" 표시만 남길까요?
2. D-007의 p99 45ms를 52ms로 고칠까요, 원본 그대로 둘까요?
