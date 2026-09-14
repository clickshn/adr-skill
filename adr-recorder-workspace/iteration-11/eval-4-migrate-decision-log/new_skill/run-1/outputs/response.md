docs/decisions.md의 D-007을 `docs/adr/ADR-005-grpc-internal-communication.md`로 옮겼습니다.

**작성 기준**

- **번호:** 셸로 확인해 보니 `docs/adr/`에 ADR-001~004가 있어서 005를 붙였습니다.
- **Status / Date:** 기존 결정 로그를 옮긴 것이라 Status는 `Accepted`입니다. Date는 원본에 적힌 시행일인 `2026-03-02`입니다. 원본에 결정일은 따로 없습니다.
- **Decision Source:** `Human`입니다. 규칙에 따라 Confidence는 넣지 않았습니다.
- **Alternatives:** 원본에 있는 두 가지(GraphQL 페더레이션, REST 유지 + 응답 캐싱)만 옮겼고, 기각 사유도 원본 그대로입니다.
  - Recheck if는 원본에 적힌 조건인 "플랫폼팀 4명 이상"만 GraphQL 페더레이션에 넣었고, Review Trigger에도 이 조건을 모았습니다.
  - 캐싱 대안은 원본에 재검토 조건이 없어서 그 줄을 뺐습니다.
- **Reversibility / Implementation:** 저장소를 직접 보고 작성했습니다. 현재 시행 구간은 1개이고 RPC도 `GetStock` 1개입니다. 서비스 코드는 이 저장소에 없어서 REST 엔드포인트가 남아 있는지는 확인하지 못했습니다.

**원본과 근거 문서의 차이 1건**

- D-007에는 p99가 "180ms → 45ms"로 적혀 있습니다. 그런데 D-007이 근거로 든 `bench/grpc-loadtest-2026-02.md`를 보면, 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정값(2026-02-11)입니다. 문서는 재측정한 **52ms**가 최종값이라고 명시합니다.
- ADR의 Evidence에는 최종값 52ms를 쓰고, 45ms와의 차이를 한 줄로 적어 두었습니다. 어느 값이든 SLO(100ms) 안이라 결론은 같습니다.

**커밋 인용**

- 메시지가 gRPC 관련인 `7d7cef8`("docs: gRPC 부하테스트 결과 추가")와 `ea70f75`("feat(inventory): gRPC 재고 조회 엔드포인트")는 `git show --stat`으로 보니 변경 파일이 없는 빈 커밋이었습니다. 그래서 인용하지 않았습니다.
- 대신 bench 문서와 proto를 실제로 추가한 `8c3a73e`를 인용했습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다. 원본 `docs/decisions.md`도 그대로입니다.

---

원본 `docs/decisions.md`의 D-007 항목은 어떻게 할까요?

1. 항목 삭제
2. 항목은 남기고 "→ ADR-005로 이관됨" 표시만 추가 (이 경우 45ms 수치도 52ms로 고칠지 같이 알려주세요)
