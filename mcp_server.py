"""Auto-generated FastMCP server."""
import os
from typing import Any
from tools.pull_projects_tool import pull_projects_tool
from tools.pull_documents_tool import pull_documents_tool
from tools.pull_members_tool import pull_members_tool
from tools.mail_to_tool import mail_to_tool
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

organization_id = os.environ.get("organization_id")
message = os.environ.get("message")

# organization_id를 고정으로 사용하는 래퍼 함수들
def pull_projects(organization_id: str, message: str) -> Any:
    """
    Call this tool if user want to check, list up or retrieve detailed information about our projects. It provides all projects's information, names, and descriptions.
    
    Parameters
    ----------
        organization_id (str): Unique identifier of the organization to pull project ids from database
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    print("organization_id: ", organization_id)
    print("message: ", message)
    return pull_projects_tool(organization_id, message)

def pull_documents(organization_id: str, message: str) -> Any:
    """
    Get documents' names, descriptions from database

    Parameters
    ----------
        organization_id (str): Unique identifier of the organization to pull project ids and document ids from database
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    return pull_documents_tool(organization_id, message)

def pull_members(organization_id: str, message: str) -> Any:
    """
    Get member information from projects or organizations

    Parameters
    ----------
        organization_id (str): Unique identifier of the organization to pull project ids and document ids from database
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """    
    return pull_members_tool(organization_id, message)

def mail_to(organization_id: str, message: str):
    """
    Send email messages to specified recipients with attachment support

    Parameters
    ----------
        organization_id (str): Unique identifier of the organization to pull project ids and document ids from database
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
    
port = int(os.environ.get("PORT", 10000))

mcp = FastMCP("AtomsMCP", host="0.0.0.0", port=port)

mcp.add_tool(pull_projects)
mcp.add_tool(pull_documents)
mcp.add_tool(pull_members)
mcp.add_tool(mail_to)

if __name__ == "__main__":
    print(f"Starting MCP server on 0.0.0.0:{port}")
    mcp.run(transport="sse")