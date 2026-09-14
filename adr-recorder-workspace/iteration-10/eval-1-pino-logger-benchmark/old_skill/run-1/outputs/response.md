`docs/adr/ADR-003-pino-logger.md`를 만들었습니다(기존 ADR-001, 002 다음 번호).

**요약**
- **Status:** Proposed (새로 내린 결정이라, package.json이 이미 바뀌었어도 Proposed로 시작)
- **Decision:** order-api 로거를 winston에서 pino ^9.4.0으로 교체하고, 개발용으로 pino-pretty ^11.2.2 추가
- **Evidence:** autocannon 측정 결과 winston은 p99 38ms / 8.2k req/s, pino는 p99 21ms / 11.5k req/s
- **Alternatives:**
  - winston 유지: 측정 수치가 더 나빠 제외
  - bunyan: 마지막 릴리스가 3년 전이라 제외. **Recheck if**는 "유지보수 재개 시"
- **Review Trigger:** bunyan 유지보수 재개
- **Reversibility:** Yes / Low. 로거를 쓰는 호출부가 src/server.js 1곳뿐이라 영향 범위가 작습니다.

**확인이 필요한 부분**
- **`src/logger.js`가 아직 winston을 씁니다.** package.json에서 winston이 빠졌는데 `src/logger.js`는 여전히 `require('winston')`을 호출합니다. 이 상태로 새로 설치하면 서버가 기동하다 실패합니다. ADR의 Risks와 Implementation 체크리스트에 적어 두었습니다. 이 스킬은 docs/adr/ 밖의 파일을 확인 없이 고치지 않으니, logger.js를 pino로 바꿔 드릴지 알려주세요.
- **로그 형식이 바뀝니다.** winston의 `message`와 문자열 레벨이 pino에서는 `msg`와 숫자 레벨로 바뀝니다. 로그 수집·검색 쪽 설정도 확인이 필요해 Negative와 모니터링 항목에 넣었습니다.
- **벤치마크 조건이 없습니다.** 동시 연결 수, 측정 시간, 대상 엔드포인트가 기록되지 않아 재현하기 어렵다는 점을 Risks에 한 줄 적었습니다. 조건을 알려주시면 Evidence에 보완하겠습니다.
