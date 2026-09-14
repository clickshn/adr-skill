`docs/adr/ADR-003-pino-logger.md`에 ADR을 남겼습니다. Status는 Proposed이고, 직접 내린 결정이라 Decision Source는 Human으로 적었습니다.

**담은 내용**
- **Evidence / Rationale:** autocannon 결과 — p99 38ms → 21ms(약 45% 감소), 처리량 8.2k → 11.5k req/s(약 40% 증가)
- **Alternatives:**
  - winston 유지: 벤치마크 수치 때문에 기각
  - bunyan: 마지막 릴리스가 3년 전이라 기각
- **Review Trigger:** bunyan 유지보수가 다시 시작되면 재검토
- **Reversibility:** 로거 생성이 `src/logger.js` 한 곳에 모여 있어서 되돌리기 쉬움(Low)

**확인이 필요한 점**
`src/logger.js`가 아직 `require('winston')`을 쓰고 있습니다. package.json에서 winston을 뺐기 때문에, 이대로 `npm install`하면 서버가 시작할 때 모듈을 찾지 못해 실패합니다. 이 교체 작업은 ADR의 Implementation 체크리스트 첫 항목에 넣어 두었습니다.

pino로 바꾸면 로그 출력 형식(level 표기 등)이 달라지니, 로그 수집이나 검색 쿼리에 영향이 있는지도 확인해 보세요. 이 내용은 Risks에 적어 두었습니다.
