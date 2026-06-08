from typing import Optional
import requests

class ProviderRegistry:
    """Tracks provider health and costs."""
    
    PROVIDERS = {
        "fireworks": {"url": "https://api.fireworks.ai/inference/v1/models", "healthy": True},
        "openrouter": {"url": "https://openrouter.ai/api/v1/models", "healthy": True},
        "cerebras": {"url": "https://api.cerebras.ai/v1/models", "healthy": True},
        "groq": {"url": "https://api.groq.com/openai/v1/models", "healthy": True},
        "anthropic": {"url": "https://api.anthropic.com/v1/models", "healthy": True},
    }
    
    def __init__(self):
        self.status = {}
    
    def check_health(self, provider: str) -> bool:
        cfg = self.PROVIDERS.get(provider)
        if not cfg:
            return False
        try:
            r = requests.get(cfg["url"], timeout=5)
            ok = r.status_code == 200
            self.status[provider] = ok
            return ok
        except Exception:
            self.status[provider] = False
            return False
    
    def all_healthy(self) -> dict:
        return {p: self.check_health(p) for p in self.PROVIDERS}
