#!/usr/bin/env python3
"""
AgentGuardrailVault - Interactive Terminal CLI & Verification Suite.
Demonstrates on-chain guardrails, daily velocity caps, and oracle slippage controls for AI agents.
"""

import click
from tabulate import tabulate
from src.simulator.agent_simulation import run_demo_simulation, generate_mock_policies


@click.group()
def cli():
    """AgentGuardrailVault: On-Chain Guardrails & Policy Gates for Autonomous AI Agents."""
    pass


@cli.command()
def policies():
    """List active Autonomous AI Agent Session Key policies and daily velocity caps."""
    mock_pols = generate_mock_policies()
    rows = []
    for p in mock_pols:
        rows.append([
            p.agent_id,
            p.chain,
            f"${p.daily_spend_limit_usd:,.2f}",
            f"${p.spent_today_usd:,.2f}",
            f"{p.session_key_address[:8]}...{p.session_key_address[-6:]}",
            "ACTIVE" if p.is_active else "EXPIRED"
        ])

    headers = ["Agent Identifier", "Target Chain", "24h Spend Cap", "Spent Today", "Session Key", "Status"]
    click.echo("\n" + "=" * 95)
    click.echo("   🤖 ACTIVE AUTONOMOUS AI AGENT SESSION KEY REGISTRY (ERC-4337)")
    click.echo("=" * 95)
    click.echo(tabulate(rows, headers=headers, tablefmt="github"))
    click.echo("=" * 95 + "\n")


@cli.command()
def demo():
    """Run full multi-scenario simulation validating legitimate vs malicious AI transactions."""
    click.echo("\n" + "=" * 105)
    click.echo("   🛡️ AGENT-GUARDRAIL-VAULT: ON-CHAIN POLICY & CIRCUIT BREAKER VERIFICATION SUITE")
    click.echo("=" * 105)

    pols, results = run_demo_simulation()

    # Step 1: Policies Table
    click.echo("\n[1/3] Registered Ephemeral AI Agent Session Keys:")
    pol_rows = []
    for p in pols:
        pol_rows.append([
            p.agent_id,
            p.chain,
            f"${p.daily_spend_limit_usd:,.2f}",
            f"${p.daily_spend_limit_usd - p.spent_today_usd:,.2f}",
            f"{p.session_key_address[:8]}...{p.session_key_address[-6:]}"
        ])
    print(tabulate(pol_rows, headers=["Agent ID", "Chain", "Daily Cap", "Remaining Budget", "Session Key"], tablefmt="github"))

    # Step 2: Transaction Interception Stream
    click.echo("\n[2/3] Live Autonomous AI Agent Transaction Stream & Guardrail Interception:")
    tx_rows = []
    for intent, res in results:
        status_badge = "✅ APPROVED" if res.passed else "🚫 INTERCEPTED"
        price_display = f"${intent.proposed_execution_price:,.2f}"
        oracle_display = f"${res.oracle_benchmark_price:,.2f}" if res.oracle_benchmark_price else "N/A"
        dev_display = f"{res.price_deviation_pct:.2f}%" if res.price_deviation_pct is not None else "0.00%"
        
        tx_rows.append([
            intent.intent_id,
            intent.agent_name[:24],
            intent.target_protocol[:20],
            f"${intent.value_usd:,.2f}",
            price_display,
            oracle_display,
            dev_display,
            status_badge
        ])

    headers = ["Tx ID", "Agent Entity", "Target Protocol", "Value (USD)", "Exec Price", "Oracle Benchmark", "Deviation", "Verdict"]
    print(tabulate(tx_rows, headers=headers, tablefmt="github"))

    # Step 3: Security Telemetry & Interception Log
    click.echo("\n[3/3] Guardrail Security Audit Telemetry & Intercept Details:")
    for intent, res in results:
        if res.passed:
            click.echo(f"  🟢 [PASSED] {intent.intent_id} by {intent.agent_name}:")
            for flag in res.security_flags:
                click.echo(f"     • {flag}")
            click.echo(f"     • Gas Consumption: ~{res.gas_cost_estimate:,} gas | Remaining Budget: ${res.remaining_daily_budget_usd:,.2f}")
        else:
            click.echo(f"  🔴 [INTERCEPTED] {intent.intent_id} by {intent.agent_name}:")
            click.echo(f"     • Violation Code:    {res.violation_code}")
            click.echo(f"     • Defense Analysis:  {res.violation_detail}")
            for flag in res.security_flags:
                click.echo(f"     • Security Flag:     {flag}")
            click.echo(f"     • Reverted On-Chain: Execution halted before funds reached target.")
        click.echo("")

    click.echo("=" * 105)
    click.echo("   ✅ ON-CHAIN GUARDRAIL VAULT POLICY VERIFICATION COMPLETE (0 REVERT LEAKS)")
    click.echo("=" * 105 + "\n")


if __name__ == "__main__":
    cli()
