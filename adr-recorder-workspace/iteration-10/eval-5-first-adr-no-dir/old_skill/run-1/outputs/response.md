`docs/adr/001-async-verification-email-with-celery.md`를 만들었습니다.

- 프로젝트에 `docs/adr/` 디렉터리가 없었습니다(기존 ADR 없음). 그래서 디렉터리를 새로 만들고 번호를 **001**부터 시작했습니다.
- **반영한 내용:** `pyproject.toml` diff의 `celery>=5.4` 추가, 배경(SMTP가 느리면 가입 API도 같이 느려짐), 브로커(이미 운영 중인 RabbitMQ), 기각한 대안 2개(RQ는 Redis를 새로 운영해야 해서, 현행 동기 발송 유지는 문제를 해결하지 못해서)
- **Status는 Proposed입니다.** 새로 내린 결정이라서 그렇습니다. 참고로 `app/mail.py`는 아직 요청 처리 중 동기 발송 그대로입니다.
- **생략한 항목**
  - Confidence: Decision Source가 Human이라서
  - Evidence 섹션: 측정 수치가 없어서
  - Recheck if 줄과 Review Trigger 섹션: 대화에 재검토 조건이 없어서
- **코드에서 확인한 점:** `send_verification`이 `smtplib.SMTP("smtp.internal", 25)`에 timeout 없이 연결합니다. 그래서 SMTP 지연이 요청에 그대로 전파됩니다. 이 내용은 Context에 한 줄로 넣었습니다.
- **Reversibility:** Yes / Low로 적었습니다. 동기 호출로 되돌리고 워커를 내리면 되고, RabbitMQ는 원래 쓰던 것이라 걷어낼 인프라가 없습니다.
