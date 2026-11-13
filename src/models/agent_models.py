"""Data models for Autonomous AI Agent session policies and execution guardrails."""

from pydantic import BaseModel, Field
from typing import Optional, List


class SessionKeyPolicy(BaseModel):
    agent_id: str
    session_key_address: str
    chain: str  # "Base" | "Arbitrum"
    is_active: bool = True
    expires_at_timestamp: int
    daily_spend_limit_usd: float = Field(ge=0.0)
    spent_today_usd: float = 0.0


class AgentExecutionIntent(BaseModel):
    intent_id: str
    agent_name: str
    session_key: str
    target_protocol: str
    target_address: str
    function_signature: str
    value_usd: float
    asset_symbol: str
    proposed_execution_price: float
    raw_calldata: str


class GuardrailAuditResult(BaseModel):
    intent_id: str
    agent_name: str
    passed: bool
    verdict: str  # "APPROVED" | "INTERCEPTED"
    violation_code: Optional[str] = None
    violation_detail: Optional[str] = None
    oracle_benchmark_price: Optional[float] = None
    price_deviation_pct: Optional[float] = None
    remaining_daily_budget_usd: float
    gas_cost_estimate: int
    security_flags: List[str] = Field(default_factory=list)
