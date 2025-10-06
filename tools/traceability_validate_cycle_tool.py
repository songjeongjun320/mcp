"""
Traceability Cycle Validation Tool
Validates if creating a relationship would cause a cycle using stored procedure.
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

def get_supabase() -> Client:
    """Initialize Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)

def traceability_validate_cycle_tool(
    organization_id: str,
    ancestor_id: str,
    descendant_id: str,
    max_depth: int = 100
) -> dict:
    """
    Validate if creating a relationship would cause a cycle.

    Args:
        organization_id: Organization ID for scoping
        ancestor_id: Proposed parent requirement ID
        descendant_id: Proposed child requirement ID
        max_depth: Maximum depth to check (default: 100)

    Returns:
        {
            success: bool,
            would_create_cycle: bool,
            cycle_path: list[{requirement_id, name, external_id}] | None,
            error: str | None
        }
    """
    try:
        # Validate UUIDs
        uuid.UUID(ancestor_id)
        uuid.UUID(descendant_id)
        uuid.UUID(organization_id)
    except ValueError:
        return {
            "success": False,
            "would_create_cycle": False,
            "error": "Invalid UUID format",
            "error_code": "INVALID_UUID"
        }

    # Check for self-reference
    if ancestor_id == descendant_id:
        return {
            "success": False,
            "would_create_cycle": True,
            "error": "Self-reference not allowed",
            "error_code": "SELF_REFERENCE_NOT_ALLOWED"
        }

    try:
        sb = get_supabase()

        # Call stored procedure for cycle detection
        resp = sb.rpc("check_requirement_cycle", {
            "p_ancestor_id": ancestor_id,
            "p_descendant_id": descendant_id
        }).execute()

        would_create_cycle = getattr(resp, "data", False) or False

        result = {
            "success": True,
            "would_create_cycle": would_create_cycle,
            "cycle_path": None
        }

        # If cycle detected, try to get path information
        if would_create_cycle:
            try:
                # Get path from descendant back to ancestor
                path_resp = sb.rpc("get_requirement_ancestors", {
                    "p_descendant_id": descendant_id,
                    "p_max_depth": max_depth
                }).execute()

                ancestors = getattr(path_resp, "data", []) or []

                # Build cycle path if ancestor is found in ancestors
                for ancestor in ancestors:
                    if ancestor.get("requirement_id") == ancestor_id:
                        result["cycle_path"] = [{
                            "requirement_id": ancestor_id,
                            "name": ancestor.get("title", ""),
                            "external_id": None
                        }]
                        break

            except Exception:
                # Cycle detection succeeded but path retrieval failed
                pass

        return result

    except Exception as e:
        return {
            "success": False,
            "would_create_cycle": False,
            "error": str(e),
            "error_code": "DATABASE_ERROR"
        }