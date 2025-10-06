"""Auto-generated FastMCP server."""
import os
from typing import Any
from tools.pull_projects_tool import pull_projects_tool
from tools.pull_documents_tool import pull_documents_tool
from tools.pull_members_tool import pull_members_tool
from tools.mail_to_tool import mail_to_tool
from tools.traceability_query_hierarchy_tool import traceability_query_hierarchy_tool
from tools.traceability_get_tree_tool import traceability_get_tree_tool
from tools.traceability_get_all_trees_tool import traceability_get_all_trees_tool
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

organization_id = os.environ.get("organization_id")
message = os.environ.get("message")

# Helper function to clean up technical fields
def clean_result(result):
    """Remove technical fields like IDs from the result"""
    if isinstance(result, dict) and "json" in result:
        # Remove top-level technical fields
        technical_fields = ["project_ids", "user_ids", "document_ids", "id"]
        for field in technical_fields:
            if field in result["json"]:
                del result["json"][field]
        
        # Recursively clean nested structures
        _clean_nested_ids(result["json"])
    
    return result

def _clean_nested_ids(data):
    """Recursively remove id fields from nested data structures"""
    if isinstance(data, list):
        for item in data:
            _clean_nested_ids(item)
    elif isinstance(data, dict):
        # Remove id fields
        if "id" in data:
            del data["id"]
        # Continue cleaning nested structures
        for value in data.values():
            _clean_nested_ids(value)

# organization_id를 고정으로 사용하는 래퍼 함수들
def pull_projects(organization_id: str, message: str) -> Any:
    """
    Call tool if user want to check, list up or retrieve detailed information about our projects. It provides all projects's information, names, and descriptions.
    
    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    print("organization_id: ", organization_id)
    print("message: ", message)
    result = pull_projects_tool(organization_id, message)
    return clean_result(result)

def pull_documents(organization_id: str, message: str) -> Any:
    """
    If user wants to get documents' names, descriptions from database

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    return pull_documents_tool(organization_id, message)

def pull_members(organization_id: str, message: str) -> Any:
    """
    If user wants to get member information from projects or organizations

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """    
    result = pull_members_tool(organization_id, message)
    return clean_result(result)

def mail_to(organization_id: str, message: str):
    """
    If user wants to send email messages to specified recipients with attachment support

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        sender (str): name of the sender
        recipient (str): name of the recipient
        recipient_email (str): recipient's email address
        subject (str): subject of the email
        body (str): body of the email
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    return mail_to_tool(organization_id, message)

# Commented out - tool files not present
# def get_documents_by_projects(organization_id: str, message: str) -> Any:
#     result = get_documents_by_projects_tool(organization_id, message)
#     return clean_result(result)

# def task_assign(organization_id: str, message: str) -> Any:
#     result = task_assign_tool(organization_id, message)
#     return clean_result(result)

# def analyze_doc(organization_id: str, message: str) -> Any:
#     result = analyze_doc_tool(organization_id, message)
#     return clean_result(result)

# def get_project_issues(organization_id: str, message: str) -> Any:
#     result = get_project_issues_tool(organization_id, message)
#     return clean_result(result)

# def progress_reporting(organization_id: str, message: str) -> Any:
#     result = progress_reporting_tool(organization_id, message)
#     return clean_result(result)

# def milestone_tracking(organization_id: str, message: str) -> Any:
#     result = milestone_tracking_tool(organization_id, message)
#     return clean_result(result)


def traceability_query_hierarchy(
    organization_id: str,
    requirement_id: str,
    direction: str = "both",
    max_depth: int = 10,
    include_metadata: bool = True
) -> Any:
    """
    Query hierarchical relationships (ancestors/descendants) for a requirement.
    Useful for understanding requirement dependencies and structure.

    Parameters
    ----------
        organization_id (str): User's individual organization_id
        requirement_id (str): UUID of the requirement to query
        direction (str): 'ancestors', 'descendants', or 'both' (default: 'both')
        max_depth (int): Maximum depth to traverse (default: 10)
        include_metadata (bool): Include timing and count metadata (default: True)

    Returns
    -------
    Any
        {
            success: bool,
            requirement: dict,
            relationships: list,
            metadata: dict | None,
            error: str | None
        }
    """
    result = traceability_query_hierarchy_tool(
        organization_id, requirement_id, direction, max_depth, include_metadata
    )
    return clean_result(result)


def traceability_get_tree(
    project_id: str,
    include_metadata: bool = True
) -> Any:
    """
    Get the complete hierarchical tree view for a SINGLE project.

    Shows parent-child relationships, depth levels, and full hierarchy path
    for all requirements in the specified project.

    Parameters
    ----------
        project_id (str): UUID of the project to get tree for
        include_metadata (bool): Include statistics (total nodes, root nodes, max depth)

    Returns
    -------
    Any
        {
            success: bool,
            tree: list[{
                requirement_id: str,
                title: str,
                parent_id: str | None,
                depth: int,
                path: str,
                has_children: bool
            }],
            hierarchy_view: list[str],
            metadata: dict | None,
            error: str | None
        }
    """
    result = traceability_get_tree_tool(project_id, include_metadata)
    return clean_result(result)

def traceability_get_all_trees(
    organization_id: str,
    include_metadata: bool = True
) -> Any:
    """
    **RECOMMENDED** Get ALL projects' traceability trees for an organization.

    This is the most convenient way to see all traceability hierarchies at once.
    Returns trees for every project in the organization.

    Use this when you want to see the complete traceability picture across
    all projects, instead of querying each project individually.

    Parameters
    ----------
        organization_id (str): User's organization ID
        include_metadata (bool): Include statistics for each project

    Returns
    -------
    Any
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
    result = traceability_get_all_trees_tool(organization_id, include_metadata)
    return clean_result(result)
    
port = int(os.environ.get("PORT", 10000))

mcp = FastMCP("AtomsMCP", host="0.0.0.0", port=port)

mcp.add_tool(pull_projects)
mcp.add_tool(pull_documents)
mcp.add_tool(pull_members)
# mcp.add_tool(mail_to)

# Add new tools
# mcp.add_tool(get_documents_by_projects)
# mcp.add_tool(task_assign)
# mcp.add_tool(analyze_doc)
# mcp.add_tool(get_project_issues)
# mcp.add_tool(progress_reporting)
# mcp.add_tool(milestone_tracking)

# Add traceability tools
mcp.add_tool(traceability_get_all_trees)  # RECOMMENDED - get all projects at once
mcp.add_tool(traceability_get_tree)  # Get single project tree
mcp.add_tool(traceability_query_hierarchy)  # Query specific requirement relationships

if __name__ == "__main__":
    print(f"Starting MCP server on 0.0.0.0:{port}")
    mcp.run(transport="sse")