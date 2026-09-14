`docs/adr/` 디렉터리가 없어서 새로 만들고 번호는 001부터 시작했습니다.

**생성:** `docs/adr/001-celery-async-verification-email.md`

기록한 내용은 이렇습니다.

- **Status:** Proposed — 새로 내리는 결정이라 코드(pyproject.toml에 celery 추가)가 이미 바뀌어 있어도 Proposed로 시작했습니다.
- **Context:** `app/mail.py`의 `send_verification`이 가입 요청 처리 경로에서 `smtplib`로 동기 발송 중이고, SMTP가 느리면 가입 API 응답까지 느려지는 문제. 제약으로 "브로커는 이미 운영 중인 RabbitMQ 재사용, 신규 인프라 없음"을 적었습니다.
- **Decision:** Celery `>=5.4` + 기존 RabbitMQ, 가입 API는 enqueue만 하고 워커가 SMTP 발송.
- **Alternatives:** RQ — Redis를 새로 운영해야 해서 기각. 재검토 조건은 말씀에 없어서 `Recheck if` 줄을 뺐고, 그래서 Review Trigger 섹션도 만들지 않았습니다.
- **Evidence:** 측정 수치가 없어서 섹션을 만들지 않고, "SMTP가 느릴 때 가입 API도 느려진다"는 관찰은 Context에 넣었습니다.
- **Reversibility:** Yes / 롤백은 enqueue를 직접 호출로 되돌리고 celery 의존성 제거(현재 HEAD `558ed63` 기준) / Migration Cost Low.

참고로 커밋 `558ed63`("feat: 가입 인증 메일 발송")은 `git show --stat`으로 보니 변경 파일이 없는 빈 커밋이었습니다. 그래서 동기 발송 구현의 근거로는 실제로 `app/mail.py`를 추가한 `ebfea45`를 References에 인용했고, `558ed63`은 롤백 기준점(현재 위치) 표시로만 썼습니다.

측정값(예: 가입 API p95 지연, SMTP 응답 시간)이나 재검토 조건이 있으면 알려주세요. Evidence / Review Trigger 섹션을 채워 넣겠습니다.
