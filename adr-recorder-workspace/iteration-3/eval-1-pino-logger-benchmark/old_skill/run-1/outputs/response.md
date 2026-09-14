`docs/adr/ADR-003-pino-logger.md`로 ADR 남겼습니다. 기존에 ADR-001, 002가 있어서 003으로 이어 붙였어요.

**들어간 내용**
- **Status:** Proposed. 새로 내린 결정이라 Proposed로 시작합니다. 머지하시면 Accepted로 바꿔주세요.
- **Decision Source:** Human. 직접 내린 결정이라 Confidence 필드는 뺐습니다.
- **Evidence:** autocannon 결과를 그대로 넣었습니다. winston p99 38ms, 8.2k req/s → pino p99 21ms, 11.5k req/s. p99는 약 45% 줄고 처리량은 약 40% 늘었어요.
- **Alternatives**
  - winston 유지: 벤치마크에서 지연과 처리량 둘 다 pino보다 나빠서 기각했습니다.
  - bunyan: 마지막 릴리스가 3년 전이라 기각했습니다. 다시 볼 조건(Recheck if)은 "유지보수 재개"로 적었고, 이 조건을 Review Trigger에도 넣었습니다.
- **Implementation:** package.json 교체(winston 제거, pino ^9.4.0 추가, pino-pretty ^11.2.2를 devDependencies에 추가)는 완료로 체크했습니다. 남은 항목은 로거 호출부 이관, 테스트, 배포 후 모니터링, lockfile 갱신입니다.
- **Risks:** 로그 포맷이 바뀌면 기존 로그 수집·검색·알림 설정이 영향을 받을 수 있다는 점을 적어뒀습니다.

벤치마크 조건(커넥션 수, 측정 시간, 엔드포인트)은 말씀하신 적이 없어서 적지 않았습니다. 알려주시면 Evidence에 한 줄 더 넣을게요.
