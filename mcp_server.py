"""Auto-generated FastMCP server."""
import os
from typing import Any
from tools.pull_projects_tool import pull_projects_tool
from tools.pull_documents_tool import pull_documents_tool
from tools.pull_members_tool import pull_members_tool
from tools.mail_to_tool import mail_to_tool
from tools.get_documents_by_projects_tool import get_documents_by_projects_tool
from tools.task_assign_tool import task_assign_tool
from tools.analyze_doc_tool import analyze_doc_tool
from tools.get_project_issues_tool import get_project_issues_tool
from tools.progress_reporting_tool import progress_reporting_tool
from tools.milestone_tracking_tool import milestone_tracking_tool
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

def get_documents_by_projects(organization_id: str, message: str) -> Any:
    """
    Get documents from specific projects within an organization

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): User's request message containing project specifications

    Returns
    -------
    Any
        Structured result containing documents from specified projects
    """
    result = get_documents_by_projects_tool(organization_id, message)
    return clean_result(result)

def task_assign(organization_id: str, message: str) -> Any:
    """
    Retrieve task assignments for team members in projects

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): User's request message for task assignment information

    Returns
    -------
    Any
        Structured result containing task assignments by team members and projects
    """
    result = task_assign_tool(organization_id, message)
    return clean_result(result)

def analyze_doc(organization_id: str, message: str) -> Any:
    """
    Analyze document content and provide AI-powered summary and insights

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): User's request message specifying which document to analyze

    Returns
    -------
    Any
        Structured result containing document analysis and AI-generated summary
    """
    result = analyze_doc_tool(organization_id, message)
    return clean_result(result)

def get_project_issues(organization_id: str, message: str) -> Any:
    """
    Retrieve all issues/tasks from projects within an organization

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): User's request message for project issues information

    Returns
    -------
    Any
        Structured result containing issues/tasks from all projects
    """
    result = get_project_issues_tool(organization_id, message)
    return clean_result(result)

def progress_reporting(organization_id: str, message: str) -> Any:
    """
    Generate comprehensive progress reports for projects in an organization

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): User's request message for progress reporting

    Returns
    -------
    Any
        Structured result containing detailed progress reports for all projects
    """
    result = progress_reporting_tool(organization_id, message)
    return clean_result(result)

def milestone_tracking(organization_id: str, message: str) -> Any:
    """
    Track and analyze project milestones and key achievements

    Parameters
    ----------
        organization_id (str): User's individual organization_id. Get this from mcp.json.
        message (str): User's request message for milestone tracking

    Returns
    -------
    Any
        Structured result containing milestone tracking data and analysis
    """
    result = milestone_tracking_tool(organization_id, message)
    return clean_result(result)
    
port = int(os.environ.get("PORT", 10000))

mcp = FastMCP("AtomsMCP", host="0.0.0.0", port=port)

mcp.add_tool(pull_projects)
mcp.add_tool(pull_documents)
mcp.add_tool(pull_members)
# mcp.add_tool(mail_to)

# Add new tools
mcp.add_tool(get_documents_by_projects)
mcp.add_tool(task_assign)
mcp.add_tool(analyze_doc)
mcp.add_tool(get_project_issues)
mcp.add_tool(progress_reporting)
mcp.add_tool(milestone_tracking)

if __name__ == "__main__":
    print(f"Starting MCP server on 0.0.0.0:{port}")
    mcp.run(transport="sse")