D-007을 `docs/adr/ADR-005-grpc-internal-communication.md`로 옮겼습니다. 기존 ADR이 001~004까지 있어서 번호는 005입니다.

**옮긴 방식**
- **Status: Accepted.** 원본에 "확정, 2026-03-02부터 checkout ↔ inventory 구간 시행 중"으로 적혀 있어서 Proposed가 아니라 Accepted로 했습니다. 원본에 확정 날짜가 따로 없어서 Date에는 시행 시작일(2026-03-02)을 넣었습니다.
- **Decision Source: Human.** 이미 사람이 내린 결정이라 Confidence 필드는 뺐습니다.
- **대안 2개**(GraphQL 페더레이션, REST 유지 + 응답 캐싱)는 원본에 적힌 기각 사유를 그대로 옮겼습니다. 원본에 없는 Pros, 그리고 캐싱 대안의 재검토 조건은 추측해서 채우지 않았습니다.
- **Review Trigger**에는 원본에 있는 재검토 조건 하나만 넣었습니다: "플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션 재검토".
- **Reversibility**와 **Implementation**은 `proto/inventory.proto`와 커밋 25dad14, 15d4779를 보고 작성했습니다. 저장소에는 inventory의 REST 핸들러 코드가 없어서, 롤백할 때 쓸 기존 REST 엔드포인트가 아직 있는지는 확인하지 못했습니다.

**원본과 수치가 다릅니다**
D-007은 부하테스트 p99를 "180ms → 45ms"로 적었지만, `bench/grpc-loadtest-2026-02.md`의 최종값은 **52ms**입니다. 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이고, 벤치 문서가 재측정한 52ms를 최종값으로 명시하고 있습니다. 그래서 ADR의 Evidence에는 52ms를 쓰고 이 차이를 한 줄로 적었습니다. 52ms여도 SLO(100ms) 안이라 결정 근거는 그대로 유효합니다. 페이로드 약 60% 감소(4.8KB → 1.9KB)는 원본과 일치합니다.

`docs/decisions.md`의 D-007 항목은 손대지 않았습니다. 결정 로그에서 D-007을 지우거나 "ADR-005로 이관" 표시로 바꿀까요?
