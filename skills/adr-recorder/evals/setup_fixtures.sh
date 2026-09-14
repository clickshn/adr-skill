#!/usr/bin/env bash
# adr-recorder 평가용 fixture 저장소 생성.
# 사용법: setup_fixtures.sh <fixtures_dir>
set -euo pipefail

OUT="${1:?fixtures dir required}"
rm -rf "$OUT"
mkdir -p "$OUT"

g() { git -c user.name="Dev Team" -c user.email="dev@example.com" -c core.autocrlf=false "$@"; }

# ---------------------------------------------------------------------------
# 1) pino-logger-benchmark: Node 프로젝트, 기존 ADR 2개(ADR-001/002), 미커밋 package.json 변경
# ---------------------------------------------------------------------------
R="$OUT/pino-logger-benchmark"
mkdir -p "$R/docs/adr" "$R/src"
cat > "$R/package.json" <<'EOF'
{
  "name": "order-api",
  "version": "1.4.0",
  "private": true,
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.19.2",
    "pg": "^8.12.0",
    "winston": "^3.13.0"
  },
  "devDependencies": {
    "jest": "^29.7.0"
  }
}
EOF
cat > "$R/src/server.js" <<'EOF'
const express = require('express');
const logger = require('./logger');

const app = express();
app.get('/health', (req, res) => res.json({ ok: true }));
app.listen(3000, () => logger.info('order-api listening on 3000'));
EOF
cat > "$R/src/logger.js" <<'EOF'
const winston = require('winston');

module.exports = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
});
EOF
cat > "$R/docs/adr/ADR-001-express-framework.md" <<'EOF'
# ADR-001: HTTP 프레임워크로 Express 사용

- **Status:** Accepted
- **Date:** 2025-11-03
- **Decision:** order-api의 HTTP 프레임워크로 Express 4를 사용한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

주문 API 서버의 HTTP 레이어 선택이 필요했다.

## Decision

### Selected

- **Technology:** Express 4

## Rationale

1. 팀 전원이 Express 경험 보유.

## Consequences

### Positive

- 온보딩 비용 낮음.
EOF
cat > "$R/docs/adr/ADR-002-postgresql-primary-db.md" <<'EOF'
# ADR-002: 주 데이터베이스로 PostgreSQL 사용

- **Status:** Accepted
- **Date:** 2025-11-10
- **Decision:** 주문 데이터 저장소로 PostgreSQL 16을 사용한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

트랜잭션 보장이 필요한 주문 데이터 저장소가 필요했다.

## Decision

### Selected

- **Technology:** PostgreSQL 16

## Rationale

1. 트랜잭션·JSONB 지원.

## Consequences

### Positive

- 운영 경험 풍부.
EOF
( cd "$R" && g init -q -b main && g add -A && g commit -q -m "feat: order-api 초기 구성 (express, pg, winston)" \
  && g commit -q --allow-empty -m "docs: ADR-002 PostgreSQL 결정 기록" \
  && g commit -q --allow-empty -m "fix: 주문 조회 페이지네이션 off-by-one" )
# 미커밋 변경: winston -> pino
cat > "$R/package.json" <<'EOF'
{
  "name": "order-api",
  "version": "1.4.0",
  "private": true,
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.19.2",
    "pg": "^8.12.0",
    "pino": "^9.4.0"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "pino-pretty": "^11.2.2"
  }
}
EOF

# ---------------------------------------------------------------------------
# 2) empty-context-ask: 깨끗한 워킹트리, 최근 커밋에 결정처럼 보이는 메시지 존재
# ---------------------------------------------------------------------------
R="$OUT/empty-context-ask"
mkdir -p "$R/docs/adr" "$R/src"
cat > "$R/package.json" <<'EOF'
{
  "name": "notification-service",
  "version": "0.9.2",
  "private": true,
  "dependencies": {
    "kafkajs": "^2.2.4",
    "fastify": "^4.28.1"
  }
}
EOF
cat > "$R/src/index.js" <<'EOF'
const { Kafka } = require('kafkajs');
const kafka = new Kafka({ clientId: 'notification-service', brokers: ['kafka:9092'] });
module.exports = kafka;
EOF
cat > "$R/docs/adr/ADR-001-fastify.md" <<'EOF'
# ADR-001: HTTP 프레임워크로 Fastify 사용

