`docs/adr/` 디렉터리가 없었습니다. 그래서 새로 만들었고, 이 저장소의 첫 ADR이라 **001번**으로 시작했습니다.

**생성한 파일:** `docs/adr/001-signup-verification-mail-celery.md`

| 항목 | 내용 |
| --- | --- |
| 제목 | ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리 |
| Status | Proposed (새로 내린 결정이라서) |
| Decision Source | Human (Confidence 생략) |
| 선택 | Celery (`celery>=5.4`) + 기존 운영 중인 RabbitMQ 브로커 |
| Alternatives | 현행 유지(동기 발송): SMTP가 느릴 때 가입 API도 같이 느려져서 기각 / RQ: Redis를 새로 운영해야 해서 기각 |
| Reversibility | Yes, Migration Cost Low (직접 호출로 되돌리고 celery 의존성을 빼면 됨) |

참고 사항:
- 저장소를 확인해 보니 `app/mail.py`는 아직 요청 처리 중에 `smtplib`로 `smtp.internal:25`에 직접 동기 발송하고 있습니다(커밋 c44bbf9). 지금까지 바뀐 건 `pyproject.toml`에 추가한 `celery>=5.4`뿐이고 아직 커밋 전입니다. 태스크 전환, 워커 구성, 모니터링은 ADR의 Implementation 체크리스트에 적어 두었습니다.
- 대화에 측정 수치(예: SMTP 지연 시간)가 없어서 Evidence 섹션은 만들지 않았습니다. 대화에 재검토 조건도 없어서 Recheck if와 Review Trigger도 넣지 않았습니다.
- `docs/adr/` 밖의 파일은 수정하지 않았습니다.
