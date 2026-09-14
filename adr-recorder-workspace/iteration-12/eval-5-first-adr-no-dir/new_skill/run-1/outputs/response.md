ADR을 새로 만들었습니다.

**생성 파일:** `docs/adr/001-celery-async-signup-verification-email.md`

프로젝트에 `docs/adr/` 디렉터리가 아예 없어서(기존 ADR 파일 없음) 디렉터리를 새로 만들고 번호를 **001**부터 시작했습니다.

**기록한 내용**
- **Decision:** 가입 요청 처리 중 동기 발송하던 인증 메일을 Celery 태스크로 분리, 브로커는 기존 운영 중인 RabbitMQ.
- **Status:** Proposed — `pyproject.toml`에 `celery>=5.4`가 이미 들어가 있지만, 기존 결정 로그 이관이 아니라 새로 내리는 결정이라 Proposed로 시작했습니다.
- **Alternatives:** RQ(Redis를 새로 운영해야 해서 제외), 현행 유지(동기 발송 — SMTP 지연이 가입 API로 전파되는 게 이번 문제 자체).
- **Evidence 섹션은 넣지 않았습니다.** "SMTP가 느리면 가입 API도 느려진다"는 정성적 관찰이라 Context에 적었고, 실측 수치가 없어 Evidence는 생략했습니다.
- **Review Trigger도 생략했습니다.** 대화에 재검토 조건이 없었고, 기각 사유를 뒤집은 조건("Redis를 운영하게 되면 재검토")은 지어낸 것이라 쓰지 않았습니다.

**확인 과정에서 하나 짚어둘 점:** 커밋 로그상 `f8ac775 feat: 가입 인증 메일 발송`이 동기 발송 구현처럼 보여서 근거로 인용하려 했는데, `git show --stat`으로 확인해 보니 **파일 변경이 없는 빈 커밋**이었습니다. 실제 `app/mail.py`의 동기 발송 코드는 `8014104 feat: signup-api 초기 구성`에 들어 있어서, ADR에는 8014104를 인용했습니다. (롤백 기준점으로서의 HEAD 위치 표시로는 f8ac775를 그대로 썼습니다.)

ADR은 `docs/adr/` 안에만 만들었고, 그 밖의 파일은 건드리지 않았습니다.
