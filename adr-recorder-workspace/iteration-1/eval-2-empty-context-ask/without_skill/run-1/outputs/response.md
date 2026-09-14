ADR 작성 전에 어떤 결정을 기록할지 확인이 필요합니다. 주제를 말씀해 주지 않으셨고, 결정 배경을 제가 지어내면 ADR의 의미가 없어지기 때문입니다.

저장소를 살펴본 결과(`docs/adr/`, `package.json`, `src/index.js`, git 이력) 아직 ADR로 남기지 않은 결정이 하나 보입니다.

- **이벤트 버스 RabbitMQ → Kafka 전환** (커밋 `139bdb9 feat: 이벤트 버스 RabbitMQ -> Kafka 전환`)
  - `package.json`에 `kafkajs ^2.2.4`, `src/index.js`에 Kafka 클라이언트(`brokers: ['kafka:9092']`)가 있습니다.
  - 기존 ADR은 `ADR-001-fastify.md` 하나뿐이고, 이 전환을 다룬 ADR은 없습니다.

이 전환을 **ADR-002**로 작성하면 될까요? 그렇다면 아래 내용을 알려주시면 ADR-001과 같은 형식(Status / Date / Decision / Scope / Decision Source)에 배경·대안·결과 섹션을 더해 `docs/adr/ADR-002-kafka-event-bus.md`로 작성하겠습니다.

1. **전환 이유**: RabbitMQ에서 어떤 문제가 있었나요? (처리량, 이벤트 재처리·보존, 순서 보장, 다른 서비스와의 표준화 등)
2. **검토한 대안**: RabbitMQ 유지/튜닝, RabbitMQ Streams, NATS, 클라우드 매니지드 큐 등 중에 비교한 것이 있었나요?
3. **감수한 트레이드오프**: 운영 복잡도, 마이그레이션 비용, 전달 보장 방식의 변화 등
4. **결정 시점과 결정 주체**: 날짜, 그리고 사람이 내린 결정인지(ADR-001처럼 `Human`)

다른 결정을 기록하시려는 거라면 그 주제만 한 줄로 알려주셔도 됩니다.
