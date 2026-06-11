# PROJECT_AGENT_PROMPT.md

# DataContractor: сервис data contracts и контроля качества данных для аналитического контура

## 0. Назначение документа

Этот документ является подробным проектным промптом для агентной разработки через Codex/AI coding agent.

Агент должен использовать этот файл как основное техническое задание для создания полноценного дипломного проекта по теме:

> **Разработка сервиса управления контрактами данных и контроля качества для ETL-процессов аналитического контура**

Проект должен быть реализован как инженерный production-like prototype, пригодный для:
- демонстрации на защите ВКР;
- размещения в GitHub-портфолио;
- обсуждения на собеседованиях на позиции Data Engineer / Analytics Engineer / Data Platform Engineer;
- дальнейшего расширения в сторону Data Governance / Data Quality / Data Observability.

---

## 1. Важное требование к агенту

Агент должен не просто написать код, а вести разработку как полноценный инженерный проект.

Обязательные действия агента:

1. Создать новый GitHub-репозиторий через GitHub CLI `gh`.
2. Инициализировать локальный git-репозиторий.
3. Делать разработку по этапам.
4. После каждого логического этапа делать отдельный git commit.
5. Использовать осмысленные commit messages.
6. Поддерживать `DEVELOPMENT_LOG.md` с историей реализации.
7. Поддерживать `README.md` как пользовательскую документацию.
8. Поддерживать `docs/` как техническую документацию дипломного проекта.
9. Не смешивать крупные изменения в один commit.
10. После каждого этапа запускать проверки: тесты, линтеры, форматирование, миграции, smoke tests.
11. В конце каждого этапа показывать:
    - что сделано;
    - какие файлы изменены;
    - какие команды проверки выполнены;
    - какой commit создан.

---

## 2. Команды для создания репозитория

Агент должен создать репозиторий через `gh`.

Рекомендуемое имя репозитория:

```bash
datacontractor
```

Команды:

```bash
mkdir datacontractor
cd datacontractor

git init

gh repo create datacontractor \
  --public \
  --description "Data contracts and data quality service for ETL pipelines" \
  --source=. \
  --remote=origin \
  --push
```

Если `gh` не авторизован, агент должен остановиться и сообщить пользователю:

```text
GitHub CLI is not authenticated. Run: gh auth login
```

После создания базовой структуры агент должен сделать первый commit:

```bash
git add .
git commit -m "chore: initialize project structure"
git push -u origin main
```

---

## 3. Краткое описание проекта

**DataContractor** — это сервис для управления контрактами данных, версионирования схем, проверки совместимости изменений и контроля качества данных в ETL/ELT-процессах.

Проект моделирует ситуацию, где несколько команд используют общие данные:
- backend-команда производит события или таблицы;
- ETL-процесс загружает данные в аналитическое хранилище;
- аналитики и BI-системы используют эти данные;
- изменение схемы или ухудшение качества данных может сломать downstream-процессы.

Сервис должен позволять:
- регистрировать data contracts;
- хранить версии контрактов;
- проверять входящие данные на соответствие контракту;
- выполнять quality checks;
- определять breaking changes между версиями схем;
- фиксировать нарушения;
- показывать нарушения через API/dashboard;
- интегрироваться в учебный ETL-пайплайн.

---

## 4. Академический контекст

Проект является дипломной работой по направлению, связанному с организацией и программированием вычислительных и информационных систем.

### Возможная тема ВКР

> **Разработка сервиса управления контрактами данных и контроля качества для ETL-процессов аналитического контура**

### Цель работы

Разработать программный сервис, обеспечивающий регистрацию и версионирование контрактов данных, проверку совместимости схем, контроль качества данных и фиксацию нарушений в ETL-процессах аналитического контура.

### Объект исследования

ETL/ELT-процессы и аналитические информационные системы, использующие данные из нескольких источников.

### Предмет исследования

Методы и программные средства управления контрактами данных, контроля схем и проверки качества данных.

### Практический результат

Рабочий программный комплекс, включающий:
- REST API сервиса data contracts;
- базу данных контрактов и нарушений;
- модуль проверки схем;
- модуль quality checks;
- учебный ETL-пайплайн;
- dashboard или web UI нарушений;
- документацию;
- тестовые датасеты;
- демонстрационные сценарии;
- отчёт по экспериментам.

