# adr-skill

대화나 코드 변경에서 기술 결정이 감지되면 자동으로 ADR(Architecture Decision Record) 문서를 생성하는 Claude Code Skill입니다.

## 왜 만들었나

기술 결정은 매일 내려지지만 대부분 기록되지 않습니다. "왜 이 라이브러리를 골랐지", "왜 이 모델로 바꿨지" 같은 질문에 3개월 뒤엔 스스로도 답하기 어려워집니다. 이 스킬은 그 기록을 사람이 매번 챙기지 않아도 자동으로 쌓이게 만듭니다.

일반적인 ADR과 다른 점 하나 — **"무엇을 선택했나"보다 "무엇을, 왜 기각했나"에 더 무게**를 둡니다. AI 엔지니어링 결정은 대부분 정답이 하나로 정해지는 문제가 아니라 정확도·비용·지연의 트레이드오프 임계값 문제이고, 기각 사유는 코드 어디에도 남지 않기 때문입니다.

## 설치

두 방법 중 하나만 선택하세요. 개인 스킬(심볼릭 링크)과 플러그인을 동시에 설치하면 `adr-recorder`가 중복으로 로드됩니다.

### 개인 스킬로 설치 (지금 바로 사용 가능)

```bash
git clone https://github.com/clickshn/adr-skill.git adr-skill
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\skills" -Force
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\adr-recorder" -Target "<repo-path>\skills\adr-recorder"
```

macOS/Linux:

```bash
mkdir -p ~/.claude/skills
ln -s <repo-path>/skills/adr-recorder ~/.claude/skills/adr-recorder
```

새 Claude Code 세션에서 `/skills`로 `adr-recorder`가 뜨는지 확인하세요.

### 플러그인으로 설치

```
/plugin marketplace add clickshn/adr-skill
/plugin install adr-skill@adr-skill-marketplace
```

## 사용법

**자동**: 새 의존성 추가, 아키텍처 변경, 외부 API/서비스 선택 같은 결정을 대화 중에 말하면 자동으로 감지해 `docs/adr/`에 문서를 생성합니다.

```
"OpenAI 대신 vLLM으로 자체 서빙하기로 했어. 고객 데이터 외부 반출 금지 때문에"
```

**수동**: 기존 결정 로그(README, docs/decisions.md 등)의 항목을 ADR로 옮길 때 직접 호출할 수 있습니다. 명령은 설치 방식에 따라 다릅니다.

- 개인 스킬로 설치한 경우: `/adr-recorder {결정 요약}`
- 플러그인으로 설치한 경우: `/adr-skill:adr-recorder {결정 요약}`

```
/adr-skill:adr-recorder D-007
```

인자 없이 호출하면, 기록할 결정이 명확하지 않을 때 무엇을 기록할지 되묻습니다 — 저장소를 뒤져서 추측하지 않습니다.

생성 결과가 궁금하다면 [예시 ADR](adr-recorder-workspace/example-output/001-self-host-llm-with-vllm.md)을 참고하세요.

## 이 Skill이 잡는 것

- **템플릿 일관성**: Decision Source(Human/AI-Inferred/Code-Inferred), Confidence, 조건부 섹션(Evidence/Alternatives/Implementation/References 등)을 규칙대로만 채우고, 새 헤더나 빈 필드·TODO를 만들지 않습니다.
- **추측 방지**: 대안의 수치적 근거가 대화에 없으면 지어내지 않고 되묻습니다. 단, 기존 결정 로그를 이관할 때는 원본의 정성적 사유를 그대로 쓰고 새로 캐묻지 않습니다.
- **번호 정합성**: `docs/adr/` 파일 목록을 셸로 직접 확인하고, glob 검색이 빈 결과를 줘도 그대로 믿지 않습니다. 디렉터리가 비어있으면 확인 없이 001부터 시작하고 그 사실을 알립니다.
- **쓰기 범위 제한**: `docs/adr/` 안의 파일만 생성·수정합니다. 원본 결정 로그를 포함해 그 밖의 어떤 파일도 확인 없이 건드리지 않습니다 (12회 실행에 대해 `check_scope.py`로 검증됨).
- **트리거 정확도**: 40개 문장(도메인 특화 20개 포함) 기준 발동해야 할 때 100%, 오발동 0% — `docs/adr/` 안의 파일을 건드리는 무관한 요청이나 과거 결정을 언급만 하는 코드 검색 요청 같은 근접 오탐 사례도 구분합니다.

