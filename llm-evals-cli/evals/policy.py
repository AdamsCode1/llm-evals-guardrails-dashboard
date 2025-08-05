"""Policy configuration and validation."""

from typing import Any, Dict

from pydantic import BaseModel, Field


class EvaluationPolicy(BaseModel):
    """Policy configuration for LLM evaluation."""
    
    max_latency_ms: int = Field(default=2000, description="Maximum allowed latency in milliseconds")
    require_accuracy: bool = Field(default=True, description="Whether to require accuracy match")
    enable_toxicity: bool = Field(default=True, description="Whether to enable toxicity checking")
    toxicity_threshold: float = Field(default=0.5, description="Toxicity threshold (0-1)")
    enable_pii: bool = Field(default=False, description="Whether to enable PII detection")
    
    class Config:
        extra = "forbid"  # Don't allow extra fields


def load_policy(policy_path: str) -> EvaluationPolicy:
    """Load policy from JSON file.
    
    Args:
        policy_path: Path to policy JSON file
        
    Returns:
        Validated policy configuration
    """
    import json
    from pathlib import Path
    
    path = Path(policy_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return EvaluationPolicy(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in policy file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading policy: {e}")


def policy_to_dict(policy: EvaluationPolicy) -> Dict[str, Any]:
    """Convert policy to dictionary."""
    return policy.model_dump()
