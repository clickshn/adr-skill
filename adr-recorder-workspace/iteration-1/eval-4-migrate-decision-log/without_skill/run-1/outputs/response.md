D-007을 ADR-005로 옮겼습니다. 원 로그의 p99 수치 하나가 부하테스트 최종값과 달라서 ADR에는 최종값으로 적었습니다.

**수치 정정:** D-007에는 p99가 "180ms → 45ms"로 적혀 있습니다. `bench/grpc-loadtest-2026-02.md`를 보면 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정값(02-11)이고, 재측정한 최종값은 **52ms**입니다. ADR에는 52ms를 적고, 정정했다는 메모를 본문에 남겼습니다. 52ms도 SLO 100ms 안이라 결론은 같습니다. 페이로드 약 60% 감소(4.8KB → 1.9KB)는 원 로그와 맞았습니다.

**새 파일: `docs/adr/ADR-005-grpc-internal-communication.md`**
- 헤더는 ADR-001~004 형식(Status / Date / Decision / Scope / Decision Source)을 그대로 따랐습니다. 여기에 Owner(플랫폼팀)와 이관 출처를 추가했습니다.
- 본문은 Context, Decision, Rationale(부하테스트 표), Alternatives Considered, Consequences, Re-evaluation Triggers로 나눴습니다.
- 재검토 조건 "플랫폼팀 4명 이상이 되면 GraphQL 페더레이션 재검토"는 Re-evaluation Triggers에 넣었습니다.

**수정한 파일: `docs/decisions.md`**
- D-007 본문을 지우고 "ADR-005로 이관됨 (2026-09-11)" 링크 한 줄만 남겼습니다. D-001~004가 이미 로그에서 빠져 있어서 같은 방식을 따랐습니다.

**확인해 주실 점:**
- **Date:** 원 기록에 확정일이 없어서 시행 시작일인 2026-03-02를 넣었습니다. 실제 확정일을 아시면 바꿔 주세요. 이 날짜 때문에 ADR-004(04-01)보다 날짜가 빠르지만, 번호는 기록한 순서라서 그대로 두었습니다.
- **Consequences:** 이 섹션은 원 로그에 없던 내용입니다. 결정과 proto 파일을 보고 제가 추론해서 썼습니다(스키마 버전 관리, REST와 gRPC 병행 운영, 비동기 호출은 범위 밖).

변경 사항은 커밋하지 않았습니다.
