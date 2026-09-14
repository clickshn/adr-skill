`docs/adr/ADR-002-jose-jwt-verification.md`를 생성했습니다.

기존 ADR은 `ADR-001-express-framework.md` 하나여서 다음 번호인 002로 붙였습니다. 새로 내리는 결정이라 코드가 이미 반영되어 있어도 Status는 Proposed로 시작했습니다.

**커밋 인용 관련해서 하나 짚고 넘어갑니다.**

`git log`상 `77d5c5e feat: switch to jose for JWT verification`이 이 변경을 담은 것처럼 보이지만, `git show --stat`으로 확인해보니 **변경 파일이 하나도 없는 빈 커밋**이었습니다. 실제 교체는 바로 앞의 `5576d53 chore: dependency bump`에 들어 있습니다.

```
5576d53  package.json | 4 ++--
         src/auth.js  | 9 ++++++---
```

그래서 ADR의 References/Rollback에는 `77d5c5e`가 아니라 `5576d53`을 근거 커밋으로 적었습니다. 나중에 히스토리를 되짚을 때 혼동될 수 있으니 알아두시면 좋겠습니다.

**저장소에서 확인한 내용으로 채운 부분**

- jsonwebtoken ^9.0.2 → jose ^5.9.6, express도 4.19.2 → 4.21.1로 함께 올라갔습니다(ADR은 jose 교체만 다뤘습니다).
- `verifyToken`이 동기 함수에서 `async`로 바뀌었고 반환값이 `payload`로 좁아졌습니다. 호출부에서 `await`를 빠뜨리면 Promise가 truthy라 검증 실패 토큰이 통과할 수 있어 Risks에 적어뒀습니다.
- HS256 알고리즘 화이트리스트와 `JWT_SECRET` 사용 방식은 교체 전후 동일합니다.

**확인이 필요한 부분**

Evidence(벤치마크·실측)는 근거가 없어 섹션을 만들지 않았고, Alternatives도 비워뒀습니다. **이 결정에서 기각한 대안과 근거를 알려주세요.** (예: jsonwebtoken 유지, jwt-decode, 직접 구현 등을 검토하셨다면 그 사유를 적어드리겠습니다.) 알려주시면 Alternatives와 Review Trigger 섹션을 채워 넣겠습니다.

Rationale은 지금 대화에 근거가 없어 저장소에서 확인 가능한 사실(ESM 전용 패키지, 교체 범위가 파일 1개)만으로 적어뒀으니, 실제 결정 이유가 따로 있다면 알려주세요.
