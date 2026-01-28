"""
Policy management API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

try:
    from models.schemas import PolicyConfig
    from engines.policy_engine import PolicyEngine
except ImportError:
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
                "rules_count": len(pack.get("rules", [])),
                "version": pack.get("version", "1.0.0")
            }
            for name, pack in policy_engine.rule_packs.items()
        }
    }


@router.post("/rule-packs/upload")
async def upload_rule_pack(
    pack_name: str,
    pack_data: Dict[str, Any]
):
    """Upload a custom rule pack"""
    try:
        # Validate pack structure
        if "rules" not in pack_data:
            raise HTTPException(status_code=400, detail="Rule pack must contain 'rules' array")
        
        # Add to policy engine
        policy_engine.rule_packs[pack_name] = pack_data
        
        # In production, save to file system or database
        logger.info(f"Custom rule pack uploaded: {pack_name} with {len(pack_data.get('rules', []))} rules")
        
        return {
            "status": "success",
            "pack_name": pack_name,
            "rules_count": len(pack_data.get("rules", []))
        }
    except Exception as e:
        logger.error(f"Failed to upload rule pack: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organizations/{org_name}")
async def get_organization_policy(org_name: str):
    """Get policy configuration for an organization"""
    try:
        # Check for organization-specific policy
        org_policy_path = f"config/policies/organizations/{org_name}.yaml"
        policy = policy_engine.get_policy(f"org:{org_name}")
        return policy
    except Exception as e:
        logger.error(f"Failed to get organization policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/organizations/{org_name}")
async def update_organization_policy(org_name: str, policy: PolicyConfig):
    """Update policy configuration for an organization"""
    try:
        # In production, save to database or file system
        policy_engine.policies[f"org:{org_name}"] = policy
        return policy
    except Exception as e:
        logger.error(f"Failed to update organization policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))
