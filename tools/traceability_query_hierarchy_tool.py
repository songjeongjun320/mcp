"""
Traceability Query Hierarchy Tool
Query hierarchical relationships using stored procedures.
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid
import time

load_dotenv()

def get_supabase() -> Client:
    """Initialize Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)

def traceability_query_hierarchy_tool(
    organization_id: str,
    requirement_id: str,
    direction: str = "both",
    max_depth: int = 10,
    include_metadata: bool = True
) -> dict:
    """
    Query hierarchical relationships using stored procedures.

    Args:
        organization_id: Organization ID for scoping
        requirement_id: Root requirement ID
        direction: Query direction (ancestors/descendants/both)
        max_depth: Maximum depth to traverse
        include_metadata: Include timing and count metadata

    Returns:
        {
            success: bool,
            requirement: {id, name, external_id, description},
            relationships: list[{id, name, external_id, relationship_type, depth, path}],
            metadata: {total_count, max_depth_reached, query_time_ms} | None,
            error: str | None
        }
    """
    if direction not in ["ancestors", "descendants", "both"]:
        return {
            "success": False,
            "error": "Invalid direction. Must be 'ancestors', 'descendants', or 'both'",
            "error_code": "INVALID_PARAMETER"
        }

    try:
        uuid.UUID(requirement_id)
        uuid.UUID(organization_id)
    except ValueError:
        return {
            "success": False,
            "error": "Invalid UUID format",
            "error_code": "INVALID_UUID"
        }

    try:
        sb = get_supabase()
        start_time = time.time()

        # Get base requirement info with org validation
        req_resp = sb.table("requirements").select(
            "id, name, external_id, description, documents!inner(project_id, projects!inner(organization_id))"
        ).eq("id", requirement_id).eq("documents.projects.organization_id", organization_id).single().execute()

        base_req = getattr(req_resp, "data", None)
        if not base_req:
            return {
                "success": False,
                "error": "Requirement not found or access denied",
                "error_code": "REQUIREMENT_NOT_FOUND"
            }

        relationships = []

        # Query ancestors
        if direction in ["ancestors", "both"]:
            try:
                ancestors_resp = sb.rpc("get_requirement_ancestors", {
                    "p_descendant_id": requirement_id,
                    "p_max_depth": max_depth
                }).execute()

                ancestors = getattr(ancestors_resp, "data", []) or []
                for ancestor in ancestors:
                    relationships.append({
                        "id": ancestor.get("requirement_id"),
                        "name": ancestor.get("title", ""),
                        "external_id": None,
                        "description": None,
                        "relationship_type": "ancestor",
                        "depth": ancestor.get("depth", 0),
                        "path": None,
                        "has_children": ancestor.get("direct_parent", False)
                    })
            except Exception:
                pass

        # Query descendants
        if direction in ["descendants", "both"]:
            try:
                descendants_resp = sb.rpc("get_requirement_descendants", {
                    "p_ancestor_id": requirement_id,
                    "p_max_depth": max_depth
                }).execute()

                descendants = getattr(descendants_resp, "data", []) or []
                for descendant in descendants:
                    relationships.append({
                        "id": descendant.get("requirement_id"),
                        "name": descendant.get("title", ""),
                        "external_id": None,
                        "description": None,
                        "relationship_type": "descendant",
                        "depth": descendant.get("depth", 0),
                        "path": None,
                        "has_children": descendant.get("direct_parent", False)
                    })
            except Exception:
                pass

        result = {
            "success": True,
            "requirement": {
                "id": base_req["id"],
                "name": base_req["name"],
                "external_id": base_req.get("external_id"),
                "description": base_req.get("description")
            },
            "relationships": relationships
        }

        if include_metadata:
            query_time_ms = int((time.time() - start_time) * 1000)
            result["metadata"] = {
                "total_count": len(relationships),
                "max_depth_reached": any(r["depth"] >= max_depth for r in relationships),
                "query_time_ms": query_time_ms
            }

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "DATABASE_ERROR"
        }