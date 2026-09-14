---
name: adr-recorder
description: 새 의존성 추가, 아키텍처 변경, 외부 API/서비스 선택 시 ADR 문서를 자동 생성. package.json/requirements.txt 변경, DB·통신 프로토콜 변경, "~쓰기로 했다"류 결정 발화에 반응.
---

## 최근 변경 컨텍스트

- 의존성 파일 diff: !`git diff HEAD -- '*.txt' '*.json' '*.toml' '*.lock'`
- 최근 커밋: !`git log --oneline -5`

## 언제 발동하는가

- 새 의존성(라이브러리) 추가
- 아키텍처 변경 (DB, 통신 방식, 메시징 등)
- 외부 API·서비스 선택/교체

## 무엇을 하는가

0. git diff가 비어있고, 대화에서 명시적으로 언급된 결정도 없으면,
   저장소를 탐색하지 말고 "어떤 결정을 ADR로 기록할까요?"라고 되묻고 멈춘다.
1. `docs/adr/`에 다음 번호로 ADR 파일 생성, 아래 템플릿과 생성 규칙을 따른다.
2. 위 diff와 대화 맥락에서 배경·결정·대안을 추출한다.
3. Alternatives의 구체적 사유(수치)가 대화에 없으면, 생성 후 "이 결정에서 기각한 대안과 수치적 근거를 알려주세요"라고 되묻는다. 추측해서 채우지 않는다.

### 생성 규칙

- 섹션별 생성 조건은 템플릿 내 HTML 주석을 따른다. 조건 미충족 시 해당 섹션을 만들지 않는다(빈 섹션·TODO로 채우지 않음).
- Confidence는 Evidence에 실측 수치가 있으면 High, 정성적 추론만 있으면 Low, 섞이면 Medium. Decision Source가 Human이면 필드를 생략한다.
- Review Trigger는 Alternatives의 Recheck if만 모아서 작성한다. Alternatives가 없으면 Review Trigger도 생성하지 않는다.
- 템플릿의 섹션 헤더와 필드명은 고정한다. 새 섹션이나 필드를 임의로 추가하지 않는다.
- 템플릿에 없는 유용한 발견(예: 원본 문서와 실측값 불일치)은 가장 가까운 기존 섹션 안에 한 줄로 녹인다.
- References처럼 값이 없는 필드는 줄 자체를 생략한다. 커밋 해시·산출물 경로 등은 Documentation 필드 아래 붙인다.
- 기존 결정 로그(D-XXX 등)를 ADR로 옮기는 경우, 원본에 이미 확정/시행 중으로 기록돼 있으면 Status를 Accepted로 한다. 새로 내리는 결정만 Proposed로 시작한다.

### 템플릿

# ADR-{NNN}: {결정 제목}

- **Status:** Proposed
- **Date:** YYYY-MM-DD
- **Decision:** {한 줄 요약}
- **Scope:** {프로젝트/서비스/컴포넌트}
- **Decision Source:** Human | AI-Inferred | Code-Inferred
- **Confidence:** High | Medium | Low <!-- Human이면 생략 -->

---

## Context <!-- 필수 -->

### Problem

### Constraints

## Decision <!-- 필수 -->

### Selected

- **Technology:**
- **Architecture:**
- **Implementation:**

## Rationale <!-- 필수 -->

1.

## Evidence <!-- 실제 근거 있을 때만 -->

- **Benchmark:**
- **Experiment:**
- **Production Data:**
- **Cost:**

## Alternatives <!-- 발견 가능한 경우만 -->

### {Alternative 1}

- **Pros:**
- **Cons:**
- **Rejected because:**
- **Recheck if:**

## Consequences <!-- 필수 -->

### Positive

### Negative

### Risks

## Implementation <!-- 구현 결정일 때만 -->

- [ ] 구현 작업
- [ ] 테스트
- [ ] 모니터링
- [ ] 문서/설정 업데이트

## Reversibility <!-- 가능하면 항상 -->

- **Reversible:** Yes | Partial | No
- **Rollback:**
- **Migration Cost:** Low | Medium | High

## Review Trigger <!-- Alternatives 없으면 생성 안 함 -->

## References <!-- PR/Issue/Related ADR/근거 문서 중 하나라도 있을 때만 -->

- **PR:**
- **Issue:**
- **Related ADR:**
- **Documentation:**

## AI/ML Details <!-- AI/ML 결정일 때만 -->

- **Model:**
- **Evaluation:**
- **Inference:**

### Evaluation

| Metric | Before | After | Target |
| ------ | -----: | ----: | -----: |
