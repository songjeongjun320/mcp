"""
Traceability Generate Matrix Tool
Generate comprehensive traceability matrix for a project.
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

def traceability_generate_matrix_tool(
    organization_id: str,
    project_id: str,
    include_documents: bool = True,
    relationship_types: Optional[List[str]] = None,
    include_orphans: bool = True
) -> dict:
    """
    Generate comprehensive traceability matrix for a project.

    Args:
        organization_id: Organization ID for scoping
        project_id: Project ID to analyze
        include_documents: Include document information
        relationship_types: Filter specific relationship types
        include_orphans: Include requirements with no links

    Returns:
        {
            success: bool,
            matrix: {
                requirements: list[{id, name, external_id, document_name,
                                  parent_count, child_count, total_links}],
                relationships: list[{source_id, target_id, type, description}],
                statistics: {total_requirements, total_relationships,
                           orphan_requirements, coverage_percentage}
            },
            error: str | None
        }
    """
    try:
        sb = get_supabase()

        # Get all requirements in project with org validation
        req_select = "id, name, external_id, document_id"
        if include_documents:
            req_select += ", documents!inner(name, project_id, projects!inner(organization_id))"
        else:
            req_select += ", documents!inner(project_id, projects!inner(organization_id))"

        req_resp = sb.table("requirements").select(req_select).eq(
            "documents.project_id", project_id
        ).eq("documents.projects.organization_id", organization_id).eq("is_deleted", False).execute()

        requirements_data = getattr(req_resp, "data", []) or []

        # Get all trace links for these requirements
        req_ids = [req["id"] for req in requirements_data]

        if not req_ids:
            return {
                "success": True,
                "matrix": {
                    "requirements": [],
                    "relationships": [],
                    "statistics": {
                        "total_requirements": 0,
                        "total_relationships": 0,
                        "orphan_requirements": 0,
                        "coverage_percentage": 0.0
                    }
                }
            }

        # Get relationships
        links_q = sb.table("trace_links").select(
            "source_id, target_id, link_type, description"
        ).eq("is_deleted", False)

        # Filter by relationship types if specified
        if relationship_types:
            links_q = links_q.in_("link_type", relationship_types)

        # Get links where either source or target is in our requirements
        links_q = links_q.or_(
            f"source_id.in.({','.join(req_ids)}),target_id.in.({','.join(req_ids)})"
        )

        links_resp = links_q.execute()
        relationships_data = getattr(links_resp, "data", []) or []

        # Process requirements with link counts
        requirements = []
        requirement_link_counts = {}

        # Count links for each requirement
        for req in requirements_data:
            req_id = req["id"]
            parent_count = sum(1 for link in relationships_data if link["target_id"] == req_id)
            child_count = sum(1 for link in relationships_data if link["source_id"] == req_id)
            total_links = parent_count + child_count

            requirement_link_counts[req_id] = total_links

            req_data = {
                "id": req_id,
                "name": req["name"],
                "external_id": req.get("external_id"),
                "parent_count": parent_count,
                "child_count": child_count,
                "total_links": total_links
            }

            if include_documents:
                doc = req.get("documents", {}) or {}
                req_data["document_name"] = doc.get("name", "")
            else:
                req_data["document_name"] = ""

            requirements.append(req_data)

        # Filter orphans if requested
        if not include_orphans:
            requirements = [req for req in requirements if req["total_links"] > 0]

        # Process relationships
        relationships = []
        for link in relationships_data:
            relationships.append({
                "source_id": link["source_id"],
                "target_id": link["target_id"],
                "type": link["link_type"],
                "description": link.get("description")
            })

        # Calculate statistics
        total_requirements = len(requirements_data)
        total_relationships = len(relationships)
        orphan_requirements = sum(1 for count in requirement_link_counts.values() if count == 0)
        coverage_percentage = ((total_requirements - orphan_requirements) / total_requirements * 100) if total_requirements > 0 else 0.0

        return {
            "success": True,
            "matrix": {
                "requirements": requirements,
                "relationships": relationships,
                "statistics": {
                    "total_requirements": total_requirements,
                    "total_relationships": total_relationships,
                    "orphan_requirements": orphan_requirements,
                    "coverage_percentage": round(coverage_percentage, 2)
                }
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "DATABASE_ERROR"
        }