- **Status:** Accepted
- **Date:** 2026-02-14
- **Decision:** notification-service에 Fastify를 사용한다.
- **Scope:** notification-service
- **Decision Source:** Human
EOF
( cd "$R" && g init -q -b main && g add -A && g commit -q -m "chore: notification-service 초기 구성" \
  && g commit -q --allow-empty -m "feat: 이벤트 버스 RabbitMQ -> Kafka 전환" \
  && g commit -q --allow-empty -m "test: 이메일 템플릿 스냅샷 테스트 추가" \
  && g commit -q --allow-empty -m "fix: 푸시 알림 재시도 백오프 계산 오류" )

# ---------------------------------------------------------------------------
# 3) redis-session-no-numbers: Python, 4자리 ADR 번호 규칙, requirements.txt 미커밋 변경
# ---------------------------------------------------------------------------
R="$OUT/redis-session-no-numbers"
mkdir -p "$R/docs/adr" "$R/app"
cat > "$R/requirements.txt" <<'EOF'
fastapi==0.112.2
uvicorn==0.30.6
sqlalchemy==2.0.32
EOF
cat > "$R/app/session.py" <<'EOF'
# 프로세스 메모리 기반 세션 저장소
_sessions: dict[str, dict] = {}


def get(session_id: str) -> dict | None:
    return _sessions.get(session_id)


def put(session_id: str, data: dict) -> None:
    _sessions[session_id] = data
EOF
cat > "$R/docs/adr/0001-record-architecture-decisions.md" <<'EOF'
# ADR-0001: 아키텍처 결정을 ADR로 기록

- **Status:** Accepted
- **Date:** 2026-01-05
- **Decision:** 주요 아키텍처 결정은 docs/adr/에 ADR로 기록한다.
- **Scope:** member-portal
- **Decision Source:** Human
EOF
( cd "$R" && g init -q -b main && g add -A && g commit -q -m "feat: member-portal 초기 구성" \
  && g commit -q --allow-empty -m "feat: 로그인/로그아웃 API" )
cat > "$R/requirements.txt" <<'EOF'
fastapi==0.112.2
uvicorn==0.30.6
sqlalchemy==2.0.32
redis==5.0.8
EOF

# ---------------------------------------------------------------------------
# 4) migrate-decision-log: 기존 결정 로그(D-XXX) -> ADR 이관, 근거 문서와 수치 불일치
# ---------------------------------------------------------------------------
R="$OUT/migrate-decision-log"
mkdir -p "$R/docs/adr" "$R/bench" "$R/proto"
for n in 1 2 3 4; do
  cat > "$R/docs/adr/ADR-00$n-placeholder-$n.md" <<EOF
# ADR-00$n: 기존 결정 $n

- **Status:** Accepted
- **Date:** 2026-0$n-01
- **Decision:** (기존 결정 $n)
- **Scope:** checkout-platform
- **Decision Source:** Human
EOF
done
mv "$R/docs/adr/ADR-001-placeholder-1.md" "$R/docs/adr/ADR-001-monorepo.md"
mv "$R/docs/adr/ADR-002-placeholder-2.md" "$R/docs/adr/ADR-002-k8s-deploy.md"
mv "$R/docs/adr/ADR-003-placeholder-3.md" "$R/docs/adr/ADR-003-postgres-read-replica.md"
mv "$R/docs/adr/ADR-004-placeholder-4.md" "$R/docs/adr/ADR-004-feature-flags.md"
cat > "$R/docs/decisions.md" <<'EOF'
# 결정 로그

ADR 도입 이전의 결정 기록. 하나씩 docs/adr/로 이관 중.

## D-005: 결제 웹훅 재시도 큐를 SQS로

- 상태: 보류 (2026-01-20)
- 메모: 비용 검토 후 재논의.

## D-006: 프론트엔드 상태관리 Zustand 채택

- 상태: 확정 (2026-02-03)
- 메모: Redux 보일러플레이트 부담.

## D-007: 서비스 간 내부 통신 REST → gRPC 전환