---

## 5. Основная проблема, которую решает проект

В аналитических системах данные часто проходят цепочку:

```text
source systems → ETL/ELT → DWH → marts → BI dashboards / ML models
```

Если источник меняет данные без согласования, ломаются downstream-процессы.

Примеры проблем:
- поле `user_id` переименовали в `client_id`;
- тип `amount` изменился со `string` на `decimal`;
- обязательное поле стало nullable;
- в колонке `event_type` появились неожиданные значения;
- данные перестали обновляться вовремя;
- количество строк резко упало;
- в данных появились дубликаты;
- нарушилась свежесть данных;
- аналитическая витрина загрузила невалидные данные.

Data contracts должны предотвращать такие проблемы.

---

## 6. Целевая архитектура

```text
                    ┌────────────────────────┐
                    │   Contract Registry    │
                    │  versions, owners, SLA │
                    └───────────┬────────────┘
                                │
                                ▼
┌──────────────┐      ┌─────────────────────┐      ┌──────────────┐
│ Data Source  │ ───▶ │ ETL Validation Step │ ───▶ │ Data Warehouse│
└──────────────┘      └──────────┬──────────┘      └──────────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │ Quality Engine    │
                       │ schema + rules    │
                       └─────────┬─────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │ Violations Store  │
                       └─────────┬─────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │ Dashboard / API   │
                       └───────────────────┘
```

---

## 7. Технологический стек

Базовый рекомендуемый стек:

```text
Python 3.11+
FastAPI
PostgreSQL
SQLAlchemy
Alembic
Pydantic
Pandas
Pytest
Docker
Docker Compose
Streamlit or simple FastAPI HTML dashboard
GitHub Actions
```

Дополнительно, если будет время:
- Great Expectations или Soda Core как comparison/reference layer;
- dbt-like demo;
- OpenAPI documentation;
- Prometheus metrics;
- simple lineage view.

Для первого полноценного варианта лучше не добавлять слишком много внешних data governance tools. Основную бизнес-логику нужно реализовать самостоятельно.

---

## 8. Основные модули системы

### 8.1 Contract Registry

Модуль хранения и управления data contracts.

Функции:
- создать контракт;
- получить контракт;
- получить список контрактов;
- получить конкретную версию;
- создать новую версию;
- сравнить версии;
- пометить контракт активным/архивным;
- хранить владельца и потребителей данных.

Контракт должен содержать:
- имя контракта;
- версию;
- описание;
- владельца;
- список потребителей;
- схему данных;
- quality rules;
- SLA/freshness constraints;
- совместимость;
- дату создания;
- статус.

---

### 8.2 Schema Registry Lite

Упрощённый schema registry.

Должен уметь:
- хранить схемы;
- проверять входящие данные на соответствие схеме;
- сравнивать две версии схемы;
- определять breaking changes.

Минимальная модель поля:

```json
{
  "name": "user_id",
  "type": "integer",
  "required": true,
  "nullable": false,
  "description": "Unique user identifier"
}
```

Поддерживаемые типы:
- string;
- integer;
- float;
- decimal;
- boolean;
- date;
- timestamp;
- enum.

---

### 8.3 Compatibility Checker

Модуль анализа совместимости изменений схемы.

Breaking changes:
- удаление обязательного поля;
- изменение типа поля;
- изменение nullable с `true` на `false`;
- удаление значения из enum;
- переименование поля без alias;
- изменение semantics без версии major.

Non-breaking changes:
- добавление optional поля;
- добавление nullable поля;
- добавление нового значения enum;
- добавление description;
- добавление quality rule с warning severity.

Результат проверки должен возвращать:

```json
{
  "compatible": false,
  "breaking_changes": [
    {
      "field": "user_id",
      "change": "field_removed",
      "severity": "critical",
      "message": "Required field user_id was removed"
    }
  ],
  "warnings": []
}
```

---

### 8.4 Quality Check Engine

Модуль проверки качества данных.

Обязательные проверки:
- `not_null`;
- `unique`;
- `min_value`;
- `max_value`;
- `allowed_values`;
- `regex`;
- `type_check`;
- `row_count_min`;
- `row_count_max`;
- `freshness`;
- `duplicate_rate`;
- `null_rate`;
- `schema_match`.

