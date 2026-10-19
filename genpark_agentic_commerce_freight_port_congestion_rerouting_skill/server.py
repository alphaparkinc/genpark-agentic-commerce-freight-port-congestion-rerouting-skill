# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Freight Port Congestion Rerouting & Demurrage Sentinel Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "assess_port_dwell_congestion_risk",
    "description": "Analyze incoming vessel ETA, port container dwell time, and assess demurrage fine escalation risk.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "port_code": {
          "type": "string",
          "description": "e.g. USLAX, USLGB, NLRTM, CNSHA"
        },
        "current_median_berth_wait_days": {
          "type": "number"
        },
        "container_free_days_allowed": {
          "type": "integer"
        },
        "daily_demurrage_rate_usd": {
          "type": "number"
        }
      },
      "required": [
        "port_code",
        "current_median_berth_wait_days",
        "container_free_days_allowed",
        "daily_demurrage_rate_usd"
      ]
    }
  },
  {
    "name": "synthesize_intermodal_reroute_solution",
    "description": "Calculate trade-off between ocean anchorage waiting fees and expedited intermodal rail/truck bypass from secondary port.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "destination_inland_hub": {
          "type": "string"
        },
        "primary_port_congestion_cost_usd": {
          "type": "number"
        },
        "secondary_port_drayage_cost_usd": {
          "type": "number"
        },
        "secondary_port_rail_cost_usd": {
          "type": "number"
        }
      },
      "required": [
        "destination_inland_hub",
        "primary_port_congestion_cost_usd",
        "secondary_port_drayage_cost_usd",
        "secondary_port_rail_cost_usd"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-agentic-commerce-freight-port-congestion-rerouting-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-agentic-commerce-freight-port-congestion-rerouting-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "assess_port_dwell_congestion_risk",
            "arguments": {
                "port_code": "USLAX",
                "current_median_berth_wait_days": 8.5,
                "container_free_days_allowed": 4,
                "daily_demurrage_rate_usd": 275.0
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: assess_port_dwell_congestion_risk")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
