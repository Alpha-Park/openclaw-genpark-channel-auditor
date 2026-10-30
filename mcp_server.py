# -*- coding: utf-8 -*-
import sys, json
from client import OpenClawGenParkChannelAuditor

client = OpenClawGenParkChannelAuditor()

TOOLS = [
    {
        "name": "compute_shapley_attribution",
        "description": "Calculates cooperative game Shapley values across multi-touch marketing coalitions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "channels": {"type": "array", "items": {"type": "string"}},
                "coalition_values": {"type": "object"}
            },
            "required": ["channels", "coalition_values"]
        }
    },
    {
        "name": "compute_markov_removal_effects",
        "description": "Computes first-order Markov chain touchpoint graph removal effects and weights.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                "conversion_weights": {"type": "array", "items": {"type": "number"}}
            },
            "required": ["paths"]
        }
    },
    {
        "name": "audit_incrementality_lift",
        "description": "Audits test vs control incrementality lift, iROAS, and z-score significance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "test_conversions": {"type": "number"},
                "control_conversions": {"type": "number"},
                "test_spend": {"type": "number"},
                "control_spend": {"type": "number"}
            },
            "required": ["test_conversions", "control_conversions", "test_spend", "control_spend"]
        }
    }
]

def handle_request(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        params = req.get("params", {})
        tname = params.get("name")
        args = params.get("arguments", {})
        if tname == "compute_shapley_attribution":
            res = client.compute_shapley_attribution(args["channels"], args["coalition_values"])
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "compute_markov_removal_effects":
            res = client.compute_markov_removal_effects(args["paths"], args.get("conversion_weights"))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "audit_incrementality_lift":
            res = client.audit_incrementality_lift(args["test_conversions"], args["control_conversions"], args["test_spend"], args["control_spend"])
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32600, "message": "Invalid Request"}}

def main():
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