Каждая проверка должна иметь:
- имя;
- поле;
- параметры;
- severity: info/warning/error/critical;
- результат;
- число нарушенных строк;
- примеры нарушений.

Пример правила:

```yaml
quality_rules:
  - name: user_id_not_null
    type: not_null
    field: user_id
    severity: critical

  - name: event_type_allowed_values
    type: allowed_values
    field: event_type
    values:
      - login
      - logout
      - purchase
    severity: error

  - name: event_time_freshness
    type: freshness
    field: event_time
    max_delay_minutes: 60
    severity: warning
```

---

### 8.5 Violation Store

Хранилище нарушений.

Должно фиксировать:
- contract name;
- contract version;
- dataset name;
- check name;
- check type;
- severity;
- status;
- number of failed rows;
- sample failed records;
- timestamp;
- ETL run ID;
- message.

Статусы:
- open;
- acknowledged;
- resolved;
- ignored.

---

### 8.6 ETL Demo Pipeline

Учебный ETL-процесс, который показывает практическое применение.

Сценарий:

```text
CSV/API/source table
    ↓
extract
    ↓
validate schema
    ↓
run quality checks
    ↓
if ok: load to warehouse
if fail: block load and write violation
```

Нужно реализовать:
- набор synthetic datasets;
- корректный датасет;
- датасет с нарушением схемы;
- датасет с null values;
- датасет с invalid enum;
- датасет с duplicates;
- датасет с stale timestamps;
- pipeline runner.

Команда:

```bash
python -m datacontractor.etl.run --dataset demo/users_events_valid.csv --contract users_events
```

---

### 8.7 Dashboard / UI

Минимальный dashboard можно сделать на Streamlit или простых FastAPI HTML templates.

Dashboard должен показывать:
- список контрактов;
- версии контрактов;
- статус последней проверки;
- violations по severity;
- последние ETL runs;
- график количества нарушений;
- детали конкретного нарушения;
- sample failed rows.

Для первого варианта Streamlit допустим и быстрее.

---

### 8.8 API

REST API должно иметь OpenAPI-документацию через FastAPI.

Минимальные endpoints:

```text
GET    /health

POST   /contracts
GET    /contracts
GET    /contracts/{contract_name}
GET    /contracts/{contract_name}/versions
GET    /contracts/{contract_name}/versions/{version}
POST   /contracts/{contract_name}/versions

POST   /contracts/{contract_name}/validate-schema
POST   /contracts/{contract_name}/validate-data
POST   /contracts/{contract_name}/compare-versions

GET    /violations
GET    /violations/{violation_id}
PATCH  /violations/{violation_id}/status

GET    /etl/runs
GET    /etl/runs/{run_id}
```

---

## 9. Рекомендуемая структура репозитория

```text
datacontractor/
  app/
    main.py
    api/
      __init__.py
      routes_health.py
      routes_contracts.py
      routes_validation.py
      routes_violations.py
      routes_etl.py
    core/
      config.py
      logging.py
      errors.py
    db/
      base.py
      session.py
      models.py
      repositories.py
    schemas/
      contract.py
      validation.py
      violation.py
      etl.py
    services/
      contract_service.py
      schema_validator.py
      compatibility_checker.py
      quality_engine.py
      violation_service.py
      etl_service.py
    quality/
      checks.py
      result.py
      registry.py
    dashboard/
      streamlit_app.py

  data/
    contracts/
      users_events_v1.yaml
      users_events_v2_valid.yaml
      users_events_v2_breaking.yaml
    datasets/
      users_events_valid.csv
      users_events_missing_field.csv
      users_events_nulls.csv
      users_events_invalid_enum.csv
      users_events_duplicates.csv
      users_events_stale.csv

  migrations/
    versions/

  tests/
    unit/
      test_schema_validator.py
      test_compatibility_checker.py
      test_quality_engine.py
      test_contract_service.py
    integration/
      test_contract_api.py
      test_validation_api.py
      test_etl_pipeline.py

  docs/
    architecture.md
    api.md
    data_contract_format.md
    quality_checks.md
    demo_scenarios.md
    diploma_notes.md
    experiments.md

  scripts/
    seed_demo_data.py
    run_demo_etl.py
    reset_db.py

  .github/
    workflows/
      ci.yml

  docker-compose.yml
  Dockerfile
  Makefile
  pyproject.toml
  alembic.ini
  README.md
  PROJECT_AGENT_PROMPT.md
  DEVELOPMENT_LOG.md
  config.example.yaml
  .env.example
  .gitignore
```

