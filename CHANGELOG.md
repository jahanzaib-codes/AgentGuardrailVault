# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-13

### Added
- **Core Smart Contracts**:
  - `AgentGuardrailVault.sol`: ERC-4337 smart vault with scoped ephemeral session keys.
  - Multi-tier policy engine: 24-hour spending velocity caps, calldata selector extraction (`bytes4(payload[:4])`), and target whitelisting.
  - Dynamic Oracle corridor slippage verification using live Chainlink / Pyth benchmarks.
  - Multi-sig emergency halt circuit breaker.
- **Verification Engine & Interactive CLI**:
  - Terminal simulation harness (`cli.py`) testing legitimate vs anomalous agent transactions.
  - Multi-stage Docker containerization and Docker Compose orchestration.
  - Automated CI/CD workflow testing Python 3.10 and 3.11 with Flake8 compliance.
