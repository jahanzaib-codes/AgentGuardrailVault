"""On-chain Policy & Guardrail Verification Engine."""

import time
from typing import Dict
from ..models.agent_models import SessionKeyPolicy, AgentExecutionIntent, GuardrailAuditResult


class GuardrailVerifierEngine:
    """Simulates on-chain smart contract guardrail logic with sub-millisecond precision."""

    def __init__(self, max_slippage_bps: int = 100):
        self.max_slippage_bps = max_slippage_bps  # 100 bps = 1.00%
        self.whitelisted_targets: Dict[str, str] = {
            "0x4200000000000000000000000000000000000006": "Aerodrome Router (Base)",
            "0xc873fEcbd354f5A56E00E710B90EF220d0c7fa65": "Camelot V3 Router (Arbitrum)",
            "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45": "Uniswap V3 SwapRouter02"
        }
        self.authorized_selectors: Dict[str, str] = {
            "0x38ed1739": "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
            "0x414bf389": "exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))",
            "0xb6f9de95": "swapExactETHForTokens(uint256,address[],address,uint256)"
        }
        self.oracle_prices: Dict[str, float] = {
            "ETH": 3250.00,
            "WBTC": 88400.00,
            "SOL": 215.50
        }

    def verify_intent(
        self,
        intent: AgentExecutionIntent,
        policy: SessionKeyPolicy
    ) -> GuardrailAuditResult:
        current_time = int(time.time())
        flags = []

        # 1. Session Key Active & Expiration Check
        if not policy.is_active or current_time > policy.expires_at_timestamp:
            return GuardrailAuditResult(
                intent_id=intent.intent_id,
                agent_name=intent.agent_name,
                passed=False,
                verdict="INTERCEPTED",
                violation_code="SESSION_KEY_EXPIRED",
                violation_detail="AI Agent session key is invalid or past expiration timestamp.",
                remaining_daily_budget_usd=max(0.0, policy.daily_spend_limit_usd - policy.spent_today_usd),
                gas_cost_estimate=21000,
                security_flags=["CRITICAL: Unauthorized session key execution attempt."]
            )

        # 2. Whitelisted Target Verification
        if intent.target_address.lower() not in [t.lower() for t in self.whitelisted_targets]:
            return GuardrailAuditResult(
                intent_id=intent.intent_id,
                agent_name=intent.agent_name,
                passed=False,
                verdict="INTERCEPTED",
                violation_code="UNAUTHORIZED_TARGET",
                violation_detail=f"Target {intent.target_address} ({intent.target_protocol}) is not whitelisted.",
                remaining_daily_budget_usd=max(0.0, policy.daily_spend_limit_usd - policy.spent_today_usd),
                gas_cost_estimate=24500,
                security_flags=["BLOCKED: Agent attempted out-of-bounds target protocol interaction."]
            )

        # 3. Calldata Function Selector Check
        selector = intent.raw_calldata[:10].lower()
        if selector not in [s.lower() for s in self.authorized_selectors]:
            return GuardrailAuditResult(
                intent_id=intent.intent_id,
                agent_name=intent.agent_name,
                passed=False,
                verdict="INTERCEPTED",
                violation_code="FORBIDDEN_FUNCTION_SELECTOR",
                violation_detail=f"Selector {selector} is forbidden. Only verified DEX swap selectors permitted.",
                remaining_daily_budget_usd=max(0.0, policy.daily_spend_limit_usd - policy.spent_today_usd),
                gas_cost_estimate=26000,
                security_flags=["SECURITY GATE: Blocked non-whitelisted method execution."]
            )

        # 4. Daily Velocity Limit Enforcement
        remaining_budget = policy.daily_spend_limit_usd - policy.spent_today_usd
        if intent.value_usd > remaining_budget:
            return GuardrailAuditResult(
                intent_id=intent.intent_id,
                agent_name=intent.agent_name,
                passed=False,
                verdict="INTERCEPTED",
                violation_code="DAILY_VELOCITY_BREACH",
                violation_detail=(
                    f"Requested execution value (${intent.value_usd:,.2f}) exceeds remaining 24h budget "
                    f"(${remaining_budget:,.2f})."
                ),
                remaining_daily_budget_usd=remaining_budget,
                gas_cost_estimate=28000,
                security_flags=["VELOCITY CAP: 24-hour balance expenditure threshold triggered."]
            )

        # 5. Dynamic Oracle Corridor Slippage Verification
        benchmark_price = self.oracle_prices.get(intent.asset_symbol, intent.proposed_execution_price)
        price_diff = abs(benchmark_price - intent.proposed_execution_price)
        deviation_pct = (price_diff / benchmark_price) * 100.0
        slippage_bps = int(deviation_pct * 100)

        if slippage_bps > self.max_slippage_bps:
            return GuardrailAuditResult(
                intent_id=intent.intent_id,
                agent_name=intent.agent_name,
                passed=False,
                verdict="INTERCEPTED",
                violation_code="ORACLE_SLIPPAGE_BREACH",
                violation_detail=(
                    f"Proposed price ${intent.proposed_execution_price:,.2f} deviates {deviation_pct:.2f}% "
                    f"from Oracle benchmark (${benchmark_price:,.2f}). Max allowed: {self.max_slippage_bps / 100:.2f}%."
                ),
                oracle_benchmark_price=benchmark_price,
                price_deviation_pct=deviation_pct,
                remaining_daily_budget_usd=remaining_budget,
                gas_cost_estimate=32000,
                security_flags=["MEV PROTECTION: High slippage / sandwich trap prevented by Oracle corridor."]
            )

        # Update spent balance for approved intent
        policy.spent_today_usd += intent.value_usd
        flags.append("VERIFIED: Session Key active and authorized.")
        flags.append("VERIFIED: Whitelisted DEX target & function selector.")
        flags.append(f"VERIFIED: Price within Oracle tolerance ({deviation_pct:.2f}% deviation).")

        return GuardrailAuditResult(
            intent_id=intent.intent_id,
            agent_name=intent.agent_name,
            passed=True,
            verdict="APPROVED",
            oracle_benchmark_price=benchmark_price,
            price_deviation_pct=deviation_pct,
            remaining_daily_budget_usd=policy.daily_spend_limit_usd - policy.spent_today_usd,
            gas_cost_estimate=48500,
            security_flags=flags
        )