---

## 10. Формат data contract

Контракты должны храниться в YAML.

Пример:

```yaml
name: users_events
version: 1.0.0
description: User activity events used by analytics team
owner: user-platform-team
consumers:
  - analytics-team
  - marketing-bi
  - churn-model-team

schema:
  fields:
    - name: user_id
      type: integer
      required: true
      nullable: false
      description: Unique user identifier

    - name: event_type
      type: enum
      required: true
      nullable: false
      values:
        - login
        - logout
        - purchase
      description: Type of user event

    - name: event_time
      type: timestamp
      required: true
      nullable: false
      description: Event timestamp in UTC

    - name: amount
      type: decimal
      required: false
      nullable: true
      description: Purchase amount if event_type is purchase

quality_rules:
  - name: user_id_not_null
    type: not_null
    field: user_id
    severity: critical

  - name: event_type_allowed
    type: allowed_values
    field: event_type
    values:
      - login
      - logout
      - purchase
    severity: error

  - name: event_time_freshness
    type: freshness
    field: event_time
    max_delay_minutes: 1440
    severity: warning

sla:
  update_frequency: daily
  max_delay_minutes: 1440

compatibility:
  mode: backward
```

---

## 11. База данных

Использовать PostgreSQL.

Основные таблицы:

### contracts

Поля:
- id;
- name;
- description;
- owner;
- status;
- created_at;
- updated_at.

### contract_versions

Поля:
- id;
- contract_id;
- version;
- schema_json;
- quality_rules_json;
- sla_json;
- compatibility_mode;
- is_active;
- created_at.

### validation_runs

Поля:
- id;
- contract_id;
- contract_version_id;
- dataset_name;
- status;
- started_at;
- finished_at;
- rows_checked;
- violations_count.

### violations

Поля:
- id;
- validation_run_id;
- contract_name;
- contract_version;
- check_name;
- check_type;
- field_name;
- severity;
- status;
- failed_rows_count;
- sample_records_json;
- message;
- created_at;
- updated_at.

---

## 12. API behavior requirements

### Создание контракта

`POST /contracts`

Должен:
- валидировать YAML/JSON contract;
- проверить уникальность имени;
- сохранить контракт;
- сохранить первую версию;
- вернуть contract id и version.

### Добавление версии

`POST /contracts/{contract_name}/versions`

Должен:
- проверить, существует ли контракт;
- сравнить новую версию с активной;
- выявить breaking changes;
- если есть breaking changes, вернуть compatibility report;
- сохранить версию, если пользователь явно разрешил breaking changes или если версия совместима.

### Проверка данных

`POST /contracts/{contract_name}/validate-data`

Должен:
- принять CSV-файл или путь к dataset в demo mode;
- загрузить данные;
- проверить схему;
- выполнить quality checks;
- создать validation_run;
- записать violations;
- вернуть summary.

Пример ответа:

```json
{
  "contract": "users_events",
  "version": "1.0.0",
  "dataset": "users_events_invalid_enum.csv",
  "status": "failed",
  "rows_checked": 1000,
  "violations_count": 1,
  "violations": [
    {
      "check_name": "event_type_allowed",
      "severity": "error",
      "failed_rows_count": 12,
      "message": "Field event_type contains values outside allowed set"
    }
  ]
}
```

---

## 13. Quality checks: detailed behavior

### not_null

Fails if field contains null/NaN/empty value.

### unique

Fails if duplicate values exist in the field.

### allowed_values

Fails if value is not in configured allowed list.

### regex

Fails if string does not match configured regex.

### min_value / max_value

Fails if numeric value is outside configured range.

### type_check

Fails if value cannot be cast to expected type.

### row_count_min / row_count_max

Fails if dataset row count is outside configured boundary.

### freshness

Fails if max timestamp in configured field is older than threshold.

### duplicate_rate

Fails if duplicate ratio exceeds threshold.

### null_rate

Fails if null ratio exceeds threshold.

---

## 14. Demo scenarios

The project must include demo scenarios.

### Scenario 1: Valid dataset

Input:
- `users_events_valid.csv`