## 실사용 사례

**[clickshn/multiagent-research-lab](https://github.com/clickshn/multiagent-research-lab)** —
외부 LLM 벤더에 의존하지 않는 멀티에이전트 리서치 시스템(LangGraph + 자체 호스팅 vLLM,
AWS ECS Fargate 배포). 세션 8회에 걸쳐 이 스킬로 **ADR 17건 + Amendment 6건**을 기록했고,
그 목록이 [README §8.1](https://github.com/clickshn/multiagent-research-lab#81-adr-목록)에 있습니다.

빈 작업 디렉터리 기준 평가로는 드러나지 않았던 것이 거기서 나왔습니다.

- **Amendment가 실제로 쓰였습니다.** "전제가 바뀌면 새 ADR로 덮지 말고 Amendment를 붙인다"는
  규칙이 6번 발동했습니다 — 재검색 루프의 실효성이 실측으로 기각되거나(ADR-006), 가설이
  대조군 측정으로 뒤집히거나(ADR-005), 배포 리전·비용이 확정되는(ADR-013) 식입니다.
  **"무엇을 알고 그렇게 정했는지"와 "나중에 무엇이 달라졌는지"가 둘 다 남습니다.**
- **기각 사유에 무게를 두는 설계가 값을 했습니다.** EKS·App Runner를 왜 기각했는지,
  Qdrant로 왜 안 옮겼는지가 각 ADR의 Alternatives에 수치와 함께 남아 있어 같은 논의가
  반복되지 않았습니다.
- ⚠️ 다만 이것은 **한 사람이 한 레포에서 쓴 기록**이라 위 "검증" 절의 수치와 같은 급의
  근거는 아닙니다. 여러 사람·여러 레포에서의 동작은 여전히 측정되지 않았습니다.

## 이 Skill이 못 잡는 것 (아직 검증 안 됨)

- **결정과 실행 요청이 섞인 문장** (예: "GPT로 바꾸기로 했으니 client 코드도 바꿔줘") — 트리거되는 게 맞다고 보고 있지만 실측 검증은 안 됨
- **사소한 비아키텍처 결정** (변수명 컨벤션, PR 리뷰어 수 등)이 오발동을 일으키는지
- **결정 철회** 발화 ("아까 정한 거 취소하고 기존대로 가자")
- **실제 저장소 환경**에서의 트리거 정확도 — 지금까지 측정은 파일이 없는 빈 작업 디렉터리 기준이라, 기존 파일을 먼저 살펴본 뒤 스킬을 호출하는 경우까지는 확인되지 않았습니다
- 모든 correctness 평가는 **버전당 1회 실행** 기준이라, 결과가 얼마나 안정적인지(variance)는 측정되지 않았습니다

## 검증

`adr-recorder-workspace/`에는 SKILL.md를 14차례 반복 개선하며 나온 전체 평가 기록
(iteration-1~13, 스킬 스냅샷 14개, 각 라운드별 실행 결과)이 그대로 남아있습니다.
최종 결과만이 아니라 어떤 문제가 나왔고 어떻게 고쳤는지의 과정 전체를 추적할 수 있습니다.

테스트 데이터는 `skills/adr-recorder/evals/`와 `adr-recorder-workspace/trigger-eval/`에 있고, 검증 도구(`check_adr.py`, `check_scope.py`, `trigger_eval_win.py`)는 레포 루트에 있습니다.

- **콘텐츠 정확성**: [skill-creator](https://github.com/anthropics/claude-plugins-official)로 4~6개 케이스 기준 평가, v1→v4 반복을 거쳐 최종 100% (85% → 100%)
- **트리거 정확도**: `trigger_eval_win.py`로 측정 — 일반 20문장 100%, 도메인 특화 20문장(AI 엔지니어링 결정) 100%. 이 스크립트는 adr-recorder 전용이 아니라, Windows에서 임의의 Claude Code 스킬의 description 트리거 정확도를 재는 범용 도구입니다.
- **쓰기 범위**: `check_scope.py`로 실행 전후 저장소 파일을 대조해 `docs/adr/` 밖 변경이 없는지 확인

재현:

```bash
claude
skill-creator로 adr-recorder 스킬 평가해줘
```

```bash
python trigger_eval_win.py --eval-set adr-recorder-workspace/trigger-eval/eval_set.json \
    --skill-path skills/adr-recorder --cwd <중립 디렉터리> --model claude-opus-5 \
    --runs-per-query 3 --out results.json
```

## License

MIT
