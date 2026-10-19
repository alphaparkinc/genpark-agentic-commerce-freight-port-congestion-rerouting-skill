# -*- coding: utf-8 -*-
"""Freight Port Congestion Rerouting Skill for GenPark Agentic Commerce."""
import json
from typing import Dict, Any

def assess_port_dwell_congestion_risk(port_code: str, current_median_berth_wait_days: float, container_free_days_allowed: int, daily_demurrage_rate_usd: float) -> Dict[str, Any]:
    excess_dwell_days = max(0.0, current_median_berth_wait_days - float(container_free_days_allowed))
    projected_penalty_usd = round(excess_dwell_days * daily_demurrage_rate_usd, 2)

    if excess_dwell_days > 4.0:
        congestion_status = "CRITICAL_BOTTLENECK"
        action = "Initiate emergency feeder vessel transshipment or dry port diversion."
    elif excess_dwell_days > 0.0:
        congestion_status = "MODERATE_DELAY"
        action = "Lodge priority drayage reservation and apply for extended container free time."
    else:
        congestion_status = "OPTIMAL_FLOW"
        action = "Port dwell within free-time allowance; no demurrage penalties expected."

    return {
        "port_code": port_code.upper(),
        "median_berth_wait_days": current_median_berth_wait_days,
        "contracted_free_days": container_free_days_allowed,
        "penalized_dwell_days": round(excess_dwell_days, 1),
        "daily_demurrage_rate_usd": daily_demurrage_rate_usd,
        "projected_demurrage_penalty_usd": projected_penalty_usd,
        "congestion_status": congestion_status,
        "recommended_logistics_action": action,
        "sentinel": "GenPark Global Ocean Freight Watchdog"
    }

def synthesize_intermodal_reroute_solution(destination_inland_hub: str, primary_port_congestion_cost_usd: float, secondary_port_drayage_cost_usd: float, secondary_port_rail_cost_usd: float) -> Dict[str, Any]:
    total_bypass_cost_usd = round(secondary_port_drayage_cost_usd + secondary_port_rail_cost_usd, 2)
    net_savings_usd = round(primary_port_congestion_cost_usd - total_bypass_cost_usd, 2)

    if net_savings_usd > 0.0:
        recommendation = "EXECUTE_SECONDARY_PORT_BYPASS"
        rationale = f"Bypassing congested terminal saves ${net_savings_usd} in net demurrage and late fulfillment penalties."
    else:
        recommendation = "MAINTAIN_ORIGINAL_BERTH_QUEUE"
        rationale = f"Intermodal rerouting surcharges (${total_bypass_cost_usd}) exceed primary port delay demurrage (${primary_port_congestion_cost_usd})."

    return {
        "destination_hub": destination_inland_hub,
        "primary_terminal_hold_cost_usd": primary_port_congestion_cost_usd,
        "reroute_intermodal_cost_usd": total_bypass_cost_usd,
        "net_arbitrage_savings_usd": net_savings_usd,
        "strategic_recommendation": recommendation,
        "decision_rationale": rationale
    }
