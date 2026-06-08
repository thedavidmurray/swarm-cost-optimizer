import argparse, json, sys
from .router import CostRouter

def main():
    parser = argparse.ArgumentParser(description="Swarm Cost Optimizer")
    parser.add_argument("--config", default="agents.json", help="Path to agents config")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--quality", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--max-cost", type=float, default=0.10, help="Max cost per 1k tokens")
    parser.add_argument("--profile", default="default", help="Profile name")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("dashboard", nargs="?", help="Run dashboard")
    args = parser.parse_args()

    router = CostRouter.from_file(args.config)
    decision = router.route(args.task, quality=args.quality, max_cost=args.max_cost, profile=args.profile)
    out = {
        "model": decision.model,
        "provider": decision.provider,
        "estimated_cost": decision.estimated_cost,
        "quality_score": decision.quality_score,
        "reason": decision.reason,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"\u2705 Routed to {decision.model} ({decision.provider})")
        print(f"   Cost: ${decision.estimated_cost:.4f}/1k | Quality: {decision.quality_score:.2f}")
        print(f"   Reason: {decision.reason}")

if __name__ == "__main__":
    main()