Expected:
- schema valid;
- all quality checks pass;
- validation run status = passed;
- no violations.

### Scenario 2: Missing required field

Input:
- `users_events_missing_field.csv`

Expected:
- schema validation fails;
- violation severity = critical;
- ETL load blocked.

### Scenario 3: Invalid enum values

Input:
- `users_events_invalid_enum.csv`

Expected:
- allowed_values check fails;
- violations recorded;
- dashboard shows error.

### Scenario 4: Null values

Input:
- `users_events_nulls.csv`

Expected:
- not_null check fails;
- failed rows sample saved.

### Scenario 5: Duplicates

Input:
- `users_events_duplicates.csv`

Expected:
- unique or duplicate_rate check fails.

### Scenario 6: Stale data

Input:
- `users_events_stale.csv`

Expected:
- freshness check fails.

### Scenario 7: Breaking schema change

Input:
- `users_events_v2_breaking.yaml`

Expected:
- compatibility checker detects breaking changes;
- report generated.

---

## 15. Dashboard requirements

Dashboard should include:

1. Contracts overview.
2. Contract detail page.
3. Versions list.
4. Latest validation runs.
5. Violations by severity.
6. Violations table.
7. Validation run detail.
8. Sample failed records.
9. Demo run button or instructions.

If using Streamlit, file path:

```text
app/dashboard/streamlit_app.py
```

Run command:

```bash
streamlit run app/dashboard/streamlit_app.py
```

---

## 16. CLI / Makefile commands

Makefile must include:

```makefile
install
dev
test
lint
format
migrate
seed
api
dashboard
demo-valid
demo-invalid-schema
demo-invalid-enum
demo-nulls
demo-duplicates
demo-stale
docker-up
docker-down
clean
```

Example:

```bash
make docker-up
make migrate
make seed
make api
make dashboard
make demo-valid
make demo-invalid-enum
make test
```

---

## 17. Docker Compose

`docker-compose.yml` must include:

- PostgreSQL;
- API service;
- dashboard service, optional;
- optional pgAdmin, if useful.

Minimal:

```text
postgres
api
dashboard
```

The project should work with:

```bash
docker compose up --build
```

---

## 18. Testing requirements

Tests are mandatory.

### Unit tests

Must cover:
- schema validation;
- type casting;
- compatibility checking;
- each quality check;
- violation creation;
- config loading.

### Integration tests

Must cover:
- contract creation via API;
- validation via API;
- ETL demo pipeline;
- DB persistence of validation runs and violations.

### Minimum test target

By the end of development:

```text
At least 30 tests
All tests passing
```

Run:

```bash
pytest
```

---

## 19. CI requirements

GitHub Actions workflow:

`.github/workflows/ci.yml`

Must run:
- install dependencies;
- formatting check;
- lint;
- tests;
- optional Docker build.

Recommended tools:
- pytest;
- ruff;
- black;
- mypy optional.

---

## 20. Documentation requirements

README.md must include:
- project description;
- architecture diagram;
- features;
- tech stack;
- quick start;
- API examples;
- demo scenarios;
- screenshots placeholders;
- testing;
- limitations;
- roadmap.

Docs folder must include:

### docs/architecture.md

Explain:
- components;
- data flow;
- validation flow;
- DB model.

### docs/data_contract_format.md

Explain:
- YAML format;
- schema fields;
- quality rules;
- compatibility modes.

### docs/quality_checks.md

Explain:
- each check;
- parameters;
- examples;
- expected result.

### docs/demo_scenarios.md

Explain:
- all demo datasets;
- expected outcomes.

### docs/experiments.md

Explain:
- validation time by dataset size;
- number of checks;
- results table.

### docs/diploma_notes.md

Explain:
- goal;
- object;
- subject;
- novelty/practical significance;
- chapter structure;
- possible defense demo.

---

## 21. Development log

`DEVELOPMENT_LOG.md` must be updated after each milestone.

Format:

````markdown
# Development Log

## Milestone 1 — Project initialization

Date: YYYY-MM-DD

### Completed
- ...

### Commands executed
```bash
...
```

### Commit
`chore: initialize project structure`

### Notes
- ...
````

---

## 22. Milestones and commits

Agent must follow these milestones.

---

### Milestone 1: Project initialization

