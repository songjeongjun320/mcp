"""
Traceability Get Tree Tool
Get complete requirement tree view for a project using get_requirement_tree() function.
This shows the hierarchical structure of all requirements in a project.
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid
import time
import json

load_dotenv()

# Debug mode - set to True to see detailed logging
DEBUG = os.environ.get("DEBUG_TRACEABILITY", "true").lower() == "true"

def debug_print(message: str, data=None):
    """Print debug information if DEBUG is enabled"""
    if DEBUG:
        print(f"[TRACE_TREE] {message}")
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

def traceability_get_tree_tool(
    project_id: str,
    include_metadata: bool = True
) -> dict:
    """
    Get complete requirement tree view for a project.
    This is the PRIMARY tool for viewing traceability hierarchy.

    Uses the get_requirement_tree() PostgreSQL function to retrieve:
    - All root nodes (requirements with no parents)
    - Complete hierarchical structure with parent-child relationships
    - Depth information for each node
    - Path strings showing the hierarchy

    Args:
        project_id: Project ID to get tree for
        include_metadata: Include statistics and metadata

    Returns:
        {
            success: bool,
            tree: list[{
                requirement_id: str,
                title: str,  # external_id or name
                parent_id: str | None,  # NULL for root nodes
                depth: int,  # 0 for root, 1, 2, ... for children
                path: str,  # e.g., "REQ-001 > REQ-002 > REQ-003"
                has_children: bool
            }],
            hierarchy_view: list[str],  # Human-readable hierarchy paths
            metadata: {
                total_nodes: int,
                root_nodes: int,
                max_depth: int,
                orphan_nodes: int,
                query_time_ms: int
            } | None,
            error: str | None
        }
    """
    debug_print("=" * 80)
    debug_print(f"Starting traceability_get_tree_tool with project_id: {project_id}")

    try:
        uuid.UUID(project_id)
        debug_print("[OK] project_id UUID validation passed")
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

        # Step 1: Call the get_requirement_tree stored procedure
        debug_print("\nStep 1: Calling get_requirement_tree() PostgreSQL function...")
        tree_resp = sb.rpc("get_requirement_tree", {
            "p_project_id": project_id
        }).execute()

        tree_data = getattr(tree_resp, "data", []) or []
        debug_print(f"[OK] Retrieved {len(tree_data)} total nodes from database")

        if DEBUG and len(tree_data) > 0:
            debug_print("\nSample raw data (first 3 nodes):", tree_data[:3])

        # Step 2: Get requirements_closure data for debugging
        debug_print("\nStep 2: Fetching requirements_closure data for analysis...")

        # Get all requirement IDs from tree
        req_ids = [node.get("requirement_id") for node in tree_data if node.get("requirement_id")]
        debug_print(f"Found {len(req_ids)} requirement IDs")

        if req_ids and DEBUG:
            # Fetch closure data
            closure_resp = sb.table("requirements_closure").select(
                "ancestor_id, descendant_id, depth"
            ).in_("ancestor_id", req_ids[:50]).execute()  # Limit for debugging

            closure_data = getattr(closure_resp, "data", []) or []
            debug_print(f"[OK] Retrieved {len(closure_data)} closure relationships")
            if len(closure_data) > 0:
                debug_print("Sample closure data (first 5):", closure_data[:5])

        # Step 3: Filter to only show nodes that are part of hierarchies
        debug_print("\nStep 3: Filtering nodes (has_children || depth > 0)...")
        filtered_tree = [
            node for node in tree_data
            if node.get("has_children", False) or node.get("depth", 0) > 0
        ]
        debug_print(f"[OK] Filtered to {len(filtered_tree)} nodes in hierarchies")
        debug_print(f"  Excluded {len(tree_data) - len(filtered_tree)} orphan nodes")

        # Step 4: Sort by path to maintain hierarchical order
        debug_print("\nStep 4: Sorting by path...")
        filtered_tree.sort(key=lambda x: x.get("path", ""))
        debug_print("[OK] Nodes sorted by hierarchical path")

        # Step 5: Create human-readable hierarchy view
        debug_print("\nStep 5: Creating human-readable hierarchy view...")
        hierarchy_view = []
        for node in filtered_tree:
            depth = node.get("depth", 0)
            title = node.get("title", "Unknown")
            indent = "  " * depth

            if depth == 0:
                hierarchy_view.append(f"ROOT: {title}")
            else:
                hierarchy_view.append(f"{indent}+-- {title}")

        debug_print(f"[OK] Created {len(hierarchy_view)} hierarchy view lines")

        if DEBUG and len(hierarchy_view) > 0:
            debug_print("\nHierarchy preview (first 10 lines):")
            for line in hierarchy_view[:10]:
                print(f"    {line}")

        # Step 6: Build result
        result = {
            "success": True,
            "tree": filtered_tree,
            "hierarchy_view": hierarchy_view
        }

        if include_metadata:
            query_time_ms = int((time.time() - start_time) * 1000)

            # Calculate statistics
            total_nodes = len(tree_data)
            filtered_nodes = len(filtered_tree)
            root_nodes = sum(1 for node in filtered_tree if node.get("depth", 0) == 0)
            orphan_nodes = total_nodes - filtered_nodes
            max_depth = max((node.get("depth", 0) for node in filtered_tree), default=0)

            result["metadata"] = {
                "total_nodes": filtered_nodes,
                "all_nodes_including_orphans": total_nodes,
                "root_nodes": root_nodes,
                "max_depth": max_depth,
                "orphan_nodes": orphan_nodes,
                "query_time_ms": query_time_ms
            }

            debug_print("\nMetadata:")
            debug_print(None, result["metadata"])

        debug_print("\n[SUCCESS] Tree view generated successfully")
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