- 상태: 확정, 2026-03-02부터 checkout ↔ inventory 구간 시행 중
- 배경: checkout → inventory 재고 조회 호출이 주문당 평균 6회. REST+JSON 직렬화 비용으로 피크 시간 p99 지연이 SLO(100ms)를 초과.
- 결정: 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환. 외부 공개 API는 REST 유지.
- 근거: 사내 부하테스트(bench/grpc-loadtest-2026-02.md) 결과 p99 180ms → 45ms, 페이로드 크기 약 60% 감소.
- 대안:
  - GraphQL 페더레이션: 스키마 관리·게이트웨이 운영 부담이 현 인원(플랫폼팀 2명)으로 감당 불가해 기각. 플랫폼팀이 4명 이상으로 늘면 재검토.
  - REST 유지 + 응답 캐싱: 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려워 기각.
- 담당: 플랫폼팀
EOF
cat > "$R/bench/grpc-loadtest-2026-02.md" <<'EOF'
# gRPC 전환 부하테스트 (2026-02-18)

- 도구: k6, 500 VU, 10분
- 대상: checkout → inventory 재고 조회

| 프로토콜 | p50 | p99 | 평균 페이로드 |
| -------- | --: | --: | ------------: |
| REST+JSON | 41ms | 180ms | 4.8KB |
| gRPC | 12ms | 52ms | 1.9KB |

비고: 1차 측정(2026-02-11)에서는 gRPC p99 45ms였으나 커넥션 풀 워밍업 누락으로 재측정. 위 표가 최종값.
EOF
cat > "$R/proto/inventory.proto" <<'EOF'
syntax = "proto3";
package inventory.v1;

service InventoryService {
  rpc GetStock (GetStockRequest) returns (GetStockResponse);
}

message GetStockRequest { string sku = 1; }
message GetStockResponse { string sku = 1; int32 quantity = 2; }
EOF
( cd "$R" && g init -q -b main && g add -A && g commit -q -m "chore: checkout-platform 결정 로그 및 ADR 001-004" \
  && g commit -q --allow-empty -m "feat(inventory): gRPC 재고 조회 엔드포인트" \
  && g commit -q --allow-empty -m "docs: gRPC 부하테스트 결과 추가" )

# ---------------------------------------------------------------------------
# 5) first-adr-no-dir: docs/ 자체가 없는 프로젝트의 첫 ADR, pyproject.toml 미커밋 변경
# ---------------------------------------------------------------------------
R="$OUT/first-adr-no-dir"
mkdir -p "$R/app"
cat > "$R/pyproject.toml" <<'EOF'
[project]
name = "signup-api"
version = "0.3.1"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.112",
    "sqlalchemy>=2.0",
]
EOF
cat > "$R/app/mail.py" <<'EOF'
import smtplib
from email.message import EmailMessage


def send_verification(to: str, token: str) -> None:
    # 가입 요청 처리 중 동기 발송
    msg = EmailMessage()
    msg["To"] = to
    msg["Subject"] = "이메일 인증"
    msg.set_content(f"https://example.com/verify?token={token}")
    with smtplib.SMTP("smtp.internal", 25) as s:
        s.send_message(msg)
EOF
( cd "$R" && g init -q -b main && g add -A && g commit -q -m "feat: signup-api 초기 구성" \
  && g commit -q --allow-empty -m "feat: 가입 인증 메일 발송" )
cat > "$R/pyproject.toml" <<'EOF'
[project]
name = "signup-api"
version = "0.3.1"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.112",
    "sqlalchemy>=2.0",
    "celery>=5.4",
]
EOF

# ---------------------------------------------------------------------------
# 6) empty-adr-dir: docs/adr/는 커밋돼 있지만 .gitkeep만 존재, package.json 미커밋 변경
# ---------------------------------------------------------------------------
R="$OUT/empty-adr-dir"
mkdir -p "$R/docs/adr" "$R/src"
touch "$R/docs/adr/.gitkeep"
cat > "$R/package.json" <<'EOF'
{
  "name": "partner-gateway",
  "version": "2.1.0",
  "private": true,
  "dependencies": {
    "express": "^4.19.2",
    "express-session": "^1.18.0"
  }
}
EOF
cat > "$R/src/auth.js" <<'EOF'
const session = require('express-session');