Tasks:
- create GitHub repo through `gh`;
- create Python project structure;
- add FastAPI skeleton;
- add README skeleton;
- add Makefile;
- add `.gitignore`;
- add `.env.example`;
- add `DEVELOPMENT_LOG.md`;
- add `PROJECT_AGENT_PROMPT.md`.

Expected commit:

```bash
git commit -m "chore: initialize project structure"
```

Verification:
```bash
python --version
make test
git status
```

---

### Milestone 2: Database and models

Tasks:
- configure PostgreSQL;
- add SQLAlchemy models;
- add Alembic migrations;
- add DB session;
- create tables:
  - contracts;
  - contract_versions;
  - validation_runs;
  - violations.

Expected commit:

```bash
git commit -m "feat: add database models and migrations"
```

Verification:
```bash
make docker-up
make migrate
```

---

### Milestone 3: Contract schema and registry API

Tasks:
- implement contract Pydantic schemas;
- implement create contract;
- implement list contracts;
- implement get contract;
- implement get versions;
- implement add version.

Expected commit:

```bash
git commit -m "feat: implement contract registry api"
```

Verification:
```bash
pytest tests/integration/test_contract_api.py
```

---

### Milestone 4: Schema validator

Tasks:
- implement field type model;
- implement schema validation for pandas DataFrame;
- implement missing required field detection;
- implement type checking;
- implement enum validation;
- add unit tests.

Expected commit:

```bash
git commit -m "feat: add schema validation engine"
```

Verification:
```bash
pytest tests/unit/test_schema_validator.py
```

---

### Milestone 5: Compatibility checker

Tasks:
- compare contract versions;
- detect breaking changes;
- detect non-breaking changes;
- create compatibility report;
- add tests.

Expected commit:

```bash
git commit -m "feat: add contract compatibility checker"
```

Verification:
```bash
pytest tests/unit/test_compatibility_checker.py
```

---

### Milestone 6: Quality check engine

Tasks:
- implement check registry;
- implement not_null;
- implement unique;
- implement allowed_values;
- implement regex;
- implement min/max;
- implement row_count;
- implement freshness;
- implement null_rate;
- implement duplicate_rate;
- add tests.

Expected commit:

```bash
git commit -m "feat: implement data quality checks"
```

Verification:
```bash
pytest tests/unit/test_quality_engine.py
```

---

### Milestone 7: Data validation API

Tasks:
- implement validate-data endpoint;
- load CSV;
- run schema validator;
- run quality checks;
- create validation_run;
- persist violations;
- return validation summary.

Expected commit:

```bash
git commit -m "feat: add data validation api"
```

Verification:
```bash
pytest tests/integration/test_validation_api.py
```

---

### Milestone 8: Demo datasets and ETL pipeline

Tasks:
- create sample contracts;
- create demo datasets;
- implement ETL runner;
- block load on critical errors;
- add Makefile demo commands.

Expected commit:

```bash
git commit -m "feat: add demo etl pipeline and datasets"
```

Verification:
```bash
make demo-valid
make demo-invalid-schema
make demo-invalid-enum
```

---

### Milestone 9: Violations API and dashboard

Tasks:
- implement violations list;
- implement violation detail;
- implement update status;
- implement dashboard;
- show contracts, validation runs, violations.

Expected commit:

```bash
git commit -m "feat: add violations dashboard"
```

Verification:
```bash
make dashboard
```

---

### Milestone 10: Docker, CI, and documentation

Tasks:
- finalize Dockerfile;
- finalize docker-compose;
- add GitHub Actions CI;
- complete README;
- complete docs;
- add demo script for defense;
- update DEVELOPMENT_LOG.

Expected commit:

```bash
git commit -m "chore: finalize docker ci and documentation"
```

Verification:
```bash
docker compose up --build
pytest
```

---

### Milestone 11: Experiments and diploma artifacts

Tasks:
- run validation experiments;
- measure validation time for different dataset sizes;
- create results table;
- write docs/experiments.md;
- write docs/diploma_notes.md;
- add screenshots placeholders or generated screenshots if available.

Expected commit:

```bash
git commit -m "docs: add experiments and diploma materials"
```

Verification:
```bash
git status
```

---

## 23. Definition of Done

Project is considered complete when:

