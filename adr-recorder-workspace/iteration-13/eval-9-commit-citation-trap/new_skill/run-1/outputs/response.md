`docs/adr/ADR-002-jose-jwt-verification.md`를 생성했습니다. 기존에 ADR-001(Express)이 있어서 002로 번호를 이었습니다.

**커밋 인용 관련해서 짚고 갈 게 있습니다.** `git log`에 `77d5c5e feat: switch to jose for JWT verification`이라는 딱 맞는 메시지의 커밋이 있어서 이걸 근거로 인용하려다, `git show --stat`으로 확인해 보니 **빈 커밋**이었습니다. 실제 jose 교체는 바로 앞의 `5576d53 chore: dependency bump`에 들어 있습니다.

```
5576d53  package.json | 4 ++--      express ^4.19.2→^4.21.1, jsonwebtoken ^9.0.2 → jose ^5.9.6
         src/auth.js  | 9 ++++---   jwt.verify(sync) → await jwtVerify(...)
```

그래서 ADR의 References에는 `77d5c5e`가 아니라 `5576d53`을 적었습니다. 메시지와 내용이 어긋나 있으니 나중에 이력을 추적할 때 헷갈릴 수 있겠네요.

작성한 내용 요약:

- **Status:** Proposed — 코드는 이미 바뀌어 있지만 새로 내리는 결정이라 Proposed로 시작했습니다.
- **Decision Source:** Human (직접 말씀해 주신 결정이라 Confidence 필드는 생략)
- 코드에서 확인한 사항: HS256 알고리즘 화이트리스트는 유지됐고, 시크릿은 `TextEncoder`로 인코딩해 재사용하며, `verifyToken`이 **동기에서 async로 바뀌었습니다**. 다만 현재 저장소에는 호출부가 없어서(`src/`에 `auth.js` 한 파일뿐) await 누락 여부를 코드로 검증하지 못했습니다 — Risks에 적어 뒀습니다.
- express 마이너 업그레이드가 같은 커밋에 섞여 있어 롤백 범위가 넓어지는 점도 Risks와 Rollback에 함께 적었습니다.
- 측정 수치가 없어서 Evidence 섹션은 만들지 않았습니다.

**하나 여쭤볼 게 있습니다. 이 결정에서 기각한 대안과 그 근거를 알려주세요.** 대화에 대안이 언급되지 않아 Alternatives 섹션을 비워 뒀고(그에 따라 Review Trigger도 생성하지 않았습니다), Rationale도 "기록된 근거 없음"으로만 남겨 둔 상태입니다. jsonwebtoken을 계속 쓰는 선택지를 왜 접으셨는지 — 유지보수 상태, ESM/엣지 런타임 호환, 알고리즘 처리 안전성 같은 이유 중 무엇이었는지 알려주시면 Rationale과 Alternatives를 채워 넣겠습니다.
