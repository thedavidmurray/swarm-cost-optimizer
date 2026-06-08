from __future__ import annotations
import json, os, time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RoutingDecision:
    model: str
    provider: str
    estimated_cost: float
    quality_score: float
    reason: str
    timestamp: float = field(default_factory=time.time)
    task_category: str = ""

class CostRouter:
    def __init__(self, agents_json: dict, budgets: Optional[dict] = None):
        self.agents = agents_json
        self.budgets = budgets or {}
        self._spend_log: list[dict] = []

    @classmethod
    def from_file(cls, path: str = "agents.json") -> "CostRouter":
        with open(path) as f:
            data = json.load(f)
        return cls(data.get("agents", {}), data.get("budgets", {}))

    def route(self, task: str, quality: str = "medium", max_cost: float = 0.10, profile: str = "default") -> RoutingDecision:
        agents = self.agents
        category = self._infer_category(task)
        candidates = []
        for name, cfg in agents.items():
            cost = cfg.get("cost_per_1k", 0.0)
            if cost > max_cost:
                continue
            q = cfg.get("quality", 0.5)
            if quality == "high" and q < 0.8:
                continue
            if quality == "low" and q > 0.6:
                continue
            candidates.append((name, cfg))
        if not candidates:
            candidates = list(agents.items())
        candidates.sort(key=lambda x: x[1].get("cost_per_1k", 0.0))
        best = candidates[0]
        decision = RoutingDecision(
            model=best[0],
            provider=best[1].get("provider", "unknown"),
            estimated_cost=best[1].get("cost_per_1k", 0.0),
            quality_score=best[1].get("quality", 0.5),
            reason=f"category={category} quality={quality} budget={max_cost}",
            task_category=category,
        )
        self._log(decision)
        return decision

    def _infer_category(self, task: str) -> str:
        t = task.lower()
        if any(k in t for k in ("design", "architecture", "system", "plan")):
            return "architecture"
        if any(k in t for k in ("code", "implement", "build", "fix", "debug")):
            return "coding"
        if any(k in t for k in ("research", "search", "find", "analyze")):
            return "research"
        return "routine"

    def _log(self, decision: RoutingDecision):
        entry = {
            "ts": decision.timestamp,
            "model": decision.model,
            "provider": decision.provider,
            "cost": decision.estimated_cost,
            "quality": decision.quality_score,
            "category": decision.task_category,
            "reason": decision.reason,
        }
        self._spend_log.append(entry)
        log_dir = os.path.expanduser("~/claude-projects/logs/cost-optimizer")
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/routing.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")

    def summary(self) -> dict:
        total = sum(e["cost"] for e in self._spend_log)
        return {
            "decisions": len(self._spend_log),
            "total_estimated_cost": round(total, 4),
            "models_used": sorted(set(e["model"] for e in self._spend_log)),
        }