module.exports = session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
});
EOF
( cd "$R" && g init -q -b main && g add -A && g commit -q -m "chore: partner-gateway 초기 구성, docs/adr 디렉터리 추가" \
  && g commit -q --allow-empty -m "feat: 파트너 주문 조회 API" )
cat > "$R/package.json" <<'EOF'
{
  "name": "partner-gateway",
  "version": "2.1.0",
  "private": true,
  "dependencies": {
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2"
  }
}
EOF

# ---------------------------------------------------------------------------
# 7) no-commit-repo: git init만 하고 커밋이 하나도 없는 저장소 (HEAD 없음, 파일은 전부 미추적)
# ---------------------------------------------------------------------------
R="$OUT/no-commit-repo"
mkdir -p "$R/app"
cat > "$R/requirements.txt" <<'EOF'
fastapi==0.112.2
openai==1.40.0
EOF
cat > "$R/app/llm_client.py" <<'EOF'
from openai import OpenAI

client = OpenAI()


def summarize(text: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"다음 고객 문의를 요약해줘:\n{text}"}],
    )
    return resp.choices[0].message.content
EOF
( cd "$R" && g init -q -b main )

# ---------------------------------------------------------------------------
# 8) non-git-folder: git 저장소가 아닌 일반 폴더
# 주의: 상위 디렉터리에 git 저장소가 있으면 git이 그것을 찾아 조건이 깨진다.
#       run 복사본은 git 저장소 밖에 두거나, GIT_CEILING_DIRECTORIES를 repo의 상위(run) 디렉터리로 지정해 실행한다.
# ---------------------------------------------------------------------------
R="$OUT/non-git-folder"
mkdir -p "$R/src"
cat > "$R/package.json" <<'EOF'
{
  "name": "internal-dashboard",
  "version": "0.4.0",
  "private": true,
  "dependencies": {
    "express": "^4.19.2"
  }
}
EOF
cat > "$R/src/index.js" <<'EOF'
const express = require('express');

const app = express();
app.get('/health', (req, res) => res.json({ ok: true }));
app.listen(8080);
EOF

# ---------------------------------------------------------------------------
# 9) commit-citation-trap: 커밋 인용 함정. 워킹트리는 깨끗함(git diff 비어 있음).
#    실제 jose 전환(package.json, src/auth.js)은 평범한 메시지의 커밋에 있고,
#    그 위에 그럴듯한 메시지의 빈 커밋이 있다. 메시지만 보고 인용하면 빈 커밋을 고르게 된다.
# ---------------------------------------------------------------------------
R="$OUT/commit-citation-trap"
mkdir -p "$R/docs/adr" "$R/src"
cat > "$R/package.json" <<'EOF'
{
  "name": "account-api",
  "version": "3.2.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2"
  }
}
EOF
cat > "$R/src/auth.js" <<'EOF'
import jwt from 'jsonwebtoken';

export function verifyToken(token) {
  return jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] });
}
EOF
cat > "$R/docs/adr/ADR-001-express-framework.md" <<'EOF'
# ADR-001: HTTP 프레임워크로 Express 사용

- **Status:** Accepted
- **Date:** 2026-01-12
- **Decision:** account-api의 HTTP 프레임워크로 Express 4를 사용한다.
- **Scope:** account-api
- **Decision Source:** Human
EOF
( cd "$R" && g init -q -b main && g add -A && g commit -q -m "feat: account-api 초기 구성" )
# 실제 jose 전환 커밋: 메시지는 평범하게
cat > "$R/package.json" <<'EOF'
{
  "name": "account-api",
  "version": "3.2.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "express": "^4.21.1",
    "jose": "^5.9.6"
  }
}
EOF
cat > "$R/src/auth.js" <<'EOF'
import { jwtVerify } from 'jose';

const secret = new TextEncoder().encode(process.env.JWT_SECRET);

export async function verifyToken(token) {
  const { payload } = await jwtVerify(token, secret, { algorithms: ['HS256'] });
  return payload;
}
EOF
# 그 위에 파일 변경 없는 빈 커밋: 메시지는 그럴듯하게
( cd "$R" && g add -A && g commit -q -m "chore: dependency bump" \
  && g commit -q --allow-empty -m "feat: switch to jose for JWT verification" )

echo "fixtures created in $OUT"
