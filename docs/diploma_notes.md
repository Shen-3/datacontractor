# Diploma Notes

## Goal

Develop a software service ensuring registration and versioning of data contracts, schema compatibility checking, data quality control, and violation tracking in ETL processes of analytical systems.

## Object of Research

ETL/ELT processes and analytical information systems using data from multiple sources.

## Subject of Research

Methods and software tools for data contract management, schema control, and data quality verification.

## Novelty and Practical Significance

Unlike existing solutions (Great Expectations, Soda Core), DataContractor provides:
- Integrated contract registry with versioning and compatibility checking
- Unified quality engine with 13 check types
- Breaking change detection between contract versions
- Violation tracking with severity levels and status management
- Demo ETL pipeline for educational purposes

The service can be used as:
- A foundation for data governance in analytical systems
- An educational tool for teaching data engineering concepts
- A prototype for production data quality platforms

## Chapter Structure

### Chapter 1: Theoretical Foundations
- Data contracts concept and necessity
- ETL/ELT process challenges
- Data quality control methods
- Schema evolution and compatibility
- Overview of existing solutions

### Chapter 2: System Design
- Requirements analysis
- Architecture design
- Database schema
- API specification
- Quality check types

### Chapter 3: Implementation
- Technology stack selection
- Contract registry implementation
- Schema validation engine
- Compatibility checker
- Quality engine
- Violation store
- REST API
- Dashboard

### Chapter 4: Testing and Experiments
- Unit and integration tests
- Demo scenarios
- Performance experiments
- Comparison with existing tools

## Defense Demo Script

1. Open README and architecture diagram
2. Start: `docker compose up --build`
3. Open API docs at `http://localhost:8000/docs`
4. Show registered contract `users_events`
5. Run valid dataset: `make demo-valid` → status: passed
6. Run invalid enum: `make demo-invalid-enum` → violation shown
7. Run missing field: `make demo-invalid-schema` → critical violation, blocked
8. Show breaking schema version comparison
9. Show dashboard with violations by severity
10. Show tests: `pytest -v`
11. Show CI pipeline in GitHub Actions
12. Show commit history by milestone
