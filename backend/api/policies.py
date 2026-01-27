"""
Policy management API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..models.schemas import PolicyConfig
from ..engines.policy_engine import PolicyEngine

router = APIRouter()
logger = logging.getLogger(__name__)

policy_engine = PolicyEngine()


@router.get("/{repository}", response_model=PolicyConfig)
async def get_policy(repository: str):
    """Get policy configuration for a repository"""
    try:
        policy = policy_engine.get_policy(repository)
        return policy
    except Exception as e:
        logger.error(f"Failed to get policy for {repository}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{repository}", response_model=PolicyConfig)
async def update_policy(repository: str, policy: PolicyConfig):
    """Update policy configuration for a repository"""
    try:
        # In production, this would save to database or file system
        policy_engine.policies[repository] = policy
        return policy
    except Exception as e:
        logger.error(f"Failed to update policy for {repository}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rule-packs")
async def list_rule_packs():
    """List available rule packs"""
    return {
        "rule_packs": list(policy_engine.rule_packs.keys()),
        "details": {
            name: {
                "name": pack.get("name", name),
                "description": pack.get("description", ""),
                "rules_count": len(pack.get("rules", []))
            }
            for name, pack in policy_engine.rule_packs.items()
        }
    }
