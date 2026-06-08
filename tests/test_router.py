import json, tempfile, os
from swarm_cost_optimizer.router import CostRouter

def test_route_by_cost():
    agents = {
        "gpt-4o-mini": {"cost_per_1k": 0.01, "quality": 0.7, "provider": "openai"},
        "gpt-4o": {"cost_per_1k": 0.05, "quality": 0.9, "provider": "openai"},
        "claude-3-haiku": {"cost_per_1k": 0.02, "quality": 0.6, "provider": "anthropic"},
    }
    router = CostRouter(agents)
    d = router.route("Summarize this article", quality="low", max_cost=0.10)
    assert d.model == "claude-3-haiku"
    assert d.estimated_cost == 0.02

def test_route_by_quality():
    agents = {
        "gpt-4o-mini": {"cost_per_1k": 0.01, "quality": 0.7, "provider": "openai"},
        "gpt-4o": {"cost_per_1k": 0.05, "quality": 0.9, "provider": "openai"},
    }
    router = CostRouter(agents)
    d = router.route("Design a system architecture", quality="high", max_cost=0.10)
    assert d.model == "gpt-4o"
    assert d.quality_score == 0.9

def test_from_file():
    data = {"agents": {"llama-3-70b": {"cost_per_1k": 0.02, "quality": 0.8, "provider": "fireworks"}}, "budgets": {"default": 1.0}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name
    try:
        router = CostRouter.from_file(path)
        d = router.route("Test", quality="medium", max_cost=0.10)
        assert d.model == "llama-3-70b"
    finally:
        os.unlink(path)
