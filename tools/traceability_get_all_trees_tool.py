"""
Traceability Get ALL Trees Tool
Get ALL projects' requirement tree views for an organization.
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid
import time
import json

load_dotenv()

# Debug mode
DEBUG = os.environ.get("DEBUG_TRACEABILITY", "true").lower() == "true"

def debug_print(message: str, data=None):
    """Print debug information if DEBUG is enabled"""
    if DEBUG:
        print(f"[TRACE_ALL] {message}")
        if data is not None:
            print(json.dumps(data, indent=2, default=str))

def get_supabase() -> Client:
    """Initialize Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    # Try SERVICE_ROLE_KEY first (has full permissions), then fallback to ANON_KEY
    key = (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or
           os.environ.get("SUPABASE_KEY") or
           os.environ.get("SUPABASE_ANON_KEY"))
    if not url or not key:
        raise ValueError("SUPABASE_URL and a valid key must be set")
    return create_client(url, key)

def traceability_get_all_trees_tool(
    organization_id: str,
    include_metadata: bool = True
) -> dict:
    """
    Get ALL projects' requirement tree views for an organization.

    This queries ALL projects in the organization and returns their hierarchy trees.

    Args:
        organization_id: Organization ID
        include_metadata: Include statistics and metadata

    Returns:
        {
            success: bool,
            organization_id: str,
            projects: list[{
                project_id: str,
                project_name: str,
                tree: list[...],
                hierarchy_view: list[str],
                metadata: dict
            }],
            summary: {
                total_projects: int,
                total_requirements: int,
                total_relationships: int,
                query_time_ms: int
            },
            error: str | None
        }
    """
    debug_print("=" * 80)
    debug_print(f"Starting traceability_get_all_trees_tool")
    debug_print(f"Organization ID: {organization_id}")

    try:
        uuid.UUID(organization_id)
        debug_print("[OK] organization_id UUID validation passed")
    except ValueError as e:
        debug_print(f"[ERROR] Invalid UUID format: {e}")
        return {
            "success": False,
            "error": "Invalid UUID format",
            "error_code": "INVALID_UUID"
        }

    try:
        sb = get_supabase()
        debug_print("[OK] Supabase client initialized")
        start_time = time.time()

        # Step 1: Get all projects in organization
        debug_print("\nStep 1: Getting all projects in organization...")
        projects_resp = sb.table("projects").select(
            "id, name, description"
        ).eq("organization_id", organization_id).execute()

        projects_data = getattr(projects_resp, "data", []) or []
        debug_print(f"[OK] Found {len(projects_data)} projects")

        if DEBUG and len(projects_data) > 0:
            debug_print("Projects:", [{"id": p["id"], "name": p["name"]} for p in projects_data])

        # Step 2: Get tree for each project
        debug_print("\nStep 2: Getting tree for each project...")
        all_projects = []
        total_requirements = 0
        total_relationships = 0

        for idx, project in enumerate(projects_data, 1):
            project_id = project["id"]
            project_name = project["name"]

            debug_print(f"\n  [{idx}/{len(projects_data)}] Processing: {project_name}")
            debug_print(f"  Project ID: {project_id}")

            # Call get_requirement_tree for this project
            tree_resp = sb.rpc("get_requirement_tree", {
                "p_project_id": project_id
            }).execute()

            tree_data = getattr(tree_resp, "data", []) or []
            debug_print(f"  [OK] Retrieved {len(tree_data)} nodes")

            # Filter to only show nodes in hierarchies
            filtered_tree = [
                node for node in tree_data
                if node.get("has_children", False) or node.get("depth", 0) > 0
            ]

            # Sort by path
            filtered_tree.sort(key=lambda x: x.get("path", ""))

            # Create hierarchy view
            hierarchy_view = []
            for node in filtered_tree:
                depth = node.get("depth", 0)
                title = node.get("title", "Unknown")
                indent = "  " * depth

                if depth == 0:
                    hierarchy_view.append(f"ROOT: {title}")
                else:
                    hierarchy_view.append(f"{indent}+-- {title}")

            # Count relationships (nodes with depth > 0)
            relationships = sum(1 for node in filtered_tree if node.get("depth", 0) > 0)

            project_result = {
                "project_id": project_id,
                "project_name": project_name,
                "tree": filtered_tree,
                "hierarchy_view": hierarchy_view
            }

            if include_metadata:
                root_nodes = sum(1 for node in filtered_tree if node.get("depth", 0) == 0)
                max_depth = max((node.get("depth", 0) for node in filtered_tree), default=0)

                project_result["metadata"] = {
                    "total_nodes": len(filtered_tree),
                    "root_nodes": root_nodes,
                    "max_depth": max_depth,
                    "relationships": relationships
                }

            all_projects.append(project_result)
            total_requirements += len(filtered_tree)
            total_relationships += relationships

            if DEBUG:
                debug_print(f"  Tree preview (first 5 lines):")
                for line in hierarchy_view[:5]:
                    print(f"    {line}")

        # Step 3: Build result
        debug_print(f"\nStep 3: Building final result...")
        result = {
            "success": True,
            "organization_id": organization_id,
            "projects": all_projects
        }

        if include_metadata:
            query_time_ms = int((time.time() - start_time) * 1000)
            result["summary"] = {
                "total_projects": len(all_projects),
                "total_requirements": total_requirements,
                "total_relationships": total_relationships,
                "query_time_ms": query_time_ms
            }

            debug_print("\nSummary:")
            debug_print(None, result["summary"])

        debug_print("\n[SUCCESS] All trees generated successfully")
        debug_print("=" * 80)
        return result

    except Exception as e:
        debug_print(f"\n[ERROR] {str(e)}")
        import traceback
        debug_print("Traceback:", traceback.format_exc())
        debug_print("=" * 80)
        return {
            "success": False,
            "error": str(e),
            "error_code": "DATABASE_ERROR"
        }
