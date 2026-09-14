D-007을 `docs/adr/ADR-005-grpc-internal-communication.md`로 옮겼습니다.

**번호와 형식**
- `docs/adr/`에 ADR-001부터 004까지 있어서 005번으로 만들었습니다.
- 기존 결정 로그를 옮긴 것이라 Status는 Accepted, Decision Source는 Human으로 했습니다. Human이라 Confidence 필드는 뺐습니다.
- Date는 원본에 적힌 시행일 2026-03-02입니다.

**내용 출처**
- 배경, 결정, 근거, 대안 두 가지(GraphQL 페더레이션, REST 유지 + 응답 캐싱)는 원본 문장을 그대로 옮겼습니다.
- Recheck if와 Review Trigger에는 원본에 적힌 조건(플랫폼팀 4명 이상이면 GraphQL 재검토)만 넣었습니다. REST + 캐싱 쪽은 원본에 재검토 조건이 없어서 해당 줄을 뺐습니다.
- Reversibility는 저장소를 보고 채웠습니다. 저장소에는 `proto/inventory.proto`만 있고 서비스 코드가 없어서, REST 엔드포인트를 함께 유지하고 있는지는 확인하지 못했습니다.

**확인이 필요한 부분: 수치가 다릅니다**
- D-007에는 p99가 180ms에서 **45ms**로 줄었다고 적혀 있습니다.
- 그런데 근거로 인용된 `bench/grpc-loadtest-2026-02.md`를 보면 45ms는 2026-02-11 1차 측정값입니다. 커넥션 풀 워밍업이 빠진 측정이라 다시 쟀고, 최종값은 **52ms**입니다.
- ADR의 Evidence와 Rationale에는 최종값 52ms를 쓰고, 이 차이를 Evidence에 한 줄로 적어 두었습니다. 두 값 모두 SLO(100ms) 안이라 결정 자체는 달라지지 않습니다.
- 참고로 커밋 `ea70f75`(gRPC 재고 조회 엔드포인트)와 `7d7cef8`(부하테스트 결과 추가)은 변경 파일이 없는 빈 커밋입니다. 그래서 References에는 실제로 파일이 추가된 `8c3a73e`와 파일 경로를 적었습니다.

`docs/decisions.md`는 건드리지 않았습니다. 원본 D-007을 어떻게 할지 알려주세요.
1. D-007 항목을 삭제한다.
2. 항목은 남기고 "→ ADR-005로 이관" 표시만 붙인다.

위 45ms 표기도 이참에 52ms로 고칠지 함께 알려주세요.
