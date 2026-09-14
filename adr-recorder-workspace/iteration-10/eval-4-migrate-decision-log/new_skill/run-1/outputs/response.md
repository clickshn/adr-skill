D-007을 `docs/adr/ADR-005-grpc-internal-communication.md`로 옮겼습니다. `docs/adr/`에 ADR-001~004가 이미 있어서 005번을 붙였습니다.

**원본에서 가져온 것**
- Status: Accepted (기존 결정 로그 이관)
- Date: 2026-03-02 (원본에 적힌 시행일. 오늘 날짜가 아님)
- Decision Source: Human. 그래서 Confidence는 넣지 않았습니다.
- Context, Decision, Alternatives는 원본의 배경·결정·대안을 그대로 옮겼습니다.
- 재검토 조건은 원본에 적힌 하나만 넣었습니다(GraphQL 페더레이션: 플랫폼팀 4명 이상). Review Trigger에도 이 조건만 있습니다. REST+캐싱 대안은 원본에 재검토 조건이 없어서 Recheck if를 비워 두었습니다.

**원본과 근거 문서가 다른 점: p99 수치**
- D-007에는 "p99 180ms → 45ms"라고 적혀 있습니다.
- 그런데 D-007이 인용한 `bench/grpc-loadtest-2026-02.md`를 보면 45ms는 1차 측정(2026-02-11) 값입니다. 커넥션 풀 워밍업을 빠뜨려서 다시 측정했고, **최종값은 52ms**입니다.
- ADR의 Evidence와 Rationale에는 벤치 최종값인 52ms를 쓰고, 45ms가 어디서 나온 값인지도 한 줄로 적었습니다.
- 페이로드 "약 60% 감소"는 벤치 결과(4.8KB → 1.9KB)와 맞습니다.

**저장소를 확인해서 채운 섹션**
- Implementation: `proto/inventory.proto`(`InventoryService.GetStock`)가 정의되어 있고 checkout ↔ inventory 구간은 전환이 끝났습니다. 나머지 내부 호출 구간은 원본에 대상이 없어서 미완료로 두었습니다.
- Reversibility:
  - REST로 되돌리면 벤치 기준 p99가 180ms로 돌아가 SLO를 다시 넘습니다.
  - 저장소에 서비스 코드가 없어서 REST 엔드포인트가 아직 남아 있는지는 확인하지 못했습니다.
- References:
  - 파일이 실제로 추가된 커밋은 979e62c입니다.
  - 919fb33, 4b0137d는 gRPC 관련 커밋 메시지만 있고 파일 변경은 없습니다. 이 사실도 함께 적었습니다.

`docs/decisions.md`는 건드리지 않았습니다. 원본 D-007 항목은 어떻게 할까요?

1. 삭제
2. 항목은 남기고 "→ ADR-005로 이관" 표시만 추가

표시를 남기신다면 원본의 p99 45ms를 벤치 최종값 52ms로 고칠지도 알려주세요.
