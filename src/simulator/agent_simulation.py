"""Multi-Scenario Autonomous AI Agent Execution Simulator."""

import time
from typing import List, Tuple
from ..models.agent_models import SessionKeyPolicy, AgentExecutionIntent, GuardrailAuditResult
from ..engine.guardrail_verifier import GuardrailVerifierEngine


def generate_mock_policies() -> List[SessionKeyPolicy]:
    now = int(time.time())
    return [
        SessionKeyPolicy(
            agent_id="agent-base-alpha-01",
            session_key_address="0x71C8360f3a8b79d23B5A1a61c3B7cD2190E7A81A",
            chain="Base",
            is_active=True,
            expires_at_timestamp=now + 86400 * 7,  # 7 days
            daily_spend_limit_usd=25000.0,
            spent_today_usd=0.0
        ),
        SessionKeyPolicy(
            agent_id="agent-arb-rebalancer-02",
            session_key_address="0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7",
            chain="Arbitrum",
            is_active=True,
            expires_at_timestamp=now + 86400 * 3,  # 3 days
            daily_spend_limit_usd=50000.0,
            spent_today_usd=0.0
        ),
        SessionKeyPolicy(
            agent_id="agent-compromised-03",
            session_key_address="0x2546BcD3c84621e976D8185a91A922aE77ECEc30",
            chain="Base",
            is_active=True,
            expires_at_timestamp=now + 86400 * 1,
            daily_spend_limit_usd=10000.0,
            spent_today_usd=0.0
        )
    ]


def run_demo_simulation() -> Tuple[List[SessionKeyPolicy], List[Tuple[AgentExecutionIntent, GuardrailAuditResult]]]:
    engine = GuardrailVerifierEngine(max_slippage_bps=100)  # 1.0% max slippage
    policies = generate_mock_policies()
    policy_map = {p.agent_id: p for p in policies}

    intents = [
        # Scenario 1: Legitimate Rebalance on Aerodrome (Base) - SAFE
        AgentExecutionIntent(
            intent_id="TX-BASE-001",
            agent_name="Autonomous Momentum AI (Base)",
            session_key=policies[0].session_key_address,
            target_protocol="Aerodrome V2 (Base)",
            target_address="0x4200000000000000000000000000000000000006",
            function_signature="swapExactTokensForTokens",
            value_usd=4500.0,
            asset_symbol="ETH",
            proposed_execution_price=3258.00,  # 0.24% delta vs 3250.00
            raw_calldata="0x38ed17390000000000000000000000000000000000000000000000000de0b6b3a7640000"
        ),
        # Scenario 2: Valid Arbitrum V3 Swap on Camelot - SAFE
        AgentExecutionIntent(
            intent_id="TX-ARB-002",
            agent_name="Cross-L2 StatArb Agent (Arbitrum)",
            session_key=policies[1].session_key_address,
            target_protocol="Camelot V3 Router (Arbitrum)",
            target_address="0xc873fEcbd354f5A56E00E710B90EF220d0c7fa65",
            function_signature="exactInputSingle",
            value_usd=12000.0,
            asset_symbol="WBTC",
            proposed_execution_price=88550.00,  # 0.17% delta vs 88400.00
            raw_calldata="0x414bf3890000000000000000000000000000000000000000000000000000000000000020"
        ),
        # Scenario 3: Malicious Drain Attempt targeting Unwhitelisted Attacker Contract - BLOCKED
        AgentExecutionIntent(
            intent_id="TX-SCAM-003",
            agent_name="Compromised Session Key / Rogue Prompt",
            session_key=policies[2].session_key_address,
            target_protocol="Unverified Phishing Vault",
            target_address="0xDeadDeaDDEADdeAddeAdDEAdDEADDEADdeadBEef",
            function_signature="drainTreasury",
            value_usd=8000.0,
            asset_symbol="ETH",
            proposed_execution_price=3250.00,
            raw_calldata="0x70a082310000000000000000000000000000000000000000000000000000000000000000"
        ),
        # Scenario 4: Frontrunned Sandwich Attack (High Slippage Hallucination) - BLOCKED
        AgentExecutionIntent(
            intent_id="TX-SLIP-004",
            agent_name="Autonomous Momentum AI (Base)",
            session_key=policies[0].session_key_address,
            target_protocol="Aerodrome V2 (Base)",
            target_address="0x4200000000000000000000000000000000000006",
            function_signature="swapExactTokensForTokens",
            value_usd=6000.0,
            asset_symbol="ETH",
            proposed_execution_price=3480.00,  # 7.07% delta vs 3250.00 (Exceeds 1.0% limit!)
            raw_calldata="0x38ed17390000000000000000000000000000000000000000000000000de0b6b3a7640000"
        ),
        # Scenario 5: Velocity Cap Overflow (Exceeds Daily Spending Budget) - BLOCKED
        AgentExecutionIntent(
            intent_id="TX-OVER-005",
            agent_name="Autonomous Momentum AI (Base)",
            session_key=policies[0].session_key_address,
            target_protocol="Aerodrome V2 (Base)",
            target_address="0x4200000000000000000000000000000000000006",
            function_signature="swapExactTokensForTokens",
            value_usd=30000.0,  # Exceeds remaining $20,500.00 budget!
            asset_symbol="ETH",
            proposed_execution_price=3252.00,
            raw_calldata="0x38ed17390000000000000000000000000000000000000000000000000de0b6b3a7640000"
        )
    ]

    results = []
    # Map intents to policies
    agent_to_policy = {
        "TX-BASE-001": policy_map["agent-base-alpha-01"],
        "TX-ARB-002": policy_map["agent-arb-rebalancer-02"],
        "TX-SCAM-003": policy_map["agent-compromised-03"],
        "TX-SLIP-004": policy_map["agent-base-alpha-01"],
        "TX-OVER-005": policy_map["agent-base-alpha-01"]
    }

    for intent in intents:
        pol = agent_to_policy[intent.intent_id]
        res = engine.verify_intent(intent, pol)
        results.append((intent, res))

    return policies, results
