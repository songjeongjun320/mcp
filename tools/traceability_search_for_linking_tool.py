"""
Traceability Search for Linking Tool
Search requirements available for linking with filtering and pagination.
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, List

load_dotenv()

def get_supabase() -> Client:
    """Initialize Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)

def traceability_search_for_linking_tool(
    organization_id: str,
    project_id: Optional[str] = None,
    document_id: Optional[str] = None,
    exclude_requirement_id: Optional[str] = None,
    search_query: Optional[str] = None,
    requirement_type: Optional[str] = None,
    status: Optional[List[str]] = None,
    exclude_existing_links: bool = True,
    max_results: int = 100,
    offset: int = 0
) -> dict:
    """
    Search requirements available for linking with filtering and pagination.

    Args:
        organization_id: Organization ID for scoping
        project_id: Optional project scope
        document_id: Optional document scope
        exclude_requirement_id: Exclude specific requirement
        search_query: Text search in name/description
        requirement_type: Filter by requirement type
        status: Filter by status values
        exclude_existing_links: Exclude already linked requirements
        max_results: Maximum results (default: 100)
        offset: Pagination offset (default: 0)

    Returns:
        {
            success: bool,
            requirements: list[{id, name, external_id, description, document_name,
                              project_name, status, type, can_link, existing_relationship}],
            pagination: {total, offset, limit, has_more},
            error: str | None
        }
    """
    try:
        sb = get_supabase()

        # Build base query with joins
        select_fields = """
            id, name, external_id, description, status, type,
            documents!inner(id, name, project_id, projects!inner(id, name, organization_id))
        """

        q = sb.table("requirements").select(select_fields).eq("is_deleted", False)

        # Organization scoping
        q = q.eq("documents.projects.organization_id", organization_id)

        # Project scoping
        if project_id:
            q = q.eq("documents.project_id", project_id)

        # Document scoping
        if document_id:
            q = q.eq("document_id", document_id)

        # Exclude specific requirement
        if exclude_requirement_id:
            q = q.neq("id", exclude_requirement_id)

        # Text search
        if search_query:
            q = q.or_(f"name.ilike.%{search_query}%,description.ilike.%{search_query}%")

        # Type filter
        if requirement_type:
            q = q.eq("type", requirement_type)

        # Status filter
        if status and len(status) > 0:
            q = q.in_("status", status)

        # Get total count for pagination
        count_resp = q.select("*", count="exact", head=True).execute()
        total_count = getattr(count_resp, "count", 0) or 0

        # Apply pagination
        start = offset
        end = offset + max_results - 1
        q = q.order("name").range(start, end)

        resp = q.execute()
        raw_requirements = getattr(resp, "data", []) or []

        # Process results
        requirements = []
        for req in raw_requirements:
            doc = req.get("documents", {}) or {}
            project = (doc.get("projects", {}) or {})

            processed_req = {
                "id": req["id"],
                "name": req["name"],
                "external_id": req.get("external_id"),
                "description": req.get("description"),
                "document_name": doc.get("name", ""),
                "project_name": project.get("name", ""),
                "status": req.get("status", ""),
                "type": req.get("type", ""),
                "can_link": True,
                "existing_relationship": None
            }

            requirements.append(processed_req)

        return {
            "success": True,
            "requirements": requirements,
            "pagination": {
                "total": total_count,
                "offset": offset,
                "limit": max_results,
                "has_more": offset + max_results < total_count
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "DATABASE_ERROR"
        }