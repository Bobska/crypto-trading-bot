# Crypto Trading Bot - AI Coding Instructions

## Project Overview
This is a cryptocurrency trading bot system designed for automated trading strategies. The codebase will follow a microservices-like architecture with clear separation between trading logic, market data, risk management, and portfolio tracking.

## Architecture Principles
- **Event-driven design**: Market data flows through event streams to trading strategies
- **Plugin-based strategies**: Trading algorithms are implemented as pluggable modules
- **Risk-first approach**: All trades must pass through risk management layers
- **Configuration-driven**: Trading parameters, API keys, and limits defined in config files

## Key Components (To Be Developed)
```
src/
├── core/              # Core trading engine and event system
├── strategies/        # Trading strategy implementations
├── data/             # Market data ingestion and processing
├── risk/             # Risk management and position sizing
├── portfolio/        # Portfolio tracking and reporting
└── adapters/         # Exchange API integrations
```

## Development Workflow
- Use environment variables for sensitive data (API keys, secrets)
- Implement comprehensive logging for trade decisions and market events
- All strategies must include backtesting capabilities
- Real money trading requires explicit configuration flags

## Critical Patterns
- **Strategy Interface**: All trading strategies implement a common interface with `analyze()`, `signal()`, and `execute()` methods
- **Risk Checks**: Every trade decision flows through configurable risk validators
- **Event Sourcing**: Market events and trade decisions are logged for replay and analysis
- **Circuit Breakers**: Automatic shutoffs for loss limits and API failures

## Configuration Management
- `config/` directory contains environment-specific settings
- Trading parameters in `strategies.yml`
- Risk limits in `risk-management.yml`
- Exchange credentials via environment variables only

## Testing Strategy
- Unit tests for all strategy logic with mock market data
- Integration tests for exchange adapters using sandbox APIs
- Backtesting framework for historical strategy validation
- Never test with real money in development

## Security Considerations
- API keys stored in environment variables, never in code
- Rate limiting for all exchange API calls
- Encrypted storage for sensitive portfolio data
- Audit logging for all trading decisions

## Development Standards
All code changes must follow the standards defined in `.github/DEVELOPMENT_STANDARDS.md`, including:
- Conventional commit messages and semantic branch naming
- SOLID principles and clean architecture patterns
- Comprehensive testing and documentation requirements
- Atomic commits with clear separation of concerns

---
*This file will be updated as the codebase develops. Focus on maintaining clear boundaries between components and ensuring all trading logic is testable and auditable.*