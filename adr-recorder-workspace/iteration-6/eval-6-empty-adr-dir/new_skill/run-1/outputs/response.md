ADR을 작성했어요: `docs/adr/001-api-auth-session-to-jwt.md`

- docs/adr/에는 `.gitkeep`만 있고 기존 ADR이 없어서 **001번**으로 시작했어요.
- 새 결정이라 Status는 **Proposed**예요. 결정 주체는 직접 결정하신 거라 Human으로 적었고 Confidence는 넣지 않았어요.
- 기각한 대안 "세션 유지 + 파트너용 API 키 발급"은 말씀하신 그대로 적었어요(키 회전 관리를 따로 만들어야 해서 기각). Review Trigger도 여기에 맞춰 적었어요.
- 측정 수치가 없어서 Evidence 섹션은 뺐어요.

**확인이 필요한 점**
`src/auth.js`가 아직 `require('express-session')`을 하고 있어요. package.json에서는 express-session을 뺐기 때문에, 의존성을 다시 설치하면 모듈을 못 찾아서 서버가 뜨지 않아요. ADR의 Risks와 Implementation에 적어두기만 했고, docs/adr/ 밖이라 코드는 건드리지 않았어요. JWT 검증 미들웨어로 바꿔드릴까요?
