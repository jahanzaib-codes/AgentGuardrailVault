# AgentGuardrailVault 🛡️🤖

[![CI](https://github.com/jahanzaib-codes/AgentGuardrailVault/actions/workflows/ci.yml/badge.svg)](https://github.com/jahanzaib-codes/AgentGuardrailVault/actions/workflows/ci.yml)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.24-363636.svg)](https://soliditylang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker Ready](https://img.shields.io/badge/docker-ready-brightgreen.svg)](Dockerfile)
[![Chains](https://img.shields.io/badge/Chains-Base%20%7C%20Arbitrum%20%7C%20Ethereum-blueviolet.svg)](#supported-networks)

An institutional-grade **ERC-4337 smart account vault and on-chain policy gate** engineered to provide non-custodial execution guardrails for autonomous AI agents across **Base** and **Arbitrum**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AGENT-GUARDRAIL-VAULT ARCHITECTURE                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   [ Autonomous AI Agent ] (LLM / Reinforcement Learning Model)                         │
│             │                                                                          │
│             ▼ (Signs UserOperation via Scoped Ephemeral Session Key)                   │
│   [ ERC-4337 EntryPoint / AgentGuardrailVault ]                                        │
│             │                                                                          │
│             ├──► [ Session Key Authenticator ] ──► Expiration & Signature Check        │
│             │                                                                          │
│             ├──► [ 24h Velocity Cap ]          ──► Spend Rate Limit Enforcement         │
│             │                                                                          │
│             ├──► [ Calldata Selector Gate ]    ──► bytes4 Whitelist (Swap Only)        │
│             │                                                                          │
│             └──► [ Oracle Corridor Gate ]      ──► Chainlink / Pyth Slippage Corridor  │
│                                                                                        │
│             ▼ (All Security Invariants Verified)                                       │
│   [ Target DEX Execution: Aerodrome (Base) / Camelot (Arbitrum) ]                      │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Features

- **Scoped Ephemeral Session Keys**: AI agents hold time-bounded signing keys without possessing master protocol ownership. Keys expire automatically and require cryptographic rotation.
- **24-Hour Spending Velocity Caps**: Mathematically enforces daily expenditure limits per agent to prevent catastrophic capital drain in the event of prompt injection or model hallucination.
- **Calldata Function Selector Whitelist**: Inspects `bytes4(payload[:4])` at the EVM execution layer to prevent agents from calling administrative or unauthorized methods.
- **Dynamic Oracle Slippage Corridor**: Compares agent execution prices against live decentralized oracle feeds (Chainlink AggregatorV3 & Pyth Network) with configurable basis-point slippage thresholds (e.g. 100 bps / 1.00%).
- **Multi-Sig Emergency Circuit Breaker**: Immediate pause switch enabling external sentinels or multisigs to halt agent routes during market anomalies.

---

## 🛡️ Guardrail Policy Matrix

| Security Layer | Enforced Condition | Revert Trigger | Attack Vector Prevented |
| :--- | :--- | :--- | :--- |
| **Session Key Gate** | `block.timestamp <= expiresAt` | `SessionKeyInvalidOrExpired()` | Stale / compromised key re-use |
| **Target Whitelist** | `whitelistedTargets[target] == true` | `TargetNotPermitted()` | Phishing / malicious drain contracts |
| **Selector Inspection** | `authorizedSelectors[bytes4] == true` | `SelectorForbidden()` | Privilege escalation (`upgradeTo`, etc.) |
| **Daily Velocity Cap** | `spentToday + value <= dailySpendLimit` | `DailyVelocityExceeded()` | Runaway trades / rapid treasury drain |
| **Oracle Slippage** | `deviation <= maxSlippageBps` | `OracleSlippageBreached()` | MEV sandwich attacks / bad routing |
| **Emergency Switch** | `isEmergencyHalted == false` | `SystemHalted()` | Flash-loan or protocol insolvency events |

---

## 🚀 Quick Start & CLI Demo

### 1. Installation

```bash
git clone https://github.com/jahanzaib-codes/AgentGuardrailVault.git
cd AgentGuardrailVault
pip install -r requirements.txt
```

### 2. Run Interactive Terminal Verification Suite

```bash
# Run multi-scenario agent verification demo
python cli.py demo

# Inspect registered agent session keys and daily budgets
python cli.py policies
```

### Terminal Output Preview

```
=========================================================================================================
   🛡️ AGENT-GUARDRAIL-VAULT: ON-CHAIN POLICY & CIRCUIT BREAKER VERIFICATION SUITE
=========================================================================================================

[1/3] Registered Ephemeral AI Agent Session Keys:
| Agent ID                | Chain    | Daily Cap   | Remaining Budget   | Session Key       |
|-------------------------|----------|-------------|--------------------|-------------------|
| agent-base-alpha-01     | Base     | $25,000.00  | $20,500.00         | 0x71C836...E7A81A |
| agent-arb-rebalancer-02 | Arbitrum | $50,000.00  | $38,000.00         | 0x89205A...2c43e7 |

[2/3] Live Autonomous AI Agent Transaction Stream & Guardrail Interception:
| Tx ID       | Target Protocol      | Value (USD)   | Exec Price   | Oracle Benchmark   | Verdict        |
|-------------|----------------------|---------------|--------------|--------------------|----------------|
| TX-BASE-001 | Aerodrome V2 (Base)  | $4,500.00     | $3,258.00    | $3,250.00          | ✅ APPROVED    |
| TX-SCAM-003 | Unverified Phishing  | $8,000.00     | $3,250.00    | N/A                | 🚫 INTERCEPTED |
| TX-SLIP-004 | Aerodrome V2 (Base)  | $6,000.00     | $3,480.00    | $3,250.00          | 🚫 INTERCEPTED |
| TX-OVER-005 | Aerodrome V2 (Base)  | $30,000.00    | $3,252.00    | N/A                | 🚫 INTERCEPTED |
```

---

## 🐳 Docker Deployment

```bash
# Build and run container with docker-compose
docker-compose up -d --build

# View real-time logs
docker-compose logs -f guardrail-vault
```

---

## 📁 Repository Structure

```
AgentGuardrailVault/
├── contracts/
│   ├── core/
│   │   └── AgentGuardrailVault.sol   # Production smart vault and execution gate
│   └── interfaces/
│       ├── IAgentGuardrail.sol       # Guardrail event and data interfaces
│       └── IOracleRouter.sol         # Chainlink / Pyth oracle router interface
├── src/
│   ├── engine/
│   │   └── guardrail_verifier.py     # Sub-millisecond policy evaluation engine
│   ├── models/
│   │   └── agent_models.py           # Pydantic data schemas
│   └── simulator/
│       └── agent_simulation.py       # Multi-scenario autonomous execution simulator
├── cli.py                            # Interactive Click terminal interface
├── main.py                           # Standalone entrypoint
├── foundry.toml                      # Foundry build and RPC network profile
├── Dockerfile                        # Multi-stage production container
├── docker-compose.yml                # Microservice container orchestration
├── requirements.txt                  # Locked Python dependencies
├── CONTRIBUTING.md                   # Open source contribution guidelines
├── SECURITY.md                       # Security policy and disclosure runbook
├── CHANGELOG.md                      # Release notes history
└── README.md                         # Architecture documentation
```

---

## 🤝 Professional Consultation & Custom Smart Contract Engineering

Looking for production-grade smart contracts, ERC-4337 Account Abstraction infrastructure, or custom AI agent on-chain execution guardrails?

- **Fiverr**: [jahanzaib313110](https://www.fiverr.com/jahanzaib313110)
- **Telegram**: [@JanzebBlockdev](https://t.me/JanzebBlockdev)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