- GitHub repository exists.
- All milestones have separate commits.
- API starts successfully.
- PostgreSQL migrations work.
- At least one contract can be created.
- Contract versions are stored.
- Compatibility checker detects breaking changes.
- Schema validator detects invalid datasets.
- Quality engine supports at least 8 checks.
- Demo ETL pipeline runs.
- Violations are stored in DB.
- Dashboard shows validation results.
- Docker Compose starts project.
- GitHub Actions CI passes.
- At least 30 tests pass.
- README is complete.
- `docs/` contains architecture and diploma notes.
- `DEVELOPMENT_LOG.md` is updated.
- Defense demo can be performed in 5–7 minutes.

---

## 24. Defense demo script

The final demo should follow this sequence:

1. Open README and architecture diagram.
2. Start project:

```bash
docker compose up --build
```

3. Open API docs:

```text
http://localhost:8000/docs
```

4. Show registered contract `users_events`.
5. Run valid dataset:

```bash
make demo-valid
```

6. Show validation passed.
7. Run invalid enum dataset:

```bash
make demo-invalid-enum
```

8. Show violation in API/dashboard.
9. Run missing field dataset:

```bash
make demo-invalid-schema
```

10. Show critical schema violation and blocked ETL load.
11. Show breaking schema version comparison.
12. Show dashboard with violations by severity.
13. Show tests and CI.
14. Show GitHub commits by milestone.

---

## 25. Non-goals

Do not implement in the first version:
- full enterprise data catalog;
- full data lineage system;
- complex RBAC;
- Kafka integration;
- dbt integration;
- production-grade web UI;
- distributed validation engine;
- ML anomaly detection;
- full Great Expectations clone.

These can be listed as future work.

---

## 26. Expected final README positioning

The project should be described as:

```text
DataContractor is a production-like educational data contracts and data quality platform for ETL pipelines. It provides a contract registry, schema compatibility checks, data quality validation, violation tracking, a demo ETL pipeline, and a dashboard for monitoring data contract violations.
```

---

## 27. Agent operating rules

The agent must follow these rules:

1. Always read this file before starting a new milestone.
2. Do not skip milestones unless explicitly instructed by the user.
3. Prefer small, reviewable commits.
4. Before committing, run relevant tests.
5. Do not commit broken code knowingly.
6. Do not silently remove requirements.
7. When a requirement is too large, implement a minimal working version and document the limitation.
8. Keep project runnable locally.
9. Keep Docker Compose functional.
10. Keep README and DEVELOPMENT_LOG updated.
11. Use clear names and simple architecture.
12. Prioritize correctness and demonstrability over excessive features.
13. Do not add unnecessary external services.
14. Do not implement fake tests that do not validate behavior.
15. Keep the project suitable for diploma defense and portfolio review.

---

## 28. First task for Codex

Start with this exact task:

```text
Read PROJECT_AGENT_PROMPT.md. Create a new GitHub repository named datacontractor using gh. Initialize the Python/FastAPI project structure according to section 9. Add README.md skeleton, DEVELOPMENT_LOG.md, Makefile, pyproject.toml, .gitignore, .env.example, docker-compose.yml skeleton, and a minimal FastAPI app with GET /health. Make the first commit with message "chore: initialize project structure" and push it to origin. After completion, show the created file tree, commands executed, and verification results.
```

---

## 29. Second task for Codex

After Milestone 1 is complete:

```text
Implement Milestone 2 from PROJECT_AGENT_PROMPT.md. Add PostgreSQL configuration, SQLAlchemy models, Alembic migrations, database session management, and Docker Compose PostgreSQL service. Create tables contracts, contract_versions, validation_runs, and violations. Add basic tests for database model creation. Run migrations and tests. Commit as "feat: add database models and migrations" and push.
```

---

## 30. Third task for Codex

After Milestone 2 is complete:

```text
Implement Milestone 3 from PROJECT_AGENT_PROMPT.md. Add Contract Registry API with endpoints to create contracts, list contracts, get contract by name, list versions, and add new version. Use Pydantic schemas and repository/service layers. Add integration tests. Commit as "feat: implement contract registry api" and push.
```

---

## 31. Final instruction to Codex

Build this project as a real engineering artifact, not as a toy example. Every feature must be demonstrable through API, CLI/Makefile, tests, or dashboard. The final repository must be understandable to a reviewer who opens GitHub without prior context.
