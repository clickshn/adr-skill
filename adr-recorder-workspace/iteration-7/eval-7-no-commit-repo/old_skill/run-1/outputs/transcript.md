# Transcript: eval-7-no-commit-repo / old_skill / run-1

- 스킬: `C:\adr-skill\adr-recorder-workspace\skill-snapshot-v6\SKILL.md`
- `<REPO>` = `C:\Users\USER\AppData\Local\Temp\claude\C--adr-skill\b9213c63-ad8c-49e2-a27b-a9483ed759b3\scratchpad\iter7\eval-7-no-commit-repo\old_skill\repo`
- 날짜: 2026-09-11
- 사용자 요청: "OpenAI 대신 vLLM으로 자체 서빙하기로 했어. 고객 데이터 외부 반출 금지 때문에"

## 도구 호출 목록 (순서대로)

1. Read `C:\adr-skill\adr-recorder-workspace\skill-snapshot-v6\SKILL.md` (스킬 로드)
2. Bash `cd "<REPO>" && git diff HEAD -- '*.txt' '*.json' '*.toml' '*.lock' 2>/dev/null || echo "(HEAD 없음: ...)"` (컨텍스트 명령 1)
3. Bash `cd "<REPO>" && git log --oneline -5 2>/dev/null || echo "(커밋 기록 없음)"` (컨텍스트 명령 2; 2번과 병렬 실행)
4. Bash `ls -la docs/adr/`, `git status`, `find . -path ./.git -prune -o -type f -print` (규칙 1에 따라 셸로 ADR 목록 확인 + 저장소 구성 파악)
5. Read `<REPO>/app/llm_client.py`
6. Read `<REPO>/requirements.txt` (5번과 병렬 실행)
7. Write `<REPO>/docs/adr/001-self-host-llm-with-vllm.md` (ADR 생성)
8. Bash `ls -la docs/adr/; git status --short` (생성 확인)
9. [bookkeeping] Write `outputs/response.md`
10. [bookkeeping] Write `outputs/transcript.md`
11. [bookkeeping] Write `outputs/001-self-host-llm-with-vllm.md` (ADR 사본)

(8~11번은 한 번에 병렬로 실행)

## 컨텍스트 명령 결과 (스킬 로드 시 주입된 것으로 간주)

| # | 명령 | 종료 코드 | 출력 |
|---|------|-----------|------|
| 1 | `git diff HEAD -- '*.txt' '*.json' '*.toml' '*.lock' 2>/dev/null \|\| echo "(HEAD 없음: 아직 커밋이 없거나 git 저장소가 아님)"` | 0 (git diff는 HEAD가 없어 실패했고, 폴백 echo가 성공) | `(HEAD 없음: 아직 커밋이 없거나 git 저장소가 아님)` |
| 2 | `git log --oneline -5 2>/dev/null \|\| echo "(커밋 기록 없음)"` | 0 (git log가 실패했고, 폴백 echo가 성공) | `(커밋 기록 없음)` |

`git status` 결과: `main` 브랜치, "No commits yet", 추적되지 않은 파일은 `app/`와 `requirements.txt`.

## 주요 판단 근거

- **규칙 0(되묻고 멈춤) 미적용:** 이 규칙은 diff가 비어 있고 대화에도 결정이 없을 때만 적용된다. 이번에는 diff는 비어 있었지만(HEAD 없음) 사용자가 결정("OpenAI 대신 vLLM 자체 서빙")을 직접 말했으므로 해당하지 않는다.
- **번호 001:** `ls docs/adr/` 결과 "No such file or directory"(종료 코드 2). 디렉터리가 없으므로 질문 없이 001로 시작했고, 응답에서 그 사실을 알렸다.
- **Status: Proposed.** 이관이 아니라 새로 내린 결정이다. 코드는 아직 OpenAI를 쓰고 있다.
- **Decision Source: Human.** 사용자가 직접 결정을 말했다. 그래서 Confidence 필드는 생략했다.
- **Evidence 생략:** 측정 수치가 없다. 정성적 관찰(고객 문의 원문이 외부로 전송됨)은 Context에 적었다.
- **Alternatives:**
  - 대화에 등장한 대안은 OpenAI API(현행) 하나이고, 기각 사유("고객 데이터 외부 반출 금지")가 구체적으로 주어졌다. 따라서 규칙 3의 "대안과 근거를 알려주세요" 질문은 필요 없었다.
  - 다른 자체 서빙 엔진 같은 언급되지 않은 대안은 추가하지 않았고, 사용자에게 캐묻지도 않았다.
  - Pros와 Cons는 저장소에서 확인한 사실(이미 구현됨, 고객 문의 원문을 외부로 전송)로만 채웠다.
- **Review Trigger:** Alternatives의 Recheck if 한 줄만 모았다.
- **Reversibility: Partial.** 외부 조건(반출 금지 정책)이 바뀌어야만 되돌릴 수 있기 때문이다.
  - Rollback은 저장소에서 확인했다. LLM 호출 코드가 `app/llm_client.py`의 `summarize()` 한 곳뿐이고, `openai==1.40.0` 의존성도 남아 있다. 그래서 Migration Cost는 Low로 두었다.
- **Implementation / AI/ML Details 포함:** 구현이 필요한 결정이고 LLM에 관한 결정이다.
  - AI/ML Details에서 Evaluation 필드와 표는 값이 없어 생략했다.
  - Model은 "현재 gpt-4o, 자체 서빙 모델 미정"으로 적었다.
- **References 생략:** PR, 이슈, 관련 ADR, 근거 문서, 커밋 해시가 하나도 없다.
- **템플릿에 없는 발견 처리:**
  - `OpenAI()`에 `base_url`이 없으면 기본 엔드포인트가 api.openai.com이라는 데이터 반출 위험은 Risks에 한 줄로 넣었다.
  - vLLM OpenAI 호환 서버를 쓰면 SDK를 유지할 수 있다는 선택지는 Implementation에 한 줄로 넣었다.
  - 커밋이 없다는 사실은 Constraints에 한 줄로 넣었다.
- **수정 범위:** `docs/adr/` 밖의 파일(`app/llm_client.py`, `requirements.txt`)은 수정하지 않았다.
