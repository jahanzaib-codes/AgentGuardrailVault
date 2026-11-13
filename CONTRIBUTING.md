# Contributing to AgentGuardrailVault

Thank you for your interest in contributing to **AgentGuardrailVault**. This project implements institutional ERC-4337 smart vault infrastructure and on-chain policy guardrails for autonomous AI agents across Base, Arbitrum, and Ethereum.

## Guidelines

1. **Smart Contracts**:
   - Write clean, type-safe Solidity `0.8.24` code.
   - Use custom errors for all reverts to conserve execution gas.
   - Strictly follow Checks-Effects-Interactions patterns.
2. **Commit Conventions**:
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat(...)`: New features
   - `fix(...)`: Bug fixes
   - `docs(...)`: Documentation updates
   - `infra(...)`: CI/CD or Docker configurations
3. **Pull Request Workflow**:
   - Run `python cli.py demo` locally before submitting PRs.
   - Ensure zero warnings under `flake8`.
